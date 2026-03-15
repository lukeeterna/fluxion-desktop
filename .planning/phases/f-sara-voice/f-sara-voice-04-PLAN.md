---
phase: f-sara-voice
plan: 04
type: execute
wave: 2
depends_on:
  - f-sara-voice-02
files_modified:
  - src/components/setup/SetupWizard.tsx
  - src/components/impostazioni/VoiceSaraQuality.tsx
autonomous: true

must_haves:
  truths:
    - "SetupWizard step 9 (new) shows voice quality selector — ONLY on capable hardware (≥8GB RAM, ≥4 core)"
    - "On capable hardware: 'Alta Qualita' radio selected by default, 'Veloce' option available, 'Scarica (1.2GB)' button visible"
    - "On incapable hardware: 'Veloce' selected and recommended, 'Alta Qualita' option shown with warning"
    - "Selecting a mode calls POST /api/tts/mode — persists choice"
    - "VoiceSaraQuality.tsx in Impostazioni shows same selector + current mode from GET /api/tts/mode"
    - "Both components use fetch to /api/tts/hardware (port 3002) — hardware detection is backend-driven"
    - "npm run type-check passes with 0 errors"
  artifacts:
    - path: "src/components/impostazioni/VoiceSaraQuality.tsx"
      provides: "Post-install voice quality selector in Impostazioni"
      exports: ["VoiceSaraQuality"]
      min_lines: 80
    - path: "src/components/setup/SetupWizard.tsx"
      provides: "SetupWizard step 9 for voice quality selection"
      contains: "Alta Qualita"
  key_links:
    - from: "src/components/setup/SetupWizard.tsx"
      to: "http://127.0.0.1:3002/api/tts/hardware"
      via: "fetch in useEffect on step 9 mount"
      pattern: "api/tts/hardware"
    - from: "src/components/impostazioni/VoiceSaraQuality.tsx"
      to: "http://127.0.0.1:3002/api/tts/mode"
      via: "fetch in useEffect on mount"
      pattern: "api/tts/mode"
---

<objective>
Add voice quality selection to SetupWizard (step 9, after Sara Groq key step) and create VoiceSaraQuality.tsx in Impostazioni.

Purpose: The user must be able to choose TTS quality during setup and change it post-install. UI calls the backend endpoints from plan 02 — hardware detection is server-side (Python reads RAM/CPU), UI only reads the response. TypeScript strict throughout (zero `any`).

Output:
- src/components/impostazioni/VoiceSaraQuality.tsx (new file)
- src/components/setup/SetupWizard.tsx (modified — add step 9)
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@src/components/setup/SetupWizard.tsx
@src/components/impostazioni/VoiceAgentSettings.tsx
@.planning/phases/f-sara-voice/f-sara-voice-02-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create VoiceSaraQuality.tsx in Impostazioni</name>
  <files>src/components/impostazioni/VoiceSaraQuality.tsx</files>
  <action>
Create src/components/impostazioni/VoiceSaraQuality.tsx:

```typescript
// FLUXION - Sara Voice Quality Settings
// Allows post-install TTS mode change via Impostazioni → Sara → Qualità Voce
import React, { useEffect, useState } from 'react';

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
        {/* Auto option */}
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
            <p className="text-slate-400 text-xs">Sara sceglie in base all'hardware del PC</p>
          </div>
        </label>

        {/* Quality option */}
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
            <p className="text-slate-400 text-xs">Voce naturale italiana · 400-800ms · Download 1.2GB</p>
            {modeInfo && !modeInfo.model_downloaded && (
              <p className="text-amber-400 text-xs mt-1">Modello non scaricato — usare Setup Wizard per scaricare</p>
            )}
            {!hardware?.capable && hardware && (
              <p className="text-amber-400 text-xs mt-1">
                Potrebbe essere lenta su questo PC ({hardware.ram_gb}GB RAM)
              </p>
            )}
          </div>
        </label>

        {/* Fast option */}
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
```

Note: VOICE_AGENT_URL is hardcoded to 127.0.0.1:3002 — correct for Tauri desktop app where voice agent runs locally. No need for env var (always local).
  </action>
  <verify>
npm run type-check (from /Volumes/MontereyT7/FLUXION) must show 0 errors for this file.
  </verify>
  <done>
