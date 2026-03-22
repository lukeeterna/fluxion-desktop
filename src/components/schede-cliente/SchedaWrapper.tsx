// ═══════════════════════════════════════════════════════════════════
// FLUXION - SchedaWrapper — Shared visual wrapper for all vertical cards
// Glassmorphism header · StatChips · Alert badges · Accent colors
// ═══════════════════════════════════════════════════════════════════

import { type FC, type ReactNode } from 'react';
import { Button } from '../ui/button';
import { Save, Loader2 } from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// COLOR MAP
// ─────────────────────────────────────────────────────────────────────

type AccentColor = 'purple' | 'blue' | 'red' | 'pink' | 'green' | 'indigo';

interface ColorTokens {
  gradient: string;
  iconBg: string;
  iconText: string;
  borderAccent: string;
  iconBorder: string;
  shadowAccent: string;
  btnBg: string;
  btnHover: string;
  btnShadow: string;
  statIconText: string;
  blurCircle1: string;
  blurCircle2: string;
}

const COLOR_MAP: Record<AccentColor, ColorTokens> = {
  purple: {
    gradient: 'from-purple-950/60',
    iconBg: 'bg-purple-500/15',
    iconText: 'text-purple-400',
    borderAccent: 'border-purple-500/10',
    iconBorder: 'border-purple-500/25',
    shadowAccent: 'shadow-purple-500/10',
    btnBg: 'bg-purple-600',
    btnHover: 'hover:bg-purple-500',
    btnShadow: 'shadow-purple-900/40',
    statIconText: 'text-purple-300',
    blurCircle1: 'bg-purple-500/8',
    blurCircle2: 'bg-purple-400/5',
  },
  blue: {
    gradient: 'from-blue-950/60',
    iconBg: 'bg-blue-500/15',
    iconText: 'text-blue-400',
    borderAccent: 'border-blue-500/10',
    iconBorder: 'border-blue-500/25',
    shadowAccent: 'shadow-blue-500/10',
    btnBg: 'bg-blue-600',
    btnHover: 'hover:bg-blue-500',
    btnShadow: 'shadow-blue-900/40',
    statIconText: 'text-blue-300',
    blurCircle1: 'bg-blue-500/8',
    blurCircle2: 'bg-blue-400/5',
  },
  red: {
    gradient: 'from-red-950/60',
    iconBg: 'bg-red-500/15',
    iconText: 'text-red-400',
    borderAccent: 'border-red-500/10',
    iconBorder: 'border-red-500/25',
    shadowAccent: 'shadow-red-500/10',
    btnBg: 'bg-red-600',
    btnHover: 'hover:bg-red-500',
    btnShadow: 'shadow-red-900/40',
    statIconText: 'text-red-300',
    blurCircle1: 'bg-red-500/8',
    blurCircle2: 'bg-red-400/5',
  },
  pink: {
    gradient: 'from-pink-950/60',
    iconBg: 'bg-pink-500/15',
    iconText: 'text-pink-400',
    borderAccent: 'border-pink-500/10',
    iconBorder: 'border-pink-500/25',
    shadowAccent: 'shadow-pink-500/10',
    btnBg: 'bg-pink-600',
    btnHover: 'hover:bg-pink-500',
    btnShadow: 'shadow-pink-900/40',
    statIconText: 'text-pink-300',
    blurCircle1: 'bg-pink-500/8',
    blurCircle2: 'bg-pink-400/5',
  },
  green: {
    gradient: 'from-green-950/60',
    iconBg: 'bg-green-500/15',
    iconText: 'text-green-400',
    borderAccent: 'border-green-500/10',
    iconBorder: 'border-green-500/25',
    shadowAccent: 'shadow-green-500/10',
    btnBg: 'bg-green-600',
    btnHover: 'hover:bg-green-500',
    btnShadow: 'shadow-green-900/40',
    statIconText: 'text-green-300',
    blurCircle1: 'bg-green-500/8',
    blurCircle2: 'bg-green-400/5',
  },
  indigo: {
    gradient: 'from-indigo-950/60',
    iconBg: 'bg-indigo-500/15',
    iconText: 'text-indigo-400',
    borderAccent: 'border-indigo-500/10',
    iconBorder: 'border-indigo-500/25',
    shadowAccent: 'shadow-indigo-500/10',
    btnBg: 'bg-indigo-600',
    btnHover: 'hover:bg-indigo-500',
    btnShadow: 'shadow-indigo-900/40',
    statIconText: 'text-indigo-300',
    blurCircle1: 'bg-indigo-500/8',
    blurCircle2: 'bg-indigo-400/5',
  },
};

