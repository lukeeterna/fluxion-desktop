// ═══════════════════════════════════════════════════════════════════
// FLUXION - Sara Trial Banner
// Shows countdown for Sara AI trial period (Base tier).
// Shows offline warning when approaching grace period limit.
// ═══════════════════════════════════════════════════════════════════

import { Clock, WifiOff, AlertTriangle, Sparkles } from 'lucide-react';
import { openUrl } from '@tauri-apps/plugin-opener';
import type { PhoneHomeState } from '../../hooks/use-phone-home';

interface SaraTrialBannerProps {
  phoneHome: PhoneHomeState;
}

export function SaraTrialBanner({ phoneHome }: SaraTrialBannerProps) {
  const { result, saraEnabled, saraDaysRemaining, tier } = phoneHome;

  // Nothing to show if no result yet or Pro tier (Sara always on)
  if (!result) return null;
  if (tier === 'pro' || tier === 'enterprise') return null;

  // Sara expired — show upgrade CTA
  if (!saraEnabled && result.status !== 'offline') {
    return (
      <div className="mx-4 mt-2 rounded-lg bg-amber-900/30 border border-amber-700/50 px-4 py-3 flex items-center gap-3">
        <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-amber-200">
            <strong>Sara AI non è più attiva.</strong>{' '}
            Passa a FLUXION Pro per riattivare Sara e le prenotazioni automatiche.
          </p>
        </div>
        <button
          onClick={() => openUrl('https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702')}
          className="shrink-0 rounded-md bg-amber-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-amber-500 transition-colors cursor-pointer border-none"
        >
          Passa a Pro
        </button>
      </div>
    );
  }

  // Offline warning — grace period running
  if (result.status === 'offline' && !saraEnabled) {
    return (
      <div className="mx-4 mt-2 rounded-lg bg-red-900/30 border border-red-700/50 px-4 py-3 flex items-center gap-3">
        <WifiOff className="h-5 w-5 text-red-400 shrink-0" />
        <p className="text-sm text-red-200">
          <strong>Modalità offline.</strong>{' '}
          Sara è disattivata — connettiti a internet per riattivare.
        </p>
      </div>
    );
  }

  // Trial countdown — show only when ≤14 days remaining
  if (saraDaysRemaining !== null && saraDaysRemaining <= 14 && saraDaysRemaining > 0) {
    const isUrgent = saraDaysRemaining <= 3;
    const bgClass = isUrgent
      ? 'bg-orange-900/30 border-orange-700/50'
      : 'bg-cyan-900/20 border-cyan-700/30';
    const textClass = isUrgent ? 'text-orange-200' : 'text-cyan-200';
    const iconClass = isUrgent ? 'text-orange-400' : 'text-cyan-400';
    const Icon = isUrgent ? Clock : Sparkles;

    return (
      <div className={`mx-4 mt-2 rounded-lg ${bgClass} border px-4 py-3 flex items-center gap-3`}>
        <Icon className={`h-5 w-5 ${iconClass} shrink-0`} />
        <div className="flex-1 min-w-0">
          <p className={`text-sm ${textClass}`}>
            {isUrgent ? (
              <>
                <strong>Sara si disattiva tra {saraDaysRemaining} giorn{saraDaysRemaining === 1 ? 'o' : 'i'}!</strong>{' '}
                Passa a Pro per tenerla attiva.
              </>
            ) : (
              <>
                <strong>{saraDaysRemaining} giorni rimanenti</strong> del periodo di prova Sara.{' '}
                Passa a Pro per tenerla per sempre.
              </>
            )}
          </p>
        </div>
        <button
          onClick={() => openUrl('https://fluxion.lemonsqueezy.com/checkout/buy/14806a0d-ac44-44af-a051-8fe8c559d702')}
          className="shrink-0 rounded-md bg-cyan-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-cyan-500 transition-colors cursor-pointer border-none"
        >
          Passa a Pro
        </button>
      </div>
    );
  }

  return null;
}
