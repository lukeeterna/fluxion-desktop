// ═══════════════════════════════════════════════════════════════════
// FLUXION - SMTP Settings Component
// Configure email settings for supplier order sending
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { openUrl } from '@tauri-apps/plugin-opener';
import { Mail, Eye, EyeOff, Save, TestTube, Loader2, CheckCircle2, XCircle } from 'lucide-react';

interface SmtpSettingsData {
  smtp_host: string;
  smtp_port: number;
  smtp_email_from: string;
  smtp_password: string;
  smtp_enabled: boolean;
}

interface GmailOAuthStatus {
  connected: boolean;
  email: string;
}

export const SmtpSettings: FC = () => {
  const [settings, setSettings] = useState<SmtpSettingsData>({
    smtp_host: 'smtp.gmail.com',
    smtp_port: 587,
    smtp_email_from: '',
    smtp_password: '',
    smtp_enabled: false,
  });
  const [gmailStatus, setGmailStatus] = useState<GmailOAuthStatus>({ connected: false, email: '' });
  const [connecting, setConnecting] = useState(false);
  const [gmailError, setGmailError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadSettings();

    // Listen for OAuth result events from Tauri backend
    let unlistenSuccess: (() => void) | undefined;
    let unlistenError: (() => void) | undefined;

    listen<{ email: string }>('gmail-oauth-success', (event) => {
      setGmailStatus({ connected: true, email: event.payload.email });
      setConnecting(false);
      setGmailError(null);
      setMessage({ type: 'success', text: `Gmail connesso: ${event.payload.email}` });
    }).then((fn) => {
      unlistenSuccess = fn;
    });

    listen<{ message: string }>('gmail-oauth-error', (event) => {
      setGmailError(event.payload.message);
      setConnecting(false);
    }).then((fn) => {
      unlistenError = fn;
    });

    return () => {
      unlistenSuccess?.();
      unlistenError?.();
    };
  }, []);

  const loadSettings = async () => {
    try {
      const [smtpData, gmailData] = await Promise.all([
        invoke<SmtpSettingsData>('get_smtp_settings'),
        invoke<GmailOAuthStatus>('get_gmail_oauth_status'),
      ]);
      setSettings(smtpData);
      setGmailStatus(gmailData);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectGmail = async () => {
    setConnecting(true);
    setGmailError(null);
    setMessage(null);
    try {
      await invoke('start_gmail_oauth');
      // Result arrives via event listeners above
    } catch (error) {
      setConnecting(false);
      setGmailError(`Errore avvio OAuth: ${error}`);
    }
  };

  const handleDisconnectGmail = async () => {
    try {
      await invoke('disconnect_gmail_oauth');
      setGmailStatus({ connected: false, email: '' });
      setMessage({ type: 'success', text: 'Gmail disconnesso' });
    } catch (error) {
      setMessage({ type: 'error', text: `Disconnessione fallita: ${error}` });
    }
  };

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
          <Label htmlFor="smtp-enabled" className="text-slate-300">SMTP attivo</Label>
          <Switch
            id="smtp-enabled"
            checked={settings.smtp_enabled}
            onCheckedChange={(checked) => setSettings({ ...settings, smtp_enabled: checked })}
          />
        </div>
      </div>

      {/* ── Gmail OAuth2 Section ── */}
      <div className="mb-6 rounded-lg border border-slate-700 bg-slate-950 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Google G logo */}
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white shadow">
              <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
            </div>

            <div>
              <p className="text-sm font-semibold text-white">
                {gmailStatus.connected ? 'Gmail connesso' : 'Connetti con Google'}
              </p>
              {gmailStatus.connected ? (
                <p className="flex items-center gap-1 text-xs text-green-400">
                  <CheckCircle2 className="h-3 w-3" />
                  {gmailStatus.email}
                </p>
              ) : (
                <p className="text-xs text-slate-400">
                  OAuth2 — più sicuro di App Password, zero configurazione tecnica
                </p>
              )}
            </div>
          </div>

          {gmailStatus.connected ? (
            <Button
              variant="outline"
              size="sm"
              onClick={handleDisconnectGmail}
              className="border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              <XCircle className="mr-1.5 h-3.5 w-3.5" />
              Disconnetti
            </Button>
          ) : (
            <Button
              size="sm"
              onClick={handleConnectGmail}
              disabled={connecting}
              className="bg-white text-slate-900 hover:bg-slate-100 disabled:opacity-60"
            >
              {connecting && <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />}
              {connecting ? 'Connessione in corso...' : 'Connetti Gmail'}
            </Button>
          )}
        </div>

        {gmailError && (
          <p className="mt-3 rounded border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-400">
            {gmailError}
          </p>
        )}

        {!gmailStatus.connected && !connecting && (
          <p className="mt-3 text-xs text-slate-500">
            Il browser si aprirà per il login Google — nessuna password da configurare manualmente.
          </p>
        )}
      </div>

      {/* ── Divider ── */}
      <div className="relative my-6">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-slate-700" />
        </div>
        <div className="relative flex justify-center">
          <span className="bg-slate-900 px-3 text-xs text-slate-500">
            oppure configura SMTP manualmente
          </span>
        </div>
      </div>

      {/* ── Manual SMTP Form ── */}
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
          <Label htmlFor="smtp-email" className="text-slate-300">Email mittente</Label>
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
            Password app
            <span
              onClick={() => openUrl('https://myaccount.google.com/apppasswords')}
              className="ml-2 text-xs text-cyan-400 hover:text-cyan-300 underline cursor-pointer"
              role="link"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && openUrl('https://myaccount.google.com/apppasswords')}
            >
              (Genera per Gmail)
            </span>
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
          Test SMTP
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
          Salva SMTP
        </Button>
      </div>

      {/* Help text */}
      <p className="text-xs text-slate-500 mt-4">
        Per Gmail senza OAuth: genera una "Password app" da{' '}
        <span
          onClick={() => openUrl('https://myaccount.google.com/apppasswords')}
          className="text-cyan-400 hover:underline cursor-pointer"
          role="link"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && openUrl('https://myaccount.google.com/apppasswords')}
        >
          myaccount.google.com/apppasswords
        </span>{' '}
        (richiede 2FA attivo).
      </p>
    </Card>
  );
};
