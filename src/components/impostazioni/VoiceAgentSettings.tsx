// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Agent Sara Settings
// Configurazione chiave API Groq per assistente vocale 24/7
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { VoiceSaraQuality } from './VoiceSaraQuality';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Mic, Eye, EyeOff, Save, TestTube, Loader2, ExternalLink } from 'lucide-react';
import { openUrl } from '@tauri-apps/plugin-opener';
import { useSetupConfig, useSaveSetupConfig } from '@/hooks/use-setup';
import { defaultSetupConfig } from '@/types/setup';

type TestStatus = 'idle' | 'testing' | 'ok' | 'warn' | 'error';

export const VoiceAgentSettings: FC = () => {
  const setupConfig = useSetupConfig();
  const saveConfig = useSaveSetupConfig();

  const [localKey, setLocalKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [testStatus, setTestStatus] = useState<TestStatus>('idle');
  const [testMsg, setTestMsg] = useState('');
  const [saveMsg, setSaveMsg] = useState('');

  // Pre-fill da DB al mount
  useEffect(() => {
    if (setupConfig.data?.groq_api_key) {
      setLocalKey(setupConfig.data.groq_api_key);
    }
  }, [setupConfig.data?.groq_api_key]);

  const isKeyValid = localKey.startsWith('gsk_') && localKey.length > 10;
  const isActive = isKeyValid;

  const handleTest = async () => {
    if (!localKey) {
      setTestStatus('error');
      setTestMsg('Inserisci una chiave API prima di testare');
      return;
    }
    if (!isKeyValid) {
      setTestStatus('error');
      setTestMsg('Formato non valido — la chiave deve iniziare con gsk_');
      return;
    }

    setTestStatus('testing');
    setTestMsg('');

    try {
      const res = await fetch('http://127.0.0.1:3002/health', {
        signal: AbortSignal.timeout(4000),
      });
      if (res.ok) {
        setTestStatus('ok');
        setTestMsg('Voice agent raggiungibile — Sara e operativa');
      } else {
        setTestStatus('warn');
        setTestMsg('Formato valido — Sara partira al prossimo avvio');
      }
    } catch {
      setTestStatus('warn');
      setTestMsg('Formato valido — Sara partira al prossimo avvio');
    }
  };

  const handleSave = async () => {
    setSaveMsg('');
    const existingConfig = setupConfig.data ?? defaultSetupConfig;
    try {
      await saveConfig.mutateAsync({ ...existingConfig, groq_api_key: localKey });
      setSaveMsg('Chiave salvata');
      setTimeout(() => setSaveMsg(''), 3000);
    } catch (err) {
      setSaveMsg(`Errore nel salvataggio: ${err}`);
    }
  };

  const handleOpenGroq = async () => {
    try {
      await openUrl('https://console.groq.com/keys');
    } catch {
      // fallback se plugin non disponibile
    }
  };

  const testMsgColor =
    testStatus === 'ok'
      ? 'text-green-400'
      : testStatus === 'warn'
        ? 'text-amber-400'
        : 'text-red-400';

  return (
    <Card className="p-6 bg-slate-900 border-slate-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Mic className="w-6 h-6 text-cyan-500" />
            Assistente Vocale Sara
          </h2>
          <p className="text-sm text-slate-400">
            Configura la chiave API per abilitare l'assistente vocale 24/7
          </p>
        </div>
        {/* Status badge */}
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold ${
            isActive
              ? 'bg-green-500/20 text-green-400 border border-green-500/30'
              : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
          }`}
        >
          {isActive ? 'Attivo' : 'Non configurata'}
        </span>
      </div>

      {/* Istruzioni */}
      <div className="mb-5 p-4 bg-slate-950 rounded-lg border border-slate-700 space-y-2 text-sm text-slate-300">
        <p className="font-medium text-slate-200 mb-1">Come attivare Sara (2 minuti):</p>
        <p>
          1.{' '}
          <button
            type="button"
            onClick={handleOpenGroq}
            className="text-cyan-400 hover:text-cyan-300 underline inline-flex items-center gap-1"
          >
            console.groq.com/keys
            <ExternalLink className="w-3 h-3" />
          </button>{' '}
          — crea un account gratuito (solo email)
        </p>
        <p>2. Clicca "Create API Key", dai il nome "Fluxion", copia la chiave</p>
        <p>3. Incolla qui sotto (inizia con gsk_) e clicca Salva</p>
      </div>

      {/* Input chiave */}
      <div className="space-y-2 mb-5">
        <Label htmlFor="groq-api-key" className="text-slate-300">
          Chiave API Fluxion AI
        </Label>
        <div className="relative">
          <Input
            id="groq-api-key"
            type={showKey ? 'text' : 'password'}
            value={localKey}
            onChange={(e) => {
              setLocalKey(e.target.value);
              setTestStatus('idle');
              setTestMsg('');
            }}
            placeholder="gsk_xxxxxxxxxxxxxxxxxxxx"
            className="bg-slate-950 border-slate-700 text-white pr-10"
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0 text-slate-400"
            onClick={() => setShowKey(!showKey)}
          >
            {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Test message */}
      {testMsg && (
        <p className={`text-sm mb-4 ${testMsgColor}`}>{testMsg}</p>
      )}

      {/* Save message */}
      {saveMsg && (
        <p
          className={`text-sm mb-4 ${saveMsg.startsWith('Errore') ? 'text-red-400' : 'text-green-400'}`}
        >
          {saveMsg}
        </p>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <Button
          onClick={handleTest}
          disabled={testStatus === 'testing' || !localKey}
          variant="outline"
          className="border-slate-700 text-slate-300 hover:bg-slate-800"
          data-testid="voice-settings-testa"
        >
          {testStatus === 'testing' ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <TestTube className="w-4 h-4 mr-2" />
          )}
          Testa
        </Button>
        <Button
          onClick={handleSave}
          disabled={saveConfig.isPending || !localKey}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
          data-testid="voice-settings-salva"
        >
          {saveConfig.isPending ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Save className="w-4 h-4 mr-2" />
          )}
          Salva
        </Button>
      </div>

      <p className="text-xs text-slate-500 mt-4">
        Il piano gratuito Groq include 14.400 riconoscimenti vocali al giorno — sufficiente per qualsiasi PMI.
      </p>

      {/* Qualità Voce Sara */}
      <div className="mt-6 pt-6 border-t border-slate-700">
        <VoiceSaraQuality />
      </div>
    </Card>
  );
};
