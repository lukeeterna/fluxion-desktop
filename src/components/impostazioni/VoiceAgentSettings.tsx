// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Agent Sara Settings
// Sara è gestita automaticamente da FLUXION AI — zero configurazione
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { VoiceSaraQuality } from './VoiceSaraQuality';
import { Card } from '@/components/ui/card';
import { Mic, CheckCircle, Wifi, WifiOff } from 'lucide-react';

export const VoiceAgentSettings: FC = () => {
  const [pipelineStatus, setPipelineStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    const checkPipeline = async () => {
      try {
        const res = await fetch('http://127.0.0.1:3002/health', {
          signal: AbortSignal.timeout(3000),
        });
        setPipelineStatus(res.ok ? 'online' : 'offline');
      } catch {
        setPipelineStatus('offline');
      }
    };
    checkPipeline();
    const interval = setInterval(checkPipeline, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="p-6 bg-slate-900 border-slate-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Mic className="w-6 h-6 text-cyan-500" />
            Sara — Receptionist AI
          </h2>
          <p className="text-sm text-slate-400">
            Assistente vocale per prenotazioni 24/7
          </p>
        </div>
        {/* Status badge */}
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold ${
            pipelineStatus === 'online'
              ? 'bg-green-500/20 text-green-400 border border-green-500/30'
              : pipelineStatus === 'offline'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
          }`}
        >
          {pipelineStatus === 'online' ? 'Attiva' : pipelineStatus === 'offline' ? 'Non disponibile' : 'Verifica...'}
        </span>
      </div>

      {/* Status card — gestito automaticamente */}
      <div className="mb-5 p-4 bg-slate-950 rounded-lg border border-slate-700 space-y-3">
        <div className="flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-400 shrink-0" />
          <div>
            <p className="text-sm font-medium text-white">Gestita automaticamente da FLUXION AI</p>
            <p className="text-xs text-slate-400 mt-0.5">
              Sara funziona senza configurazione. Nessuna chiave API da inserire.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {pipelineStatus === 'online' ? (
            <Wifi className="w-5 h-5 text-green-400 shrink-0" />
          ) : (
            <WifiOff className="w-5 h-5 text-amber-400 shrink-0" />
          )}
          <div>
            <p className="text-sm text-slate-300">
              {pipelineStatus === 'online'
                ? 'Sara è operativa e pronta a rispondere ai clienti'
                : pipelineStatus === 'offline'
                  ? 'Sara si attiverà automaticamente al prossimo avvio'
                  : 'Controllo connessione in corso...'}
            </p>
          </div>
        </div>
      </div>

      {/* Info inclusa nella licenza */}
      <p className="text-xs text-slate-500 mb-4">
        Sara è inclusa nella tua licenza FLUXION. Nessun costo aggiuntivo, nessun abbonamento.
      </p>

      {/* Qualità Voce Sara */}
      <div className="pt-6 border-t border-slate-700">
        <VoiceSaraQuality />
      </div>
    </Card>
  );
};
