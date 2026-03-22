// ═══════════════════════════════════════════════════════════════════
// FLUXION - SchedaTabs — Shared tab styling for all vertical cards
// Matches Parrucchiere's premium tab design
// ═══════════════════════════════════════════════════════════════════

import { type FC, type ReactNode } from 'react';
import { TabsList, TabsTrigger } from '../ui/tabs';

type AccentColor = 'purple' | 'blue' | 'red' | 'pink' | 'green' | 'indigo';

const BADGE_COLORS: Record<AccentColor, string> = {
  purple: 'bg-purple-500/20 text-purple-300',
  blue: 'bg-blue-500/20 text-blue-300',
  red: 'bg-red-500/20 text-red-300',
  pink: 'bg-pink-500/20 text-pink-300',
  green: 'bg-green-500/20 text-green-300',
  indigo: 'bg-indigo-500/20 text-indigo-300',
};

interface TabDef {
  value: string;
  icon: ReactNode;
  label: string;
  badge?: number;
  alert?: boolean;
}

interface SchedaTabsProps {
  tabs: TabDef[];
  accentColor: AccentColor;
}

export const SchedaTabs: FC<SchedaTabsProps> = ({ tabs, accentColor }) => {
  const badgeColor = BADGE_COLORS[accentColor];

  return (
    <TabsList className="bg-slate-800/80 border border-slate-700/50 p-1 rounded-xl mb-6 h-auto flex flex-wrap gap-1">
      {tabs.map((tab) => (
        <TabsTrigger
          key={tab.value}
          value={tab.value}
          className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg
            data-[state=active]:bg-slate-700 data-[state=active]:text-white data-[state=active]:shadow
            text-slate-500 hover:text-slate-300 transition-colors"
        >
          <span className={tab.alert ? 'text-red-400' : ''}>{tab.icon}</span>
          {tab.label}
          {tab.badge !== undefined && tab.badge > 0 && (
            <span className={`ml-0.5 px-1.5 py-0.5 ${badgeColor} text-[10px] rounded-full font-bold`}>
              {tab.badge}
            </span>
          )}
          {tab.alert && (
            <span className="ml-0.5 w-1.5 h-1.5 bg-red-400 rounded-full" />
          )}
        </TabsTrigger>
      ))}
    </TabsList>
  );
};
