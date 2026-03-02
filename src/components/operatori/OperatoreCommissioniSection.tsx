// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatore Commissioni Section (B5)
// Gestione commissioni: percentuale, fisso mensile, bonus soglia
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { Plus, Trash2, Loader2, Euro, Pencil, CheckCircle2, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  useOperatoreCommissioni,
  useCreateCommissione,
  useUpdateCommissione,
  useDeleteCommissione,
  type TipoCommissione,
  type CreateCommissioneInput,
  type UpdateCommissioneInput,
  type OperatoreCommissione,
} from '@/hooks/use-operatori-commissioni';
import { cn } from '@/lib/utils';

// ───────────────────────────────────────────────────────────────────
// Costanti
// ───────────────────────────────────────────────────────────────────

const TIPI_COMMISSIONE: {
  value: TipoCommissione;
  label: string;
  description: string;
  color: string;
}[] = [
  {
    value: 'percentuale_servizio',
    label: '% Servizi',
    description: 'Percentuale sul fatturato servizi',
    color: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
  },
  {
    value: 'percentuale_prodotti',
    label: '% Prodotti',
    description: 'Percentuale sul fatturato prodotti',
    color: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  },
  {
    value: 'fisso_mensile',
    label: 'Fisso mensile',
    description: 'Importo fisso ogni mese',
    color: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  },
  {
    value: 'soglia_bonus',
    label: 'Bonus soglia',
    description: 'Bonus al raggiungimento di un obiettivo',
    color: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  },
];

function getTipoMeta(tipo: TipoCommissione) {
  return TIPI_COMMISSIONE.find((t) => t.value === tipo) ?? TIPI_COMMISSIONE[0];
}

function formatDate(dateStr: string): string {
  const [y, m, d] = dateStr.split('-');
  return `${d}/${m}/${y}`;
}

