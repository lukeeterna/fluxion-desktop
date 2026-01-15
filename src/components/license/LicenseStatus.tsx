// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Status Badge (Phase 8)
// Shows current license status in header/settings
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Key,
  CheckCircle,
  Clock,
  AlertTriangle,
  XCircle,
  Sparkles,
  RefreshCw,
  LogOut,
  Loader2,
} from 'lucide-react';
import { useLicenseStatus, useValidateLicenseOnline, useDeactivateLicense } from '@/hooks/use-license';
import { LICENSE_TIERS, getLicenseExpiryMessage } from '@/types/license';
import { LicenseDialog } from './LicenseDialog';

interface LicenseStatusProps {
  showDetails?: boolean;
  className?: string;
}

export function LicenseStatus({ showDetails = false, className }: LicenseStatusProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { data: status, isLoading } = useLicenseStatus();
  const validateMutation = useValidateLicenseOnline();
  const deactivateMutation = useDeactivateLicense();

  if (isLoading) {
    return (
      <Badge variant="outline" className={className}>
        <Loader2 className="h-3 w-3 animate-spin mr-1" />
        Caricamento...
      </Badge>
    );
  }

  if (!status) return null;

  const tierInfo = LICENSE_TIERS[status.tier] || LICENSE_TIERS.none;
  const expiryMessage = getLicenseExpiryMessage(status);

  // Determine badge variant and icon
  const getBadgeConfig = () => {
    if (!status.is_valid) {
      return {
        variant: 'destructive' as const,
        icon: <XCircle className="h-3 w-3 mr-1" />,
        text: 'Licenza Scaduta',
      };
    }

    switch (status.tier) {
      case 'trial':
        return {
          variant: 'secondary' as const,
          icon: <Clock className="h-3 w-3 mr-1" />,
          text: `Trial (${status.days_remaining}g)`,
        };
      case 'ia':
        return {
          variant: 'default' as const,
          icon: <Sparkles className="h-3 w-3 mr-1" />,
          text: 'FLUXION IA',
        };
      case 'base':
        return {
          variant: 'outline' as const,
          icon: <CheckCircle className="h-3 w-3 mr-1" />,
          text: 'FLUXION Base',
        };
      default:
        return {
          variant: 'outline' as const,
          icon: <Key className="h-3 w-3 mr-1" />,
          text: tierInfo.name,
        };
    }
  };

  const badgeConfig = getBadgeConfig();

  if (!showDetails) {
    return (
      <>
        <Badge
          variant={badgeConfig.variant}
          className={`cursor-pointer ${className}`}
          onClick={() => setDialogOpen(true)}
        >
          {badgeConfig.icon}
          {badgeConfig.text}
        </Badge>
        <LicenseDialog open={dialogOpen} onOpenChange={setDialogOpen} />
      </>
    );
  }

  // Full details view for settings page
  return (
    <div className={`rounded-lg border p-4 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Key className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Licenza</h3>
        </div>
        <Badge variant={badgeConfig.variant}>
          {badgeConfig.icon}
          {badgeConfig.text}
        </Badge>
      </div>

      <div className="space-y-3 text-sm">
        {/* Status Info */}
        <div className="flex justify-between">
          <span className="text-muted-foreground">Piano:</span>
          <span className="font-medium">{tierInfo.name}</span>
        </div>

        <div className="flex justify-between">
          <span className="text-muted-foreground">Stato:</span>
          <span className={`font-medium ${status.is_valid ? 'text-green-600' : 'text-red-600'}`}>
            {status.is_valid ? 'Attiva' : 'Non valida'}
          </span>
        </div>

        {status.days_remaining !== null && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Scadenza:</span>
            <span className="font-medium">
              {status.days_remaining > 0
                ? `${status.days_remaining} giorni`
                : 'Scaduta'}
            </span>
          </div>
        )}

        {status.machine_name && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Dispositivo:</span>
            <span className="font-medium truncate max-w-[150px]">
              {status.machine_name}
            </span>
          </div>
        )}

        {status.last_validated_at && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Ultima verifica:</span>
            <span className="font-medium">
              {new Date(status.last_validated_at).toLocaleDateString('it-IT')}
            </span>
          </div>
        )}

        {/* Expiry Warning */}
        {expiryMessage && (
          <div className="flex items-center gap-2 p-2 rounded bg-yellow-50 border border-yellow-200 text-yellow-800">
            <AlertTriangle className="h-4 w-4" />
            <span className="text-xs">{expiryMessage}</span>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          {!status.is_activated && (
            <Button
              size="sm"
              onClick={() => setDialogOpen(true)}
              className="flex-1"
            >
              <Key className="h-4 w-4 mr-1" />
              Attiva Licenza
            </Button>
          )}

          {status.is_activated && (
            <>
              <Button
                size="sm"
                variant="outline"
                onClick={() => validateMutation.mutate()}
                disabled={validateMutation.isPending}
                className="flex-1"
              >
                {validateMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4 mr-1" />
                    Verifica
                  </>
                )}
              </Button>

              <Popover>
                <PopoverTrigger asChild>
                  <Button size="sm" variant="ghost">
                    <LogOut className="h-4 w-4" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-64">
                  <p className="text-sm mb-3">
                    Vuoi disattivare la licenza su questo dispositivo?
                  </p>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => deactivateMutation.mutate()}
                    disabled={deactivateMutation.isPending}
                    className="w-full"
                  >
                    {deactivateMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      'Disattiva'
                    )}
                  </Button>
                </PopoverContent>
              </Popover>
            </>
          )}
        </div>
      </div>

      <LicenseDialog open={dialogOpen} onOpenChange={setDialogOpen} />
    </div>
  );
}