- VoiceSaraQuality.tsx exists at src/components/impostazioni/
- Compiles without TypeScript errors
- Uses no `any` types
- Calls /api/tts/hardware and /api/tts/mode correctly
  </done>
</task>

<task type="auto">
  <name>Task 2: Add step 9 (Qualità Voce Sara) to SetupWizard.tsx</name>
  <files>src/components/setup/SetupWizard.tsx</files>
  <action>
In SetupWizard.tsx, make these targeted changes:

**1. Add state variables** (near other useState declarations, after groqTestStatus):
```typescript
const [ttsHardware, setTtsHardware] = useState<{
  capable: boolean;
  ram_gb: number;
  cpu_cores: number;
  model_downloaded: boolean;
} | null>(null);
const [ttsMode, setTtsMode] = useState<'quality' | 'fast' | 'auto'>('auto');
const [ttsDownloading, setTtsDownloading] = useState(false);
const [ttsDownloadMsg, setTtsDownloadMsg] = useState('');
```

**2. Add useEffect for step 9 hardware detection** (after existing useEffect hooks):
```typescript
useEffect(() => {
  if (step !== 9) return;
  void (async () => {
    try {
      const res = await fetch('http://127.0.0.1:3002/api/tts/hardware');
      if (res.ok) {
        const hw = await res.json() as typeof ttsHardware;
        setTtsHardware(hw);
        // Pre-select recommended mode
        if (hw?.capable) setTtsMode('quality');
        else setTtsMode('fast');
      }
    } catch {
      // voice agent offline — user can still choose manually
    }
  })();
}, [step]);
```

**3. Add handleTtsDownload function** (near handleTtsDownload, after testGroqConnection):
```typescript
const handleTtsDownload = async () => {
  setTtsDownloading(true);
  setTtsDownloadMsg('Download in corso (1.2GB)...');
  try {
    // Persist mode selection first
    await fetch('http://127.0.0.1:3002/api/tts/mode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'quality' }),
    });
    setTtsMode('quality');
    setTtsDownloadMsg('Modalità Alta Qualità selezionata. Il download del modello avverrà al primo avvio di Sara.');
  } catch {
    setTtsDownloadMsg('Impossibile contattare Sara — la modalità verrà applicata al prossimo avvio.');
  } finally {
    setTtsDownloading(false);
  }
};
```
Note: actual Qwen3-TTS model download is deferred to first Sara startup (not during wizard) because the wizard runs in Tauri frontend and the download must happen in the Python backend. The wizard just persists the mode preference.

**4. Update totalSteps** — change from 8 to 9:
Find `const totalSteps = 8` (or similar) and update to 9.

