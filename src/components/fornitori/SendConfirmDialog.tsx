// ═══════════════════════════════════════════════════════════════════
// FLUXION - Send Confirmation Dialog
// Preview and confirm before sending order via Email/WhatsApp
// ═══════════════════════════════════════════════════════════════════

import { type FC } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Mail, MessageCircle, Send, X } from 'lucide-react';

interface SendConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  type: 'email' | 'whatsapp';
  recipient: string;
  recipientName: string;
  orderNumber: string;
  message: string;
  onConfirm: () => void;
  isSending?: boolean;
}

export const SendConfirmDialog: FC<SendConfirmDialogProps> = ({
  open,
  onOpenChange,
  type,
  recipient,
  recipientName,
  orderNumber,
  message,
  onConfirm,
  isSending = false,
}) => {
  const isWhatsApp = type === 'whatsapp';
  const Icon = isWhatsApp ? MessageCircle : Mail;
  const colorClass = isWhatsApp ? 'text-green-400' : 'text-cyan-400';
  const bgClass = isWhatsApp ? 'bg-green-500' : 'bg-cyan-500';
  const borderClass = isWhatsApp ? 'border-green-700' : 'border-cyan-700';

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-950 border-slate-800 max-w-2xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="text-white flex items-center gap-2">
            <Icon className={`h-5 w-5 ${colorClass}`} />
            Conferma Invio {isWhatsApp ? 'WhatsApp' : 'Email'}
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Verifica il messaggio prima di inviare
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto space-y-4 py-4">
          {/* Recipient Info */}
          <div className={`p-3 rounded-lg border ${borderClass} bg-slate-900/50`}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-xs uppercase tracking-wide">Destinatario</p>
                <p className="text-white font-medium">{recipientName}</p>
                <p className={`text-sm ${colorClass}`}>{recipient}</p>
              </div>
              <Badge className={`${bgClass} text-white`}>
                {orderNumber}
              </Badge>
            </div>
          </div>

          {/* Message Preview */}
          <div className="space-y-2">
            <p className="text-slate-400 text-xs uppercase tracking-wide">Anteprima Messaggio</p>
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 max-h-[300px] overflow-y-auto">
              <pre className="text-slate-200 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                {message}
              </pre>
            </div>
          </div>

          {/* Warning */}
          <div className="flex items-start gap-2 p-3 bg-yellow-900/20 border border-yellow-800/50 rounded-lg">
            <span className="text-yellow-500 text-lg">⚠️</span>
            <p className="text-yellow-200 text-sm">
              {isWhatsApp
                ? 'Il messaggio verrà inviato automaticamente tramite WhatsApp. Assicurati che il numero sia corretto.'
                : 'Si aprirà il tuo client email con il messaggio pre-compilato. Dovrai cliccare "Invia" nel client email.'
              }
            </p>
          </div>
        </div>

        <DialogFooter className="border-t border-slate-800 pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isSending}
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
          >
            <X className="h-4 w-4 mr-2" />
            Annulla
          </Button>
          <Button
            onClick={onConfirm}
            disabled={isSending}
            className={`${bgClass} hover:opacity-90 text-white`}
          >
            <Send className="h-4 w-4 mr-2" />
            {isSending ? 'Invio in corso...' : 'Conferma Invio'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
