// ═══════════════════════════════════════════════════════════════════
// FLUXION - Calendario Page
// Calendar view with appointments booking
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useMemo } from 'react';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, Plus } from 'lucide-react';
import { useAppuntamenti } from '@/hooks/use-appuntamenti';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import type { AppuntamentoDettagliato, GetAppuntamentiParams } from '@/types/appuntamento';
import { AppuntamentoDialog } from '@/components/calendario/AppuntamentoDialog';

// ───────────────────────────────────────────────────────────────────
// Date Utilities
// ───────────────────────────────────────────────────────────────────

function formatMonthYear(date: Date): string {
  return new Intl.DateTimeFormat('it-IT', { month: 'long', year: 'numeric' }).format(date);
}

function getMonthDays(year: number, month: number): Date[] {
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const days: Date[] = [];

  // Add padding days from previous month
  const firstDayOfWeek = firstDay.getDay();
  const paddingDays = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1;

  for (let i = paddingDays; i > 0; i--) {
    const day = new Date(year, month, 1 - i);
    days.push(day);
  }

  // Add all days of current month
  for (let i = 1; i <= lastDay.getDate(); i++) {
    days.push(new Date(year, month, i));
  }

  // Add padding days from next month to complete grid (42 days = 6 weeks)
  const remainingDays = 42 - days.length;
  for (let i = 1; i <= remainingDays; i++) {
    days.push(new Date(year, month + 1, i));
  }

  return days;
}