**5. Add step 9 JSX** (after the closing `}` of step 8 block, before Navigation Buttons):
```tsx
{/* STEP 9: Qualità Voce Sara */}
{step === 9 && (
  <div className="space-y-5">
    <div>
      <h3 className="text-lg font-semibold text-white flex items-center gap-2">
        <span>🎙️</span> Qualità Voce di Sara
      </h3>
      <p className="text-slate-400 text-sm mt-1">
        Scegli come vuoi che suoni Sara. Puoi cambiarlo in qualsiasi momento da Impostazioni.
      </p>
    </div>

    {ttsHardware && (
      <div className="bg-slate-700/50 rounded-lg p-3 text-xs text-slate-400">
        PC rilevato: {ttsHardware.ram_gb}GB RAM · {ttsHardware.cpu_cores} core
        {ttsHardware.capable ? ' · Compatibile con Alta Qualità ✓' : ' · Consigliamo Veloce'}
      </div>
    )}

    <div className="space-y-3">
      {/* Quality option */}
      <label className={`flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-colors ${
        ttsMode === 'quality' ? 'border-cyan-500 bg-cyan-900/20' : 'border-slate-600 hover:border-slate-500'
      }`}>
        <input
          type="radio"
          name="wizard-tts-mode"
          checked={ttsMode === 'quality'}
          onChange={() => setTtsMode('quality')}
          className="mt-0.5"
        />
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-white font-medium text-sm">Alta Qualità</span>
            {ttsHardware?.capable && (
              <span className="text-xs bg-cyan-700 text-cyan-200 px-2 py-0.5 rounded-full">⭐ CONSIGLIATO</span>
            )}
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Qwen3-TTS · Voce naturale e fluente · Download 1.2GB al primo avvio
          </p>
          {ttsHardware && !ttsHardware.capable && (
            <p className="text-amber-400 text-xs mt-1">
              Potrebbe essere lenta su questo PC ({ttsHardware.ram_gb}GB RAM — consigliato 8GB)
            </p>
          )}
        </div>
      </label>

      {/* Fast option */}
      <label className={`flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-colors ${
        ttsMode === 'fast' ? 'border-cyan-500 bg-cyan-900/20' : 'border-slate-600 hover:border-slate-500'
      }`}>
        <input
          type="radio"
          name="wizard-tts-mode"
          checked={ttsMode === 'fast'}
          onChange={() => setTtsMode('fast')}
          className="mt-0.5"
        />
        <div>
          <div className="flex items-center gap-2">
            <span className="text-white font-medium text-sm">Veloce (Piper)</span>
            {ttsHardware && !ttsHardware.capable && (
              <span className="text-xs bg-cyan-700 text-cyan-200 px-2 py-0.5 rounded-full">⭐ CONSIGLIATO</span>
            )}
          </div>
          <p className="text-slate-400 text-xs mt-1">~50ms · Nessun download · Funziona su tutti i PC</p>
        </div>
      </label>
    </div>

    {ttsMode === 'quality' && (
      <button
        type="button"
        onClick={() => void handleTtsDownload()}
        disabled={ttsDownloading}
        className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
      >
        {ttsDownloading ? 'Configurazione...' : 'Usa Alta Qualità →'}
      </button>
    )}

    {ttsMode === 'fast' && (
      <button
        type="button"
        onClick={() => void (async () => {
          try {
            await fetch('http://127.0.0.1:3002/api/tts/mode', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ mode: 'fast' }),
            });
          } catch { /* offline — mode saved on next start */ }
          setTtsDownloadMsg('Modalità Veloce selezionata.');
        })()}
        className="w-full py-2.5 bg-slate-600 hover:bg-slate-500 text-white text-sm font-medium rounded-lg transition-colors"
      >
        Usa Veloce →
      </button>
    )}

    {ttsDownloadMsg && (
      <p className="text-green-400 text-xs">{ttsDownloadMsg}</p>
    )}

    <div className="bg-slate-700/50 rounded-lg p-3">
      <p className="text-slate-400 text-xs">
        Puoi modificare la qualità voce in qualsiasi momento da
        <strong className="text-slate-300"> Impostazioni → Voice Agent → Qualità Voce Sara</strong>.
      </p>
    </div>
  </div>
)}
```

After updating SetupWizard, run:
```bash
npm run type-check
```
Fix any TypeScript errors before marking task done.
  </action>
  <verify>
npm run type-check from /Volumes/MontereyT7/FLUXION — must show 0 errors.
Grep check:
grep -n "step === 9" src/components/setup/SetupWizard.tsx | head -5
grep -n "ttsHardware\|ttsMode\|ttsDownloading" src/components/setup/SetupWizard.tsx | wc -l
# Should be > 5 matches
  </verify>
  <done>
- SetupWizard.tsx has step 9 JSX block for voice quality selection
- totalSteps updated to 9
- ttsHardware, ttsMode, ttsDownloading state declared
- npm run type-check passes with 0 errors
- No `any` types used
  </done>
</task>

</tasks>

<verification>
npm run type-check
# Expected: 0 errors

grep -c "step === 9" /Volumes/MontereyT7/FLUXION/src/components/setup/SetupWizard.tsx
# Expected: >= 1

ls /Volumes/MontereyT7/FLUXION/src/components/impostazioni/VoiceSaraQuality.tsx
# Expected: file exists
</verification>

<success_criteria>
- VoiceSaraQuality.tsx created with no TypeScript errors
- SetupWizard.tsx step 9 added with voice quality selector
- UI correctly handles both capable and incapable hardware states
- Hardware detection is API-driven (not browser navigator — Python backend reads RAM/CPU)
- npm run type-check: 0 errors
</success_criteria>

<output>
After completion, create .planning/phases/f-sara-voice/f-sara-voice-04-SUMMARY.md
</output>
