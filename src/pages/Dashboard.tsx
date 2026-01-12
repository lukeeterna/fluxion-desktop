// ═══════════════════════════════════════════════════════════════════
// FLUXION - Dashboard Home Page
// Panoramica attività con statistiche reali
// ═══════════════════════════════════════════════════════════════════

import { type FC } from 'react'
import { useQuery } from '@tanstack/react-query'
import { invoke } from '@tauri-apps/api/core'
import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/card'
import {
  Calendar,
  Users,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  Star,
  ArrowRight,
} from 'lucide-react'

// Types
interface DashboardStats {
  appuntamenti_oggi: number
  appuntamenti_settimana: number
  clienti_totali: number
  clienti_vip: number
  clienti_nuovi_mese: number
  fatturato_mese: number
  fatture_da_pagare: number
  servizio_top_nome: string
  servizio_top_conteggio: number
}

interface AppuntamentoOggi {
  id: string
  cliente_nome: string
  servizio_nome: string
  ora: string
  stato: string
}

// ───────────────────────────────────────────────────────────────────
// Hooks
// ───────────────────────────────────────────────────────────────────

function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => invoke<DashboardStats>('get_dashboard_stats'),
    staleTime: 60 * 1000, // 1 minuto
    refetchInterval: 5 * 60 * 1000, // Refresh ogni 5 minuti
  })
}

function useAppuntamentiOggi() {
  return useQuery({
    queryKey: ['appuntamenti-oggi'],
    queryFn: () => invoke<AppuntamentoOggi[]>('get_appuntamenti_oggi'),
    staleTime: 60 * 1000,
  })
}

// ───────────────────────────────────────────────────────────────────
// Components
// ───────────────────────────────────────────────────────────────────

const StatCard: FC<{
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  color: string
  link?: string
  testId?: string
}> = ({ title, value, subtitle, icon, color, link, testId }) => {
  const content = (
    <Card
      className={`p-5 bg-slate-900 border-slate-800 hover:bg-slate-800/70 transition-colors ${link ? 'cursor-pointer' : ''}`}
      data-testid={testId}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400 mb-1">{title}</p>
          <p className={`text-3xl font-bold ${color}`}>{value}</p>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`p-2 rounded-lg bg-slate-800 ${color}`}>
          {icon}
        </div>
      </div>
      {link && (
        <div className="flex items-center gap-1 mt-3 text-xs text-slate-500">
          <span>Vedi dettagli</span>
          <ArrowRight className="h-3 w-3" />
        </div>
      )}
    </Card>
  )

  return link ? <Link to={link}>{content}</Link> : content
}

const StatoAppuntamento: FC<{ stato: string }> = ({ stato }) => {
  switch (stato) {
    case 'completato':
      return <CheckCircle className="h-4 w-4 text-emerald-500" />
    case 'confermato':
      return <Clock className="h-4 w-4 text-cyan-500" />
    case 'cancellato':
    case 'no_show':
      return <XCircle className="h-4 w-4 text-red-500" />
    default:
      return <Clock className="h-4 w-4 text-slate-500" />
  }
}

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

