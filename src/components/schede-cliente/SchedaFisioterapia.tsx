// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Fisioterapia Component
// Scheda cliente specifica per centri fisioterapia e riabilitazione
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { Slider } from '../ui/slider';
import { Progress } from '../ui/progress';
import { useSchedaFisioterapia, useSaveSchedaFisioterapia } from '../../hooks/use-schede-cliente';
import type { SchedaFisioterapia as SchedaFisioterapiaType, Seduta } from '../../types/scheda-cliente';
import { 
  Activity, 
  Calendar, 
  TrendingUp, 
  AlertCircle,
  Save,
  Plus,
  Trash2,
  CheckCircle2,
  Clock
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

interface SchedaFisioterapiaProps {
  clienteId: string;
}

const ZONE_CORPO = [
  'cervicale', 'spalla_dx', 'spalla_sx', 'gomito_dx', 'gomito_sx',
  'polso_dx', 'polso_sx', 'dorso', 'lombare', 'anca_dx', 'anca_sx',
  'ginocchio_dx', 'ginocchio_sx', 'caviglia_dx', 'caviglia_sx'
];

const SCALE_VALUTAZIONE = [
  { id: 'vas', label: 'VAS Dolore (0-10)', min: 0, max: 10 },
  { id: 'oswestry', label: 'Oswestry Disability Index', min: 0, max: 100 },
  { id: 'ndi', label: 'Neck Disability Index', min: 0, max: 50 },
  { id: 'sf36', label: 'SF-36 Physical', min: 0, max: 100 },
];

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Scala Valutazione
// ─────────────────────────────────────────────────────────────────────

interface ScalaValutazioneProps {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
  readOnly?: boolean;
}

function ScalaValutazione({ label, value, min, max, onChange, readOnly }: ScalaValutazioneProps) {
  return (
    <div className="space-y-2 bg-slate-900 p-4 rounded-lg">
      <div className="flex justify-between items-center">
        <Label className="text-slate-300">{label}</Label>
        <span className="text-cyan-400 font-bold text-lg">{value}</span>
      </div>
      {!readOnly && (
        <Slider
          value={[value]}
          min={min}
          max={max}
          step={1}
          onValueChange={(vals) => onChange(vals[0])}
          className="w-full"
        />
      )}
      <div className="flex justify-between text-xs text-slate-500">
        <span>{min}</span>
        <span>{max}</span>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Tabella Sedute
// ─────────────────────────────────────────────────────────────────────

interface TabellaSeduteProps {
  sedute: Seduta[];
  onChange: (sedute: Seduta[]) => void;
  readOnly?: boolean;
}

function TabellaSedute({ sedute, onChange, readOnly }: TabellaSeduteProps) {
  const [newSeduta, setNewSeduta] = useState<Partial<Seduta>>({
    data: new Date().toISOString().split('T')[0],
    trattamento: '',
    note: '',
    completata: false,
  });

  const addSeduta = () => {
    if (!newSeduta.trattamento) return;
    
    const seduta: Seduta = {
      id: crypto.randomUUID(),
      data: newSeduta.data || new Date().toISOString().split('T')[0],
      trattamento: newSeduta.trattamento,
      note: newSeduta.note,
      completata: newSeduta.completata || false,
    };
    
    onChange([...sedute, seduta]);
    setNewSeduta({
      data: new Date().toISOString().split('T')[0],
      trattamento: '',
      note: '',
      completata: false,
    });
  };

  const removeSeduta = (id: string) => {
    onChange(sedute.filter(s => s.id !== id));
  };

  const toggleCompletata = (id: string) => {
    onChange(sedute.map(s => 
      s.id === id ? { ...s, completata: !s.completata } : s
    ));
  };

  const completate = sedute.filter(s => s.completata).length;
  const percentuale = sedute.length > 0 ? (completate / sedute.length) * 100 : 0;

  return (
    <div className="space-y-4">
      {/* Progresso */}
      <div className="bg-slate-900 p-4 rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <span className="text-white font-medium">Progresso Trattamento</span>
          <span className="text-cyan-400">{completate} / {sedute.length} sedute</span>
        </div>
        <Progress value={percentuale} className="h-2" />
      </div>

      {!readOnly && (
        <div className="grid grid-cols-5 gap-2 bg-slate-800 p-4 rounded-lg">
          <Input
            type="date"
            value={newSeduta.data}
            onChange={(e) => setNewSeduta({ ...newSeduta, data: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Input
            placeholder="Trattamento"
            value={newSeduta.trattamento}
            onChange={(e) => setNewSeduta({ ...newSeduta, trattamento: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Input
            placeholder="Note"
            value={newSeduta.note || ''}
            onChange={(e) => setNewSeduta({ ...newSeduta, note: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white col-span-2"
          />
          <Button type="button" onClick={addSeduta} className="bg-cyan-600 hover:bg-cyan-700">
            <Plus className="w-4 h-4 mr-1" />
            Aggiungi
          </Button>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-800 text-slate-400">
            <tr>
              <th className="p-3 text-left">Data</th>
              <th className="p-3 text-left">Trattamento</th>
              <th className="p-3 text-left">Note</th>
              <th className="p-3 text-left">Stato</th>
              {!readOnly && <th className="p-3 text-left">Azioni</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {sedute.length === 0 ? (
              <tr>
                <td colSpan={readOnly ? 4 : 5} className="p-4 text-center text-slate-500">
                  Nessuna seduta registrata
                </td>
              </tr>
            ) : (
              sedute.map((s) => (
                <tr key={s.id} className={`bg-slate-800/50 ${s.completata ? 'opacity-60' : ''}`}>
                  <td className="p-3 text-white">{s.data}</td>
                  <td className="p-3">
                    <Badge variant={s.completata ? "default" : "secondary"}>
                      {s.trattamento}
                    </Badge>
                  </td>
                  <td className="p-3 text-slate-300">{s.note || '-'}</td>
                  <td className="p-3">
                    <button
                      type="button"
                      onClick={() => !readOnly && toggleCompletata(s.id)}
                      className={`flex items-center gap-1 ${s.completata ? 'text-green-400' : 'text-slate-400'}`}
                    >
                      {s.completata ? <CheckCircle2 className="w-4 h-4" /> : <Clock className="w-4 h-4" />}
                      {s.completata ? 'Completata' : 'Pianificata'}
                    </button>
                  </td>
                  {!readOnly && (
                    <td className="p-3">
                      <Button
                        type="button"
                        size="sm"
                        variant="destructive"
                        onClick={() => removeSeduta(s.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </td>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: SchedaFisioterapia Principale
// ─────────────────────────────────────────────────────────────────────

export function SchedaFisioterapia({ clienteId }: SchedaFisioterapiaProps) {
  const { data: scheda, isLoading } = useSchedaFisioterapia(clienteId);
  const saveScheda = useSaveSchedaFisioterapia();
  const [activeTab, setActiveTab] = useState('generale');

  const [formData, setFormData] = useState<Partial<SchedaFisioterapiaType>>({
    zona_principale: '',
    zone_secondarie: [],
    valutazione_iniziale: { vas_dolore: 5 },
    scale_valutazione: {},
    sedute_effettuate: [],
    numero_sedute_prescritte: 10,
    frequenza_settimanale: '2x',
  });

  if (scheda && !formData.id) {
    setFormData(scheda);
  }

  const handleSave = async () => {
    await saveScheda.mutateAsync({
      clienteId,
      data: formData as SchedaFisioterapiaType,
    });
  };

  if (isLoading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8 text-center text-slate-400">
          Caricamento scheda...
        </CardContent>
      </Card>
    );
  }

  const updateScalaValutazione = (id: string, value: number) => {
    setFormData({
      ...formData,
      scale_valutazione: {
        ...formData.scale_valutazione,
        [id]: value,
      },
    });
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-500/20 rounded-lg">
            <Activity className="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <CardTitle className="text-white">Scheda Fisioterapia</CardTitle>
            <p className="text-sm text-slate-400">Gestione terapie riabilitative</p>
          </div>
        </div>
        <Button 
          onClick={handleSave} 
          disabled={saveScheda.isPending}
          className="bg-cyan-600 hover:bg-cyan-700"
        >
          <Save className="w-4 h-4 mr-2" />
          {saveScheda.isPending ? 'Salvataggio...' : 'Salva'}
        </Button>
      </CardHeader>

      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-slate-900 mb-6">
            <TabsTrigger value="generale" className="data-[state=active]:bg-slate-700">
              <Activity className="w-4 h-4 mr-2" />
              Generale
            </TabsTrigger>
            <TabsTrigger value="zone" className="data-[state=active]:bg-slate-700">
              <AlertCircle className="w-4 h-4 mr-2" />
              Zone
            </TabsTrigger>
            <TabsTrigger value="valutazioni" className="data-[state=active]:bg-slate-700">
              <TrendingUp className="w-4 h-4 mr-2" />
              Valutazioni
            </TabsTrigger>
            <TabsTrigger value="sedute" className="data-[state=active]:bg-slate-700">
              <Calendar className="w-4 h-4 mr-2" />
              Sedute
            </TabsTrigger>
          </TabsList>

          {/* Generale */}
          <TabsContent value="generale" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Data Inizio Terapia</Label>
                <Input
                  type="date"
                  value={formData.data_inizio_terapia || ''}
                  onChange={(e) => setFormData({ ...formData, data_inizio_terapia: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Data Fine Prevista</Label>
                <Input
                  type="date"
                  value={formData.data_fine_terapia || ''}
                  onChange={(e) => setFormData({ ...formData, data_fine_terapia: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Motivo Primo Accesso</Label>
              <Textarea
                value={formData.motivo_primo_accesso || ''}
                onChange={(e) => setFormData({ ...formData, motivo_primo_accesso: e.target.value })}
                placeholder="Descrivi il motivo del primo accesso..."
                className="bg-slate-700 border-slate-600 text-white min-h-[80px]"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Diagnosi Medica</Label>
              <Textarea
                value={formData.diagnosi_medica || ''}
                onChange={(e) => setFormData({ ...formData, diagnosi_medica: e.target.value })}
                placeholder="Diagnosi del medico specialista..."
                className="bg-slate-700 border-slate-600 text-white min-h-[80px]"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Diagnosi Fisioterapica</Label>
              <Textarea
                value={formData.diagnosi_fisioterapica || ''}
                onChange={(e) => setFormData({ ...formData, diagnosi_fisioterapica: e.target.value })}
                placeholder="Valutazione fisioterapica..."
                className="bg-slate-700 border-slate-600 text-white min-h-[80px]"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Numero Sedute Prescritte</Label>
                <Input
                  type="number"
                  value={formData.numero_sedute_prescritte || ''}
                  onChange={(e) => setFormData({ ...formData, numero_sedute_prescritte: parseInt(e.target.value) })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Frequenza Settimanale</Label>
                <select
                  value={formData.frequenza_settimanale || ''}
                  onChange={(e) => setFormData({ ...formData, frequenza_settimanale: e.target.value })}
                  className="w-full bg-slate-700 border-slate-600 text-white rounded-md p-2"
                >
                  <option value="">Seleziona...</option>
                  <option value="1x">1x a settimana</option>
                  <option value="2x">2x a settimana</option>
                  <option value="3x">3x a settimana</option>
                  <option value="4x">4x a settimana</option>
                  <option value="5x">5x a settimana</option>
                </select>
              </div>
            </div>
          </TabsContent>

          {/* Zone */}
          <TabsContent value="zone" className="space-y-4">
            <div className="space-y-2">
              <Label className="text-slate-300">Zona Principale</Label>
              <select
                value={formData.zona_principale || ''}
                onChange={(e) => setFormData({ ...formData, zona_principale: e.target.value })}
                className="w-full bg-slate-700 border-slate-600 text-white rounded-md p-2"
              >
                <option value="">Seleziona zona...</option>
                {ZONE_CORPO.map(z => (
                  <option key={z} value={z}>{z.replace('_', ' ').toUpperCase()}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Zone Secondarie</Label>
              <div className="grid grid-cols-3 gap-2">
                {ZONE_CORPO.map(zona => (
                  <label key={zona} className="flex items-center gap-2 p-2 bg-slate-700 rounded cursor-pointer hover:bg-slate-600">
                    <input
                      type="checkbox"
                      checked={formData.zone_secondarie?.includes(zona) || false}
                      onChange={(e) => {
                        const current = formData.zone_secondarie || [];
                        if (e.target.checked) {
                          setFormData({ ...formData, zone_secondarie: [...current, zona] });
                        } else {
                          setFormData({ ...formData, zone_secondarie: current.filter(z => z !== zona) });
                        }
                      }}
                      className="rounded border-slate-500"
                    />
                    <span className="text-sm text-slate-300 capitalize">{zona.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Controindicazioni</Label>
              <Textarea
                value={formData.controindicazioni || ''}
                onChange={(e) => setFormData({ ...formData, controindicazioni: e.target.value })}
                placeholder="Eventuali controindicazioni..."
                className="bg-slate-700 border-slate-600 text-white min-h-[100px]"
              />
            </div>
          </TabsContent>

          {/* Valutazioni */}
          <TabsContent value="valutazioni" className="space-y-4">
            <div className="space-y-4">
              <ScalaValutazione
                label="VAS Dolore (0 = nessun dolore, 10 = dolore massimo)"
                value={formData.valutazione_iniziale?.vas_dolore || 0}
                min={0}
                max={10}
                onChange={(v) => setFormData({
                  ...formData,
                  valutazione_iniziale: { ...formData.valutazione_iniziale, vas_dolore: v }
                })}
              />

              {SCALE_VALUTAZIONE.slice(1).map(scala => (
                <ScalaValutazione
                  key={scala.id}
                  label={scala.label}
                  value={formData.scale_valutazione?.[scala.id] || 0}
                  min={scala.min}
                  max={scala.max}
                  onChange={(v) => updateScalaValutazione(scala.id, v)}
                />
              ))}
            </div>

            <div className="space-y-2 pt-4">
              <Label className="text-slate-300">Esito Trattamento</Label>
              <select
                value={formData.esito_trattamento || ''}
                onChange={(e) => setFormData({ ...formData, esito_trattamento: e.target.value })}
                className="w-full bg-slate-700 border-slate-600 text-white rounded-md p-2"
              >
                <option value="">Seleziona...</option>
                <option value="in_corso">In Corso</option>
                <option value="miglioramento">Miglioramento</option>
                <option value="stabile">Stabile</option>
                <option value="peggioramento">Peggioramento</option>
              </select>
            </div>
          </TabsContent>

          {/* Sedute */}
          <TabsContent value="sedute" className="space-y-4">
            <TabellaSedute
              sedute={formData.sedute_effettuate || []}
              onChange={(sedute) => setFormData({ ...formData, sedute_effettuate: sedute })}
            />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
