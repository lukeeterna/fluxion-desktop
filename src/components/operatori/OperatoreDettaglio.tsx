// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatore Dettaglio
// Pagina dettaglio operatore con tab: Servizi | Assenze | Orari
// ═══════════════════════════════════════════════════════════════════

import { type FC } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Wrench,
  CalendarOff,
  Clock,
  Crown,
  UserCheck,
  UserX,
  BarChart2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useOperatore } from '@/hooks/use-operatori';
import { OperatoreServiziSection } from './OperatoreServiziSection';
import { OperatoreAssenzeSection } from './OperatoreAssenzeSection';
import { OperatoreOrariSection } from './OperatoreOrariSection';
import { OperatoreStatisticheSection } from './OperatoreStatisticheSection';
import { cn } from '@/lib/utils';

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

function getInitials(nome: string, cognome: string) {
  return `${nome.charAt(0)}${cognome.charAt(0)}`.toUpperCase();
}

const RUOLO_LABELS: Record<string, string> = {
  admin: 'Amministratore',
  operatore: 'Operatore',
  reception: 'Reception',
};

const RUOLO_COLORS: Record<string, string> = {
  admin: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  operatore: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30',
  reception: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
};

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const OperatoreDettaglio: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: operatore, isLoading } = useOperatore(id ?? '');

  // ── Loading ──
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // ── Non trovato ──
  if (!operatore) {
    return (
      <div className="text-center p-12">
        <p className="text-slate-400 mb-4">Operatore non trovato.</p>
        <Button
          variant="outline"
          className="border-slate-700 text-slate-300 hover:bg-slate-800"
          onClick={() => navigate('/operatori')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Torna alla lista
        </Button>
      </div>
    );
  }

  const isAdmin = operatore.ruolo === 'admin';
  const isAttivo = operatore.attivo === 1;

  return (
    <div className="space-y-6">
      {/* ── Breadcrumb / Back ── */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => navigate('/operatori')}
          className="flex items-center gap-1.5 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Operatori
        </button>
        <span className="text-slate-700">/</span>
        <span className="text-sm text-slate-300">
          {operatore.nome} {operatore.cognome}
        </span>
      </div>

      {/* ── Header operatore ── */}
      <div className="flex items-center gap-4 p-5 bg-slate-900 border border-slate-800 rounded-xl">
        {/* Avatar */}
        <div
          className="w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl flex-shrink-0"
          style={{ backgroundColor: operatore.colore || '#64748b' }}
        >
          {getInitials(operatore.nome, operatore.cognome)}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl font-bold text-white">
              {operatore.nome} {operatore.cognome}
            </h1>
            {isAdmin && <Crown className="w-4 h-4 text-amber-400" />}
            {isAttivo
              ? <UserCheck className="w-4 h-4 text-green-400" />
              : <UserX className="w-4 h-4 text-slate-500" />
            }
          </div>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <Badge
              variant="outline"
              className={cn(
                'text-xs',
                RUOLO_COLORS[operatore.ruolo] ?? RUOLO_COLORS.operatore
              )}
            >
              {RUOLO_LABELS[operatore.ruolo] ?? operatore.ruolo}
            </Badge>
            {operatore.email && (
              <span className="text-xs text-slate-500">{operatore.email}</span>
            )}
            {operatore.telefono && (
              <span className="text-xs text-slate-500">{operatore.telefono}</span>
            )}
          </div>
        </div>

        {/* Stato */}
        <div
          className={cn(
            'ml-auto px-2.5 py-1 rounded-full text-xs font-medium flex-shrink-0',
            isAttivo
              ? 'bg-green-500/15 text-green-400'
              : 'bg-slate-700 text-slate-400'
          )}
        >
          {isAttivo ? 'Attivo' : 'Inattivo'}
        </div>
      </div>

      {/* ── Tabs ── */}
      <Tabs defaultValue="statistiche" className="w-full">
        <TabsList className="bg-slate-900 border border-slate-800 w-full sm:w-auto">
          <TabsTrigger
            value="statistiche"
            className="data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400 gap-2"
          >
            <BarChart2 className="w-4 h-4" />
            Statistiche
          </TabsTrigger>
          <TabsTrigger
            value="servizi"
            className="data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400 gap-2"
          >
            <Wrench className="w-4 h-4" />
            Servizi
          </TabsTrigger>
          <TabsTrigger
            value="assenze"
            className="data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400 gap-2"
          >
            <CalendarOff className="w-4 h-4" />
            Assenze
          </TabsTrigger>
          <TabsTrigger
            value="orari"
            className="data-[state=active]:bg-slate-800 data-[state=active]:text-white text-slate-400 gap-2"
          >
            <Clock className="w-4 h-4" />
            Orari
          </TabsTrigger>
        </TabsList>

        {/* ── Tab: Statistiche ── */}
        <TabsContent
          value="statistiche"
          className="mt-4 p-5 bg-slate-900 border border-slate-800 rounded-xl"
        >
          <div className="mb-4">
            <h2 className="text-base font-semibold text-white">Statistiche</h2>
            <p className="text-sm text-slate-500 mt-0.5">
              KPI mensili e trend di{' '}
              <span className="text-slate-300">{operatore.nome}</span>.
            </p>
          </div>
          <OperatoreStatisticheSection
            operatoreId={operatore.id}
            nomeOperatore={operatore.nome}
          />
        </TabsContent>

        {/* ── Tab: Servizi ── */}
        <TabsContent
          value="servizi"
          className="mt-4 p-5 bg-slate-900 border border-slate-800 rounded-xl"
        >
          <div className="mb-4">
            <h2 className="text-base font-semibold text-white">
              Servizi abilitati
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Seleziona i servizi che{' '}
              <span className="text-slate-300">{operatore.nome}</span> può
              erogare.
            </p>
          </div>
          <OperatoreServiziSection operatoreId={operatore.id} />
        </TabsContent>

        {/* ── Tab: Assenze ── */}
        <TabsContent
          value="assenze"
          className="mt-4 p-5 bg-slate-900 border border-slate-800 rounded-xl"
        >
          <div className="mb-4">
            <h2 className="text-base font-semibold text-white">
              Assenze & Ferie
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Ferie, malattia, infortuni, permessi e altre assenze.
            </p>
          </div>
          <OperatoreAssenzeSection
            operatoreId={operatore.id}
            nomeOperatore={operatore.nome}
          />
        </TabsContent>

        {/* ── Tab: Orari ── */}
        <TabsContent
          value="orari"
          className="mt-4 p-5 bg-slate-900 border border-slate-800 rounded-xl"
        >
          <div className="mb-4">
            <h2 className="text-base font-semibold text-white">
              Orari di lavoro
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              Configura gli orari settimanali per{' '}
              <span className="text-slate-300">{operatore.nome}</span>.
            </p>
          </div>
          <OperatoreOrariSection operatoreId={operatore.id} />
        </TabsContent>
      </Tabs>
    </div>
  );
};
