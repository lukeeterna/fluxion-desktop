// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatore Servizi Section
// Checkbox list per abilitare/disabilitare servizi per operatore
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { Save, Loader2, CheckSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useServizi } from '@/hooks/use-servizi';
import { useOperatoreServizi, useUpdateOperatoreServizi } from '@/hooks/use-operatori-servizi';
import { cn } from '@/lib/utils';

// ───────────────────────────────────────────────────────────────────
// Props
// ───────────────────────────────────────────────────────────────────

interface OperatoreServiziSectionProps {
  operatoreId: string;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const OperatoreServiziSection: FC<OperatoreServiziSectionProps> = ({
  operatoreId,
}) => {
  const { data: tuttiServizi = [] } = useServizi();
  const { data: serviziAbilitati = [], isLoading } = useOperatoreServizi(operatoreId);
  const updateMutation = useUpdateOperatoreServizi();

  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [dirty, setDirty] = useState(false);

  // Inizializza selezione dai dati DB
  useEffect(() => {
    setSelected(new Set(serviziAbilitati));
    setDirty(false);
  }, [serviziAbilitati]);

  const toggle = (servizioId: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(servizioId)) {
        next.delete(servizioId);
      } else {
        next.add(servizioId);
      }
      return next;
    });
    setDirty(true);
  };

  const handleSave = async () => {
    await updateMutation.mutateAsync({
      operatoreId,
      servizioIds: Array.from(selected),
    });
    setDirty(false);
  };

  // Raggruppa per categoria
  const byCategoria = tuttiServizi.reduce<Record<string, typeof tuttiServizi>>(
    (acc, s) => {
      const cat = s.categoria ?? 'Generale';
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(s);
      return acc;
    },
    {}
  );

  // ── Loading ──
  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
      </div>
    );
  }

  // ── Nessun servizio configurato ──
  if (tuttiServizi.length === 0) {
    return (
      <div className="text-center p-8 text-slate-500">
        <CheckSquare className="w-10 h-10 mx-auto mb-3 opacity-30" />
        <p className="text-sm">Nessun servizio configurato.</p>
        <p className="text-xs mt-1">Aggiungi servizi dalla sezione Servizi.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ── Contatore selezionati ── */}
      <p className="text-xs text-slate-500">
        {selected.size} di {tuttiServizi.length} servizi abilitati
      </p>

      {/* ── Lista per categoria ── */}
      {Object.entries(byCategoria).map(([categoria, servizi]) => (
        <div key={categoria}>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            {categoria}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {servizi.map((s) => {
              const isSelected = selected.has(s.id);
              return (
                <button
                  key={s.id}
                  onClick={() => toggle(s.id)}
                  className={cn(
                    'flex items-center gap-3 p-3 rounded-lg border text-left transition-all',
                    isSelected
                      ? 'border-cyan-500/50 bg-cyan-500/10 text-white'
                      : 'border-slate-700 bg-slate-950 text-slate-400 hover:border-slate-600 hover:text-slate-300'
                  )}
                >
                  {/* Checkbox */}
                  <div
                    className={cn(
                      'w-4 h-4 rounded border-2 flex-shrink-0 flex items-center justify-center',
                      isSelected
                        ? 'border-cyan-400 bg-cyan-400'
                        : 'border-slate-600'
                    )}
                  >
                    {isSelected && (
                      <svg
                        className="w-3 h-3 text-slate-950"
                        viewBox="0 0 12 12"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <polyline points="2,6 5,9 10,3" />
                      </svg>
                    )}
                  </div>

                  {/* Dot colore servizio */}
                  <div
                    className="w-2 h-2 rounded-full flex-shrink-0"
                    style={{ backgroundColor: s.colore }}
                  />

                  {/* Info servizio */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{s.nome}</p>
                    <p className="text-xs text-slate-500">
                      {s.durata_minuti}min · €{s.prezzo.toFixed(0)}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      ))}

      {/* ── Salva ── */}
      {dirty && (
        <div className="flex justify-end pt-2 border-t border-slate-800">
          <Button
            onClick={handleSave}
            disabled={updateMutation.isPending}
            className="bg-cyan-500 hover:bg-cyan-600 text-white"
          >
            {updateMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Salva Servizi
          </Button>
        </div>
      )}
    </div>
  );
};
