import * as fs from "fs";
import * as path from "path";
import * as net from "net";
import { EventEmitter } from "events";
import os from "os";
import { exec, spawn } from "child_process";
import { setInterval, clearInterval } from "timers";

// ============================================================================
// Types
// ============================================================================

export interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  timestamp: string;
  checks: {
    mcpServerRunning: boolean;
    mcpServerResponsive: boolean;
    tauriAppRunning: boolean;
    networkConnectivity: boolean;
    diskSpace: boolean;
    cpuUsage: number;
    memoryUsage: number;
    errorCount: number;
  };
  issues: string[];
  suggestions: string[];
}

export interface SystemMetrics {
  timestamp: string;
  uptime: number;
  cpu: { usage: number; count: number };
  memory: { used: number; total: number; percentage: number };
  disk: { used: number; total: number; percentage: number };
  processes: { mcp: boolean; tauri: boolean };
  network: { connected: boolean; latency?: number };
  errors: Array<{
    timestamp: string;
    type: string;
    message: string;
    severity: "low" | "medium" | "high" | "critical";
  }>;
}

// ============================================================================
// Management Agent
// ============================================================================

export class SystemManagementAgent extends EventEmitter {
  private logDir: string;
  private healthCheckInterval: ReturnType<typeof setInterval> | null = null;
  private metricsInterval: ReturnType<typeof setInterval> | null = null;
  private logRotationInterval: ReturnType<typeof setInterval> | null = null;
  private startTime: number = Date.now();
  private errorLog: Array<{
    timestamp: string;
    type: string;
    message: string;
    severity: string;
  }> = [];
  private metrics: SystemMetrics[] = [];
  private maxErrorsLog: number = 1000;
  private maxMetricsLog: number = 1000;
  private consecutiveFailures: number = 0;

  // Configuration
  private config = {
    healthCheckInterval: 5000, // 5 seconds
    metricsCollectionInterval: 10000, // 10 seconds
    logRotationInterval: 3600000, // 1 hour
    logRetentionDays: 7,
    autoRestartThreshold: 3, // Restart if 3 consecutive failures
    diskSpaceThreshold: 0.1, // Alert if <10% free
    cpuThreshold: 85,
    memoryThreshold: 85,
    errorThreshold: 10, // Alert if >10 errors in 5 minutes
  };

  constructor(logDir: string = "./logs") {
    super();
    this.logDir = logDir;
    this.initializeLogging();
  }

  // ========================================================================
  // Initialization
  // ========================================================================

  private initializeLogging(): void {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }

