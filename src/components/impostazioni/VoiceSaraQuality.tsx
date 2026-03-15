// ═══════════════════════════════════════════════════════════════════
// FLUXION - Sara Voice Quality Settings
// Allows post-install TTS mode change via Impostazioni → Sara → Qualità Voce
// ═══════════════════════════════════════════════════════════════════

import { useEffect, useState } from 'react';

const VOICE_AGENT_URL = 'http://127.0.0.1:3002';

interface HardwareInfo {
  capable: boolean;
  ram_gb: number;
  cpu_cores: number;
  recommended_mode: 'quality' | 'fast';
  model_downloaded: boolean;
}

interface TTSModeInfo {
  current_mode: 'quality' | 'fast' | 'auto';
  model_downloaded: boolean;
  reference_audio_path: string | null;
}

type TTSMode = 'quality' | 'fast' | 'auto';

export function VoiceSaraQuality() {
  const [hardware, setHardware] = useState<HardwareInfo | null>(null);
  const [modeInfo, setModeInfo] = useState<TTSModeInfo | null>(null);
  const [selectedMode, setSelectedMode] = useState<TTSMode>('auto');
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const [hwRes, modeRes] = await Promise.all([
          fetch(`${VOICE_AGENT_URL}/api/tts/hardware`),
          fetch(`${VOICE_AGENT_URL}/api/tts/mode`),
        ]);
        if (hwRes.ok) setHardware(await hwRes.json() as HardwareInfo);
        if (modeRes.ok) {
          const info = await modeRes.json() as TTSModeInfo;
          setModeInfo(info);
          setSelectedMode(info.current_mode);
        }
      } catch {
        // Voice agent not running — show offline state
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg('');
    try {
      const res = await fetch(`${VOICE_AGENT_URL}/api/tts/mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: selectedMode }),
      });
      if (res.ok) {
        setSaveMsg('Modalità salvata. Riavvia Sara per applicare.');
      } else {
        setSaveMsg('Errore nel salvataggio.');
      }
    } catch {
      setSaveMsg('Sara non raggiungibile. Avvia prima il voice agent.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p className="text-slate-400 text-sm">Caricamento...</p>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-white font-medium text-sm mb-1">Qualità Voce Sara</h4>
        {hardware && (
          <p className="text-slate-400 text-xs mb-3">
            Hardware rilevato: {hardware.ram_gb}GB RAM · {hardware.cpu_cores} core
            {hardware.capable
              ? ' — PC compatibile con Alta Qualità'
              : ' — PC datato: consigliamo Veloce'}
          </p>
        )}
        {!hardware && (
          <p className="text-amber-400 text-xs mb-3">
            Voice agent non attivo — avviare Sara per rilevare hardware.
          </p>
        )}
      </div>

      <div className="space-y-2">
        <label className="flex items-start gap-3 p-3 rounded-lg border border-slate-600 cursor-pointer hover:border-slate-500 transition-colors">
          <input
            type="radio"
            name="tts-mode"
            value="auto"
            checked={selectedMode === 'auto'}
            onChange={() => setSelectedMode('auto')}
            className="mt-0.5"
          />
          <div>
            <p className="text-slate-200 text-sm font-medium">Automatico (consigliato)</p>
            <p className="text-slate-400 text-xs">Sara sceglie in base all&apos;hardware del PC</p>
          </div>
        </label>

        <label className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
          hardware?.capable
            ? 'border-cyan-600 hover:border-cyan-500'
            : 'border-slate-600 hover:border-slate-500'
        }`}>
          <input
            type="radio"
            name="tts-mode"
            value="quality"
            checked={selectedMode === 'quality'}
            onChange={() => setSelectedMode('quality')}
            className="mt-0.5"
          />
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <p className="text-slate-200 text-sm font-medium">Alta Qualità (Qwen3-TTS)</p>
              {hardware?.capable && (
                <span className="text-xs bg-cyan-700 text-cyan-200 px-1.5 py-0.5 rounded">CONSIGLIATO</span>
              )}
            </div>
            <p className="text-slate-400 text-xs">Voce naturale italiana · 400-800ms · Download 1.2GB al primo avvio</p>
            {modeInfo && !modeInfo.model_downloaded && (
              <p className="text-amber-400 text-xs mt-1">Modello non ancora scaricato — verrà scaricato al primo avvio di Sara</p>
            )}
            {!hardware?.capable && hardware && (
              <p className="text-amber-400 text-xs mt-1">
                Potrebbe essere lenta su questo PC ({hardware.ram_gb}GB RAM)
              </p>
            )}
          </div>
        </label>

        <label className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
          !hardware?.capable
            ? 'border-cyan-600 hover:border-cyan-500'
            : 'border-slate-600 hover:border-slate-500'
        }`}>
          <input
            type="radio"
            name="tts-mode"
            value="fast"
            checked={selectedMode === 'fast'}
            onChange={() => setSelectedMode('fast')}
            className="mt-0.5"
          />
          <div>
            <div className="flex items-center gap-2">
              <p className="text-slate-200 text-sm font-medium">Veloce (Piper)</p>
              {hardware && !hardware.capable && (
                <span className="text-xs bg-cyan-700 text-cyan-200 px-1.5 py-0.5 rounded">CONSIGLIATO</span>
              )}
            </div>
            <p className="text-slate-400 text-xs">Voce italiana · ~50ms · Nessun download</p>
          </div>
        </label>
      </div>

      <button
        type="button"
        onClick={() => void handleSave()}
        disabled={saving}
        className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-sm rounded-lg transition-colors disabled:opacity-50"
      >
        {saving ? 'Salvataggio...' : 'Salva modalità'}
      </button>

      {saveMsg && (
        <p className={`text-xs ${saveMsg.includes('Errore') || saveMsg.includes('non raggiungibile') ? 'text-red-400' : 'text-green-400'}`}>
          {saveMsg}
        </p>
      )}
    </div>
  );
}