function formatDateISO(date: Date): string {
  // Use LOCAL date components, not UTC
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function isSameDay(date1: Date, date2: Date): boolean {
  return (
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate()
  );
}

function isToday(date: Date): boolean {
  return isSameDay(date, new Date());
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const Calendario: FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [appuntamentoDialogOpen, setAppuntamentoDialogOpen] = useState(false);
  const [editingAppuntamento, setEditingAppuntamento] = useState<AppuntamentoDettagliato | null>(null);
  const [expandedDays, setExpandedDays] = useState<Set<string>>(new Set()); // Track expanded days

  // Calculate month start/end for query
  const monthParams: GetAppuntamentiParams = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    return {
      start_date: formatDateISO(firstDay),
      end_date: formatDateISO(lastDay),
    };
  }, [currentDate]);

  const { data: appuntamenti, isLoading, error } = useAppuntamenti(monthParams);

  // Get days grid
  const days = useMemo(() => {
    return getMonthDays(currentDate.getFullYear(), currentDate.getMonth());
  }, [currentDate]);

  // Group appointments by date
  const appointmentsByDate = useMemo(() => {
    if (!appuntamenti) return new Map();

    const map = new Map<string, typeof appuntamenti>();
    appuntamenti.forEach((app) => {
      const date = new Date(app.data_ora_inizio);
      const key = formatDateISO(date);
      const existing = map.get(key) || [];
      map.set(key, [...existing, app]);
    });

    return map;
  }, [appuntamenti]);

  // Navigation handlers
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Check if day is in current month
  const isCurrentMonth = (day: Date) => {
    return day.getMonth() === currentDate.getMonth();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <CalendarIcon className="w-8 h-8 text-cyan-500" />
          <h1 className="text-3xl font-bold text-white">Calendario</h1>
        </div>

        <Button
          onClick={() => {
            setEditingAppuntamento(null);
            setAppuntamentoDialogOpen(true);
          }}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nuovo Appuntamento
        </Button>
      </div>

      {/* Calendar Controls */}
      <div className="flex items-center justify-between bg-slate-900/50 p-4 rounded-lg border border-slate-800">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={goToPreviousMonth}
            className="border-slate-700 hover:bg-slate-800"
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={goToNextMonth}
            className="border-slate-700 hover:bg-slate-800"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>

        <h2 className="text-xl font-semibold text-white capitalize">
          {formatMonthYear(currentDate)}
        </h2>

        <Button
          variant="outline"
          onClick={goToToday}
          className="border-slate-700 hover:bg-slate-800"
        >
          Oggi
        </Button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p className="text-red-500">
            Errore nel caricamento degli appuntamenti: {(error as Error).message}
          </p>
        </div>
      )}

      {/* Calendar Grid */}
      {!isLoading && !error && (
        <div className="bg-slate-900/50 rounded-lg border border-slate-800 overflow-hidden">
          {/* Weekday Headers */}
          <div className="grid grid-cols-7 bg-slate-800/50 border-b border-slate-700">
            {['Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab', 'Dom'].map((day) => (
              <div
                key={day}
                className="p-3 text-center text-sm font-medium text-slate-400 border-r border-slate-700 last:border-r-0"
              >
                {day}
              </div>
            ))}
          </div>

          {/* Days Grid */}
          <div className="grid grid-cols-7">
            {days.map((day, index) => {
              const dayKey = formatDateISO(day);
              const dayAppointments = appointmentsByDate.get(dayKey) || [];
              const isInCurrentMonth = isCurrentMonth(day);
              const isTodayDate = isToday(day);

              return (
                <div
                  key={index}
                  className={`
                    min-h-[120px] p-2 border-r border-b border-slate-700 last:border-r-0
                    ${!isInCurrentMonth ? 'bg-slate-900/30' : 'bg-slate-900/10'}
                    ${isTodayDate ? 'bg-cyan-500/5 border-cyan-500/30' : ''}
                    hover:bg-slate-800/30 transition-colors cursor-pointer
                  `}
                >
                  {/* Day Number */}
                  <div className="flex items-center justify-between mb-2">
                    <span
                      className={`
                        text-sm font-medium
                        ${!isInCurrentMonth ? 'text-slate-600' : 'text-slate-300'}
                        ${isTodayDate ? 'text-cyan-400 font-bold' : ''}
                      `}
                    >
                      {day.getDate()}
                    </span>
                    {isTodayDate && (
                      <span className="w-2 h-2 bg-cyan-500 rounded-full"></span>
                    )}
                  </div>

                  {/* Appointments */}
                  <div className="space-y-1">
                    {(() => {
                      const isExpanded = expandedDays.has(dayKey);
                      const visibleAppointments = isExpanded ? dayAppointments : dayAppointments.slice(0, 3);

                      return (
                        <>
                          {visibleAppointments.map((app: AppuntamentoDettagliato) => {
                            const startTime = new Date(app.data_ora_inizio).toLocaleTimeString('it-IT', {
                              hour: '2-digit',
                              minute: '2-digit',
                            });

                            return (
                              <div
                                key={app.id}
                                className="text-xs p-1.5 rounded border-l-2 truncate cursor-pointer hover:opacity-80 transition-opacity"
                                style={{
                                  backgroundColor: `${app.servizio_colore}15`,
                                  borderLeftColor: app.servizio_colore,
                                }}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setEditingAppuntamento(app);
                                  setAppuntamentoDialogOpen(true);
                                }}
                                title={`${app.servizio_nome} - ${app.cliente_nome} ${app.cliente_cognome}`}
                              >
                                <div className="font-medium text-white">{startTime}</div>
                                <div className="text-slate-400 truncate">
                                  {app.cliente_nome} {app.cliente_cognome}
                                </div>
                              </div>
                            );
                          })}

                          {/* Show "+N more" clickable button if there are more than 3 appointments */}
                          {dayAppointments.length > 3 && (
                            <div
                              className="text-xs text-cyan-400 hover:text-cyan-300 font-medium text-center pt-1 cursor-pointer transition-colors"
                              onClick={(e) => {
                                e.stopPropagation();
                                setExpandedDays(prev => {
                                  const next = new Set(prev);
                                  if (isExpanded) {
                                    next.delete(dayKey);
                                  } else {
                                    next.add(dayKey);
                                  }
                                  return next;
                                });
                              }}
                            >
                              {isExpanded
                                ? '− Mostra meno'
                                : `+${dayAppointments.length - 3} altri`
                              }
                            </div>
                          )}
                        </>
                      );
                    })()}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Stats Footer */}
      {!isLoading && !error && appuntamenti && (
        <div className="flex items-center justify-between text-sm text-slate-400">
          <div>
            {appuntamenti.length} appuntament{appuntamenti.length !== 1 ? 'i' : 'o'} questo mese
          </div>
          <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded border-l-2 border-cyan-500 bg-cyan-500/15"></div>
              <span>Confermato</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded border-l-2 border-green-500 bg-green-500/15"></div>
              <span>Completato</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded border-l-2 border-red-500 bg-red-500/15"></div>
              <span>Cancellato</span>
            </div>
          </div>
        </div>
      )}

      {/* Appuntamento Dialog */}
      <AppuntamentoDialog
        open={appuntamentoDialogOpen}
        onOpenChange={(open) => {
          setAppuntamentoDialogOpen(open);
          if (!open) {
            setEditingAppuntamento(null);
          }
        }}
        editingAppuntamento={editingAppuntamento}
        onSuccess={() => {
          // Refresh calendar data
          setAppuntamentoDialogOpen(false);
          setEditingAppuntamento(null);
        }}
      />
    </div>
  );
};
