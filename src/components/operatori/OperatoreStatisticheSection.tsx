// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatore Statistiche Section (B4)
// KPI mensili + trend ultimi 6 mesi + YTD per singolo operatore
// ═══════════════════════════════════════════════════════════════════

import { type FC, useMemo } from 'react';
import { BarChart2, TrendingUp, Users, Euro, CalendarCheck, UserX } from 'lucide-react';
import { useKpiOperatoreStorico, type KpiOperatore } from '@/hooks/use-operatori-kpi';
import { cn } from '@/lib/utils';

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

function getMeseISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

function getAnnoISO() {
  return String(new Date().getFullYear());
}

function formatMeseLabel(mese: string, short = false): string {
  const [year, month] = mese.split('-');
  const d = new Date(parseInt(year), parseInt(month) - 1, 1);
  if (short) {
    return d.toLocaleDateString('it-IT', { month: 'short' });
  }
  return d.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' });
}

function formatEuro(value: number): string {
  if (value >= 1000) return `€${(value / 1000).toFixed(1)}k`;
  return `€${value.toFixed(0)}`;
}

const EMPTY_KPI: KpiOperatore = {
  id: '',
  nome_completo: '',
  mese: null,
  appuntamenti_completati: 0,
  no_show: 0,
  clienti_unici: 0,
  fatturato_generato: 0,
  ticket_medio: null,
};

// ───────────────────────────────────────────────────────────────────
// KPI Card
// ───────────────────────────────────────────────────────────────────

interface KpiCardProps {
  label: string;
  value: string;
  icon: FC<{ className?: string }>;
  color: string;
  sub?: string;
}

const KpiCard: FC<KpiCardProps> = ({ label, value, icon: Icon, color, sub }) => (
  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col gap-1">
    <div className="flex items-center gap-2 mb-1">
      <Icon className={cn('w-4 h-4', color)} />
      <p className="text-xs text-slate-500 uppercase tracking-wide">{label}</p>
    </div>
    <p className={cn('text-2xl font-bold', color)}>{value}</p>
    {sub && <p className="text-xs text-slate-500">{sub}</p>}
  </div>
);

// ───────────────────────────────────────────────────────────────────
// Bar Chart CSS
// ───────────────────────────────────────────────────────────────────

interface BarChartProps {
  data: Array<{ mese: string; fatturato: number; completati: number }>;
}

