// ═══════════════════════════════════════════════════════════════════
// FLUXION - First Run Wizard (S184 α.3.1-E)
// 8-step pre-flight check al primo avvio post-install:
//   1. Welcome (intro privacy + cosa controlleremo)
//   2. Network probe → CF Worker /health (Sara online vs offline)
//   3. Microphone permission probe (getUserMedia + OS guidance)
//   4. DB path writable + cloud-sync detection (consume α.3.0-B)
//   5. Ports 3001/3002 collision detection
//   6. Voice agent /health
//   7. AV/Defender guidance (only Windows)
//   8. Complete (CTA continua)
//
// Persiste flag `fluxion-preflight-completed-v1` in localStorage.
// Mostrato BEFORE SetupWizard nel flow App.tsx.
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect, useCallback, type ReactElement } from "react";
import { invoke } from "@tauri-apps/api/core";

// ───────────────────────────────────────────────────────────────────
// Types (mirror Rust commands/preflight.rs)
// ───────────────────────────────────────────────────────────────────

interface NetworkCheck {
  online: boolean;
  status: "online" | "limited" | "offline" | string;
  proxy_reachable: boolean;
  latency_ms: number | null;
  message: string;
}

interface MicGuidance {
  os: string;
  permission_url: string | null;
  instructions: string[];
}

interface DbPathCheck {
  path: string;
  writable: boolean;
  cloud_provider: string | null;
  free_disk_bytes: number;
  warning: string | null;
}

interface PortsCheck {
  http_bridge_busy: boolean;
  voice_pipeline_busy: boolean;
  conflict: boolean;
  message: string;
}

interface VoiceReadyCheck {
  ready: boolean;
  status: string;
  version: string | null;
  error: string | null;
}

type StepStatus = "idle" | "running" | "ok" | "warn" | "fail";

type MicStatus = "idle" | "asking" | "granted" | "denied" | "unsupported";

const COMPLETED_KEY = "fluxion-preflight-completed-v1";

