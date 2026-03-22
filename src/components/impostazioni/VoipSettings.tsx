// ═══════════════════════════════════════════════════════════════════
// FLUXION - VoIP Settings (F15)
// Configurazione SIP EHIWEB per ricezione chiamate telefoniche
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Phone, Eye, EyeOff, Save, Loader2, RefreshCw } from 'lucide-react';

// ─────────────────────────────────────────────────────────────────
// Types (mirrors Rust VoiceAgentConfig + VoipStatus)
// ─────────────────────────────────────────────────────────────────

interface VoiceAgentConfig {
  id: string;
  attivo: number;
  voce_modello: string;
  saluto_personalizzato: string | null;
  orario_attivo_da: string;
  orario_attivo_a: string;
  giorni_attivi: string;
  max_chiamate_contemporanee: number;
  timeout_risposta_secondi: number;
  trasferisci_dopo_tentativi: number;
  numero_trasferimento: string | null;
  sip_username: string | null;
  sip_password: string | null;
  sip_server: string | null;
  sip_port: number | null;
  voip_attivo: number | null;
}

interface VoipStatus {
  running: boolean;
  registered: boolean;
  rtp_active: boolean;
  sip_user: string | null;
}

// ─────────────────────────────────────────────────────────────────
// Hooks
// ─────────────────────────────────────────────────────────────────

function useVoiceConfig() {
  return useQuery({
    queryKey: ['voice-config'],
    queryFn: () => invoke<VoiceAgentConfig>('get_voice_config'),
    staleTime: 2 * 60 * 1000,
  });
}

function useVoipStatus() {
  return useQuery({
    queryKey: ['voip-status'],
    queryFn: () => invoke<VoipStatus>('get_voip_status'),
    staleTime: 30 * 1000,
    refetchInterval: 30 * 1000,
    retry: false,
  });
}

// ─────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────

