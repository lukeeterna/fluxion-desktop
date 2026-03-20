// ═══════════════════════════════════════════════════════════════════
// FLUXION - Email Settings Component
// Gmail App Password is the recommended approach for PMI
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { openUrl } from '@tauri-apps/plugin-opener';
import { Mail, Eye, EyeOff, Save, TestTube, Loader2, ExternalLink } from 'lucide-react';

interface SmtpSettingsData {
  smtp_host: string;
  smtp_port: number;
  smtp_email_from: string;
  smtp_password: string;
  smtp_enabled: boolean;
}

export const SmtpSettings: FC = () => {
  const [settings, setSettings] = useState<SmtpSettingsData>({
    smtp_host: 'smtp.gmail.com',
    smtp_port: 587,
    smtp_email_from: '',
    smtp_password: '',
    smtp_enabled: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const smtpData = await invoke<SmtpSettingsData>('get_smtp_settings');
        setSettings(smtpData);
      } catch (error) {
        console.error('Failed to load settings:', error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      await invoke('save_smtp_settings', { settings });
      setMessage({ type: 'success', text: 'Impostazioni email salvate' });
    } catch (error) {
      setMessage({ type: 'error', text: `Errore: ${error}` });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setMessage(null);
    try {
      await invoke('test_smtp_connection');
      setMessage({ type: 'success', text: 'Connessione email valida' });
    } catch (error) {
      setMessage({ type: 'error', text: `Test fallito: ${error}` });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6 bg-slate-900 border-slate-800">
        <div className="flex items-center gap-2 text-slate-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          Caricamento impostazioni email...
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6 bg-slate-900 border-slate-800">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-2">
            <Mail className="w-6 h-6 text-cyan-500" />
            Email per le notifiche
          </h2>
          <p className="text-sm text-slate-400">
            Invia ordini fornitori e reminder via email
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Label htmlFor="smtp-enabled" className="text-slate-300">Email attiva</Label>
          <Switch
            id="smtp-enabled"
            checked={settings.smtp_enabled}
            onCheckedChange={(checked) => setSettings({ ...settings, smtp_enabled: checked })}
          />
        </div>
      </div>

      {/* ── Gmail Quick Setup Guide ── */}
      <div className="mb-6 rounded-lg border border-cyan-500/30 bg-cyan-500/5 p-4">
        <p className="text-sm font-semibold text-white mb-2">Configurazione rapida Gmail (2 minuti)</p>
        <ol className="text-xs text-slate-300 space-y-1 list-decimal list-inside">
          <li>Attiva la <strong>Verifica in 2 passaggi</strong> sul tuo account Google</li>
          <li>
            Vai su{' '}
            <span
              onClick={() => openUrl('https://myaccount.google.com/apppasswords')}
              className="text-cyan-400 hover:underline cursor-pointer inline-flex items-center gap-1"
              role="link"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && openUrl('https://myaccount.google.com/apppasswords')}
            >
              Password per le app <ExternalLink className="w-3 h-3" />
            </span>
          </li>
          <li>Crea una nuova password per &quot;FLUXION&quot;</li>
          <li>Copia la password generata (16 caratteri) nel campo qui sotto</li>
        </ol>
      </div>

      {/* ── SMTP Form ── */}
      <div className="grid grid-cols-2 gap-6">
        {/* Server SMTP */}
        <div className="space-y-2">
          <Label htmlFor="smtp-host" className="text-slate-300">Server SMTP</Label>
          <Input
            id="smtp-host"
            value={settings.smtp_host}
            onChange={(e) => setSettings({ ...settings, smtp_host: e.target.value })}
            placeholder="smtp.gmail.com"
            className="bg-slate-950 border-slate-700 text-white"
          />
        </div>

        {/* Porta */}
        <div className="space-y-2">
          <Label htmlFor="smtp-port" className="text-slate-300">Porta</Label>
          <Input
            id="smtp-port"
            type="number"
            value={settings.smtp_port}
            onChange={(e) => setSettings({ ...settings, smtp_port: parseInt(e.target.value) || 587 })}
            placeholder="587"
            className="bg-slate-950 border-slate-700 text-white"
          />
        </div>

        {/* Email */}
        <div className="space-y-2">
          <Label htmlFor="smtp-email" className="text-slate-300">La tua email Gmail</Label>
          <Input
            id="smtp-email"
            type="email"
            value={settings.smtp_email_from}
            onChange={(e) => setSettings({ ...settings, smtp_email_from: e.target.value })}
            placeholder="tuaemail@gmail.com"
            className="bg-slate-950 border-slate-700 text-white"
          />
        </div>

        {/* Password */}
        <div className="space-y-2">
          <Label htmlFor="smtp-password" className="text-slate-300">
            Password per le app
          </Label>
          <div className="relative">
            <Input
              id="smtp-password"
              type={showPassword ? 'text' : 'password'}
              value={settings.smtp_password}
              onChange={(e) => setSettings({ ...settings, smtp_password: e.target.value })}
              placeholder="xxxx xxxx xxxx xxxx"
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
      </div>

      {/* Message */}
      {message && (
        <div className={`mt-4 p-3 rounded-lg ${
          message.type === 'success'
            ? 'bg-green-500/10 border border-green-500/30 text-green-400'
            : 'bg-red-500/10 border border-red-500/30 text-red-400'
        }`}>
          {message.text}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 mt-6">
        <Button
          onClick={handleTest}
          disabled={testing || !settings.smtp_email_from || !settings.smtp_password}
          variant="outline"
          className="border-slate-700 text-slate-300 hover:bg-slate-800"
        >
          {testing ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <TestTube className="w-4 h-4 mr-2" />
          )}
          Testa connessione
        </Button>
        <Button
          onClick={handleSave}
          disabled={saving}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          {saving ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Save className="w-4 h-4 mr-2" />
          )}
          Salva
        </Button>
      </div>

      {/* Help text */}
      <p className="text-xs text-slate-500 mt-4">
        Funziona con Gmail, Outlook, Yahoo e qualsiasi provider SMTP.
        Per Gmail serve la{' '}
        <span
          onClick={() => openUrl('https://myaccount.google.com/apppasswords')}
          className="text-cyan-400 hover:underline cursor-pointer"
          role="link"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && openUrl('https://myaccount.google.com/apppasswords')}
        >
          Password per le app
        </span>{' '}
        (richiede Verifica in 2 passaggi attiva).
      </p>
    </Card>
  );
};
