// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatori Page
// Gestione staff: lista, KPI mensili, servizi abilitati, azioni CRUD
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useMemo } from 'react';
import { Users, Plus, Mail, Phone, Edit, Trash2, Crown, UserCheck, UserX, Calendar, TrendingUp, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useOperatori, useDeleteOperatore } from '@/hooks/use-operatori';
import { OperatoreDialog } from './OperatoreDialog';
import type { Operatore } from '@/types/operatore';
import { useAppuntamenti } from '@/hooks/use-appuntamenti';
import { cn } from '@/lib/utils';

function getMeseDateRange(offset: number): { start_date: string; end_date: string } {
  const d = new Date();
  d.setMonth(d.getMonth() + offset);
  const y = d.getFullYear();
  const m = d.getMonth();
  const start = new Date(y, m, 1);
  const end = new Date(y, m + 1, 0);
  const fmt = (dt: Date) => dt.toISOString().slice(0, 10);
  return { start_date: fmt(start), end_date: fmt(end) };
}

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

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

function getInitials(nome: string, cognome: string) {
  return `${nome.charAt(0)}${cognome.charAt(0)}`.toUpperCase();
}

function getMeseLabel(offset: number) {
  const d = new Date();
  d.setMonth(d.getMonth() + offset);
  return d.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' });
}

