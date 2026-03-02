// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatore Assenze Section
// Gestione assenze: ferie, malattia, infortuni, permessi, ecc.
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { Plus, Trash2, Loader2, Calendar, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  useOperatoreAssenze,
  useCreateAssenza,
  useDeleteAssenza,
  type TipoAssenza,
  type CreateAssenzaInput,
} from '@/hooks/use-operatori-assenze';
import { cn } from '@/lib/utils';

// ───────────────────────────────────────────────────────────────────
// Costanti
// ───────────────────────────────────────────────────────────────────

const TIPI_ASSENZA: { value: TipoAssenza; label: string; color: string }[] = [
  { value: 'ferie',       label: 'Ferie',       color: 'bg-green-500/20 text-green-400 border-green-500/30' },
  { value: 'malattia',    label: 'Malattia',    color: 'bg-red-500/20 text-red-400 border-red-500/30' },
  { value: 'infortunio',  label: 'Infortunio',  color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
  { value: 'permesso',    label: 'Permesso',    color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  { value: 'formazione',  label: 'Formazione',  color: 'bg-purple-500/20 text-purple-400 border-purple-500/30' },
  { value: 'maternita',   label: 'Maternità',   color: 'bg-pink-500/20 text-pink-400 border-pink-500/30' },
  { value: 'altro',       label: 'Altro',       color: 'bg-slate-500/20 text-slate-400 border-slate-500/30' },
];

function getTipoMeta(tipo: TipoAssenza) {
  return TIPI_ASSENZA.find((t) => t.value === tipo) ?? TIPI_ASSENZA[TIPI_ASSENZA.length - 1];
}

function formatDate(dateStr: string): string {
  const [y, m, d] = dateStr.split('-');
  return `${d}/${m}/${y}`;
}

function countDays(inizio: string, fine: string): number {
  const a = new Date(inizio);
  const b = new Date(fine);
  return Math.max(1, Math.round((b.getTime() - a.getTime()) / 86_400_000) + 1);
}

function isAssenzaAttiva(inizio: string, fine: string): boolean {
  const today = new Date().toISOString().slice(0, 10);
  return today >= inizio && today <= fine;
}

// ───────────────────────────────────────────────────────────────────
// Inline Form
// ───────────────────────────────────────────────────────────────────

interface AddAssenzaFormProps {
  operatoreId: string;
  onCancel: () => void;
}

const AddAssenzaForm: FC<AddAssenzaFormProps> = ({ operatoreId, onCancel }) => {
  const createMutation = useCreateAssenza();
  const today = new Date().toISOString().slice(0, 10);

  const [form, setForm] = useState<CreateAssenzaInput>({
    operatore_id: operatoreId,
    data_inizio: today,
    data_fine: today,
    tipo: 'ferie',
    note: '',
  });

  const handleSubmit = async () => {
    await createMutation.mutateAsync({
      ...form,
      note: form.note?.trim() || undefined,
    });
    onCancel();
  };

  return (
    <div className="p-4 bg-slate-950 border border-slate-700 rounded-xl space-y-3">
      {/* Tipo assenza */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {TIPI_ASSENZA.map((t) => (
          <button
            key={t.value}
            onClick={() => setForm((f) => ({ ...f, tipo: t.value }))}
            className={cn(
              'px-2 py-1.5 rounded-lg border text-xs font-medium transition-all',
              form.tipo === t.value
                ? t.color
                : 'border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-400'
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Date */}
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <label className="text-xs text-slate-400">Dal</label>
          <input
            type="date"
            value={form.data_inizio}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                data_inizio: e.target.value,
                data_fine: e.target.value > f.data_fine ? e.target.value : f.data_fine,
              }))
            }
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-cyan-500"
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs text-slate-400">Al</label>
          <input
            type="date"
            value={form.data_fine}
            min={form.data_inizio}
            onChange={(e) => setForm((f) => ({ ...f, data_fine: e.target.value }))}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-cyan-500"
          />
        </div>
      </div>

      {/* Note */}
      <input
        type="text"
        placeholder="Note (opzionale)"
        value={form.note ?? ''}
        onChange={(e) => setForm((f) => ({ ...f, note: e.target.value }))}
        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500"
      />

      {/* Preview giorni */}
      <p className="text-xs text-slate-500">
        {countDays(form.data_inizio, form.data_fine)} giorno/i
      </p>

      {/* Azioni */}
      <div className="flex gap-2 justify-end">
        <Button
          variant="ghost"
          size="sm"
          onClick={onCancel}
          className="text-slate-400 hover:text-white hover:bg-slate-800"
        >
          Annulla
        </Button>
        <Button
          size="sm"
          onClick={handleSubmit}
          disabled={createMutation.isPending}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          {createMutation.isPending ? (
            <Loader2 className="w-4 h-4 animate-spin mr-1" />
          ) : (
            <Plus className="w-4 h-4 mr-1" />
          )}
          Aggiungi
        </Button>
      </div>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

interface OperatoreAssenzeSectionProps {
  operatoreId: string;
  nomeOperatore: string;
}

export const OperatoreAssenzeSection: FC<OperatoreAssenzeSectionProps> = ({
  operatoreId,
  nomeOperatore,
}) => {
  const { data: assenze = [], isLoading } = useOperatoreAssenze(operatoreId);
  const deleteMutation = useDeleteAssenza();
  const [showForm, setShowForm] = useState(false);

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
      </div>
    );
  }

  // Ordina: future → presenti → passate
  const now = new Date().toISOString().slice(0, 10);
  const future  = assenze.filter((a) => a.data_inizio > now);
  const presenti = assenze.filter((a) => a.data_inizio <= now && a.data_fine >= now);
  const passate  = assenze.filter((a) => a.data_fine < now);

  const renderAssenza = (a: (typeof assenze)[0]) => {
    const meta = getTipoMeta(a.tipo);
    const attiva = isAssenzaAttiva(a.data_inizio, a.data_fine);
    const giorni = countDays(a.data_inizio, a.data_fine);

    return (
      <div
        key={a.id}
        className={cn(
          'flex items-start gap-3 p-3 rounded-lg border',
          attiva
            ? 'border-orange-500/40 bg-orange-500/5'
            : 'border-slate-800 bg-slate-950'
        )}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium border', meta.color)}>
              {meta.label}
            </span>
            {attiva && (
              <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-orange-500/20 text-orange-300 border border-orange-500/30 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" />
                In corso
              </span>
            )}
          </div>
          <p className="text-sm text-white mt-1.5 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            {formatDate(a.data_inizio)} → {formatDate(a.data_fine)}
            <span className="text-slate-500 text-xs">({giorni}gg)</span>
          </p>
          {a.note && (
            <p className="text-xs text-slate-500 mt-1 truncate">{a.note}</p>
          )}
        </div>
        <button
          onClick={() =>
            deleteMutation.mutate({ id: a.id, operatoreId })
          }
          disabled={deleteMutation.isPending}
          className="p-1.5 text-slate-600 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors flex-shrink-0"
          title="Elimina assenza"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Header + add button */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          Registro assenze di {nomeOperatore}
        </p>
        {!showForm && (
          <Button
            size="sm"
            onClick={() => setShowForm(true)}
            className="bg-cyan-500 hover:bg-cyan-600 text-white"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            Nuova Assenza
          </Button>
        )}
      </div>

      {/* Form inline */}
      {showForm && (
        <AddAssenzaForm
          operatoreId={operatoreId}
          onCancel={() => setShowForm(false)}
        />
      )}

      {/* Lista assenze */}
      {assenze.length === 0 && !showForm ? (
        <div className="text-center p-8 text-slate-500">
          <Calendar className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm">Nessuna assenza registrata.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {presenti.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-orange-400 uppercase tracking-wider mb-2">In corso</h4>
              <div className="space-y-2">{presenti.map(renderAssenza)}</div>
            </div>
          )}
          {future.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Programmate</h4>
              <div className="space-y-2">{future.map(renderAssenza)}</div>
            </div>
          )}
          {passate.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">Passate</h4>
              <div className="space-y-2 opacity-60">{passate.map(renderAssenza)}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
