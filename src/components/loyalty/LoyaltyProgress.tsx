// ═══════════════════════════════════════════════════════════════════
// FLUXION - Loyalty Progress Component (Fase 5)
// Tessera timbri digitale con progress bar
// ═══════════════════════════════════════════════════════════════════

import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { useLoyaltyInfo, useToggleVipStatus } from '@/hooks/use-loyalty'
import { getLoyaltyBadge } from '@/types/loyalty'
import { Star, Crown, Gift } from 'lucide-react'

interface LoyaltyProgressProps {
  clienteId: string
  showVipToggle?: boolean
  compact?: boolean
}

export function LoyaltyProgress({
  clienteId,
  showVipToggle = false,
  compact = false,
}: LoyaltyProgressProps) {
  const { data: loyalty, isLoading } = useLoyaltyInfo(clienteId)
  const toggleVip = useToggleVipStatus()

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-4 bg-muted rounded w-full" />
      </div>
    )
  }

  if (!loyalty) return null

  const badge = getLoyaltyBadge(loyalty)
  const isAtMilestone = loyalty.progress_percent >= 100

  if (compact) {
    return (
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="flex items-center gap-2">
              {loyalty.is_vip && <Crown className="h-4 w-4 text-yellow-500" />}
              <Progress value={loyalty.progress_percent} className="w-16 h-2" />
              <span className="text-xs text-muted-foreground">
                {loyalty.loyalty_visits}/{loyalty.loyalty_threshold}
              </span>
            </div>
          </TooltipTrigger>
          <TooltipContent>
            <p>
              {badge.emoji} {badge.label}
              {loyalty.visits_remaining > 0 &&
                ` - Mancano ${loyalty.visits_remaining} visite`}
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    )
  }

  return (
    <div className="space-y-3 p-4 rounded-lg border bg-card">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Star className="h-5 w-5 text-yellow-500" />
          <span className="font-medium">Tessera Fedeltà</span>
        </div>

        <div className="flex items-center gap-2">
          {loyalty.is_vip && (
            <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
              <Crown className="h-3 w-3 mr-1" />
              VIP
            </Badge>
          )}
          <Badge
            variant={isAtMilestone ? 'default' : 'outline'}
            className={isAtMilestone ? 'bg-green-600' : ''}
          >
            {badge.emoji} {badge.label}
          </Badge>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <Progress value={loyalty.progress_percent} className="h-3" />
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>
            {loyalty.loyalty_visits} / {loyalty.loyalty_threshold} visite
          </span>
          <span>
            {isAtMilestone ? (
              <span className="text-green-600 font-medium flex items-center gap-1">
                <Gift className="h-4 w-4" />
                Premio sbloccato!
              </span>
            ) : (
              `Mancano ${loyalty.visits_remaining} visite`
            )}
          </span>
        </div>
      </div>

      {/* Timbri Visuali */}
      <div className="flex gap-1 flex-wrap">
        {Array.from({ length: loyalty.loyalty_threshold }).map((_, i) => (
          <div
            key={i}
            className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
              i < loyalty.loyalty_visits
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-muted-foreground'
            }`}
          >
            {i < loyalty.loyalty_visits ? '✓' : i + 1}
          </div>
        ))}
      </div>

      {/* VIP Toggle */}
      {showVipToggle && (
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-2">
            <Crown className="h-4 w-4 text-yellow-500" />
            <Label htmlFor="vip-toggle" className="text-sm">
              Cliente VIP
            </Label>
          </div>
          <Switch
            id="vip-toggle"
            checked={loyalty.is_vip}
            onCheckedChange={(checked) =>
              toggleVip.mutate({ clienteId, isVip: checked })
            }
            disabled={toggleVip.isPending}
          />
        </div>
      )}

      {/* Referral Source */}
      {loyalty.referral_source && (
        <div className="text-xs text-muted-foreground pt-2 border-t">
          Consigliato da: {loyalty.referral_source}
        </div>
      )}
    </div>
  )
}