function formatEuro(value: number | null): string {
  if (value === null) return '—';
  return `€${value.toLocaleString('it-IT', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
}

function formatPercent(value: number | null): string {
  if (value === null) return '—';
  return `${value}%`;
}

function isAttiva(c: OperatoreCommissione): boolean {
  const today = new Date().toISOString().slice(0, 10);
  return c.valida_dal <= today && (c.valida_al === null || c.valida_al >= today);
}

function getCommissioneLabel(c: OperatoreCommissione): string {
  switch (c.tipo) {
    case 'percentuale_servizio':
    case 'percentuale_prodotti':
      return formatPercent(c.percentuale);
    case 'fisso_mensile':
      return formatEuro(c.importo_fisso);
    case 'soglia_bonus':
      return `Soglia ${formatEuro(c.soglia_fatturato)} → Bonus ${formatEuro(c.bonus_importo)}`;
    default:
      return '—';
  }
}

// ───────────────────────────────────────────────────────────────────
// Form fields per tipo
// ───────────────────────────────────────────────────────────────────

interface FormState {
  tipo: TipoCommissione;
  percentuale: string;
  importo_fisso: string;
  soglia_fatturato: string;
  bonus_importo: string;
  valida_dal: string;
  valida_al: string;
  note: string;
}

function getEmptyForm(): FormState {
  const today = new Date().toISOString().slice(0, 10);
  return {
    tipo: 'percentuale_servizio',
    percentuale: '',
    importo_fisso: '',
    soglia_fatturato: '',
    bonus_importo: '',
    valida_dal: today,
    valida_al: '',
    note: '',
  };
}

function formToCreateInput(
  operatoreId: string,
  form: FormState,
): CreateCommissioneInput {
  const base: CreateCommissioneInput = {
    operatore_id: operatoreId,
    tipo: form.tipo,
    valida_dal: form.valida_dal,
    valida_al: form.valida_al || undefined,
    note: form.note.trim() || undefined,
  };

  if (form.tipo === 'percentuale_servizio' || form.tipo === 'percentuale_prodotti') {
    base.percentuale = parseFloat(form.percentuale) || undefined;
  } else if (form.tipo === 'fisso_mensile') {
    base.importo_fisso = parseFloat(form.importo_fisso) || undefined;
  } else if (form.tipo === 'soglia_bonus') {
    base.soglia_fatturato = parseFloat(form.soglia_fatturato) || undefined;
    base.bonus_importo = parseFloat(form.bonus_importo) || undefined;
  }

  return base;
}

function formToUpdateInput(form: FormState): UpdateCommissioneInput {
  const base: UpdateCommissioneInput = {
    tipo: form.tipo,
    valida_dal: form.valida_dal,
    valida_al: form.valida_al || undefined,
    note: form.note.trim() || undefined,
  };

  if (form.tipo === 'percentuale_servizio' || form.tipo === 'percentuale_prodotti') {
    base.percentuale = parseFloat(form.percentuale) || undefined;
  } else if (form.tipo === 'fisso_mensile') {
    base.importo_fisso = parseFloat(form.importo_fisso) || undefined;
  } else if (form.tipo === 'soglia_bonus') {
    base.soglia_fatturato = parseFloat(form.soglia_fatturato) || undefined;
    base.bonus_importo = parseFloat(form.bonus_importo) || undefined;
  }

  return base;
}

function commissioneToForm(c: OperatoreCommissione): FormState {
  return {
    tipo: c.tipo,
    percentuale: c.percentuale != null ? String(c.percentuale) : '',
    importo_fisso: c.importo_fisso != null ? String(c.importo_fisso) : '',
    soglia_fatturato: c.soglia_fatturato != null ? String(c.soglia_fatturato) : '',
    bonus_importo: c.bonus_importo != null ? String(c.bonus_importo) : '',
    valida_dal: c.valida_dal,
    valida_al: c.valida_al ?? '',
    note: c.note ?? '',
  };
}

// ───────────────────────────────────────────────────────────────────
// Inline Form
// ───────────────────────────────────────────────────────────────────

interface CommissioneFormProps {
  operatoreId: string;
  editTarget?: OperatoreCommissione;
  onCancel: () => void;
}

const CommissioneForm: FC<CommissioneFormProps> = ({
  operatoreId,
  editTarget,
  onCancel,
}) => {
  const createMutation = useCreateCommissione();
  const updateMutation = useUpdateCommissione();

  const [form, setForm] = useState<FormState>(
    editTarget ? commissioneToForm(editTarget) : getEmptyForm(),
  );

  const isEditing = !!editTarget;
  const isPending = createMutation.isPending || updateMutation.isPending;

  const handleSubmit = async () => {
    if (isEditing && editTarget) {
      await updateMutation.mutateAsync({
        id: editTarget.id,
        operatoreId,
        input: formToUpdateInput(form),
      });
    } else {
      await createMutation.mutateAsync(formToCreateInput(operatoreId, form));
    }
    onCancel();
  };

  const inputClass =
    'w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500';
  const labelClass = 'text-xs text-slate-400 mb-1 block';

  return (
    <div className="p-4 bg-slate-950 border border-slate-700 rounded-xl space-y-4">
      {/* Tipo commissione */}
      <div className="grid grid-cols-2 gap-2">
        {TIPI_COMMISSIONE.map((t) => (
          <button
            key={t.value}
            onClick={() => setForm((f) => ({ ...f, tipo: t.value }))}
            className={cn(
              'px-3 py-2 rounded-lg border text-xs font-medium transition-all text-left',
              form.tipo === t.value
                ? t.color
                : 'border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-400',
            )}
          >
            <div className="font-semibold">{t.label}</div>
            <div className="text-[10px] opacity-70 mt-0.5">{t.description}</div>
          </button>
        ))}
      </div>

      {/* Campi dinamici per tipo */}
      {(form.tipo === 'percentuale_servizio' || form.tipo === 'percentuale_prodotti') && (
        <div>
          <label className={labelClass}>Percentuale (%)</label>
          <input
            type="number"
            min="0"
            max="100"
            step="0.5"
            placeholder="es. 15"
            value={form.percentuale}
            onChange={(e) => setForm((f) => ({ ...f, percentuale: e.target.value }))}
            className={inputClass}
          />
        </div>
      )}

      {form.tipo === 'fisso_mensile' && (
        <div>
          <label className={labelClass}>Importo fisso mensile (€)</label>
          <input
            type="number"
            min="0"
            step="10"
            placeholder="es. 500"
            value={form.importo_fisso}
            onChange={(e) => setForm((f) => ({ ...f, importo_fisso: e.target.value }))}
            className={inputClass}
          />
        </div>
      )}

      {form.tipo === 'soglia_bonus' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Soglia fatturato (€)</label>
            <input
              type="number"
              min="0"
              step="100"
              placeholder="es. 3000"
              value={form.soglia_fatturato}
              onChange={(e) => setForm((f) => ({ ...f, soglia_fatturato: e.target.value }))}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Bonus al raggiungimento (€)</label>
            <input
              type="number"
              min="0"
              step="50"
              placeholder="es. 200"
              value={form.bonus_importo}
              onChange={(e) => setForm((f) => ({ ...f, bonus_importo: e.target.value }))}
              className={inputClass}
            />
          </div>
        </div>
      )}

      {/* Periodo validità */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Valida dal</label>
          <input
            type="date"
            value={form.valida_dal}
            onChange={(e) => setForm((f) => ({ ...f, valida_dal: e.target.value }))}
            className={inputClass}
          />
        </div>
        <div>
          <label className={labelClass}>Valida al (vuoto = senza scadenza)</label>
          <input
            type="date"
            value={form.valida_al}
            min={form.valida_dal}
            onChange={(e) => setForm((f) => ({ ...f, valida_al: e.target.value }))}
            className={inputClass}
          />
        </div>
      </div>

      {/* Note */}
      <div>
        <label className={labelClass}>Note (opzionale)</label>
        <input
          type="text"
          placeholder="es. Accordo verbale del 01/03/2026"
          value={form.note}
          onChange={(e) => setForm((f) => ({ ...f, note: e.target.value }))}
          className={inputClass}
        />
      </div>

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
          disabled={isPending}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          {isPending ? (
            <Loader2 className="w-4 h-4 animate-spin mr-1" />
          ) : isEditing ? (
            <CheckCircle2 className="w-4 h-4 mr-1" />
          ) : (
            <Plus className="w-4 h-4 mr-1" />
          )}
          {isEditing ? 'Salva modifiche' : 'Aggiungi'}
        </Button>
      </div>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

interface OperatoreCommissioniSectionProps {
  operatoreId: string;
  nomeOperatore: string;
}

export const OperatoreCommissioniSection: FC<OperatoreCommissioniSectionProps> = ({
  operatoreId,
  nomeOperatore,
}) => {
  const { data: commissioni = [], isLoading } = useOperatoreCommissioni(operatoreId);
  const deleteMutation = useDeleteCommissione();
  const [showForm, setShowForm] = useState(false);
  const [editTarget, setEditTarget] = useState<OperatoreCommissione | undefined>(undefined);

  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
      </div>
    );
  }

  const attive = commissioni.filter(isAttiva);
  const scadute = commissioni.filter((c) => !isAttiva(c));

  const handleEdit = (c: OperatoreCommissione) => {
    setEditTarget(c);
    setShowForm(true);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditTarget(undefined);
  };

  const renderCommissione = (c: OperatoreCommissione) => {
    const meta = getTipoMeta(c.tipo);
    const active = isAttiva(c);

    return (
      <div
        key={c.id}
        className={cn(
          'flex items-start gap-3 p-3 rounded-lg border',
          active
            ? 'border-cyan-500/30 bg-cyan-500/5'
            : 'border-slate-800 bg-slate-950 opacity-60',
        )}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={cn(
                'px-2 py-0.5 rounded-full text-xs font-medium border',
                meta.color,
              )}
            >
              {meta.label}
            </span>
            <span className="text-sm font-semibold text-white">
              {getCommissioneLabel(c)}
            </span>
            {active && (
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-green-500/20 text-green-400 border border-green-500/30">
                <CheckCircle2 className="w-3 h-3" />
                Attiva
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1.5 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Dal {formatDate(c.valida_dal)}
            {c.valida_al ? ` al ${formatDate(c.valida_al)}` : ' — senza scadenza'}
          </p>
          {c.note && (
            <p className="text-xs text-slate-500 mt-1 truncate">{c.note}</p>
          )}
        </div>
        <div className="flex gap-1 flex-shrink-0">
          <button
            onClick={() => handleEdit(c)}
            className="p-1.5 text-slate-600 hover:text-cyan-400 hover:bg-cyan-500/10 rounded transition-colors"
            title="Modifica commissione"
          >
            <Pencil className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => deleteMutation.mutate({ id: c.id, operatoreId })}
            disabled={deleteMutation.isPending}
            className="p-1.5 text-slate-600 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
            title="Elimina commissione"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">
          Struttura commissioni di {nomeOperatore}
        </p>
        {!showForm && (
          <Button
            size="sm"
            onClick={() => { setEditTarget(undefined); setShowForm(true); }}
            className="bg-cyan-500 hover:bg-cyan-600 text-white"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            Nuova commissione
          </Button>
        )}
      </div>

      {/* Form inline */}
      {showForm && (
        <CommissioneForm
          operatoreId={operatoreId}
          editTarget={editTarget}
          onCancel={handleCancel}
        />
      )}

      {/* Lista commissioni */}
      {commissioni.length === 0 && !showForm ? (
        <div className="text-center p-8 text-slate-500">
          <Euro className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm">Nessuna commissione configurata.</p>
          <p className="text-xs mt-1 text-slate-600">
            Aggiungi percentuale, fisso mensile o bonus soglia.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {attive.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-2">
                Attive
              </h4>
              <div className="space-y-2">{attive.map(renderCommissione)}</div>
            </div>
          )}
          {scadute.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
                Scadute / Future
              </h4>
              <div className="space-y-2">{scadute.map(renderCommissione)}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
