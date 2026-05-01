// ═══════════════════════════════════════════════════════════════════
// FLUXION - First-Run Network Modal (S184 α.2 STEP 5)
// Mostra modal al primo avvio se rete offline / proxy CF irraggiungibile.
// Reassicura utente che gestionale + Sara funzionano comunque (Piper locale).
// ═══════════════════════════════════════════════════════════════════

import { useEffect, useState, type ReactElement } from "react";
import { useNetworkHealth } from "@/hooks/use-network-health";

const DISMISS_KEY = "fluxion-network-modal-dismissed-v1";

export function FirstRunNetworkModal(): ReactElement | null {
  const { status, recheck } = useNetworkHealth();
  const [dismissed, setDismissed] = useState<boolean>(false);

  // Carica stato dismiss da localStorage (sopravvive a refresh, non a reinstall)
  useEffect(() => {
    try {
      if (window.localStorage.getItem(DISMISS_KEY) === "1") {
        setDismissed(true);
      }
    } catch {
      // localStorage non disponibile (modalità privata) — modal mostrata sempre
    }
  }, []);

  const handleDismiss = (): void => {
    try {
      window.localStorage.setItem(DISMISS_KEY, "1");
    } catch {
      // ignore
    }
    setDismissed(true);
  };

  const handleRetry = (): void => {
    recheck();
  };

  // Non mostrare se: già dismissato, ancora in checking, o tutto online
  if (dismissed) return null;
  if (status === "checking") return null;
  if (status === "online") return null;

  const isOffline = status === "offline";
  const title = isOffline
    ? "Sei offline — FLUXION funziona comunque"
    : "Connessione limitata — alcune funzioni potrebbero rallentare";

  const body = isOffline
    ? "FLUXION funziona al 100% offline (calendario, clienti, servizi, fatture). Sara passa automaticamente alla voce locale (Piper) — qualità leggermente inferiore ma reattiva. Quando torni online, FLUXION usa di nuovo la voce premium (Edge-TTS)."
    : "Il tuo computer è connesso a internet ma il server FLUXION non risponde. Possibili cause: DNS aziendale, firewall, o manutenzione momentanea. Sara passa alla voce locale (Piper). Riprova fra qualche minuto.";

  return (
    <div
      data-testid="first-run-network-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="frnm-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
    >
      <div className="w-full max-w-md rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl p-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-950 flex items-center justify-center flex-shrink-0">
            <svg
              className="w-6 h-6 text-amber-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d={
                  isOffline
                    ? "M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"
                    : "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                }
              />
            </svg>
          </div>

          <div className="flex-1 min-w-0">
            <h2 id="frnm-title" className="text-white text-lg font-bold mb-2">
              {title}
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed mb-4">{body}</p>

            <div className="bg-slate-800/60 rounded-lg p-3 mb-4 border border-slate-700">
              <p className="text-slate-400 text-xs leading-relaxed">
                <strong className="text-slate-200">Cosa funziona offline:</strong> calendario, clienti, fatturazione,
                servizi, operatori, schede.
                <br />
                <strong className="text-slate-200">Cosa richiede internet:</strong> Sara con voce premium (Edge-TTS),
                WhatsApp Business API, aggiornamenti.
              </p>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                data-testid="frnm-retry"
                onClick={handleRetry}
                className="flex-1 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 text-sm font-medium transition-colors"
              >
                Riprova
              </button>
              <button
                type="button"
                data-testid="frnm-dismiss"
                onClick={handleDismiss}
                className="flex-1 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium transition-colors"
              >
                Continua offline
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