export const Dashboard: FC = () => {
  const { data: stats, isLoading } = useDashboardStats()
  const { data: appuntamenti } = useAppuntamentiOggi()

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
    }).format(value)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Buongiorno!</h1>
        <p className="text-slate-400 mt-2">
          Ecco cosa succede nella tua attività oggi
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Appuntamenti oggi"
          value={isLoading ? '-' : stats?.appuntamenti_oggi ?? 0}
          subtitle={`${stats?.appuntamenti_settimana ?? 0} questa settimana`}
          icon={<Calendar className="h-5 w-5" />}
          color="text-cyan-400"
          link="/calendario"
          testId="stat-appuntamenti-oggi"
        />
        <StatCard
          title="Clienti totali"
          value={isLoading ? '-' : stats?.clienti_totali ?? 0}
          subtitle={`${stats?.clienti_nuovi_mese ?? 0} nuovi questo mese`}
          icon={<Users className="h-5 w-5" />}
          color="text-emerald-400"
          link="/clienti"
          testId="stat-clienti-totali"
        />
        <StatCard
          title="Fatturato del mese"
          value={isLoading ? '-' : formatCurrency(stats?.fatturato_mese ?? 0)}
          subtitle={`${stats?.fatture_da_pagare ?? 0} fatture da incassare`}
          icon={<TrendingUp className="h-5 w-5" />}
          color="text-amber-400"
          link="/fatture"
          testId="stat-fatturato-mese"
        />
        <StatCard
          title="Servizio top"
          value={isLoading ? '-' : stats?.servizio_top_nome ?? '-'}
          subtitle={`${stats?.servizio_top_conteggio ?? 0} prenotazioni`}
          icon={<Star className="h-5 w-5" />}
          color="text-purple-400"
          link="/servizi"
          testId="stat-servizio-top"
        />
      </div>

      {/* Secondary Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Appuntamenti di oggi */}
        <Card className="p-5 bg-slate-900 border-slate-800" data-testid="section-prossimi-appuntamenti">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Calendar className="h-5 w-5 text-cyan-400" />
              Prossimi appuntamenti
            </h2>
            <Link
              to="/calendario"
              className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
            >
              Vedi tutti <ArrowRight className="h-3 w-3" />
            </Link>
          </div>

          {!appuntamenti?.length ? (
            <div className="text-center py-8 text-slate-500">
              <Calendar className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p>Nessun appuntamento per oggi</p>
            </div>
          ) : (
            <div className="space-y-3">
              {appuntamenti.map((app) => (
                <div
                  key={app.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700"
                >
                  <div className="flex items-center gap-3">
                    <StatoAppuntamento stato={app.stato} />
                    <div>
                      <p className="text-white font-medium">{app.cliente_nome}</p>
                      <p className="text-sm text-slate-400">{app.servizio_nome}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-mono">{app.ora?.slice(0, 5) || '-'}</p>
                    <p className="text-xs text-slate-500 capitalize">
                      {app.stato === 'confermato' ? 'In attesa' : app.stato}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Riepilogo veloce */}
        <Card className="p-5 bg-slate-900 border-slate-800" data-testid="section-riepilogo-veloce">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Star className="h-5 w-5 text-amber-400" />
              Riepilogo veloce
            </h2>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
              <p className="text-sm text-slate-400">Clienti VIP</p>
              <p className="text-2xl font-bold text-amber-400">
                {stats?.clienti_vip ?? 0}
              </p>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
              <p className="text-sm text-slate-400">Fatture da incassare</p>
              <p className="text-2xl font-bold text-red-400">
                {stats?.fatture_da_pagare ?? 0}
              </p>
            </div>
          </div>

          {(stats?.fatture_da_pagare ?? 0) > 0 && (
            <div className="mt-4 p-4 rounded-lg bg-gradient-to-r from-cyan-900/30 to-purple-900/30 border border-cyan-800/50">
              <p className="text-sm text-slate-300">
                <span className="text-cyan-400 font-medium">Consiglio:</span> Hai {stats?.fatture_da_pagare ?? 0} fatture
                in attesa di pagamento. Ricorda di sollecitare i clienti!
              </p>
            </div>
          )}

          <div className="mt-4 flex gap-2">
            <Link
              to="/fatture"
              className="flex-1 py-2 px-4 bg-slate-800 hover:bg-slate-700 rounded-lg text-center text-sm text-slate-300 transition-colors"
              data-testid="btn-vai-fatture"
            >
              Fatture
            </Link>
            <Link
              to="/calendario"
              className="flex-1 py-2 px-4 bg-cyan-600 hover:bg-cyan-500 rounded-lg text-center text-sm text-white transition-colors"
              data-testid="btn-vai-calendario"
            >
              Calendario
            </Link>
          </div>
        </Card>
      </div>
    </div>
  )
}
