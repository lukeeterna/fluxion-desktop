// ═══════════════════════════════════════════════════════════════════
// FLUXION - SMTP Settings Component
// Configure email settings for supplier order sending
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Mail, Eye, EyeOff, Save, TestTube, Loader2 } from 'lucide-react';

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
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await invoke<SmtpSettingsData>('get_smtp_settings');
      setSettings(data);
    } catch (error) {
      console.error('Failed to load SMTP settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      await invoke('save_smtp_settings', { settings });
      setMessage({ type: 'success', text: 'Impostazioni SMTP salvate con successo' });
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
      setMessage({ type: 'success', text: 'Connessione SMTP valida' });
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
            Configurazione Email SMTP
          </h2>
          <p className="text-sm text-slate-400">
            Configura l'invio email per ordini fornitori
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Label htmlFor="smtp-enabled" className="text-slate-300">Attivo</Label>
          <Switch
            id="smtp-enabled"
            checked={settings.smtp_enabled}
            onCheckedChange={(checked) => setSettings({ ...settings, smtp_enabled: checked })}
          />
        </div>
      </div>

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
            App Password
            <a
              href="https://myaccount.google.com/apppasswords"
              target="_blank"
              rel="noopener noreferrer"
              className="ml-2 text-xs text-cyan-400 hover:text-cyan-300"
            >
              (Genera per Gmail)
            </a>
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
          Test Connessione
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
          Salva Impostazioni
        </Button>
      </div>

      {/* Help text */}
      <p className="text-xs text-slate-500 mt-4">
        Per Gmail, genera una "App Password" dalle impostazioni di sicurezza Google.
        Non usare la password normale dell'account.
      </p>
    </Card>
  );
};
