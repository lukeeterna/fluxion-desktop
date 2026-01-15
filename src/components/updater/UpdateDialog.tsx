// ═══════════════════════════════════════════════════════════════════
// FLUXION - Update Dialog (Phase 8)
// Shows available updates and download progress
// ═══════════════════════════════════════════════════════════════════

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Download,
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle,
  Sparkles,
} from 'lucide-react';
import { useUpdater } from '@/hooks/use-updater';

interface UpdateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function UpdateDialog({ open, onOpenChange }: UpdateDialogProps) {
  const {
    checking,
    available,
    downloading,
    progress,
    error,
    update,
    checkForUpdates,
    downloadAndInstall,
    dismissUpdate,
  } = useUpdater();

  const handleClose = () => {
    if (!downloading) {
      dismissUpdate();
      onOpenChange(false);
    }
  };

  const handleDownload = async () => {
    await downloadAndInstall();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5 text-primary" />
            Aggiornamenti FLUXION
          </DialogTitle>
          <DialogDescription>
            Verifica e installa gli aggiornamenti disponibili.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Checking State */}
          {checking && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <span className="ml-2">Verifica aggiornamenti...</span>
            </div>
          )}

          {/* No Update Available */}
          {!checking && !available && !error && (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <CheckCircle2 className="h-16 w-16 text-green-500 mb-4" />
              <h3 className="text-lg font-semibold">
                FLUXION è aggiornato
              </h3>
              <p className="text-sm text-muted-foreground">
                Stai usando l'ultima versione disponibile.
              </p>
            </div>
          )}

          {/* Update Available */}
          {available && update && !downloading && (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-4 rounded-lg border bg-primary/5">
                <Sparkles className="h-8 w-8 text-primary" />
                <div>
                  <h3 className="font-semibold">
                    Nuova versione disponibile!
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Versione {update.version} pronta per il download
                  </p>
                </div>
              </div>

              {update.body && (
                <div className="p-3 rounded border bg-muted/50">
                  <p className="text-sm font-medium mb-1">Novità:</p>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {update.body}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Downloading */}
          {downloading && (
            <div className="space-y-4 py-4">
              <div className="flex items-center gap-2">
                <Download className="h-5 w-5 text-primary animate-pulse" />
                <span className="font-medium">Download in corso...</span>
              </div>
              <Progress value={progress} className="h-2" />
              <p className="text-sm text-muted-foreground text-center">
                {progress}% completato
              </p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          {!checking && !downloading && (
            <>
              <Button variant="outline" onClick={handleClose}>
                Chiudi
              </Button>

              {!available && (
                <Button onClick={() => checkForUpdates()}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Verifica
                </Button>
              )}

              {available && (
                <Button onClick={handleDownload}>
                  <Download className="h-4 w-4 mr-2" />
                  Scarica e Installa
                </Button>
              )}
            </>
          )}

          {downloading && (
            <Button disabled>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Installazione...
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
