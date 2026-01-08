import { EventEmitter } from "events";
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
    cpu: {
        usage: number;
        count: number;
    };
    memory: {
        used: number;
        total: number;
        percentage: number;
    };
    disk: {
        used: number;
        total: number;
        percentage: number;
    };
    processes: {
        mcp: boolean;
        tauri: boolean;
    };
    network: {
        connected: boolean;
        latency?: number;
    };
    errors: Array<{
        timestamp: string;
        type: string;
        message: string;
        severity: "low" | "medium" | "high" | "critical";
    }>;
}
export declare class SystemManagementAgent extends EventEmitter {
    private logDir;
    private healthCheckInterval;
    private metricsInterval;
    private logRotationInterval;
    private startTime;
    private errorLog;
    private metrics;
    private maxErrorsLog;
    private maxMetricsLog;
    private consecutiveFailures;
    private config;
    constructor(logDir?: string);
    private initializeLogging;
    /**
     * Start all monitoring services
     */
    start(): Promise<void>;
    /**
     * Stop all monitoring services
     */
    stop(): Promise<void>;
    performHealthCheck(): Promise<HealthStatus>;
    private checkMCPServerRunning;
    private checkMCPServerResponsive;
    private checkTauriAppRunning;
    private checkNetworkConnectivity;
    private checkDiskSpace;
    private getCPUUsage;
    private getMemoryUsage;
    private getRecentErrorCount;
    private restartMCPServer;
    private restartTauriApp;
    private collectMetrics;
    log(level: "debug" | "info" | "warn" | "error", message: string, data?: unknown): void;
    private rotateLogsIfNeeded;
    getMetrics(): Promise<SystemMetrics[]>;
    getLatestMetrics(): SystemMetrics | null;
    saveMetrics(): Promise<void>;
    /**
     * Export Prometheus metrics format
     */
    getPrometheusMetrics(): string;
    getSystemStatus(): Promise<{
        health: HealthStatus;
        metrics: SystemMetrics | null;
        uptime: string;
    }>;
    private formatUptime;
}
export default SystemManagementAgent;
//# sourceMappingURL=monitoring-agent.d.ts.map