// ─────────────────────────────────────────────────────────────────────
// STAT CHIP (exported for reuse)
// ─────────────────────────────────────────────────────────────────────

interface StatChipProps {
  icon: ReactNode;
  label: string;
  value: string;
  accentColor?: AccentColor;
}

export function StatChip({ icon, label, value, accentColor = 'purple' }: StatChipProps) {
  const tokens = COLOR_MAP[accentColor];
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full backdrop-blur-sm">
      <span className={`${tokens.statIconText} w-3.5 h-3.5`}>{icon}</span>
      <span className="text-slate-400 text-xs">{label}</span>
      <span className="text-white text-xs font-semibold">{value}</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// ALERT BADGE
// ─────────────────────────────────────────────────────────────────────

interface AlertBadgeProps {
  label: string;
  icon?: ReactNode;
  color?: 'red' | 'amber';
}

function AlertBadge({ label, icon, color = 'red' }: AlertBadgeProps) {
  const colorClasses = color === 'red'
    ? 'bg-red-500/15 border-red-500/30 text-red-400'
    : 'bg-amber-500/15 border-amber-500/30 text-amber-400';
  return (
    <span className={`flex items-center gap-1 px-2 py-0.5 border rounded-full text-xs font-medium ${colorClasses}`}>
      {icon}
      {label}
    </span>
  );
}

// ─────────────────────────────────────────────────────────────────────
// WRAPPER PROPS
// ─────────────────────────────────────────────────────────────────────

interface SchedaWrapperProps {
  title: string;
  subtitle: string;
  icon: ReactNode;
  accentColor: AccentColor;
  stats?: Array<{ icon: ReactNode; label: string; value: string }>;
  onSave?: () => void;
  isSaving?: boolean;
  alerts?: Array<{ label: string; icon?: ReactNode; color?: 'red' | 'amber' }>;
  headerActions?: ReactNode;
  children: ReactNode;
  isLoading?: boolean;
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────

export const SchedaWrapper: FC<SchedaWrapperProps> = ({
  title,
  subtitle,
  icon,
  accentColor,
  stats,
  onSave,
  isSaving = false,
  alerts,
  headerActions,
  children,
  isLoading = false,
}) => {
  const tokens = COLOR_MAP[accentColor];

  if (isLoading) {
    return (
      <div className="rounded-2xl overflow-hidden border border-slate-700/60 shadow-2xl bg-slate-900">
        <div className="flex items-center justify-center py-16">
          <div className="flex flex-col items-center gap-3 text-slate-500">
            <Loader2 className="w-8 h-8 animate-spin" />
            <p className="text-sm">Caricamento scheda...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl overflow-hidden border border-slate-700/60 shadow-2xl bg-slate-900">
      {/* Glassmorphism header */}
      <div className={`relative overflow-hidden bg-gradient-to-br ${tokens.gradient} via-slate-900 to-slate-900 ${tokens.borderAccent} border-b px-6 py-5`}>
        {/* Ambient blur circles */}
        <div className={`absolute -top-10 -right-10 w-48 h-48 ${tokens.blurCircle1} rounded-full blur-3xl pointer-events-none`} />
        <div className={`absolute -bottom-8 left-20 w-32 h-32 ${tokens.blurCircle2} rounded-full blur-2xl pointer-events-none`} />

        <div className="relative flex items-start justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className={`p-3 ${tokens.iconBg} rounded-2xl ${tokens.iconBorder} border shadow-lg ${tokens.shadowAccent}`}>
              <span className={tokens.iconText}>{icon}</span>
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-lg font-bold text-white">{title}</h2>
                {alerts?.map((alert, i) => (
                  <AlertBadge key={i} label={alert.label} icon={alert.icon} color={alert.color} />
                ))}
              </div>
              <p className="text-slate-500 text-xs mt-0.5">{subtitle}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {stats?.map((stat, i) => (
              <StatChip
                key={i}
                icon={stat.icon}
                label={stat.label}
                value={stat.value}
                accentColor={accentColor}
              />
            ))}
            {headerActions}
            {onSave && (
              <Button
                onClick={onSave}
                disabled={isSaving}
                className={`${tokens.btnBg} ${tokens.btnHover} text-white shadow-lg ${tokens.btnShadow} ml-2`}
              >
                {isSaving ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Save className="w-4 h-4 mr-2" />
                )}
                {isSaving ? 'Salvataggio...' : 'Salva'}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-6">
        {children}
      </div>
    </div>
  );
};