    this.log("info", "System Management Agent initialized", {
      logDir: this.logDir,
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Start all monitoring services
   */
  async start(): Promise<void> {
    this.log("info", "Starting System Management Agent");

    // Start health checks
    this.healthCheckInterval = setInterval(
      () => this.performHealthCheck(),
      this.config.healthCheckInterval
    );

    // Start metrics collection
    this.metricsInterval = setInterval(
      () => this.collectMetrics(),
      this.config.metricsCollectionInterval
    );

    // Start log rotation
    this.logRotationInterval = setInterval(
      () => this.rotateLogsIfNeeded(),
      this.config.logRotationInterval
    );

    // Initial health check
    await this.performHealthCheck();

    this.log("info", "System Management Agent started");
    this.emit("agent_started");
  }

  /**
   * Stop all monitoring services
   */
  async stop(): Promise<void> {
    this.log("info", "Stopping System Management Agent");

    if (this.healthCheckInterval) clearInterval(this.healthCheckInterval);
    if (this.metricsInterval) clearInterval(this.metricsInterval);
    if (this.logRotationInterval) clearInterval(this.logRotationInterval);

    await this.saveMetrics();
    this.log("info", "System Management Agent stopped");
    this.emit("agent_stopped");
  }

  // ========================================================================
  // Health Checks
  // ========================================================================

  async performHealthCheck(): Promise<HealthStatus> {
    try {
      const checks = {
        mcpServerRunning: await this.checkMCPServerRunning(),
        mcpServerResponsive: await this.checkMCPServerResponsive(),
        tauriAppRunning: await this.checkTauriAppRunning(),
        networkConnectivity: await this.checkNetworkConnectivity(),
        diskSpace: await this.checkDiskSpace(),
        cpuUsage: this.getCPUUsage(),
        memoryUsage: this.getMemoryUsage(),
        errorCount: this.getRecentErrorCount(),
      };

      const issues: string[] = [];
      const suggestions: string[] = [];

      // Analyze checks
      if (!checks.mcpServerRunning) {
        issues.push("MCP Server is not running");
        suggestions.push("Restart MCP server: npm start");
      }

      if (!checks.mcpServerResponsive && checks.mcpServerRunning) {
        issues.push("MCP Server is running but not responding");
        suggestions.push("Check MCP server logs for errors");
      }

      if (!checks.tauriAppRunning) {
        issues.push("Tauri app is not running");
        suggestions.push("Start Tauri app: npm run dev");
      }

      if (!checks.networkConnectivity) {
        issues.push("Network connectivity issue");
        suggestions.push("Check SSH tunnel and network configuration");
      }

      if (!checks.diskSpace) {
        issues.push("Low disk space (<10% free)");
        suggestions.push("Clean up old logs and temporary files");
      }

      if (checks.cpuUsage > this.config.cpuThreshold) {
        issues.push(`High CPU usage: ${checks.cpuUsage.toFixed(1)}%`);
        suggestions.push("Check for resource leaks or intensive processes");
      }

      if (checks.memoryUsage > this.config.memoryThreshold) {
        issues.push(`High memory usage: ${checks.memoryUsage.toFixed(1)}%`);
        suggestions.push("Restart MCP server or Tauri app");
      }

      if (checks.errorCount > this.config.errorThreshold) {
        issues.push(`Too many errors: ${checks.errorCount} in last 5 min`);
        suggestions.push("Review error logs and check system configuration");
      }

      const status: HealthStatus = {
        status:
          issues.length === 0
            ? "healthy"
            : issues.length <= 2
              ? "degraded"
              : "unhealthy",
        timestamp: new Date().toISOString(),
        checks,
        issues,
        suggestions,
      };

      // Log status
      if (status.status !== "healthy") {
        this.log("warn", "Health check detected issues", status);
        this.emit("health_alert", status);
        this.consecutiveFailures++;

        // Try auto-recovery after threshold
        if (this.consecutiveFailures >= this.config.autoRestartThreshold) {
          if (!checks.mcpServerResponsive) {
            this.log("info", "Attempting MCP server recovery...");
            await this.restartMCPServer();
          }
          if (!checks.tauriAppRunning) {
            this.log("info", "Attempting Tauri app recovery...");
            await this.restartTauriApp();
          }
          this.consecutiveFailures = 0;
        }
      } else {
        this.consecutiveFailures = 0;
        this.log("debug", "Health check: all systems healthy");
      }

      this.emit("health_check", status);
      return status;
    } catch (error) {
      this.log(
        "error",
        "Health check failed",
        error instanceof Error ? error.message : String(error)
      );

      return {
        status: "unhealthy",
        timestamp: new Date().toISOString(),
        checks: {
          mcpServerRunning: false,
          mcpServerResponsive: false,
          tauriAppRunning: false,
          networkConnectivity: false,
          diskSpace: false,
          cpuUsage: 0,
          memoryUsage: 0,
          errorCount: 0,
        },
        issues: ["Health check failed"],
        suggestions: ["Check system logs for details"],
      };
    }
  }

  private async checkMCPServerRunning(): Promise<boolean> {
    return new Promise((resolve) => {
      exec("lsof -i :5000 | grep node", (error) => {
        resolve(!error);
      });
    });
  }

  private async checkMCPServerResponsive(): Promise<boolean> {
    return new Promise((resolve) => {
      const socket = new net.Socket();

      socket.setTimeout(2000);
      socket.on("connect", () => {
        socket.destroy();
        resolve(true);
      });
      socket.on("error", () => resolve(false));
      socket.on("timeout", () => {
        socket.destroy();
        resolve(false);
      });

      socket.connect(5000, "localhost");
    });
  }

  private async checkTauriAppRunning(): Promise<boolean> {
    return new Promise((resolve) => {
      exec("lsof -i :1420", (error) => {
        resolve(!error);
      });
    });
  }

  private async checkNetworkConnectivity(): Promise<boolean> {
    return new Promise((resolve) => {
      exec("ping -c 1 -t 3 8.8.8.8", (error) => {
        resolve(!error);
      });
    });
  }

  private async checkDiskSpace(): Promise<boolean> {
    return new Promise((resolve) => {
      exec(
        "df / | tail -1 | awk '{print $5}' | sed 's/%//'",
        (error, stdout) => {
          if (error) {
            resolve(false);
            return;
          }
          const usage = parseInt(stdout.trim(), 10);
          resolve(usage < 90); // Alert if >90% used
        }
      );
    });
  }

  private getCPUUsage(): number {
    const cpus = os.cpus();
    let totalIdle = 0;
    let totalTick = 0;

    for (const cpu of cpus) {
      for (const type in cpu.times) {
        totalTick += cpu.times[type as keyof typeof cpu.times];
      }
      totalIdle += cpu.times.idle;
    }

    return 100 - (100 * totalIdle) / totalTick;
  }

  private getMemoryUsage(): number {
    const totalMemory = os.totalmem();
    const freeMemory = os.freemem();
    const usedMemory = totalMemory - freeMemory;
    return (usedMemory / totalMemory) * 100;
  }

  private getRecentErrorCount(): number {
    const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
    return this.errorLog.filter(
      (e) => new Date(e.timestamp).getTime() > fiveMinutesAgo
    ).length;
  }

  // ========================================================================
  // Auto-Recovery
  // ========================================================================

  private async restartMCPServer(): Promise<void> {
    try {
      this.log("warn", "Restarting MCP server...");

      exec("pkill -f 'node.*mcp'", () => {
        setTimeout(() => {
          const projectDir = process.cwd().replace("/mcp-server-ts", "");
          spawn("node", [`${projectDir}/mcp-server-ts/build/index.js`], {
            detached: true,
            stdio: "ignore",
          }).unref();

          this.log("info", "MCP server restart initiated");
          this.emit("mcp_restarted");
        }, 2000);
      });
    } catch (error) {
      this.log(
        "error",
        "Failed to restart MCP server",
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  private async restartTauriApp(): Promise<void> {
    try {
      this.log("warn", "Restarting Tauri app...");

      exec("pkill -f 'tauri.*dev'", () => {
        setTimeout(() => {
          const projectDir = process.cwd().replace("/mcp-server-ts", "");
          spawn("npm", ["run", "dev"], {
            cwd: projectDir,
            detached: true,
            stdio: "ignore",
          }).unref();

          this.log("info", "Tauri app restart initiated");
          this.emit("tauri_restarted");
        }, 3000);
      });
    } catch (error) {
      this.log(
        "error",
        "Failed to restart Tauri app",
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  // ========================================================================
  // Metrics Collection
  // ========================================================================

  private async collectMetrics(): Promise<SystemMetrics> {
    const metrics: SystemMetrics = {
      timestamp: new Date().toISOString(),
      uptime: (Date.now() - this.startTime) / 1000,
      cpu: {
        usage: this.getCPUUsage(),
        count: os.cpus().length,
      },
      memory: {
        used: os.totalmem() - os.freemem(),
        total: os.totalmem(),
        percentage: this.getMemoryUsage(),
      },
      disk: {
        used: 0,
        total: 0,
        percentage: 0,
      },
      processes: {
        mcp: await this.checkMCPServerRunning(),
        tauri: await this.checkTauriAppRunning(),
      },
      network: {
        connected: await this.checkNetworkConnectivity(),
      },
      errors: this.errorLog.slice(-10).map((e) => ({
        ...e,
        severity: e.severity as "low" | "medium" | "high" | "critical",
      })),
    };

    this.metrics.push(metrics);
    if (this.metrics.length > this.maxMetricsLog) {
      this.metrics = this.metrics.slice(-this.maxMetricsLog);
    }

    return metrics;
  }

  // ========================================================================
  // Logging
  // ========================================================================

  public log(
    level: "debug" | "info" | "warn" | "error",
    message: string,
    data?: unknown
  ): void {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data,
    };

    // Console output
    const icon =
      level === "info"
        ? "[INFO]"
        : level === "warn"
          ? "[WARN]"
          : level === "error"
            ? "[ERROR]"
            : "[DEBUG]";
    console.log(`[${timestamp}] ${icon} ${message}`);
    if (data && level !== "debug") {
      console.log(JSON.stringify(data, null, 2));
    }

    // File logging (structured JSON)
    try {
      const logFile = path.join(
        this.logDir,
        `system-${new Date().toISOString().split("T")[0]}.log`
      );
      fs.appendFileSync(logFile, JSON.stringify(logEntry) + "\n");
    } catch {
      // Ignore file write errors
    }

    // Track errors
    if (level === "error") {
      this.errorLog.push({
        timestamp,
        type: message,
        message: typeof data === "string" ? data : JSON.stringify(data),
        severity: "high",
      });

      if (this.errorLog.length > this.maxErrorsLog) {
        this.errorLog = this.errorLog.slice(-this.maxErrorsLog);
      }
    }
  }

  private async rotateLogsIfNeeded(): Promise<void> {
    try {
      const logFiles = fs.readdirSync(this.logDir);
      const now = Date.now();
      const maxAge = this.config.logRetentionDays * 24 * 60 * 60 * 1000;

      for (const file of logFiles) {
        const filePath = path.join(this.logDir, file);
        const stat = fs.statSync(filePath);

        if (now - stat.mtimeMs > maxAge) {
          fs.unlinkSync(filePath);
          this.log("debug", `Rotated old log file: ${file}`);
        }
      }
    } catch (error) {
      this.log(
        "error",
        "Log rotation failed",
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  // ========================================================================
  // Metrics Export
  // ========================================================================

  public async getMetrics(): Promise<SystemMetrics[]> {
    return this.metrics;
  }

  public getLatestMetrics(): SystemMetrics | null {
    return this.metrics.length > 0 ? this.metrics[this.metrics.length - 1] : null;
  }

  public async saveMetrics(): Promise<void> {
    try {
      const metricsFile = path.join(this.logDir, "metrics.json");
      fs.writeFileSync(metricsFile, JSON.stringify(this.metrics, null, 2));
      this.log("debug", "Metrics saved to file");
    } catch (error) {
      this.log(
        "error",
        "Failed to save metrics",
        error instanceof Error ? error.message : String(error)
      );
    }
  }

  /**
   * Export Prometheus metrics format
   */
  public getPrometheusMetrics(): string {
    const latest = this.getLatestMetrics();
    if (!latest) return "";

    return `# HELP mcp_system_uptime_seconds System uptime in seconds
# TYPE mcp_system_uptime_seconds gauge
mcp_system_uptime_seconds ${latest.uptime}

# HELP mcp_cpu_usage_percent CPU usage percentage
# TYPE mcp_cpu_usage_percent gauge
mcp_cpu_usage_percent ${latest.cpu.usage}

# HELP mcp_memory_usage_percent Memory usage percentage
# TYPE mcp_memory_usage_percent gauge
mcp_memory_usage_percent ${latest.memory.percentage}

# HELP mcp_mcp_server_running MCP Server running status
# TYPE mcp_mcp_server_running gauge
mcp_mcp_server_running ${latest.processes.mcp ? 1 : 0}

# HELP mcp_tauri_app_running Tauri App running status
# TYPE mcp_tauri_app_running gauge
mcp_tauri_app_running ${latest.processes.tauri ? 1 : 0}

# HELP mcp_network_connected Network connectivity status
# TYPE mcp_network_connected gauge
mcp_network_connected ${latest.network.connected ? 1 : 0}

# HELP mcp_error_count Recent error count
# TYPE mcp_error_count gauge
mcp_error_count ${latest.errors.length}
`;
  }

  // ========================================================================
  // Status Reports
  // ========================================================================

  public async getSystemStatus(): Promise<{
    health: HealthStatus;
    metrics: SystemMetrics | null;
    uptime: string;
  }> {
    const health = await this.performHealthCheck();
    const metrics = this.getLatestMetrics();
    const uptime = this.formatUptime((Date.now() - this.startTime) / 1000);

    return { health, metrics, uptime };
  }

  private formatUptime(seconds: number): string {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    return `${days}d ${hours}h ${minutes}m`;
  }
}

export default SystemManagementAgent;
