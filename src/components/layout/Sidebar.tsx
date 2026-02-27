import { type FC, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Home,
  Calendar,
  Users,
  UserCog,
  Wrench,
  FileText,
  Wallet,
  Mic,
  Settings,
  ChevronLeft,
  ChevronRight,
  Package,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface NavItem {
  icon: typeof Home;
  label: string;
  path: string;
  testId: string;
}

interface SidebarProps {
  className?: string;
}

// ───────────────────────────────────────────────────────────────────
// Navigation Items
// ───────────────────────────────────────────────────────────────────

const NAV_ITEMS: NavItem[] = [
  { icon: Home, label: 'Dashboard', path: '/', testId: 'sidebar-dashboard' },
  { icon: Calendar, label: 'Calendario', path: '/calendario', testId: 'sidebar-calendario' },
  { icon: Users, label: 'Clienti', path: '/clienti', testId: 'sidebar-clienti' },
  { icon: Wrench, label: 'Servizi', path: '/servizi', testId: 'sidebar-servizi' },
  { icon: UserCog, label: 'Operatori', path: '/operatori', testId: 'sidebar-operatori' },
  { icon: FileText, label: 'Fatture', path: '/fatture', testId: 'sidebar-fatture' },
  { icon: Wallet, label: 'Cassa', path: '/cassa', testId: 'sidebar-cassa' },
  { icon: Package, label: 'Fornitori', path: '/fornitori', testId: 'sidebar-fornitori' },
  { icon: Mic, label: 'Voice Agent', path: '/voice', testId: 'sidebar-voice' },
  { icon: Settings, label: 'Impostazioni', path: '/impostazioni', testId: 'sidebar-impostazioni' },
];

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const Sidebar: FC<SidebarProps> = ({ className }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const location = useLocation();

  return (
    <aside
      data-testid="sidebar"
      className={cn(
        'flex flex-col h-screen bg-slate-900 border-r border-slate-800 transition-all duration-200',
        isExpanded ? 'w-60' : 'w-16',
        className
      )}
    >
      {/* Logo + Toggle */}
      <div className="h-16 border-b border-slate-800 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          {/* Logo */}
          <img
            src="/logo_fluxion.jpg"
            alt="Fluxion"
            style={{ width: 32, height: 32, borderRadius: 8 }}
            className="flex-shrink-0"
          />
          {/* Brand */}
          {isExpanded && (
            <span className="font-semibold text-white text-lg">Fluxion</span>
          )}
        </div>
        {/* Toggle Button */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          data-testid="sidebar-toggle"
          className="p-1 hover:bg-slate-800 rounded-md transition-colors"
          title={isExpanded ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {isExpanded ? (
            <ChevronLeft className="w-5 h-5 text-slate-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-slate-400" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              data-testid={item.testId}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-md transition-all',
                'hover:bg-slate-800/50',
                isActive
                  ? 'bg-teal-500/20 text-teal-400'
                  : 'text-slate-300 hover:text-white'
              )}
              title={!isExpanded ? item.label : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {isExpanded && (
                <span className="text-sm font-medium">{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="border-t border-slate-800 p-4">
        <Link
          to="/impostazioni"
          className={cn(
            'flex items-center rounded-md p-2 -m-2 hover:bg-slate-800/50 transition-colors',
            isExpanded ? 'gap-3' : 'justify-center'
          )}
          title="Vai alle Impostazioni"
        >
          {/* Avatar */}
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
            <span className="text-sm font-semibold text-white">MR</span>
          </div>
          {/* User Info */}
          {isExpanded && (
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                Mario Rossi
              </p>
              <p className="text-xs text-slate-400 truncate">Amministratore</p>
            </div>
          )}
        </Link>
      </div>
    </aside>
  );
};
