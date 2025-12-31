import { type FC } from 'react';
import { Search, Bell, User, MoreVertical } from 'lucide-react';
import { cn } from '@/lib/utils';

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
        <button
          className="p-2 hover:bg-slate-800 rounded-md transition-colors relative"
          title="Notifications"
        >
          <Bell className="w-5 h-5 text-slate-300" />
          {/* Badge */}
          <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>

        {/* User Menu */}
        <button
          className="p-2 hover:bg-slate-800 rounded-md transition-colors"
          title="User menu"
        >
          <User className="w-5 h-5 text-slate-300" />
        </button>

        {/* More Menu */}
        <button
          className="p-2 hover:bg-slate-800 rounded-md transition-colors"
          title="More options"
        >
          <MoreVertical className="w-5 h-5 text-slate-300" />
        </button>
      </div>
    </header>
  );
};