function getMeseISO(offset: number) {
  const d = new Date();
  d.setMonth(d.getMonth() + offset);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

// ───────────────────────────────────────────────────────────────────
// KPI card per singolo operatore
// ───────────────────────────────────────────────────────────────────

interface OperatoreKpiProps {
  operatoreId: string;
  meseISO: string;
  appuntamenti: Array<{
    operatore_id?: string | null;
    stato: string;
    data_ora_inizio: string;
    prezzo_finale?: number | null;
  }>;
}

const OperatoreKpi: FC<OperatoreKpiProps> = ({ operatoreId, meseISO, appuntamenti }) => {
  const filtered = useMemo(() =>
    appuntamenti.filter(a =>
      a.operatore_id === operatoreId &&
      a.data_ora_inizio?.startsWith(meseISO)
    ), [appuntamenti, operatoreId, meseISO]);

  const completati = filtered.filter(a => a.stato === 'completato').length;
  const totali = filtered.filter(a => a.stato !== 'cancellato').length;
  const noShow = filtered.filter(a => a.stato === 'no_show').length;
  const fatturato = filtered
    .filter(a => a.stato === 'completato')
    .reduce((sum, a) => sum + (a.prezzo_finale ?? 0), 0);

  if (totali === 0) {
    return (
      <p className="text-xs text-slate-600 italic">Nessun appuntamento questo mese</p>
    );
  }

  return (
    <div className="grid grid-cols-3 gap-2 mt-3">
      <div className="text-center p-2 rounded-lg bg-slate-950 border border-slate-800">
        <p className="text-lg font-bold text-cyan-400">{completati}</p>
        <p className="text-xs text-slate-500">Completati</p>
      </div>
      <div className="text-center p-2 rounded-lg bg-slate-950 border border-slate-800">
        <p className="text-lg font-bold text-green-400">€{fatturato.toFixed(0)}</p>
        <p className="text-xs text-slate-500">Fatturato</p>
      </div>
      <div className="text-center p-2 rounded-lg bg-slate-950 border border-slate-800">
        <p className={cn('text-lg font-bold', noShow > 0 ? 'text-red-400' : 'text-slate-400')}>{noShow}</p>
        <p className="text-xs text-slate-500">No-show</p>
      </div>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

export const OperatoriPage: FC = () => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedOperatore, setSelectedOperatore] = useState<Operatore | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [operatoreToDelete, setOperatoreToDelete] = useState<Operatore | undefined>();
  const [meseOffset, setMeseOffset] = useState(0);

  const { data: operatori = [], isLoading } = useOperatori(false); // tutti, anche inattivi
  const deleteMutation = useDeleteOperatore();

  const meseISO = getMeseISO(meseOffset);
  const { start_date, end_date } = getMeseDateRange(meseOffset);
  const attivi = operatori.filter(o => o.attivo === 1);
  const inattivi = operatori.filter(o => o.attivo !== 1);

  // Appuntamenti del mese per KPI (tutti gli operatori in un colpo solo)
  const { data: appuntamenti = [] } = useAppuntamenti({ start_date, end_date });

  const handleNew = () => {
    setSelectedOperatore(undefined);
    setDialogOpen(true);
  };

  const handleEdit = (op: Operatore) => {
    setSelectedOperatore(op);
    setDialogOpen(true);
  };

  const handleDeleteRequest = (op: Operatore) => {
    setOperatoreToDelete(op);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!operatoreToDelete) return;
    await deleteMutation.mutateAsync(operatoreToDelete.id);
    setDeleteDialogOpen(false);
    setOperatoreToDelete(undefined);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ── Page header ─────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-8 h-8 text-cyan-400" />
          <div>
            <h1 className="text-3xl font-bold text-white">Operatori</h1>
            <p className="text-slate-400 mt-0.5">
              {attivi.length} attivi · {inattivi.length} inattivi
            </p>
          </div>
        </div>
        <Button onClick={handleNew} className="bg-cyan-500 hover:bg-cyan-600 text-white">
          <Plus className="w-4 h-4 mr-2" />
          Nuovo Operatore
        </Button>
      </div>

      {/* ── KPI mese navigator ──────────────────────────────── */}
      <Card className="p-4 bg-slate-900 border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-slate-300">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-medium">Statistiche mensili</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setMeseOffset(m => m - 1)}
              className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-sm text-white font-medium min-w-[140px] text-center capitalize">
              {getMeseLabel(meseOffset)}
            </span>
            <button
              onClick={() => setMeseOffset(m => Math.min(m + 1, 0))}
              disabled={meseOffset >= 0}
              className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors disabled:opacity-30"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Card>

      {/* ── Operatori attivi ────────────────────────────────── */}
      {attivi.length === 0 ? (
        <Card className="p-12 bg-slate-900 border-slate-800 text-center">
          <Users className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400 text-lg">Nessun operatore attivo</p>
          <p className="text-slate-500 text-sm mt-1 mb-6">Aggiungi il tuo primo membro del team</p>
          <Button onClick={handleNew} className="bg-cyan-500 hover:bg-cyan-600 text-white">
            <Plus className="w-4 h-4 mr-2" />
            Aggiungi Operatore
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {attivi.map((op) => (
            <OperatoreCard
              key={op.id}
              operatore={op}
              appuntamenti={appuntamenti as OperatoreKpiProps['appuntamenti']}
              meseISO={meseISO}
              onEdit={handleEdit}
              onDelete={handleDeleteRequest}
            />
          ))}
        </div>
      )}

      {/* ── Operatori inattivi ──────────────────────────────── */}
      {inattivi.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-slate-400 mb-3 flex items-center gap-2">
            <UserX className="w-4 h-4" />
            Inattivi ({inattivi.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {inattivi.map((op) => (
              <OperatoreCard
                key={op.id}
                operatore={op}
                appuntamenti={appuntamenti as OperatoreKpiProps['appuntamenti']}
                meseISO={meseISO}
                onEdit={handleEdit}
                onDelete={handleDeleteRequest}
                dimmed
              />
            ))}
          </div>
        </div>
      )}

      {/* ── Dialog crea/modifica ─────────────────────────────── */}
      <OperatoreDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        operatore={selectedOperatore}
        onSubmit={() => setDialogOpen(false)}
      />

      {/* ── Delete confirm ───────────────────────────────────── */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-slate-950 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Disattiva Operatore</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Vuoi disattivare{' '}
              <span className="font-semibold text-white">
                {operatoreToDelete?.nome} {operatoreToDelete?.cognome}
              </span>
              ? Non sarà più visibile nel calendario ma i dati storici rimarranno.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Annulla
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              disabled={deleteMutation.isPending}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {deleteMutation.isPending ? 'Disattivazione...' : 'Disattiva'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────
// Operatore Card
// ───────────────────────────────────────────────────────────────────

interface OperatoreCardProps {
  operatore: Operatore;
  appuntamenti: OperatoreKpiProps['appuntamenti'];
  meseISO: string;
  onEdit: (op: Operatore) => void;
  onDelete: (op: Operatore) => void;
  dimmed?: boolean;
}

const OperatoreCard: FC<OperatoreCardProps> = ({
  operatore: op,
  appuntamenti,
  meseISO,
  onEdit,
  onDelete,
  dimmed = false,
}) => {
  const isAdmin = op.ruolo === 'admin';

  return (
    <Card
      className={cn(
        'p-5 bg-slate-900 border-slate-800 flex flex-col gap-3 transition-opacity',
        dimmed && 'opacity-50'
      )}
    >
      {/* Avatar + info */}
      <div className="flex items-start gap-3">
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
          style={{ backgroundColor: op.colore || '#64748b' }}
        >
          {getInitials(op.nome, op.cognome)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="text-white font-semibold truncate">
              {op.nome} {op.cognome}
            </p>
            {isAdmin && <Crown className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />}
            {op.attivo === 1
              ? <UserCheck className="w-3.5 h-3.5 text-green-400 flex-shrink-0" />
              : <UserX className="w-3.5 h-3.5 text-slate-600 flex-shrink-0" />
            }
          </div>
          <Badge
            variant="outline"
            className={cn('text-xs mt-1', RUOLO_COLORS[op.ruolo] ?? RUOLO_COLORS.operatore)}
          >
            {RUOLO_LABELS[op.ruolo] ?? op.ruolo}
          </Badge>
        </div>
      </div>

      {/* Contatti */}
      <div className="space-y-1">
        {op.email && (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Mail className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="truncate">{op.email}</span>
          </div>
        )}
        {op.telefono && (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Phone className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{op.telefono}</span>
          </div>
        )}
      </div>

      {/* KPI mese */}
      <div className="border-t border-slate-800 pt-3">
        <p className="text-xs text-slate-500 flex items-center gap-1 mb-1">
          <Calendar className="w-3 h-3" /> Questo mese
        </p>
        <OperatoreKpi
          operatoreId={op.id}
          meseISO={meseISO}
          appuntamenti={appuntamenti}
        />
      </div>

      {/* Azioni */}
      <div className="flex gap-2 border-t border-slate-800 pt-3 mt-auto">
        <Button
          variant="outline"
          size="sm"
          className="flex-1 border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white"
          onClick={() => onEdit(op)}
        >
          <Edit className="w-3.5 h-3.5 mr-1.5" />
          Modifica
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="border-red-500/30 text-red-400 hover:bg-red-500/10 hover:text-red-300"
          onClick={() => onDelete(op)}
          title="Disattiva"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </Button>
      </div>
    </Card>
  );
};
