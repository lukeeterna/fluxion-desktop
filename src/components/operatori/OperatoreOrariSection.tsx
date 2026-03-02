// ═══════════════════════════════════════════════════════════════════
// FLUXION - Operatore Orari Section
// Griglia settimanale con toggle chiuso/aperto + time picker per fascia
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect, useCallback } from 'react';
import { Save, Loader2, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  useOperatoreOrari,
  useSetOrariOperatore,
  type OrarioLavoro,
  type SetOrarioInput,
} from '@/hooks/use-operatori-orari';
import { cn } from '@/lib/utils';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface FasciaOraria {
  inizio: string; // "HH:MM"
  fine: string;   // "HH:MM"
  abilitata: boolean;
}

interface GiornoConfig {
  aperto: boolean;
  mattina: FasciaOraria;
  pomeriggio: FasciaOraria;
}

type OrarioSettimanale = Record<number, GiornoConfig>;

// ───────────────────────────────────────────────────────────────────
// Costanti
// ───────────────────────────────────────────────────────────────────

// Ordine visualizzazione: lunedì (1) → domenica (0)
const GIORNI_ORDINATI: number[] = [1, 2, 3, 4, 5, 6, 0];

const NOMI_GIORNI: Record<number, string> = {
  0: 'Domenica',
  1: 'Lunedì',
  2: 'Martedì',
  3: 'Mercoledì',
  4: 'Giovedì',
  5: 'Venerdì',
  6: 'Sabato',
};

const DEFAULT_MATTINA: FasciaOraria = {
  inizio: '09:00',
  fine: '13:00',
  abilitata: true,
};

const DEFAULT_POMERIGGIO: FasciaOraria = {
  inizio: '14:00',
  fine: '20:00',
  abilitata: true,
};

function defaultOrarioSettimanale(): OrarioSettimanale {
  const orario: OrarioSettimanale = {};
  for (const g of GIORNI_ORDINATI) {
    // Domenica (0) e sabato (6) chiusi per default
    const aperto = g !== 0;
    orario[g] = {
      aperto,
      mattina: { ...DEFAULT_MATTINA },
      pomeriggio: { ...DEFAULT_POMERIGGIO },
    };
  }
  return orario;
}

// ───────────────────────────────────────────────────────────────────
// Helpers: conversione DB → stato locale
// ───────────────────────────────────────────────────────────────────

function dbToOrarioSettimanale(orari: OrarioLavoro[]): OrarioSettimanale {
  const stato = defaultOrarioSettimanale();

  // Prima marca tutti i giorni che hanno almeno un orario 'lavoro' come aperti
  const giorniConLavoro = new Set(
    orari.filter((o) => o.tipo === 'lavoro').map((o) => o.giorno_settimana)
  );

  for (const g of GIORNI_ORDINATI) {
    stato[g].aperto = giorniConLavoro.has(g);

    if (!stato[g].aperto) continue;

    // Prendi le fasce 'lavoro' ordinate per ora_inizio
    const fasce = orari
      .filter((o) => o.giorno_settimana === g && o.tipo === 'lavoro')
      .sort((a, b) => a.ora_inizio.localeCompare(b.ora_inizio));

    if (fasce.length >= 1) {
      stato[g].mattina = {
        inizio: fasce[0].ora_inizio,
        fine: fasce[0].ora_fine,
        abilitata: true,
      };
    }
    if (fasce.length >= 2) {
      stato[g].pomeriggio = {
        inizio: fasce[1].ora_inizio,
        fine: fasce[1].ora_fine,
        abilitata: true,
      };
    } else {
      // Solo mattina — disabilita pomeriggio ma mantieni valori
      stato[g].pomeriggio = { ...DEFAULT_POMERIGGIO, abilitata: false };
    }
  }

  return stato;
}

// ───────────────────────────────────────────────────────────────────
// Helpers: stato locale → SetOrarioInput[]
// ───────────────────────────────────────────────────────────────────

function orarioSettimanaleToInput(stato: OrarioSettimanale): SetOrarioInput[] {
  const inputs: SetOrarioInput[] = [];

  for (const g of GIORNI_ORDINATI) {
    const giorno = stato[g];
    if (!giorno.aperto) continue;

    if (giorno.mattina.abilitata && giorno.mattina.inizio && giorno.mattina.fine) {
      inputs.push({
        giorno_settimana: g,
        ora_inizio: giorno.mattina.inizio,
        ora_fine: giorno.mattina.fine,
        tipo: 'lavoro',
      });
    }

    if (
      giorno.pomeriggio.abilitata &&
      giorno.pomeriggio.inizio &&
      giorno.pomeriggio.fine
    ) {
      inputs.push({
        giorno_settimana: g,
        ora_inizio: giorno.pomeriggio.inizio,
        ora_fine: giorno.pomeriggio.fine,
        tipo: 'lavoro',
      });
    }
  }

  return inputs;
}

