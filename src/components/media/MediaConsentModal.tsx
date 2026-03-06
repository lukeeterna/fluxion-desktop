// ═══════════════════════════════════════════════════════════════════
// FLUXION - MediaConsentModal
// GDPR consent obbligatorio per foto cliniche (Art. 9 GDPR)
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { Label } from '../ui/label';
import { useUpdateMediaConsent } from '../../hooks/use-media';
import { toast } from 'sonner';

interface Props {
  open: boolean;
  clienteId: number;
  clienteNome: string;
  onConfirmed: () => void;
  onCancel: () => void;
}

export function MediaConsentModal({
  open,
  clienteId,
  clienteNome,
  onConfirmed,
  onCancel,
}: Props) {
  const [checked, setChecked] = useState(false);
  const [saving, setSaving] = useState(false);
  const updateConsent = useUpdateMediaConsent();
  const today = new Date().toLocaleDateString('it-IT', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  });

  const handleConfirm = async () => {
    if (!checked) return;
    setSaving(true);
    try {
      await updateConsent.mutateAsync({
        clienteId,
        consenso_interno: true,
        consenso_social: false,
        consenso_clinico: true,
      });
      toast.success('Consenso GDPR registrato');
      onConfirmed();
    } catch {
      toast.error('Errore salvataggio consenso');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onCancel()}>
      <DialogContent className="max-w-md overflow-hidden">
        {/* Header GDPR */}
        <div className="-mx-6 -mt-6 mb-4 px-6 py-4 bg-gradient-to-r from-amber-500/20 to-orange-500/20 border-b border-amber-500/30">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <DialogTitle className="text-amber-300 text-base">
                Consenso GDPR — Immagini Cliniche
              </DialogTitle>
              <DialogDescription className="text-amber-400/70 text-xs mt-0.5">
                Art. 9 GDPR — Dati biometrici e sanitari
              </DialogDescription>
            </div>
          </div>
        </div>

        {/* Avviso */}
        <div className="flex items-start gap-2 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg mb-4">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-xs text-amber-300/80">
            Le immagini cliniche sono dati personali sensibili. Il GDPR richiede consenso
            esplicito e documentato prima della raccolta.
          </p>
        </div>

        {/* Dichiarazione */}
        <div className="bg-card border border-border rounded-lg p-4 mb-4 text-sm text-foreground/80 leading-relaxed">
          <p>
            Confermo di avere il{' '}
            <strong className="text-foreground">consenso scritto</strong> del paziente{' '}
            <strong className="text-primary">{clienteNome}</strong> per raccogliere e
            conservare immagini cliniche ai sensi dell'Art. 9 GDPR.
          </p>
          <p className="mt-2 text-muted-foreground text-xs">
            Data consenso: <strong>{today}</strong>
          </p>
        </div>

        {/* Checkbox */}
        <div className="flex items-start gap-3 mb-6">
          <Checkbox
            id="gdpr-consent"
            checked={checked}
            onCheckedChange={(v) => setChecked(v === true)}
            className="mt-0.5"
          />
          <Label htmlFor="gdpr-consent" className="text-sm text-foreground/80 cursor-pointer leading-relaxed">
            Confermo di avere ricevuto il modulo di consenso firmato dal paziente e che il
            documento è conservato nel fascicolo clinico del cliente.
          </Label>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button variant="outline" className="flex-1" onClick={onCancel}>
            Annulla
          </Button>
          <Button
            className="flex-1"
            disabled={!checked || saving}
            onClick={handleConfirm}
          >
            {saving ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Salvo...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Confermo consenso
              </span>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
