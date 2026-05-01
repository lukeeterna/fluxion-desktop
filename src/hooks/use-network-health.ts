// ═══════════════════════════════════════════════════════════════════
// FLUXION - Network Health Hook (S184 α.2 STEP 5)
// Detect first-run offline state per mostrare modal fallback Sara → Piper
// ═══════════════════════════════════════════════════════════════════

import { useEffect, useState } from "react";

const PROXY_HEALTH_URL = "https://fluxion-proxy.gianlucanewtech.workers.dev/health";
const HEALTH_TIMEOUT_MS = 5000;

export type NetworkStatus = "checking" | "online" | "offline" | "limited";

export interface NetworkHealth {
  status: NetworkStatus;
  /** navigator.onLine (browser-level) */
  browserOnline: boolean;
  /** FLUXION proxy CF Worker raggiungibile (5s timeout) */
  proxyReachable: boolean;
  /** Re-check forzato — utile dopo che utente ripristina rete */
  recheck: () => void;
}

/**
 * Verifica connettività di rete + raggiungibilità FLUXION proxy CF Worker.
 *
 * Stati:
 *  - `checking`: prima ispezione in corso
 *  - `online`: navigator + proxy entrambi OK → Sara qualità max (Edge-TTS)
 *  - `limited`: navigator OK ma proxy KO → DNS/firewall/proxy CF down
 *  - `offline`: navigator KO → fallback Sara → Piper locale automatico
 */
export function useNetworkHealth(): NetworkHealth {
  const [status, setStatus] = useState<NetworkStatus>("checking");
  const [browserOnline, setBrowserOnline] = useState<boolean>(
    typeof navigator !== "undefined" ? navigator.onLine : true,
  );
  const [proxyReachable, setProxyReachable] = useState<boolean>(false);
  const [tick, setTick] = useState<number>(0);

  // Browser online/offline events
  useEffect(() => {
    const handleOnline = (): void => setBrowserOnline(true);
    const handleOffline = (): void => setBrowserOnline(false);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Proxy health check
  useEffect(() => {
    let cancelled = false;
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);

    const check = async (): Promise<void> => {
      if (!browserOnline) {
        if (!cancelled) {
          setProxyReachable(false);
          setStatus("offline");
        }
        return;
      }
      try {
        const response = await fetch(PROXY_HEALTH_URL, {
          method: "GET",
          signal: controller.signal,
          // Cache disabled per first-run check accurato
          cache: "no-store",
        });
        if (cancelled) return;
        if (response.ok) {
          setProxyReachable(true);
          setStatus("online");
        } else {
          setProxyReachable(false);
          setStatus("limited");
        }
      } catch {
        if (cancelled) return;
        setProxyReachable(false);
        // Se browser dice online ma fetch fallisce → connettivita' limitata
        setStatus(browserOnline ? "limited" : "offline");
      } finally {
        window.clearTimeout(timeoutId);
      }
    };

    setStatus("checking");
    void check();

    return () => {
      cancelled = true;
      controller.abort();
      window.clearTimeout(timeoutId);
    };
  }, [browserOnline, tick]);

  const recheck = (): void => setTick((n) => n + 1);

  return { status, browserOnline, proxyReachable, recheck };
}
