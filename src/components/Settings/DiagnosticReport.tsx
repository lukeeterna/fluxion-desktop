// ═══════════════════════════════════════════════════════════════════
// FLUXION - Diagnostic Report (S184 α.3.1-F)
// "Invia rapporto" button — l'utente descrive il problema, FLUXION
// raccoglie un payload privacy-safe e lo invia (via CF Worker → Resend)
// a fluxion.gestionale@gmail.com con un ticket_id univoco.
//
// Nessun dato cliente (nomi, telefoni, transcript, XML SDI) viene inviato.
// Solo: app version, OS, percorsi anonimizzati, conteggi tabelle, esiti probe.
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const MAX_MESSAGE_CHARS = 2_000;
const MIN_MESSAGE_CHARS = 5;

interface SendDiagnosticResult {
  ok: boolean;
  ticket_id: string | null;
  message: string;
}

type SendStatus = 'idle' | 'sending' | 'success' | 'error';

export const DiagnosticReport: FC = () => {
  const [email, setEmail] = useState<string>('');
  const [message, setMessage] = useState<string>('');
  const [status, setStatus] = useState<SendStatus>('idle');
  const [resultMessage, setResultMessage] = useState<string>('');
  const [ticketId, setTicketId] = useState<string | null>(null);
  const [previewOpen, setPreviewOpen] = useState<boolean>(false);
  const [previewJson, setPreviewJson] = useState<string>('');

  const isValidEmail = (v: string): boolean => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim());

  const canSend =
    isValidEmail(email) &&
    message.trim().length >= MIN_MESSAGE_CHARS &&
    status !== 'sending';

  const handlePreview = useCallback(async () => {
    try {
      const payload = await invoke<unknown>('collect_diagnostic');
      setPreviewJson(JSON.stringify(payload, null, 2));
      setPreviewOpen(true);
    } catch (err) {
      setPreviewJson(`Errore raccolta diagnostica: ${String(err)}`);
      setPreviewOpen(true);
    }
  }, []);

  const handleSend = useCallback(async () => {
    if (!canSend) return;
    setStatus('sending');
    setResultMessage('');
    setTicketId(null);
    try {
      const res = await invoke<SendDiagnosticResult>('send_diagnostic_report', {
        args: {
          user_email: email.trim().toLowerCase(),
          user_message: message.trim(),
          sentry_event_ids: null,
        },
      });
      if (res.ok) {
        setStatus('success');
        setTicketId(res.ticket_id);
        setResultMessage(res.message);
        // Reset form on success (lasciamo l'email per comodità se manda altri ticket)
        setMessage('');
      } else {
        setStatus('error');
        setResultMessage(res.message || 'Invio non riuscito');
      }
    } catch (err) {
      setStatus('error');
      setResultMessage(String(err));
    }
  }, [canSend, email, message]);

  const charsLeft = MAX_MESSAGE_CHARS - message.length;

  return (
    <Card
      className="p-6 border-slate-700/50"
      data-testid="diagnostic-report-card"
    >
      <div className="space-y-1 mb-4">
        <h3 className="text-white text-lg font-semibold">Invia rapporto al supporto</h3>
        <p className="text-slate-400 text-sm">
          Hai un problema? Descrivilo qui sotto. FLUXION allega automaticamente
          informazioni tecniche utili (versione, OS, esiti delle verifiche) ma{' '}
          <strong className="text-slate-200">nessun dato dei tuoi clienti</strong>.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <Label htmlFor="diag-email" className="text-slate-300 text-sm">
            La tua email (per la risposta)
          </Label>
          <Input
            id="diag-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tuonome@esempio.it"
            disabled={status === 'sending'}
            data-testid="diag-email-input"
            className="mt-1 bg-slate-900 border-slate-700 text-slate-200"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <Label htmlFor="diag-message" className="text-slate-300 text-sm">
              Descrivi il problema
            </Label>
            <span
              className={`text-xs ${charsLeft < 100 ? 'text-amber-400' : 'text-slate-500'}`}
            >
              {charsLeft} caratteri rimasti
            </span>
          </div>
          <textarea
            id="diag-message"
            value={message}
            onChange={(e) => setMessage(e.target.value.slice(0, MAX_MESSAGE_CHARS))}
            placeholder="Es. Quando apro la pagina Calendario, non vedo gli appuntamenti di oggi. Ho riavviato l'app ma il problema resta…"
            disabled={status === 'sending'}
            rows={6}
            data-testid="diag-message-input"
            className="w-full rounded-md bg-slate-900 border border-slate-700 text-slate-200 text-sm px-3 py-2 resize-y focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
          {message.length > 0 && message.trim().length < MIN_MESSAGE_CHARS && (
            <p className="text-amber-400 text-xs mt-1">
              Scrivi almeno {MIN_MESSAGE_CHARS} caratteri.
            </p>
          )}
        </div>

        <div className="flex flex-wrap gap-2 items-center">
          <Button
            onClick={handleSend}
            disabled={!canSend}
            data-testid="diag-send-btn"
            className="bg-cyan-600 hover:bg-cyan-500 text-white"
          >
            {status === 'sending' ? 'Invio in corso…' : 'Invia rapporto'}
          </Button>
          <Button
            onClick={handlePreview}
            disabled={status === 'sending'}
            variant="outline"
            data-testid="diag-preview-btn"
            className="border-slate-600 text-slate-200 hover:bg-slate-800"
          >
            Vedi cosa viene inviato
          </Button>
        </div>

        {status === 'success' && ticketId && (
          <div
            data-testid="diag-success"
            className="bg-emerald-900/30 border border-emerald-700/50 rounded-lg p-3 text-emerald-200 text-sm"
          >
            <p className="font-medium">Rapporto inviato — grazie.</p>
            <p className="text-xs text-emerald-300/80 mt-1">
              Ticket: <code className="font-mono">{ticketId}</code>
              {resultMessage ? ` · ${resultMessage}` : ''}
            </p>
            <p className="text-xs text-emerald-300/80 mt-1">
              Riceverai una risposta a <strong>{email}</strong> appena possibile.
            </p>
          </div>
        )}

        {status === 'error' && (
          <div
            data-testid="diag-error"
            className="bg-red-900/30 border border-red-700/50 rounded-lg p-3 text-red-200 text-sm"
          >
            <p className="font-medium">Invio non riuscito</p>
            <p className="text-xs text-red-300/80 mt-1">{resultMessage}</p>
            <p className="text-xs text-red-300/80 mt-1">
              Puoi riprovare oppure scriverci direttamente a{' '}
              <strong>fluxion.gestionale@gmail.com</strong>.
            </p>
          </div>
        )}

        {previewOpen && (
          <div className="bg-slate-900 border border-slate-700 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-slate-200 text-sm font-medium">
                Anteprima dati inviati (privacy-safe)
              </h4>
              <button
                type="button"
                onClick={() => setPreviewOpen(false)}
                className="text-slate-400 hover:text-slate-200 text-xs"
              >
                Chiudi
              </button>
            </div>
            <pre className="text-slate-300 text-xs font-mono max-h-72 overflow-auto whitespace-pre-wrap break-all">
              {previewJson}
            </pre>
          </div>
        )}
      </div>
    </Card>
  );
};
