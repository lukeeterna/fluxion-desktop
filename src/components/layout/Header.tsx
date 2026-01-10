import { type FC, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, User, MoreVertical, Settings, HelpCircle, Info, LogOut } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface HeaderProps {
  className?: string;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const Header: FC<HeaderProps> = ({ className }) => {
  const navigate = useNavigate();
  const [notifications] = useState([
    { id: 1, text: 'Nuovo appuntamento confermato', time: '5 min fa' },
    { id: 2, text: 'Promemoria: chiusura cassa', time: '1 ora fa' },
  ]);

  return (
    <header
      className={cn(
        'h-14 bg-slate-900/50 border-b border-slate-800',
        'px-6 py-2 flex items-center justify-between gap-4',
        className
      )}
    >
      {/* Search */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Cerca clienti, servizi..."
            className={cn(
              'w-full pl-10 pr-4 py-2 bg-slate-800 text-sm rounded-md',
              'border border-slate-700',
              'focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent',
              'placeholder:text-slate-500',
              'transition-all'
            )}
          />
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-2">
        {/* Notifications */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className="p-2 hover:bg-slate-800 rounded-md transition-colors relative"
              title="Notifiche"
            >
              <Bell className="w-5 h-5 text-slate-300" />
              {notifications.length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              )}
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-72">
            <div className="px-3 py-2 font-semibold text-sm">Notifiche</div>
            <DropdownMenuSeparator />
            {notifications.length === 0 ? (
              <div className="px-3 py-4 text-sm text-muted-foreground text-center">
                Nessuna notifica
              </div>
            ) : (
              notifications.map((n) => (
                <DropdownMenuItem key={n.id} className="flex flex-col items-start gap-1 cursor-pointer">
                  <span className="text-sm">{n.text}</span>
                  <span className="text-xs text-muted-foreground">{n.time}</span>
                </DropdownMenuItem>
              ))
            )}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Profile */}
        <button
          onClick={() => navigate('/impostazioni')}
          className="p-2 hover:bg-slate-800 rounded-md transition-colors"
          title="Profilo e Impostazioni"
        >
          <User className="w-5 h-5 text-slate-300" />
        </button>

        {/* More Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              className="p-2 hover:bg-slate-800 rounded-md transition-colors"
              title="Altre opzioni"
            >
              <MoreVertical className="w-5 h-5 text-slate-300" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => navigate('/impostazioni')} className="cursor-pointer">
              <Settings className="w-4 h-4 mr-2" />
              Impostazioni
            </DropdownMenuItem>
            <DropdownMenuItem className="cursor-pointer">
              <HelpCircle className="w-4 h-4 mr-2" />
              Guida
            </DropdownMenuItem>
            <DropdownMenuItem className="cursor-pointer">
              <Info className="w-4 h-4 mr-2" />
              Informazioni
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer text-red-500 focus:text-red-500">
              <LogOut className="w-4 h-4 mr-2" />
              Esci
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};
