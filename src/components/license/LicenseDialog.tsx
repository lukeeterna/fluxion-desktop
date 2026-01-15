// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Activation Dialog (Phase 8)
// Modal for license key activation
// ═══════════════════════════════════════════════════════════════════

import { useState, useCallback } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Key,
  Loader2,
  CheckCircle2,
  XCircle,
  Sparkles,
  Clock,
} from 'lucide-react';
import { useActivateLicense, useLicenseStatus } from '@/hooks/use-license';
import { formatLicenseKey, LICENSE_TIERS } from '@/types/license';

interface LicenseDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  allowClose?: boolean;
}

export function LicenseDialog({
  open,
  onOpenChange,
  allowClose = true,
}: LicenseDialogProps) {
  const [licenseKey, setLicenseKey] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const { data: status } = useLicenseStatus();
  const activateMutation = useActivateLicense();

  const handleKeyChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatLicenseKey(e.target.value);
    setLicenseKey(formatted);
    setError(null);
  }, []);

  const handleActivate = async () => {
    if (!licenseKey || licenseKey.length < 19) {
      setError('Inserisci una chiave di licenza valida');
      return;
    }

    setError(null);
    try {
      const result = await activateMutation.mutateAsync(licenseKey);
      if (result.success) {
        setSuccess(true);
        setTimeout(() => {
          onOpenChange(false);
          setSuccess(false);
          setLicenseKey('');
        }, 2000);
      } else {
        setError(result.message);
      }
    } catch {
      setError('Errore di connessione. Riprova.');
    }
  };

  const handleContinueTrial = () => {
    if (allowClose && status?.is_valid) {
      onOpenChange(false);
    }
  };

  const tierInfo = status ? LICENSE_TIERS[status.tier] : LICENSE_TIERS.none;

  return (
    <Dialog open={open} onOpenChange={allowClose ? onOpenChange : undefined}>
      <DialogContent
        className="sm:max-w-md"
        onPointerDownOutside={(e) => !allowClose && e.preventDefault()}
        onEscapeKeyDown={(e) => !allowClose && e.preventDefault()}
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Key className="h-5 w-5 text-primary" />
            Attiva FLUXION
          </DialogTitle>
          <DialogDescription>
            Inserisci la tua chiave di licenza per attivare tutte le funzionalità.
          </DialogDescription>
        </DialogHeader>

        {success ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <CheckCircle2 className="h-16 w-16 text-green-500 mb-4" />
            <h3 className="text-lg font-semibold text-green-700">
              Licenza Attivata!
            </h3>
            <p className="text-sm text-muted-foreground">
              Grazie per aver scelto FLUXION
            </p>
          </div>
        ) : (
          <>
            {/* Current Status */}
            {status && status.tier === 'trial' && status.is_valid && (
              <Alert className="border-yellow-500/50 bg-yellow-50">
                <Clock className="h-4 w-4 text-yellow-600" />
                <AlertDescription className="text-yellow-800">
                  <strong>Prova gratuita attiva</strong> - {status.days_remaining} giorni
                  rimanenti
                </AlertDescription>
              </Alert>
            )}

            {status && !status.is_valid && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  {status.tier === 'trial'
                    ? 'Il periodo di prova è terminato. Attiva una licenza per continuare.'
                    : 'La licenza è scaduta. Rinnova per continuare.'}
                </AlertDescription>
              </Alert>
            )}

            {/* License Key Input */}
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="license-key">Chiave di Licenza</Label>
                <Input
                  id="license-key"
                  placeholder="XXXX-XXXX-XXXX-XXXX"
                  value={licenseKey}
                  onChange={handleKeyChange}
                  className="font-mono text-center text-lg tracking-wider"
                  maxLength={19}
                  disabled={activateMutation.isPending}
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Tier Info */}
              <div className="rounded-lg border p-4 bg-muted/50">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="h-4 w-4 text-purple-500" />
                  <span className="font-medium">Piani Disponibili</span>
                </div>
                <div className="text-sm text-muted-foreground space-y-1">
                  <p>
                    <strong>FLUXION Base</strong> - Gestionale completo
                  </p>
                  <p>
                    <strong>FLUXION IA</strong> - Base + Voice Agent, WhatsApp AI
                  </p>
                </div>
              </div>
            </div>

            <DialogFooter className="flex-col sm:flex-row gap-2">
              {allowClose && status?.is_valid && (
                <Button
                  variant="outline"
                  onClick={handleContinueTrial}
                  className="w-full sm:w-auto"
                >
                  Continua con {tierInfo.name}
                </Button>
              )}
              <Button
                onClick={handleActivate}
                disabled={activateMutation.isPending || !licenseKey}
                className="w-full sm:w-auto"
              >
                {activateMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Attivazione...
                  </>
                ) : (
                  <>
                    <Key className="mr-2 h-4 w-4" />
                    Attiva Licenza
                  </>
                )}
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
