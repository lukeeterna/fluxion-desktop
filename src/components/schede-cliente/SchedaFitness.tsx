// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Fitness
// Palestre, personal trainer, yoga, crossfit, piscine
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { Badge } from '../ui/badge';
import {
  Dumbbell,
  Activity,
  Heart,
  ClipboardList,
  TrendingUp,
  Plus,
  Trash2,
  Save,
  Loader2,
  Camera,
} from 'lucide-react';
import { toast } from 'sonner';
import { useSchedaFitness, useSaveSchedaFitness } from '../../hooks/use-schede-cliente';
import type { SchedaFitness as SchedaFitnessType, GiornoAllenamento, Misurazione } from '../../types/scheda-cliente';
import { ProgressTimeline } from '../media/ProgressTimeline';

// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────

const OBIETTIVI = [
  { value: 'dimagrimento', label: 'Dimagrimento' },
  { value: 'tonificazione', label: 'Tonificazione' },
  { value: 'massa', label: 'Massa muscolare' },
  { value: 'resistenza', label: 'Resistenza' },
  { value: 'salute', label: 'Salute generale' },
  { value: 'altro', label: 'Altro' },
];

const LIVELLI = [
  { value: 'principiante', label: 'Principiante' },
  { value: 'intermedio', label: 'Intermedio' },
  { value: 'avanzato', label: 'Avanzato' },
];

const FREQUENZE = [
  { value: '1x_settimana', label: '1x settimana' },
  { value: '2x_settimana', label: '2x settimana' },
  { value: '3x_settimana', label: '3x settimana' },
  { value: '4x_settimana', label: '4x settimana' },
  { value: '5x_settimana', label: '5x settimana' },
  { value: 'quotidiano', label: 'Quotidiano' },
];

const GIORNI_SETTIMANA = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica'];

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Tab Scheda Allenamento
// ─────────────────────────────────────────────────────────────────────

