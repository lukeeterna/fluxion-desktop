// ═══════════════════════════════════════════════════════════════════
// FLUXION - Analytics Mensili (Gap #9)
// Dashboard KPI + Export PDF Report Attività
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { invoke } from '@tauri-apps/api/core'
import { openPath } from '@tauri-apps/plugin-opener'
import {
  TrendingUp,
  TrendingDown,
  Calendar,
  Users,
  Star,
  Trophy,
  MessageSquare,
  FileDown,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface ServizioKpi {
  nome: string
  conteggio: number
  revenue: number
}

interface OperatoreAnalytics {
  nome_completo: string
  appuntamenti_completati: number
  revenue: number
}

interface AnalyticsMensili {
  anno: number
  mese: number
  mese_label: string
  revenue_mese: number
  revenue_mese_prec: number
  revenue_delta_pct: number
  appuntamenti_totali: number
  appuntamenti_completati: number
  appuntamenti_cancellati: number
  appuntamenti_no_show: number
  appuntamenti_confermati: number
  top_servizi: ServizioKpi[]
  top_operatori: OperatoreAnalytics[]
  clienti_nuovi: number
  clienti_ritorni: number
  wa_confermati: number
  wa_cancellati: number
  wa_confirm_rate: number
}

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('it-IT', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

function formatPct(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(1)}%`
}

// ───────────────────────────────────────────────────────────────────
// Sub-components
// ───────────────────────────────────────────────────────────────────

const KpiCard: FC<{
  title: string
  value: string
  subtitle?: string
  icon: React.ReactNode
  color: string
  badge?: string
  badgeColor?: string
}> = ({ title, value, subtitle, icon, color, badge, badgeColor }) => (
  <Card className="p-5 border-slate-700/50">
    <div className="flex items-start justify-between">
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-400 mb-1">{title}</p>
        <p className={`text-2xl font-bold ${color} truncate`}>{value}</p>
        {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-2 rounded-lg bg-slate-800 ${color} ml-3 flex-shrink-0`}>
        {icon}
      </div>
    </div>
    {badge && (
      <div className="mt-3">
        <span
          className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${badgeColor ?? 'bg-slate-800 text-slate-300'}`}
        >
          {badge}
        </span>
      </div>
    )}
  </Card>
)

const AppuntamentiBadge: FC<{ label: string; count: number; color: string }> = ({
  label,
  count,
  color,
}) => (
  <div className="flex flex-col items-center p-3 bg-slate-800/60 rounded-lg border border-slate-700">
    <span className={`text-xl font-bold ${color}`}>{count}</span>
    <span className="text-xs text-slate-400 mt-1 text-center">{label}</span>
  </div>
)

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

export const Analytics: FC = () => {
  const now = new Date()
  const [anno, setAnno] = useState(now.getFullYear())
  const [mese, setMese] = useState(now.getMonth() + 1)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [pdfError, setPdfError] = useState<string | null>(null)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['analytics-mensili', anno, mese],
    queryFn: () =>
      invoke<AnalyticsMensili>('get_analytics_mensili', { anno, mese }),
    staleTime: 2 * 60 * 1000,
  })

  function prevMonth() {
    if (mese === 1) {
      setAnno((a) => a - 1)
      setMese(12)
    } else {
      setMese((m) => m - 1)
    }
  }

  function nextMonth() {
    const currentYear = now.getFullYear()
    const currentMonth = now.getMonth() + 1
    if (anno === currentYear && mese === currentMonth) return
    if (mese === 12) {
      setAnno((a) => a + 1)
      setMese(1)
    } else {
      setMese((m) => m + 1)
    }
  }

  const isCurrentMonth =
    anno === now.getFullYear() && mese === now.getMonth() + 1

  async function handleGeneraPdf() {
    setPdfLoading(true)
    setPdfError(null)
    try {
      const path = await invoke<string>('genera_report_pdf_mensile', { anno, mese })
      await openPath(path)
    } catch (err) {
      setPdfError(err instanceof Error ? err.message : String(err))
    } finally {
      setPdfLoading(false)
    }
  }

  return (
    <div className="space-y-6" data-testid="analytics-page">
      {/* Header con month selector */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Analytics</h1>
          <p className="text-slate-400 mt-1">Report attività mensile</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Month navigator */}
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2">
            <button
              onClick={prevMonth}
              className="text-slate-400 hover:text-white transition-colors"
              title="Mese precedente"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="text-white font-medium min-w-[140px] text-center text-sm">
              {data?.mese_label ?? `${anno}-${String(mese).padStart(2, '0')}`}
            </span>
            <button
              onClick={nextMonth}
              disabled={isCurrentMonth}
              className="text-slate-400 hover:text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              title="Mese successivo"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>

          {/* PDF export */}
          <Button
            onClick={handleGeneraPdf}
            disabled={pdfLoading || isLoading}
            className="bg-cyan-600 hover:bg-cyan-500 text-white flex items-center gap-2"
            data-testid="btn-genera-pdf"
          >
            {pdfLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileDown className="h-4 w-4" />
            )}
            Genera PDF
          </Button>
        </div>
      </div>

      {pdfError && (
        <div className="flex items-center gap-2 p-3 bg-red-950/50 border border-red-800 rounded-lg text-red-300 text-sm">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          {pdfError}
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
        </div>
      )}

      {isError && (
        <div className="flex items-center gap-2 p-4 bg-red-950/50 border border-red-800 rounded-lg text-red-300">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          Errore caricamento analytics:{' '}
          {error instanceof Error ? error.message : String(error)}
        </div>
      )}

      {data && !isLoading && (
        <>
          {/* Row 1: KPI principali */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard
              title="Fatturato del mese"
              value={formatCurrency(data.revenue_mese)}
              subtitle={
                data.revenue_mese_prec > 0
                  ? `Mese prec.: ${formatCurrency(data.revenue_mese_prec)}`
                  : 'Nessun dato mese precedente'
              }
              icon={<TrendingUp className="h-5 w-5" />}
              color="text-emerald-400"
              badge={
                data.revenue_mese_prec > 0
                  ? formatPct(data.revenue_delta_pct)
                  : undefined
              }
              badgeColor={
                data.revenue_delta_pct >= 0
                  ? 'bg-emerald-950 text-emerald-400'
                  : 'bg-red-950 text-red-400'
              }
            />

            <KpiCard
              title="Appuntamenti totali"
              value={String(data.appuntamenti_totali)}
              subtitle={`${data.appuntamenti_completati} completati`}
              icon={<Calendar className="h-5 w-5" />}
              color="text-cyan-400"
            />

            <KpiCard
              title="Clienti attivi"
              value={String(data.clienti_nuovi + data.clienti_ritorni)}
              subtitle={`${data.clienti_nuovi} nuovi · ${data.clienti_ritorni} ritorni`}
              icon={<Users className="h-5 w-5" />}
              color="text-purple-400"
            />

            <KpiCard
              title="Tasso conferma WA"
              value={`${data.wa_confirm_rate.toFixed(1)}%`}
              subtitle={
                data.wa_confermati + data.wa_cancellati > 0
                  ? `${data.wa_confermati} confermati · ${data.wa_cancellati} cancellati`
                  : 'Nessuna risposta WA registrata'
              }
              icon={<MessageSquare className="h-5 w-5" />}
              color="text-amber-400"
            />
          </div>

          {/* Row 2: Appuntamenti breakdown */}
          <Card className="p-5 border-slate-700/50">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
              <Calendar className="h-5 w-5 text-cyan-400" />
              Breakdown Appuntamenti
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <AppuntamentiBadge
                label="Completati"
                count={data.appuntamenti_completati}
                color="text-emerald-400"
              />
              <AppuntamentiBadge
                label="Confermati"
                count={data.appuntamenti_confermati}
                color="text-cyan-400"
              />
              <AppuntamentiBadge
                label="Cancellati"
                count={data.appuntamenti_cancellati}
                color="text-red-400"
              />
              <AppuntamentiBadge
                label="No-show"
                count={data.appuntamenti_no_show}
                color="text-orange-400"
              />
            </div>
          </Card>

          {/* Row 3: Top servizi + Top operatori */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Top 5 Servizi */}
            <Card className="p-5 border-slate-700/50">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                <Star className="h-5 w-5 text-amber-400" />
                Top 5 Servizi
              </h2>
              {data.top_servizi.length === 0 ? (
                <p className="text-slate-500 text-sm py-4 text-center">
                  Nessun dato disponibile
                </p>
              ) : (
                <div className="space-y-2">
                  {data.top_servizi.map((svc, i) => (
                    <div
                      key={svc.nome}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span className="text-xs font-bold text-slate-500 w-4 flex-shrink-0">
                          {i + 1}
                        </span>
                        <div className="min-w-0">
                          <p className="text-white text-sm font-medium truncate">
                            {svc.nome}
                          </p>
                          <p className="text-xs text-slate-400">
                            {svc.conteggio} prenotazioni
                          </p>
                        </div>
                      </div>
                      <span className="text-emerald-400 text-sm font-semibold flex-shrink-0 ml-2">
                        {formatCurrency(svc.revenue)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Top Operatori */}
            <Card className="p-5 border-slate-700/50">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                <Trophy className="h-5 w-5 text-amber-400" />
                Operatori del Mese
              </h2>
              {data.top_operatori.length === 0 ? (
                <p className="text-slate-500 text-sm py-4 text-center">
                  Nessun dato disponibile
                </p>
              ) : (
                <div className="space-y-2">
                  {data.top_operatori.map((op, i) => (
                    <div
                      key={op.nome_completo}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <span
                          className={`text-sm font-bold w-5 text-center flex-shrink-0 ${
                            i === 0
                              ? 'text-amber-400'
                              : i === 1
                                ? 'text-slate-300'
                                : i === 2
                                  ? 'text-orange-600'
                                  : 'text-slate-500'
                          }`}
                        >
                          {i + 1}
                        </span>
                        <div className="min-w-0">
                          <p className="text-white text-sm font-medium truncate">
                            {op.nome_completo}
                          </p>
                          <p className="text-xs text-slate-400">
                            {op.appuntamenti_completati} appuntamenti completati
                          </p>
                        </div>
                      </div>
                      <span className="text-emerald-400 text-sm font-semibold flex-shrink-0 ml-2">
                        {formatCurrency(op.revenue)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* Row 4: Clienti nuovi vs ritorni + Revenue trend */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Clienti */}
            <Card className="p-5 border-slate-700/50">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                <Users className="h-5 w-5 text-purple-400" />
                Clienti — Nuovi vs Ritorni
              </h2>
              <div className="flex items-center gap-6">
                <div className="flex-1 text-center p-4 bg-slate-800/60 rounded-lg border border-slate-700">
                  <p className="text-3xl font-bold text-purple-400">
                    {data.clienti_nuovi}
                  </p>
                  <p className="text-sm text-slate-400 mt-1">Nuovi clienti</p>
                  <p className="text-xs text-slate-500 mt-0.5">Prima visita in {data.mese_label}</p>
                </div>
                <div className="flex-1 text-center p-4 bg-slate-800/60 rounded-lg border border-slate-700">
                  <p className="text-3xl font-bold text-cyan-400">
                    {data.clienti_ritorni}
                  </p>
                  <p className="text-sm text-slate-400 mt-1">Clienti fedeli</p>
                  <p className="text-xs text-slate-500 mt-0.5">Già venuti in precedenza</p>
                </div>
              </div>
              {data.clienti_nuovi + data.clienti_ritorni > 0 && (
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Nuovi</span>
                    <span>Ritorni</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full bg-purple-500 rounded-full"
                      style={{
                        width: `${(data.clienti_nuovi / (data.clienti_nuovi + data.clienti_ritorni)) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </Card>

            {/* Revenue trend */}
            <Card className="p-5 border-slate-700/50">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
                {data.revenue_delta_pct >= 0 ? (
                  <TrendingUp className="h-5 w-5 text-emerald-400" />
                ) : (
                  <TrendingDown className="h-5 w-5 text-red-400" />
                )}
                Confronto Revenue
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 text-sm">{data.mese_label}</span>
                  <span className="text-white font-bold text-lg">
                    {formatCurrency(data.revenue_mese)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 text-sm">Mese precedente</span>
                  <span className="text-slate-300 font-medium">
                    {data.revenue_mese_prec > 0
                      ? formatCurrency(data.revenue_mese_prec)
                      : '—'}
                  </span>
                </div>
                {data.revenue_mese_prec > 0 && (
                  <div
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      data.revenue_delta_pct >= 0
                        ? 'bg-emerald-950/40 border border-emerald-800'
                        : 'bg-red-950/40 border border-red-800'
                    }`}
                  >
                    <span
                      className={`text-sm font-medium ${
                        data.revenue_delta_pct >= 0
                          ? 'text-emerald-400'
                          : 'text-red-400'
                      }`}
                    >
                      Variazione
                    </span>
                    <span
                      className={`text-xl font-bold ${
                        data.revenue_delta_pct >= 0
                          ? 'text-emerald-400'
                          : 'text-red-400'
                      }`}
                    >
                      {formatPct(data.revenue_delta_pct)}
                    </span>
                  </div>
                )}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  )
}