// ───────────────────────────────────────────────────────────────────
// Props
// ───────────────────────────────────────────────────────────────────

interface OperatoreOrariSectionProps {
  operatoreId: string;
}

// ───────────────────────────────────────────────────────────────────
// Sub-component: TimeInput
// ───────────────────────────────────────────────────────────────────

interface TimeInputProps {
  value: string;
  onChange: (val: string) => void;
  disabled?: boolean;
  'aria-label': string;
}

const TimeInput: FC<TimeInputProps> = ({ value, onChange, disabled, 'aria-label': ariaLabel }) => (
  <input
    type="time"
    value={value}
    onChange={(e) => onChange(e.target.value)}
    disabled={disabled}
    aria-label={ariaLabel}
    className={cn(
      'bg-slate-900 border border-slate-700 rounded px-2 py-1 text-sm text-white',
      'focus:outline-none focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500',
      'disabled:opacity-40 disabled:cursor-not-allowed',
      '[color-scheme:dark]'
    )}
  />
);

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const OperatoreOrariSection: FC<OperatoreOrariSectionProps> = ({
  operatoreId,
}) => {
  const { data: orariDb = [], isLoading } = useOperatoreOrari(operatoreId);
  const setOrariMutation = useSetOrariOperatore();

  const [orario, setOrario] = useState<OrarioSettimanale>(defaultOrarioSettimanale);
  const [dirty, setDirty] = useState(false);

  // Inizializza stato dai dati DB
  useEffect(() => {
    setOrario(dbToOrarioSettimanale(orariDb));
    setDirty(false);
  }, [orariDb]);

  // ── Handlers ──

  const toggleGiorno = useCallback((giorno: number) => {
    setOrario((prev) => ({
      ...prev,
      [giorno]: { ...prev[giorno], aperto: !prev[giorno].aperto },
    }));
    setDirty(true);
  }, []);

  const togglePomeriggio = useCallback((giorno: number) => {
    setOrario((prev) => ({
      ...prev,
      [giorno]: {
        ...prev[giorno],
        pomeriggio: {
          ...prev[giorno].pomeriggio,
          abilitata: !prev[giorno].pomeriggio.abilitata,
        },
      },
    }));
    setDirty(true);
  }, []);

  const updateMattina = useCallback(
    (giorno: number, campo: 'inizio' | 'fine', valore: string) => {
      setOrario((prev) => ({
        ...prev,
        [giorno]: {
          ...prev[giorno],
          mattina: { ...prev[giorno].mattina, [campo]: valore },
        },
      }));
      setDirty(true);
    },
    []
  );

  const updatePomeriggio = useCallback(
    (giorno: number, campo: 'inizio' | 'fine', valore: string) => {
      setOrario((prev) => ({
        ...prev,
        [giorno]: {
          ...prev[giorno],
          pomeriggio: { ...prev[giorno].pomeriggio, [campo]: valore },
        },
      }));
      setDirty(true);
    },
    []
  );

  const handleSave = async () => {
    const inputs = orarioSettimanaleToInput(orario);
    await setOrariMutation.mutateAsync({ operatoreId, orari: inputs });
    setDirty(false);
  };

  // ── Loading ──
  if (isLoading) {
    return (
      <div className="flex justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* ── Griglia giorni ── */}
      {GIORNI_ORDINATI.map((g) => {
        const giorno = orario[g];
        const nomeGiorno = NOMI_GIORNI[g];

        return (
          <div
            key={g}
            className={cn(
              'rounded-xl border p-4 transition-colors',
              giorno.aperto
                ? 'bg-slate-950 border-slate-800'
                : 'bg-slate-950/50 border-slate-800/50'
            )}
          >
            {/* ── Riga header: nome giorno + toggle ── */}
            <div className="flex items-center justify-between gap-4">
              <span
                className={cn(
                  'text-sm font-semibold w-24 flex-shrink-0',
                  giorno.aperto ? 'text-white' : 'text-slate-500'
                )}
              >
                {nomeGiorno}
              </span>

              {/* Toggle aperto/chiuso */}
              <button
                type="button"
                onClick={() => toggleGiorno(g)}
                aria-pressed={giorno.aperto}
                aria-label={`${nomeGiorno}: ${giorno.aperto ? 'Aperto' : 'Chiuso'}`}
                className={cn(
                  'flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border transition-all',
                  giorno.aperto
                    ? 'bg-cyan-500/15 border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/25'
                    : 'bg-slate-800 border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-400'
                )}
              >
                <span
                  className={cn(
                    'w-2 h-2 rounded-full flex-shrink-0',
                    giorno.aperto ? 'bg-cyan-400' : 'bg-slate-600'
                  )}
                />
                {giorno.aperto ? 'Aperto' : 'Chiuso'}
              </button>
            </div>

            {/* ── Fasce orarie (solo se aperto) ── */}
            {giorno.aperto && (
              <div className="mt-4 space-y-3 pl-0">
                {/* Mattina */}
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-xs text-slate-400 w-20 flex-shrink-0">
                    Mattina
                  </span>
                  <div className="flex items-center gap-2">
                    <TimeInput
                      value={giorno.mattina.inizio}
                      onChange={(v) => updateMattina(g, 'inizio', v)}
                      aria-label={`${nomeGiorno} mattina inizio`}
                    />
                    <span className="text-slate-600 text-sm">→</span>
                    <TimeInput
                      value={giorno.mattina.fine}
                      onChange={(v) => updateMattina(g, 'fine', v)}
                      aria-label={`${nomeGiorno} mattina fine`}
                    />
                  </div>
                </div>

                {/* Pomeriggio */}
                <div className="flex items-center gap-3 flex-wrap">
                  <span
                    className={cn(
                      'text-xs w-20 flex-shrink-0',
                      giorno.pomeriggio.abilitata ? 'text-slate-400' : 'text-slate-600'
                    )}
                  >
                    Pomeriggio
                  </span>
                  <div className="flex items-center gap-2">
                    <TimeInput
                      value={giorno.pomeriggio.inizio}
                      onChange={(v) => updatePomeriggio(g, 'inizio', v)}
                      disabled={!giorno.pomeriggio.abilitata}
                      aria-label={`${nomeGiorno} pomeriggio inizio`}
                    />
                    <span className="text-slate-600 text-sm">→</span>
                    <TimeInput
                      value={giorno.pomeriggio.fine}
                      onChange={(v) => updatePomeriggio(g, 'fine', v)}
                      disabled={!giorno.pomeriggio.abilitata}
                      aria-label={`${nomeGiorno} pomeriggio fine`}
                    />
                    {/* Toggle pomeriggio */}
                    <button
                      type="button"
                      onClick={() => togglePomeriggio(g)}
                      aria-pressed={giorno.pomeriggio.abilitata}
                      aria-label={`${nomeGiorno} pomeriggio ${giorno.pomeriggio.abilitata ? 'abilitato' : 'disabilitato'}`}
                      className={cn(
                        'w-4 h-4 rounded border-2 flex-shrink-0 flex items-center justify-center transition-all ml-1',
                        giorno.pomeriggio.abilitata
                          ? 'border-cyan-400 bg-cyan-400'
                          : 'border-slate-600 bg-transparent hover:border-slate-500'
                      )}
                    >
                      {giorno.pomeriggio.abilitata && (
                        <svg
                          className="w-3 h-3 text-slate-950"
                          viewBox="0 0 12 12"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          aria-hidden="true"
                        >
                          <polyline points="2,6 5,9 10,3" />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* ── Legenda ── */}
      <p className="text-xs text-slate-600 flex items-center gap-1.5 pt-1">
        <Clock className="w-3 h-3" aria-hidden="true" />
        Clicca sul giorno per aprire/chiudere. La spunta sul pomeriggio lo abilita.
      </p>

      {/* ── Salva ── */}
      {dirty && (
        <div className="flex justify-end pt-3 border-t border-slate-800">
          <Button
            onClick={handleSave}
            disabled={setOrariMutation.isPending}
            className="bg-cyan-500 hover:bg-cyan-600 text-white"
          >
            {setOrariMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" aria-hidden="true" />
            ) : (
              <Save className="w-4 h-4 mr-2" aria-hidden="true" />
            )}
            Salva Orari
          </Button>
        </div>
      )}
    </div>
  );
};