const BarChart: FC<BarChartProps> = ({ data }) => {
  const maxFatturato = Math.max(...data.map(d => d.fatturato), 1);

  return (
    <div className="mt-2">
      <div className="flex items-end gap-2 h-32">
        {data.map((d) => {
          const heightPct = Math.round((d.fatturato / maxFatturato) * 100);
          const isCurrent = d.mese === getMeseISO();

          return (
            <div key={d.mese} className="flex-1 flex flex-col items-center gap-1 group">
              {/* Tooltip */}
              <div className="opacity-0 group-hover:opacity-100 transition-opacity text-xs text-white bg-slate-800 border border-slate-700 rounded px-1.5 py-0.5 whitespace-nowrap absolute -translate-y-8 pointer-events-none z-10">
                {formatEuro(d.fatturato)} · {d.completati} apt.
              </div>

              {/* Bar */}
              <div className="w-full flex-1 flex items-end relative">
                <div
                  className={cn(
                    'w-full rounded-t transition-all duration-300',
                    isCurrent ? 'bg-cyan-500' : 'bg-slate-700 group-hover:bg-slate-600'
                  )}
                  style={{ height: `${Math.max(heightPct, 4)}%` }}
                />
              </div>

              {/* Label mese */}
              <p className={cn(
                'text-xs capitalize',
                isCurrent ? 'text-cyan-400 font-semibold' : 'text-slate-500'
              )}>
                {formatMeseLabel(d.mese, true)}
              </p>
            </div>
          );
        })}
      </div>

      {/* Asse Y semplice */}
      <div className="flex justify-between mt-1 border-t border-slate-800 pt-1">
        <span className="text-xs text-slate-600">€0</span>
        <span className="text-xs text-slate-600">{formatEuro(maxFatturato)}</span>
      </div>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

interface Props {
  operatoreId: string;
  nomeOperatore: string;
}

export const OperatoreStatisticheSection: FC<Props> = ({ operatoreId, nomeOperatore }) => {
  const { data: storico = [], isLoading } = useKpiOperatoreStorico(operatoreId, 12);

  const meseISO = getMeseISO();
  const annoISO = getAnnoISO();

  // KPI mese corrente
  const kpiMese = useMemo<KpiOperatore>(
    () => storico.find(k => k.mese === meseISO) ?? EMPTY_KPI,
    [storico, meseISO]
  );

  // YTD (anno corrente)
  const ytd = useMemo(() => {
    const rowsAnno = storico.filter(k => k.mese?.startsWith(annoISO));
    return {
      appuntamenti: rowsAnno.reduce((s, k) => s + k.appuntamenti_completati, 0),
      fatturato: rowsAnno.reduce((s, k) => s + k.fatturato_generato, 0),
      noShow: rowsAnno.reduce((s, k) => s + k.no_show, 0),
      clientiUnici: Math.max(...rowsAnno.map(k => k.clienti_unici), 0),
    };
  }, [storico, annoISO]);

  // Dati per bar chart: ultimi 6 mesi in ordine cronologico
  const chartData = useMemo(() => {
    return [...storico]
      .slice(0, 6)
      .reverse()
      .map(k => ({
        mese: k.mese ?? '',
        fatturato: k.fatturato_generato,
        completati: k.appuntamenti_completati,
      }));
  }, [storico]);

  // ── Loading ──
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="w-6 h-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // ── Empty state ──
  if (storico.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <BarChart2 className="w-10 h-10 text-slate-700 mb-3" />
        <p className="text-slate-400">Nessun dato disponibile</p>
        <p className="text-slate-600 text-sm mt-1">
          Le statistiche di {nomeOperatore} appariranno qui dopo i primi appuntamenti.
        </p>
      </div>
    );
  }

  const meseLabelCorrente = formatMeseLabel(meseISO);

  return (
    <div className="space-y-6">
      {/* ── KPI Mese Corrente ── */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <CalendarCheck className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-semibold text-white capitalize">{meseLabelCorrente}</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-3">
          <KpiCard
            label="Completati"
            value={String(kpiMese.appuntamenti_completati)}
            icon={CalendarCheck}
            color="text-cyan-400"
          />
          <KpiCard
            label="Fatturato"
            value={formatEuro(kpiMese.fatturato_generato)}
            icon={Euro}
            color="text-green-400"
          />
          <KpiCard
            label="Ticket Medio"
            value={kpiMese.ticket_medio != null ? `€${kpiMese.ticket_medio.toFixed(0)}` : '—'}
            icon={TrendingUp}
            color="text-amber-400"
          />
          <KpiCard
            label="Clienti Unici"
            value={String(kpiMese.clienti_unici)}
            icon={Users}
            color="text-purple-400"
          />
          <KpiCard
            label="No-show"
            value={String(kpiMese.no_show)}
            icon={UserX}
            color={kpiMese.no_show > 0 ? 'text-red-400' : 'text-slate-500'}
            sub={kpiMese.no_show > 0 ? 'da gestire' : 'ottimo!'}
          />
        </div>
      </div>

      {/* ── Trend Ultimi 6 Mesi ── */}
      {chartData.length > 1 && (
        <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
          <div className="flex items-center gap-2 mb-3">
            <BarChart2 className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-white">Fatturato — ultimi 6 mesi</h3>
          </div>
          <BarChart data={chartData} />
        </div>
      )}

      {/* ── YTD Anno Corrente ── */}
      <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-amber-400" />
          <h3 className="text-sm font-semibold text-white">Totale {annoISO}</h3>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center">
            <p className="text-xl font-bold text-cyan-400">{ytd.appuntamenti}</p>
            <p className="text-xs text-slate-500">Completati</p>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-green-400">{formatEuro(ytd.fatturato)}</p>
            <p className="text-xs text-slate-500">Fatturato</p>
          </div>
          <div className="text-center">
            <p className={cn('text-xl font-bold', ytd.noShow > 0 ? 'text-red-400' : 'text-slate-400')}>
              {ytd.noShow}
            </p>
            <p className="text-xs text-slate-500">No-show</p>
          </div>
        </div>
      </div>
    </div>
  );
};