function TabSchedaAllenamento({
  giorni,
  onChange,
}: {
  giorni: GiornoAllenamento[];
  onChange: (giorni: GiornoAllenamento[]) => void;
}) {
  const addGiorno = () => {
    onChange([...giorni, { giorno: `Giorno ${giorni.length + 1}`, esercizi: [] }]);
  };

  const removeGiorno = (idx: number) => {
    onChange(giorni.filter((_, i) => i !== idx));
  };

  const updateGiorno = (idx: number, field: keyof GiornoAllenamento, value: string | string[]) => {
    const updated = giorni.map((g, i) =>
      i === idx ? { ...g, [field]: value } : g
    );
    onChange(updated);
  };

  const addEsercizio = (idx: number) => {
    const updated = giorni.map((g, i) =>
      i === idx ? { ...g, esercizi: [...g.esercizi, ''] } : g
    );
    onChange(updated);
  };

  const updateEsercizio = (giornoIdx: number, esercizioIdx: number, val: string) => {
    const updated = giorni.map((g, i) => {
      if (i !== giornoIdx) return g;
      const esercizi = g.esercizi.map((e, j) => (j === esercizioIdx ? val : e));
      return { ...g, esercizi };
    });
    onChange(updated);
  };

  const removeEsercizio = (giornoIdx: number, esercizioIdx: number) => {
    const updated = giorni.map((g, i) => {
      if (i !== giornoIdx) return g;
      return { ...g, esercizi: g.esercizi.filter((_, j) => j !== esercizioIdx) };
    });
    onChange(updated);
  };

  return (
    <div className="space-y-4">
      {giorni.map((giorno, idx) => (
        <div key={idx} className="bg-slate-900 rounded-lg p-4 border border-slate-700">
          <div className="flex items-center gap-2 mb-3">
            <Select
              value={GIORNI_SETTIMANA.includes(giorno.giorno) ? giorno.giorno : ''}
              onValueChange={(v) => updateGiorno(idx, 'giorno', v)}
            >
              <SelectTrigger className="bg-slate-800 border-slate-600 text-white w-40">
                <SelectValue placeholder="Giorno" />
              </SelectTrigger>
              <SelectContent>
                {GIORNI_SETTIMANA.map((g) => (
                  <SelectItem key={g} value={g}>{g}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              value={GIORNI_SETTIMANA.includes(giorno.giorno) ? '' : giorno.giorno}
              onChange={(e) => updateGiorno(idx, 'giorno', e.target.value)}
              placeholder="o descrizione libera"
              className="bg-slate-800 border-slate-600 text-white flex-1"
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => removeGiorno(idx)}
              className="text-red-400 hover:text-red-300 hover:bg-red-400/10"
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
          <div className="space-y-2 ml-2">
            {giorno.esercizi.map((es, ei) => (
              <div key={ei} className="flex gap-2">
                <Input
                  value={es}
                  onChange={(e) => updateEsercizio(idx, ei, e.target.value)}
                  placeholder="es. Squat 3×10 a 80kg"
                  className="bg-slate-700 border-slate-600 text-white text-sm"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeEsercizio(idx, ei)}
                  className="text-slate-500 hover:text-red-400 flex-shrink-0"
                >
                  <Trash2 className="w-3 h-3" />
                </Button>
              </div>
            ))}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => addEsercizio(idx)}
              className="text-cyan-400 hover:text-cyan-300 text-xs"
            >
              <Plus className="w-3 h-3 mr-1" />
              Aggiungi esercizio
            </Button>
          </div>
        </div>
      ))}
      <Button
        variant="outline"
        size="sm"
        onClick={addGiorno}
        className="border-dashed border-slate-600 text-slate-400 hover:text-white hover:border-slate-400"
      >
        <Plus className="w-4 h-4 mr-2" />
        Aggiungi giorno
      </Button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Tab Storico Misurazioni
// ─────────────────────────────────────────────────────────────────────

function TabStorico({
  storico,
  onChange,
}: {
  storico: Misurazione[];
  onChange: (s: Misurazione[]) => void;
}) {
  const addMisurazione = () => {
    const nuova: Misurazione = {
      id: `m-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      data: new Date().toISOString().split('T')[0],
    };
    onChange([nuova, ...storico]);
  };

  const updateMisurazione = (id: string, field: keyof Misurazione, value: string | number) => {
    onChange(storico.map((m) => (m.id === id ? { ...m, [field]: value } : m)));
  };

  const removeMisurazione = (id: string) => {
    onChange(storico.filter((m) => m.id !== id));
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-slate-400 text-sm">{storico.length} misurazioni registrate</p>
        <Button
          size="sm"
          onClick={addMisurazione}
          className="bg-cyan-600 hover:bg-cyan-700 text-white"
        >
          <Plus className="w-4 h-4 mr-1" />
          Nuova misurazione
        </Button>
      </div>

      {storico.length === 0 ? (
        <div className="text-center py-8 text-slate-500">
          <TrendingUp className="w-10 h-10 mx-auto mb-2 opacity-30" />
          <p className="text-sm">Nessuna misurazione registrata</p>
        </div>
      ) : (
        <div className="space-y-3">
          {storico.map((m) => (
            <div key={m.id} className="bg-slate-900 p-4 rounded-lg border border-slate-700">
              <div className="flex items-center justify-between mb-3">
                <Input
                  type="date"
                  value={m.data}
                  onChange={(e) => updateMisurazione(m.id, 'data', e.target.value)}
                  className="bg-slate-800 border-slate-600 text-white w-40"
                />
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeMisurazione(m.id)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <Label className="text-slate-400 text-xs">Peso (kg)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={m.peso ?? ''}
                    onChange={(e) => updateMisurazione(m.id, 'peso', parseFloat(e.target.value) || 0)}
                    className="bg-slate-800 border-slate-600 text-white mt-1"
                  />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs">Grasso (%)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={m.grasso ?? ''}
                    onChange={(e) => updateMisurazione(m.id, 'grasso', parseFloat(e.target.value) || 0)}
                    className="bg-slate-800 border-slate-600 text-white mt-1"
                  />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs">Note</Label>
                  <Input
                    value={m.note ?? ''}
                    onChange={(e) => updateMisurazione(m.id, 'note', e.target.value)}
                    placeholder="es. post gara"
                    className="bg-slate-800 border-slate-600 text-white mt-1"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: SchedaFitness
// ═══════════════════════════════════════════════════════════════════

export function SchedaFitness({ clienteId }: { clienteId: string }) {
  const { data: scheda, isLoading } = useSchedaFitness(clienteId);
  const saveScheda = useSaveSchedaFitness();

  const [formData, setFormData] = useState<Partial<SchedaFitnessType>>({
    cardiopatico: false,
    iperteso: false,
    diabetico: false,
    scheda_allenamento: [],
    storico_misurazioni: [],
  });

  // Carica dati dal DB al primo fetch
  if (scheda && !formData.id) {
    setFormData(scheda);
  }

  const update = <K extends keyof SchedaFitnessType>(field: K, value: SchedaFitnessType[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    try {
      await saveScheda.mutateAsync({
        clienteId,
        data: { ...formData, cliente_id: clienteId } as SchedaFitnessType,
      });
      toast.success('Scheda fitness salvata');
    } catch (err) {
      toast.error('Errore salvataggio', { description: String(err) });
    }
  };

  if (isLoading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8 text-center text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
          Caricamento scheda fitness...
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-green-500/20 rounded-lg">
            <Dumbbell className="w-6 h-6 text-green-500" />
          </div>
          <div>
            <CardTitle className="text-white">Scheda Fitness</CardTitle>
            <p className="text-sm text-slate-400">Obiettivi, allenamento e misurazioni</p>
          </div>
        </div>
        <Button
          onClick={handleSave}
          disabled={saveScheda.isPending}
          className="bg-green-600 hover:bg-green-700 text-white"
        >
          {saveScheda.isPending ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Save className="w-4 h-4 mr-2" />
          )}
          Salva
        </Button>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="profilo">
          <div className="overflow-x-auto scrollbar-none mb-4">
            <TabsList className="bg-slate-900 border border-slate-700 h-auto p-1 flex w-max min-w-full gap-0.5">
              <TabsTrigger value="profilo" className="flex items-center gap-1.5 px-3 py-2 text-xs whitespace-nowrap rounded-md text-slate-400 data-[state=active]:bg-green-700 data-[state=active]:text-white hover:text-slate-200 transition-colors">
                <Activity className="w-3.5 h-3.5 shrink-0" />Profilo
              </TabsTrigger>
              <TabsTrigger value="misurazioni" className="flex items-center gap-1.5 px-3 py-2 text-xs whitespace-nowrap rounded-md text-slate-400 data-[state=active]:bg-green-700 data-[state=active]:text-white hover:text-slate-200 transition-colors">
                <TrendingUp className="w-3.5 h-3.5 shrink-0" />Misurazioni
              </TabsTrigger>
              <TabsTrigger value="allenamento" className="flex items-center gap-1.5 px-3 py-2 text-xs whitespace-nowrap rounded-md text-slate-400 data-[state=active]:bg-green-700 data-[state=active]:text-white hover:text-slate-200 transition-colors">
                <ClipboardList className="w-3.5 h-3.5 shrink-0" />Scheda
              </TabsTrigger>
              <TabsTrigger value="salute" className="flex items-center gap-1.5 px-3 py-2 text-xs whitespace-nowrap rounded-md text-slate-400 data-[state=active]:bg-green-700 data-[state=active]:text-white hover:text-slate-200 transition-colors">
                <Heart className="w-3.5 h-3.5 shrink-0" />Salute
              </TabsTrigger>
              <TabsTrigger value="progress" className="flex items-center gap-1.5 px-3 py-2 text-xs whitespace-nowrap rounded-md text-slate-400 data-[state=active]:bg-green-700 data-[state=active]:text-white hover:text-slate-200 transition-colors">
                <Camera className="w-3.5 h-3.5 shrink-0" />Progress
              </TabsTrigger>
            </TabsList>
          </div>

          {/* ── TAB: PROFILO ── */}
          <TabsContent value="profilo" className="space-y-5">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label className="text-slate-400 mb-1 block">Obiettivo</Label>
                <Select
                  value={formData.obiettivo ?? ''}
                  onValueChange={(v) => update('obiettivo', v as SchedaFitnessType['obiettivo'])}
                >
                  <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                    <SelectValue placeholder="Seleziona..." />
                  </SelectTrigger>
                  <SelectContent>
                    {OBIETTIVI.map((o) => (
                      <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-slate-400 mb-1 block">Livello</Label>
                <Select
                  value={formData.livello ?? ''}
                  onValueChange={(v) => update('livello', v as SchedaFitnessType['livello'])}
                >
                  <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                    <SelectValue placeholder="Seleziona..." />
                  </SelectTrigger>
                  <SelectContent>
                    {LIVELLI.map((l) => (
                      <SelectItem key={l.value} value={l.value}>{l.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-slate-400 mb-1 block">Frequenza</Label>
                <Select
                  value={formData.frequenza_allenamento ?? ''}
                  onValueChange={(v) => update('frequenza_allenamento', v as SchedaFitnessType['frequenza_allenamento'])}
                >
                  <SelectTrigger className="bg-slate-900 border-slate-600 text-white">
                    <SelectValue placeholder="Seleziona..." />
                  </SelectTrigger>
                  <SelectContent>
                    {FREQUENZE.map((f) => (
                      <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Riepilogo badges */}
            {(formData.obiettivo || formData.livello || formData.frequenza_allenamento) && (
              <div className="flex gap-2 flex-wrap">
                {formData.obiettivo && (
                  <Badge className="bg-green-500/20 text-green-300 border-green-500/30">
                    {OBIETTIVI.find((o) => o.value === formData.obiettivo)?.label}
                  </Badge>
                )}
                {formData.livello && (
                  <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30">
                    {LIVELLI.find((l) => l.value === formData.livello)?.label}
                  </Badge>
                )}
                {formData.frequenza_allenamento && (
                  <Badge className="bg-purple-500/20 text-purple-300 border-purple-500/30">
                    {FREQUENZE.find((f) => f.value === formData.frequenza_allenamento)?.label}
                  </Badge>
                )}
              </div>
            )}
          </TabsContent>

          {/* ── TAB: MISURAZIONI ── */}
          <TabsContent value="misurazioni" className="space-y-5">
            {/* Misurazioni attuali */}
            <div className="bg-slate-900 rounded-lg p-4">
              <h3 className="text-white font-medium mb-3">Misurazioni attuali</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-400 text-sm mb-1 block">Peso (kg)</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={formData.peso_kg ?? ''}
                    onChange={(e) => update('peso_kg', parseFloat(e.target.value) || undefined)}
                    placeholder="es. 75.5"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-400 text-sm mb-1 block">Altezza (cm)</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={formData.altezza_cm ?? ''}
                    onChange={(e) => update('altezza_cm', parseFloat(e.target.value) || undefined)}
                    placeholder="es. 175"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-400 text-sm mb-1 block">% Grasso corporeo</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={formData.percentuale_grasso ?? ''}
                    onChange={(e) => update('percentuale_grasso', parseFloat(e.target.value) || undefined)}
                    placeholder="es. 18.5"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-400 text-sm mb-1 block">Circonferenza vita (cm)</Label>
                  <Input
                    type="number"
                    step="0.5"
                    value={formData.circonferenza_vita ?? ''}
                    onChange={(e) => update('circonferenza_vita', parseFloat(e.target.value) || undefined)}
                    placeholder="es. 82"
                    className="bg-slate-800 border-slate-600 text-white"
                  />
                </div>
              </div>
              {formData.peso_kg && formData.altezza_cm && (
                <div className="mt-3 p-3 bg-slate-800 rounded-lg">
                  <p className="text-slate-400 text-sm">
                    BMI:{' '}
                    <span className="text-white font-semibold">
                      {(formData.peso_kg / Math.pow(formData.altezza_cm / 100, 2)).toFixed(1)}
                    </span>
                  </p>
                </div>
              )}
            </div>

            {/* Storico */}
            <div>
              <h3 className="text-white font-medium mb-3">Storico misurazioni</h3>
              <TabStorico
                storico={formData.storico_misurazioni ?? []}
                onChange={(s) => update('storico_misurazioni', s)}
              />
            </div>
          </TabsContent>

          {/* ── TAB: SCHEDA ALLENAMENTO ── */}
          <TabsContent value="allenamento" className="space-y-4">
            <TabSchedaAllenamento
              giorni={formData.scheda_allenamento ?? []}
              onChange={(g) => update('scheda_allenamento', g)}
            />
          </TabsContent>

          {/* ── TAB: PROGRESS PHOTOS ── */}
          <TabsContent value="progress" className="space-y-4">
            <div className="p-4 bg-slate-900 rounded-lg">
              <h3 className="text-white font-medium mb-1 flex items-center gap-2">
                <Camera className="w-4 h-4 text-cyan-400" />
                Foto Progress
              </h3>
              <p className="text-xs text-slate-500 mb-4">
                Timeline cronologica delle trasformazioni. Le metriche vengono associate automaticamente se presenti nella scheda.
              </p>
              <ProgressTimeline clienteId={parseInt(clienteId, 10)} />
            </div>
          </TabsContent>

          {/* ── TAB: SALUTE ── */}
          <TabsContent value="salute" className="space-y-5">
            <div className="bg-slate-900 rounded-lg p-4">
              <h3 className="text-white font-medium mb-3">Condizioni mediche</h3>
              <div className="flex gap-4 flex-wrap">
                {(['cardiopatico', 'iperteso', 'diabetico'] as const).map((field) => {
                  const labels = { cardiopatico: 'Cardiopatico', iperteso: 'Iperteso', diabetico: 'Diabetico' };
                  return (
                    <button
                      key={field}
                      onClick={() => update(field, !formData[field])}
                      className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                        formData[field]
                          ? 'bg-red-500/20 border-red-500/50 text-red-300'
                          : 'bg-slate-800 border-slate-600 text-slate-400 hover:border-slate-500'
                      }`}
                    >
                      {labels[field]}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4">
              <div>
                <Label className="text-slate-400 mb-1 block">Note mediche</Label>
                <Textarea
                  value={formData.note_mediche ?? ''}
                  onChange={(e) => update('note_mediche', e.target.value)}
                  placeholder="Patologie, terapie farmacologiche, certificati medici..."
                  rows={3}
                  className="bg-slate-900 border-slate-600 text-white resize-none"
                />
              </div>
              <div>
                <Label className="text-slate-400 mb-1 block">Limitazioni fisiche</Label>
                <Textarea
                  value={formData.limitazioni_fisiche ?? ''}
                  onChange={(e) => update('limitazioni_fisiche', e.target.value)}
                  placeholder="Infortuni, disfunzioni posturali, movimenti da evitare..."
                  rows={3}
                  className="bg-slate-900 border-slate-600 text-white resize-none"
                />
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