export const VoipSettings: FC = () => {
  const qc = useQueryClient();
  const config = useVoiceConfig();
  const voipStatus = useVoipStatus();

  const [sipUser, setSipUser] = useState('');
  const [sipPassword, setSipPassword] = useState('');
  const [sipServer, setSipServer] = useState('sip.ehiweb.it');
  const [sipPort, setSipPort] = useState(5060);
  const [voipAttivo, setVoipAttivo] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');

  // Pre-fill from DB
  useEffect(() => {
    if (!config.data) return;
    setSipUser(config.data.sip_username ?? '');
    setSipPassword(config.data.sip_password ?? '');
    setSipServer(config.data.sip_server ?? 'sip.ehiweb.it');
    setSipPort(config.data.sip_port ?? 5060);
    setVoipAttivo((config.data.voip_attivo ?? 0) === 1);
  }, [config.data]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!config.data) throw new Error('Config non caricata');
      const updated: VoiceAgentConfig = {
        ...config.data,
        sip_username: sipUser || null,
        sip_password: sipPassword || null,
        sip_server: sipServer || 'sip.ehiweb.it',
        sip_port: sipPort,
        voip_attivo: voipAttivo ? 1 : 0,
      };
      return invoke<VoiceAgentConfig>('update_voice_config', { config: updated });
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['voice-config'] });
      void qc.invalidateQueries({ queryKey: ['voip-status'] });
      setSaveMsg('Configurazione VoIP salvata');
      setTimeout(() => setSaveMsg(''), 3000);
    },
    onError: (err) => {
      setSaveMsg(`Errore: ${String(err)}`);
    },
  });

  const statusBadge = () => {
    if (voipStatus.isLoading) return null;
    if (!voipStatus.data?.running) {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-slate-700 text-slate-400">
          Non avviato
        </span>
      );
    }
    if (voipStatus.data.registered) {
      return (
        <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          SIP Registrato
        </span>
      );
    }
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/20 text-amber-400 border border-amber-500/30">
        Non registrato
      </span>
    );
  };

  return (
    <Card className="p-6 border-slate-700/50 mt-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Phone className="w-5 h-5 text-purple-400" />
            Telefono VoIP (EHIWEB)
          </h3>
          <p className="text-sm text-slate-400 mt-0.5">
            Ricevi chiamate telefoniche dirette sul numero EHIWEB
          </p>
        </div>
        <div className="flex items-center gap-2">
          {statusBadge()}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => void qc.invalidateQueries({ queryKey: ['voip-status'] })}
            className="h-7 w-7 p-0 text-slate-500 hover:text-slate-300"
            title="Aggiorna stato"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      {/* Enable toggle */}
      <div className="flex items-center justify-between mb-5 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
        <div>
          <p className="text-sm font-medium text-white">Abilita ricezione chiamate</p>
          <p className="text-xs text-slate-400 mt-0.5">
            Sara risponderà automaticamente al numero EHIWEB configurato
          </p>
        </div>
        <Switch
          checked={voipAttivo}
          onCheckedChange={setVoipAttivo}
          aria-label="Abilita VoIP"
        />
      </div>

      <div className="space-y-4">
        {/* SIP Username / Numero DID */}
        <div className="space-y-1.5">
          <Label htmlFor="sip-username" className="text-slate-300 text-sm">
            Numero DID EHIWEB (username SIP)
          </Label>
          <Input
            id="sip-username"
            type="text"
            value={sipUser}
            onChange={(e) => setSipUser(e.target.value)}
            placeholder="es. 0250150001"
            className="bg-slate-950 border-slate-700 text-white"
          />
          <p className="text-xs text-slate-500">
            Il numero fisso italiano assegnato da EHIWEB (anche usato come username SIP)
          </p>
        </div>

        {/* SIP Password */}
        <div className="space-y-1.5">
          <Label htmlFor="sip-password" className="text-slate-300 text-sm">
            Password SIP
          </Label>
          <div className="relative">
            <Input
              id="sip-password"
              type={showPassword ? 'text' : 'password'}
              value={sipPassword}
              onChange={(e) => setSipPassword(e.target.value)}
              placeholder="Password SIP EHIWEB"
              className="bg-slate-950 border-slate-700 text-white pr-10"
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7 p-0 text-slate-400"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </Button>
          </div>
        </div>

        {/* SIP Server + Port (advanced) */}
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2 space-y-1.5">
            <Label htmlFor="sip-server" className="text-slate-300 text-sm">
              Server SIP
            </Label>
            <Input
              id="sip-server"
              type="text"
              value={sipServer}
              onChange={(e) => setSipServer(e.target.value)}
              placeholder="sip.ehiweb.it"
              className="bg-slate-950 border-slate-700 text-white"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="sip-port" className="text-slate-300 text-sm">
              Porta
            </Label>
            <Input
              id="sip-port"
              type="number"
              value={sipPort}
              onChange={(e) => setSipPort(Number(e.target.value))}
              className="bg-slate-950 border-slate-700 text-white"
            />
          </div>
        </div>
      </div>

      {/* Save feedback */}
      {saveMsg && (
        <p
          className={`text-sm mt-3 ${saveMsg.startsWith('Errore') ? 'text-red-400' : 'text-emerald-400'}`}
        >
          {saveMsg}
        </p>
      )}

      {/* Nota EHIWEB account */}
      <div className="mt-4 p-3 bg-purple-900/20 border border-purple-500/20 rounded-lg">
        <p className="text-xs text-purple-300">
          <span className="font-medium">Prerequisito:</span> Account sviluppatore EHIWEB con numero
          SIP attivo. Contatta EHIWEB per ottenere le credenziali SIP.
        </p>
      </div>

      {/* Save button */}
      <div className="mt-5">
        <Button
          onClick={() => void saveMutation.mutateAsync()}
          disabled={saveMutation.isPending}
          className="bg-purple-600 hover:bg-purple-700 text-white"
        >
          {saveMutation.isPending ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Save className="w-4 h-4 mr-2" />
          )}
          Salva configurazione VoIP
        </Button>
      </div>
    </Card>
  );
};