interface FirstRunWizardProps {
  onComplete: () => void;
}

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: StepStatus }): ReactElement {
  const palette: Record<StepStatus, { bg: string; text: string; label: string }> = {
    idle: { bg: "bg-slate-800", text: "text-slate-400", label: "In attesa" },
    running: { bg: "bg-cyan-900/60", text: "text-cyan-300", label: "Verifica…" },
    ok: { bg: "bg-emerald-900/60", text: "text-emerald-300", label: "OK" },
    warn: { bg: "bg-amber-900/60", text: "text-amber-300", label: "Attenzione" },
    fail: { bg: "bg-red-900/60", text: "text-red-300", label: "Errore" },
  };
  const p = palette[status];
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${p.bg} ${p.text}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          status === "ok"
            ? "bg-emerald-400"
            : status === "warn"
              ? "bg-amber-400"
              : status === "fail"
                ? "bg-red-400"
                : status === "running"
                  ? "bg-cyan-400 animate-pulse"
                  : "bg-slate-600"
        }`}
      />
      {p.label}
    </span>
  );
}

function formatBytes(bytes: number): string {
  if (bytes <= 0) return "—";
  const gb = bytes / (1024 * 1024 * 1024);
  if (gb >= 1) return `${gb.toFixed(1)} GB`;
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(0)} MB`;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export function FirstRunWizard({ onComplete }: FirstRunWizardProps): ReactElement {
  const [step, setStep] = useState<number>(1);
  const totalSteps = 8;

  // Probe results
  const [network, setNetwork] = useState<NetworkCheck | null>(null);
  const [networkStatus, setNetworkStatus] = useState<StepStatus>("idle");

  const [micStatus, setMicStatus] = useState<MicStatus>("idle");
  const [micGuidance, setMicGuidance] = useState<MicGuidance | null>(null);

  const [dbCheck, setDbCheck] = useState<DbPathCheck | null>(null);
  const [dbStatus, setDbStatus] = useState<StepStatus>("idle");

  const [ports, setPorts] = useState<PortsCheck | null>(null);
  const [portsStatus, setPortsStatus] = useState<StepStatus>("idle");

  const [voice, setVoice] = useState<VoiceReadyCheck | null>(null);
  const [voiceStatus, setVoiceStatus] = useState<StepStatus>("idle");

  // ── Probes ──────────────────────────────────────────────────────
  const runNetwork = useCallback(async () => {
    setNetworkStatus("running");
    try {
      const result = await invoke<NetworkCheck>("check_network");
      setNetwork(result);
      setNetworkStatus(
        result.status === "online" ? "ok" : result.status === "limited" ? "warn" : "warn",
      );
    } catch (err) {
      setNetwork({
        online: false,
        status: "offline",
        proxy_reachable: false,
        latency_ms: null,
        message: `Errore probe: ${String(err)}`,
      });
      setNetworkStatus("warn");
    }
  }, []);

  const runMic = useCallback(async () => {
    // Always load OS guidance first (Rust)
    try {
      const guide = await invoke<MicGuidance>("check_mic");
      setMicGuidance(guide);
    } catch {
      // ignore
    }
    if (
      typeof navigator === "undefined" ||
      !navigator.mediaDevices ||
      typeof navigator.mediaDevices.getUserMedia !== "function"
    ) {
      setMicStatus("unsupported");
      return;
    }
    setMicStatus("asking");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((t) => t.stop());
      setMicStatus("granted");
    } catch {
      setMicStatus("denied");
    }
  }, []);

  const runDb = useCallback(async () => {
    setDbStatus("running");
    try {
      const result = await invoke<DbPathCheck>("check_db_path");
      setDbCheck(result);
      if (!result.writable) setDbStatus("fail");
      else if (result.cloud_provider) setDbStatus("warn");
      else if (result.warning) setDbStatus("warn");
      else setDbStatus("ok");
    } catch (err) {
      setDbCheck({
        path: "—",
        writable: false,
        cloud_provider: null,
        free_disk_bytes: 0,
        warning: `Errore probe: ${String(err)}`,
      });
      setDbStatus("fail");
    }
  }, []);

  const runPorts = useCallback(async () => {
    setPortsStatus("running");
    try {
      const result = await invoke<PortsCheck>("check_ports");
      setPorts(result);
      setPortsStatus(result.conflict ? "warn" : "ok");
    } catch (err) {
      setPorts({
        http_bridge_busy: false,
        voice_pipeline_busy: false,
        conflict: false,
        message: `Errore probe: ${String(err)}`,
      });
      setPortsStatus("warn");
    }
  }, []);

  const runVoice = useCallback(async () => {
    setVoiceStatus("running");
    try {
      const result = await invoke<VoiceReadyCheck>("check_voice_ready");
      setVoice(result);
      setVoiceStatus(result.ready ? "ok" : "warn");
    } catch (err) {
      setVoice({
        ready: false,
        status: "probe_failed",
        version: null,
        error: `Errore probe: ${String(err)}`,
      });
      setVoiceStatus("warn");
    }
  }, []);

  // Auto-run probe quando si entra in uno step
  useEffect(() => {
    if (step === 2 && networkStatus === "idle") void runNetwork();
    if (step === 4 && dbStatus === "idle") void runDb();
    if (step === 5 && portsStatus === "idle") void runPorts();
    if (step === 6 && voiceStatus === "idle") void runVoice();
  }, [
    step,
    networkStatus,
    dbStatus,
    portsStatus,
    voiceStatus,
    runNetwork,
    runDb,
    runPorts,
    runVoice,
  ]);

  const handleComplete = useCallback(() => {
    try {
      window.localStorage.setItem(COMPLETED_KEY, "1");
    } catch {
      // ignore
    }
    onComplete();
  }, [onComplete]);

  const handleSkip = useCallback(() => {
    // Skip all (utente vuole saltare): comunque marcato come "visto"
    handleComplete();
  }, [handleComplete]);

  const goNext = (): void => setStep((s) => Math.min(s + 1, totalSteps));
  const goBack = (): void => setStep((s) => Math.max(s - 1, 1));

  const isWindows =
    micGuidance?.os === "windows" ||
    (typeof navigator !== "undefined" && /Win/i.test(navigator.platform));

  // ── Render ──────────────────────────────────────────────────────
  return (
    <div
      data-testid="first-run-wizard"
      className="min-h-screen bg-slate-900 flex items-center justify-center p-4"
    >
      <div className="w-full max-w-2xl rounded-2xl border border-slate-700 bg-slate-950 shadow-2xl">
        {/* Header con progress */}
        <div className="px-6 pt-6 pb-4 border-b border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <img
                src="/logo_fluxion.jpg"
                alt="Fluxion"
                style={{ width: 40, height: 40, borderRadius: 8, objectFit: "cover" }}
              />
              <div>
                <h1 className="text-white text-base font-bold leading-tight">
                  Verifica iniziale FLUXION
                </h1>
                <p className="text-slate-400 text-xs">
                  Passo {step} di {totalSteps}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleSkip}
              data-testid="frw-skip"
              className="text-xs text-slate-500 hover:text-slate-300"
            >
              Salta verifica
            </button>
          </div>
          <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-cyan-500 transition-all duration-300"
              style={{ width: `${(step / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Body */}
        <div className="px-6 py-6 min-h-[320px]">
          {step === 1 && (
            <div data-testid="frw-step-welcome">
              <h2 className="text-white text-xl font-bold mb-3">Benvenuto in FLUXION</h2>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                Prima di iniziare, eseguiamo qualche controllo veloce per assicurarci
                che FLUXION funzioni al meglio sul tuo computer:
              </p>
              <ul className="space-y-2 text-slate-300 text-sm">
                <li>✓ Connessione a internet (per la voce premium di Sara)</li>
                <li>✓ Permesso al microfono (per parlare con Sara)</li>
                <li>✓ Cartella dati scrivibile (no rischio cloud-sync)</li>
                <li>✓ Porte di rete libere (3001, 3002)</li>
                <li>✓ Voice agent attivo</li>
              </ul>
              <div className="mt-4 bg-slate-800/60 border border-slate-700 rounded-lg p-3">
                <p className="text-slate-400 text-xs leading-relaxed">
                  <strong className="text-slate-200">Privacy</strong>: questi controlli
                  restano sul tuo computer. Nessun dato cliente viene mai inviato
                  durante la verifica.
                </p>
              </div>
            </div>
          )}

          {step === 2 && (
            <div data-testid="frw-step-network">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-white text-xl font-bold">Connessione internet</h2>
                <StatusBadge status={networkStatus} />
              </div>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                Stiamo verificando se il server FLUXION è raggiungibile. Se non lo è,
                Sara passa automaticamente alla voce locale (Piper) e tutto il resto
                continua a funzionare.
              </p>
              <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-4 text-sm">
                <p className="text-slate-200">
                  {network?.message ?? "Verifica in corso…"}
                </p>
                {network?.latency_ms !== null && network?.latency_ms !== undefined && (
                  <p className="text-slate-500 text-xs mt-2">
                    Latenza: {network.latency_ms}ms
                  </p>
                )}
              </div>
              <button
                type="button"
                onClick={() => void runNetwork()}
                className="mt-3 px-3 py-1.5 text-xs rounded bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200"
              >
                Riprova
              </button>
            </div>
          )}

          {step === 3 && (
            <div data-testid="frw-step-mic">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-white text-xl font-bold">Permesso microfono</h2>
                <StatusBadge
                  status={
                    micStatus === "granted"
                      ? "ok"
                      : micStatus === "denied" || micStatus === "unsupported"
                        ? "warn"
                        : micStatus === "asking"
                          ? "running"
                          : "idle"
                  }
                />
              </div>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                Sara ha bisogno del microfono per ascoltare i clienti. Premi il
                pulsante: il sistema operativo ti chiederà conferma.
              </p>
              {micStatus === "idle" && (
                <button
                  type="button"
                  onClick={() => void runMic()}
                  data-testid="frw-mic-request"
                  className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium"
                >
                  Richiedi accesso al microfono
                </button>
              )}
              {micStatus === "asking" && (
                <p className="text-cyan-300 text-sm">In attesa della tua conferma…</p>
              )}
              {micStatus === "granted" && (
                <div className="bg-emerald-900/30 border border-emerald-700/50 rounded-lg p-3 text-sm text-emerald-200">
                  Microfono accessibile — Sara è pronta ad ascoltare.
                </div>
              )}
              {(micStatus === "denied" || micStatus === "unsupported") && (
                <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-4 text-sm">
                  <p className="text-amber-200 font-medium mb-2">
                    Permesso non concesso (puoi configurare manualmente)
                  </p>
                  {micGuidance?.instructions && (
                    <ol className="list-decimal list-inside text-slate-300 space-y-1 text-xs">
                      {micGuidance.instructions.map((line, i) => (
                        <li key={i}>{line}</li>
                      ))}
                    </ol>
                  )}
                  <button
                    type="button"
                    onClick={() => void runMic()}
                    className="mt-3 px-3 py-1.5 text-xs rounded bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200"
                  >
                    Riprova
                  </button>
                </div>
              )}
            </div>
          )}

          {step === 4 && (
            <div data-testid="frw-step-db">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-white text-xl font-bold">Cartella dati</h2>
                <StatusBadge status={dbStatus} />
              </div>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                Verifichiamo che FLUXION possa salvare i tuoi dati e che la cartella
                non sia sotto sincronizzazione cloud (rischio corruzione database).
              </p>
              {dbCheck && (
                <div className="space-y-3 text-sm">
                  <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-3">
                    <p className="text-slate-400 text-xs uppercase tracking-wide mb-1">
                      Percorso
                    </p>
                    <p className="text-slate-200 font-mono text-xs break-all">
                      {dbCheck.path}
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-3">
                      <p className="text-slate-400 text-xs uppercase">Scrivibile</p>
                      <p
                        className={`text-sm font-medium ${dbCheck.writable ? "text-emerald-400" : "text-red-400"}`}
                      >
                        {dbCheck.writable ? "Sì" : "No"}
                      </p>
                    </div>
                    <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-3">
                      <p className="text-slate-400 text-xs uppercase">Spazio libero</p>
                      <p className="text-slate-200 text-sm font-medium">
                        {formatBytes(dbCheck.free_disk_bytes)}
                      </p>
                    </div>
                  </div>
                  {dbCheck.cloud_provider && (
                    <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-3 text-amber-200 text-xs">
                      <strong className="block mb-1">
                        ⚠ Cloud sync rilevato: {dbCheck.cloud_provider}
                      </strong>
                      SQLite + sync cloud possono causare corruzione del database.
                      Soluzione consigliata: metti in pausa la sincronizzazione di
                      questa cartella oppure sposta FLUXION fuori dalla cartella cloud.
                    </div>
                  )}
                  {!dbCheck.cloud_provider && dbCheck.warning && (
                    <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-3 text-amber-200 text-xs">
                      {dbCheck.warning}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {step === 5 && (
            <div data-testid="frw-step-ports">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-white text-xl font-bold">Porte di rete</h2>
                <StatusBadge status={portsStatus} />
              </div>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                FLUXION usa le porte locali 3001 (HTTP Bridge) e 3002 (Voice Pipeline).
                Se sono già occupate da altre app, segnaliamo il conflitto.
              </p>
              {ports && (
                <div className="space-y-2 text-sm">
                  <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-3 flex items-center justify-between">
                    <span className="text-slate-300">Porta 3001 (HTTP Bridge)</span>
                    <span
                      className={`text-xs font-medium ${ports.http_bridge_busy ? "text-amber-400" : "text-emerald-400"}`}
                    >
                      {ports.http_bridge_busy ? "Occupata" : "Libera"}
                    </span>
                  </div>
                  <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-3 flex items-center justify-between">
                    <span className="text-slate-300">Porta 3002 (Voice Pipeline)</span>
                    <span
                      className={`text-xs font-medium ${ports.voice_pipeline_busy ? "text-amber-400" : "text-emerald-400"}`}
                    >
                      {ports.voice_pipeline_busy ? "Occupata" : "Libera"}
                    </span>
                  </div>
                  <p className="text-slate-400 text-xs mt-2">{ports.message}</p>
                </div>
              )}
            </div>
          )}

          {step === 6 && (
            <div data-testid="frw-step-voice">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-white text-xl font-bold">Voice agent (Sara)</h2>
                <StatusBadge status={voiceStatus} />
              </div>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                Verifichiamo se il motore vocale di Sara è già attivo. Se no, verrà
                avviato automaticamente al primo uso.
              </p>
              {voice && (
                <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-4 text-sm">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-slate-400 text-xs uppercase">Stato</span>
                    <span
                      className={`text-xs font-medium ${voice.ready ? "text-emerald-400" : "text-amber-400"}`}
                    >
                      {voice.status}
                    </span>
                  </div>
                  {voice.version && (
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-xs uppercase">Versione</span>
                      <span className="text-slate-200 text-xs font-mono">
                        {voice.version}
                      </span>
                    </div>
                  )}
                  {voice.error && (
                    <p className="text-amber-300 text-xs mt-2">{voice.error}</p>
                  )}
                </div>
              )}
            </div>
          )}

          {step === 7 && (
            <div data-testid="frw-step-av">
              <h2 className="text-white text-xl font-bold mb-3">
                Antivirus & Defender
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                {isWindows
                  ? "Su Windows, alcuni antivirus o Microsoft Defender potrebbero rallentare FLUXION o segnalare il voice agent come sospetto (è un falso positivo: FLUXION è firmato e tracciato)."
                  : "Su macOS la prima apertura potrebbe richiedere conferma da Gatekeeper. Una volta aperta la prima volta, le successive aperture sono dirette."}
              </p>
              {isWindows ? (
                <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-4 text-sm">
                  <p className="text-slate-200 font-medium mb-2">
                    Esclusione consigliata
                  </p>
                  <ol className="list-decimal list-inside text-slate-300 space-y-1 text-xs">
                    <li>Apri Sicurezza di Windows → Protezione da virus e minacce</li>
                    <li>Gestisci impostazioni → Aggiungi o rimuovi esclusioni</li>
                    <li>
                      Aggiungi cartella:{" "}
                      <code className="bg-slate-900 px-1 rounded">
                        %LOCALAPPDATA%\Fluxion
                      </code>
                    </li>
                    <li>
                      Lo script automatico{" "}
                      <code className="bg-slate-900 px-1 rounded">setup-win.bat</code>{" "}
                      lo fa per te (è incluso nel download).
                    </li>
                  </ol>
                </div>
              ) : (
                <div className="bg-slate-800/60 border border-slate-700 rounded-lg p-4 text-sm">
                  <p className="text-slate-200 font-medium mb-2">macOS — Gatekeeper</p>
                  <p className="text-slate-300 text-xs leading-relaxed">
                    Se al primo avvio vedi “FLUXION non può essere aperto”, vai in
                    Impostazioni di Sistema → Privacy e Sicurezza → scorri in basso e
                    clicca <strong>Apri comunque</strong>. È necessario solo una volta.
                  </p>
                </div>
              )}
            </div>
          )}

          {step === 8 && (
            <div data-testid="frw-step-complete">
              <h2 className="text-white text-xl font-bold mb-3">Tutto pronto</h2>
              <p className="text-slate-300 text-sm leading-relaxed mb-4">
                Verifica completata. Ora ti guidiamo nella configurazione iniziale:
                tipo di attività, orari, operatori, servizi.
              </p>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <StatusBadge status={networkStatus} />
                  <span className="text-slate-300">Rete</span>
                </li>
                <li className="flex items-center gap-2">
                  <StatusBadge
                    status={
                      micStatus === "granted"
                        ? "ok"
                        : micStatus === "idle"
                          ? "idle"
                          : "warn"
                    }
                  />
                  <span className="text-slate-300">Microfono</span>
                </li>
                <li className="flex items-center gap-2">
                  <StatusBadge status={dbStatus} />
                  <span className="text-slate-300">Cartella dati</span>
                </li>
                <li className="flex items-center gap-2">
                  <StatusBadge status={portsStatus} />
                  <span className="text-slate-300">Porte di rete</span>
                </li>
                <li className="flex items-center gap-2">
                  <StatusBadge status={voiceStatus} />
                  <span className="text-slate-300">Voice agent</span>
                </li>
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 flex items-center justify-between">
          <button
            type="button"
            onClick={goBack}
            disabled={step === 1}
            data-testid="frw-back"
            className="px-3 py-2 text-sm text-slate-400 hover:text-slate-200 disabled:opacity-30 disabled:cursor-not-allowed"
          >
            ← Indietro
          </button>
          {step < totalSteps ? (
            <button
              type="button"
              onClick={goNext}
              data-testid="frw-next"
              className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium"
            >
              Avanti →
            </button>
          ) : (
            <button
              type="button"
              onClick={handleComplete}
              data-testid="frw-complete"
              className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium"
            >
              Continua alla configurazione
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export function isFirstRunWizardCompleted(): boolean {
  try {
    return window.localStorage.getItem(COMPLETED_KEY) === "1";
  } catch {
    return true; // se non possiamo leggere, evitiamo di bloccare l'app
  }
}
