// ═══════════════════════════════════════════════════════════════════
// FLUXION - Dashboard Home Page
// Panoramica attività con statistiche reali
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react'
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
  Trophy,
  Cake,
  Crown,
  X,
  AlertTriangle,
  UserPlus,
  CalendarPlus,
  Sparkles,
} from 'lucide-react'
import { useCompeanniSettimana } from '@/hooks/use-loyalty'
import type { ClienteCompleanno } from '@/types/loyalty'
import { useImpostazioniStatus } from '@/hooks/use-impostazioni-status'

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

interface TopOperatoreKpi {
  id: string
  nome_completo: string
  mese: string | null
  appuntamenti_completati: number
  no_show: number
  clienti_unici: number
  fatturato_generato: number
  ticket_medio: number | null
}

// ───────────────────────────────────────────────────────────────────
// Quick Setup Banner
// ───────────────────────────────────────────────────────────────────

const BANNER_DISMISSED_KEY = 'fluxion-setup-banner-dismissed-v1'

const QuickSetupBanner: FC = () => {
  const impostazioni = useImpostazioniStatus()
  const [dismissed, setDismissed] = useState(
    () => localStorage.getItem(BANNER_DISMISSED_KEY) === 'true',
  )

  if (dismissed || impostazioni.isLoading) return null

  // Banner items: solo Sara (error) e Email (warning/optional) sono mostrati
  const items = [
    {
      id: 'sara',
      show: impostazioni.sara !== 'ok',
      label: 'Sara non è attiva — i clienti non possono prenotare telefonicamente',
      action: 'Attiva Sara',
      href: '/impostazioni#sara',
    },
    {
      id: 'email',
      show: impostazioni.email === 'warning',
      label: 'Email per le notifiche non configurata',
      action: 'Configura email',
      href: '/impostazioni#email',
    },
  ].filter((item) => item.show)

  if (items.length === 0) return null

  const handleDismiss = () => {
    localStorage.setItem(BANNER_DISMISSED_KEY, 'true')
    setDismissed(true)
  }

  return (
    <Card className="p-4 bg-amber-950/30 border-amber-500/30" data-testid="quick-setup-banner">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3 flex-1">
          <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-300 mb-2">
              FLUXION non è ancora completamente configurato
            </p>
            <div className="space-y-1.5">
              {items.map((item) => (
                <div key={item.id} className="flex items-center gap-3">
                  <span className="text-sm text-slate-300">{item.label}</span>
                  <Link
                    to={item.href}
                    className="text-xs font-medium text-cyan-400 hover:text-cyan-300 whitespace-nowrap underline-offset-2 hover:underline"
                  >
                    {item.action} →
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={handleDismiss}
          className="text-slate-500 hover:text-slate-300 transition-colors shrink-0"
          aria-label="Chiudi banner"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </Card>
  )
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

function useTopOperatoriMese() {
  return useQuery({
    queryKey: ['top-operatori-mese'],
    queryFn: () => invoke<TopOperatoreKpi[]>('get_top_operatori_mese'),
    staleTime: 5 * 60 * 1000,
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
      className={`relative overflow-hidden p-5 border-slate-700/50 hover:border-slate-600 hover:shadow-lg hover:shadow-black/20 transition-all duration-200 ${link ? 'cursor-pointer group' : ''}`}
      data-testid={testId}
    >
      {/* Top accent line */}
      <div className={`absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent ${
        color.includes('cyan') ? 'via-cyan-500/40' :
        color.includes('emerald') ? 'via-emerald-500/40' :
        color.includes('amber') ? 'via-amber-500/40' :
        'via-purple-500/40'
      } to-transparent`} />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400 mb-1.5">{title}</p>
          <p className={`text-3xl font-bold tracking-tight ${color}`}>{value}</p>
          {subtitle && (
            <p className="text-sm text-slate-500 mt-1.5">{subtitle}</p>
          )}
        </div>
        <div className={`p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/50 ${color}`}>
          {icon}
        </div>
      </div>
      {link && (
        <div className="flex items-center gap-1 mt-3 text-xs text-slate-500 group-hover:text-slate-400 transition-colors">
          <span>Vedi dettagli</span>
          <ArrowRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
        </div>
      )}
    </Card>
  )

  return link ? <Link to={link}>{content}</Link> : content
}

const RANK_COLORS = [
  'text-amber-400',
  'text-slate-300',
  'text-orange-600',
]

const CompeanniCard: FC<{ compleanni: ClienteCompleanno[] }> = ({ compleanni }) => {
  const formatGiorni = (giorni: number) => {
    if (giorni === 0) return 'Oggi!'
    if (giorni === 1) return 'Domani'
    return `Tra ${giorni} giorni`
  }

  return (
    <Card className="relative overflow-hidden p-5 border-slate-700/50" data-testid="section-compleanni">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-pink-500/30 to-transparent" />
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Cake className="h-5 w-5 text-pink-400" />
          Compleanni questa settimana
        </h2>
        <Link
          to="/clienti"
          className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
        >
          Clienti <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      {!compleanni.length ? (
        <div className="text-center py-10">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-slate-800/50 border border-slate-700/50 mb-4">
            <Cake className="h-7 w-7 text-slate-600" />
          </div>
          <p className="text-slate-400 font-medium mb-1">Nessun compleanno in vista</p>
          <p className="text-sm text-slate-500">I prossimi 7 giorni sono tranquilli</p>
        </div>
      ) : (
        <div className="space-y-2">
          {compleanni.map((c) => (
            <div
              key={c.id}
              className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700"
            >
              <div className="flex items-center gap-2">
                {c.is_vip && <Crown className="h-3.5 w-3.5 text-yellow-400 shrink-0" />}
                <div>
                  <p className="text-white text-sm font-medium">
                    {c.nome} {c.cognome}
                  </p>
                  <p className="text-xs text-slate-400">
                    Compie {c.anni} anni
                    {c.telefono && ` · ${c.telefono}`}
                  </p>
                </div>
              </div>
              <span
                className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                  c.giorni_mancanti === 0
                    ? 'bg-pink-500/20 text-pink-300'
                    : 'bg-slate-700 text-slate-300'
                }`}
              >
                {formatGiorni(c.giorni_mancanti)}
              </span>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}

const TopOperatoriCard: FC<{ operatori: TopOperatoreKpi[] }> = ({ operatori }) => {
  const formatCur = (v: number) =>
    new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(v)

  return (
    <Card className="relative overflow-hidden p-5 border-slate-700/50" data-testid="section-top-operatori">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-500/30 to-transparent" />
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Trophy className="h-5 w-5 text-amber-400" />
          Top Operatori del Mese
        </h2>
        <Link
          to="/operatori"
          className="text-sm text-cyan-400 hover:text-cyan-300 flex items-center gap-1"
        >
          Tutti <ArrowRight className="h-3 w-3" />
        </Link>
      </div>

      {!operatori.length ? (
        <div className="text-center py-10">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-slate-800/50 border border-slate-700/50 mb-4">
            <Trophy className="h-7 w-7 text-slate-600" />
          </div>
          <p className="text-slate-400 font-medium mb-1">Nessuna classifica</p>
          <p className="text-sm text-slate-500">I dati appariranno dopo il primo mese di attività</p>
        </div>
      ) : (
        <div className="space-y-3">
          {operatori.map((op, i) => (
            <div
              key={op.id}
              className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700"
            >
              <div className="flex items-center gap-3">
                <span className={`text-lg font-bold w-5 text-center ${RANK_COLORS[i] ?? 'text-slate-400'}`}>
                  {i + 1}
                </span>
                <div>
                  <p className="text-white font-medium text-sm">{op.nome_completo}</p>
                  <p className="text-xs text-slate-400">
                    {op.appuntamenti_completati} appunt. · {op.clienti_unici} clienti
                  </p>
                </div>
              </div>
              <p className="text-emerald-400 font-semibold text-sm">
                {formatCur(op.fatturato_generato)}
              </p>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
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
  const { data: topOperatori } = useTopOperatoriMese()
  const { data: compleanni = [] } = useCompeanniSettimana()

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
    }).format(value)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div data-testid="dashboard-header">
        <h1 className="text-3xl font-bold text-white">Buongiorno!</h1>
        <p className="text-slate-400 mt-2">
          Ecco cosa succede nella tua attività oggi
        </p>
      </div>

      {/* Quick Setup Banner */}
      <QuickSetupBanner />

      {/* Welcome Card — solo se DB vuoto (0 clienti e 0 appuntamenti) */}
      {!isLoading && stats && stats.clienti_totali === 0 && stats.appuntamenti_oggi === 0 && stats.appuntamenti_settimana === 0 && (
        <Card className="p-6 bg-gradient-to-br from-cyan-950/40 to-slate-900 border-cyan-800/30" data-testid="welcome-card">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-cyan-500/10 rounded-xl shrink-0">
              <Sparkles className="h-8 w-8 text-cyan-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-white mb-1">Benvenuto in FLUXION!</h2>
              <p className="text-slate-400 text-sm mb-4">
                La tua attività è pronta. Inizia aggiungendo il tuo primo cliente o creando un appuntamento.
              </p>
              <div className="flex flex-wrap gap-3">
                <Link
                  to="/clienti"
                  className="inline-flex items-center gap-2 px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium rounded-lg transition-colors"
                  data-testid="welcome-add-client"
                >
                  <UserPlus className="h-4 w-4" />
                  Aggiungi il primo cliente
                </Link>
                <Link
                  to="/calendario"
                  className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm font-medium rounded-lg transition-colors"
                  data-testid="welcome-add-appointment"
                >
                  <CalendarPlus className="h-4 w-4" />
                  Crea un appuntamento
                </Link>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Appuntamenti oggi"
          value={isLoading ? '-' : stats?.appuntamenti_oggi ?? 0}
          subtitle={`${stats?.appuntamenti_settimana ?? 0} questa settimana`}
          icon={<Calendar className="h-5 w-5" />}
          color="text-cyan-400"
          link="/calendario"
          testId="stats-appuntamenti"
        />
        <StatCard
          title="Clienti totali"
          value={isLoading ? '-' : stats?.clienti_totali ?? 0}
          subtitle={`${stats?.clienti_nuovi_mese ?? 0} nuovi questo mese`}
          icon={<Users className="h-5 w-5" />}
          color="text-emerald-400"
          link="/clienti"
          testId="stats-clienti"
        />
        <StatCard
          title="Fatturato del mese"
          value={isLoading ? '-' : formatCurrency(stats?.fatturato_mese ?? 0)}
          subtitle={`${stats?.fatture_da_pagare ?? 0} fatture da incassare`}
          icon={<TrendingUp className="h-5 w-5" />}
          color="text-amber-400"
          link="/fatture"
          testId="stats-fatturato"
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
        <Card className="relative overflow-hidden p-5 border-slate-700/50" data-testid="section-prossimi-appuntamenti">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />
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
            <div className="text-center py-10">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-slate-800/50 border border-slate-700/50 mb-4">
                <Calendar className="h-7 w-7 text-slate-600" />
              </div>
              <p className="text-slate-400 font-medium mb-1">Giornata libera!</p>
              <p className="text-sm text-slate-500">Non ci sono appuntamenti per oggi</p>
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
        <Card className="relative overflow-hidden p-5 border-slate-700/50" data-testid="section-riepilogo-veloce">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-500/30 to-transparent" />
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Star className="h-5 w-5 text-amber-400" />
              Riepilogo veloce
            </h2>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/50">
              <div className="flex items-center gap-2 mb-2">
                <Crown className="h-4 w-4 text-amber-400" />
                <p className="text-sm font-medium text-slate-400">Clienti VIP</p>
              </div>
              <p className="text-2xl font-bold tracking-tight text-amber-400">
                {stats?.clienti_vip ?? 0}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/50">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-4 w-4 text-red-400" />
                <p className="text-sm font-medium text-slate-400">Da incassare</p>
              </div>
              <p className="text-2xl font-bold tracking-tight text-red-400">
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

      {/* Bottom Row: Top Operatori + Compleanni */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TopOperatoriCard operatori={topOperatori ?? []} />
        <CompeanniCard compleanni={compleanni} />
      </div>
    </div>
  )
}
