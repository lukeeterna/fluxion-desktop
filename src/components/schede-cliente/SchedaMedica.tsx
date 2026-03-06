// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Medica Component (W2-E)
// Scheda cliente per medici generici, specialisti, psicologi, nutrizionisti
// NOTE: Rust commands (get_scheda_medica, upsert_scheda_medica) TODO su iMac
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { Textarea } from '../ui/textarea';
import { useSchedaMedica, useSaveSchedaMedica } from '../../hooks/use-schede-cliente';
import type { SchedaMedica as SchedaMedicaType, VisitaMedica, Farmaco } from '../../types/scheda-cliente';
import { toast } from 'sonner';
import {
  Stethoscope,
  AlertTriangle,
  Pill,
  ClipboardList,
  FileText,
  Save,
  Plus,
  Trash2,
  Heart,
  Camera,
} from 'lucide-react';
import { MediaUploadZone } from '../media/MediaUploadZone';
import { MediaGallery } from '../media/MediaGallery';
import { MediaConsentModal } from '../media/MediaConsentModal';

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

const GRUPPI_SANGUIGNI = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-'] as const;

const PATOLOGIE_COMUNI = [
  'Diabete tipo 1',
  'Diabete tipo 2',
  'Ipertensione',
  'Ipotiroidismo',
  'Ipertiroidismo',
  'Asma',
  'BPCO',
  'Aritmia',
  'Fibrillazione atriale',
  'Cardiopatia',
  'Depressione',
  'Ansia',
  'Artrite',
  'Artrosi',
  'Osteoporosi',
  'Celiachia',
  'Crohn',
  'Colite ulcerosa',
];

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Tag list editable
// ─────────────────────────────────────────────────────────────────────

function TagList({
  tags,
  onChange,
  placeholder,
  suggestions,
}: {
  tags: string[];
  onChange: (tags: string[]) => void;
  placeholder: string;
  suggestions?: string[];
}) {
  const [input, setInput] = useState('');
  const [showSugg, setShowSugg] = useState(false);

  const add = (value: string) => {
    const v = value.trim();
    if (!v || tags.includes(v)) return;
    onChange([...tags, v]);
    setInput('');
    setShowSugg(false);
  };

  const filtered = suggestions?.filter((s) => s.toLowerCase().includes(input.toLowerCase()) && !tags.includes(s)) ?? [];

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1.5">
        {tags.map((t) => (
          <Badge key={t} variant="outline" className="border-slate-600 text-slate-300 gap-1 text-xs">
            {t}
            <button onClick={() => onChange(tags.filter((x) => x !== t))}>
              <Trash2 className="w-2.5 h-2.5 text-slate-500 hover:text-red-400" />
            </button>
          </Badge>
        ))}
      </div>
      <div className="relative">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => { setInput(e.target.value); setShowSugg(true); }}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); add(input); } }}
            placeholder={placeholder}
            className="bg-slate-900 border-slate-700 text-white text-sm h-8"
            onFocus={() => setShowSugg(true)}
            onBlur={() => setTimeout(() => setShowSugg(false), 150)}
          />
          <Button size="sm" variant="ghost" className="h-8 text-slate-400 hover:text-white" onClick={() => add(input)}>
            <Plus className="w-3 h-3" />
          </Button>
        </div>
        {showSugg && filtered.length > 0 && (
          <div className="absolute z-10 top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-700 rounded-lg shadow-xl max-h-40 overflow-y-auto">
            {filtered.slice(0, 8).map((s) => (
              <button
                key={s}
                className="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-slate-800"
                onClick={() => add(s)}
              >
                {s}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Farmaci
// ─────────────────────────────────────────────────────────────────────

function FarmaciList({
  farmaci,
  onChange,
}: {
  farmaci: Farmaco[];
  onChange: (list: Farmaco[]) => void;
}) {
  const [showForm, setShowForm] = useState(false);
  const [newFarmaco, setNewFarmaco] = useState<Farmaco>({ nome: '', dosaggio: '', frequenza: '', dal: '' });

  const add = () => {
    if (!newFarmaco.nome.trim()) return;
    onChange([...farmaci, newFarmaco]);
    setNewFarmaco({ nome: '', dosaggio: '', frequenza: '', dal: '' });
    setShowForm(false);
  };

  return (
    <div className="space-y-2">
      {farmaci.map((f, i) => (
        <div key={i} className="flex items-center justify-between bg-slate-900 rounded-lg p-2.5 border border-slate-700">
          <div>
            <p className="text-white text-sm font-medium">{f.nome}</p>
            <p className="text-slate-500 text-xs">
              {[f.dosaggio, f.frequenza, f.dal ? `dal ${f.dal}` : ''].filter(Boolean).join(' · ')}
            </p>
          </div>
          <Button size="sm" variant="ghost" className="text-slate-600 hover:text-red-400 h-7 w-7 p-0"
            onClick={() => onChange(farmaci.filter((_, j) => j !== i))}>
            <Trash2 className="w-3 h-3" />
          </Button>
        </div>
      ))}

      {showForm ? (
        <div className="bg-slate-900 p-3 rounded-lg border border-slate-700 space-y-2">
          <Input placeholder="Nome farmaco *" value={newFarmaco.nome}
            onChange={(e) => setNewFarmaco((p) => ({ ...p, nome: e.target.value }))}
            className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
          <div className="grid grid-cols-3 gap-2">
            <Input placeholder="Dosaggio" value={newFarmaco.dosaggio ?? ''}
              onChange={(e) => setNewFarmaco((p) => ({ ...p, dosaggio: e.target.value }))}
              className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
            <Input placeholder="Frequenza" value={newFarmaco.frequenza ?? ''}
              onChange={(e) => setNewFarmaco((p) => ({ ...p, frequenza: e.target.value }))}
              className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
            <Input type="date" value={newFarmaco.dal ?? ''}
              onChange={(e) => setNewFarmaco((p) => ({ ...p, dal: e.target.value }))}
              className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
          </div>
          <div className="flex gap-2 justify-end">
            <Button size="sm" variant="ghost" className="text-slate-400 h-7 text-xs" onClick={() => setShowForm(false)}>Annulla</Button>
            <Button size="sm" className="bg-red-700 hover:bg-red-600 text-white h-7 text-xs" onClick={add}>Aggiungi</Button>
          </div>
        </div>
      ) : (
        <Button size="sm" variant="outline" className="border-slate-600 text-slate-400 hover:text-white hover:bg-slate-700 w-full text-xs"
          onClick={() => setShowForm(true)}>
          <Plus className="w-3 h-3 mr-1" /> Aggiungi farmaco
        </Button>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Visite
// ─────────────────────────────────────────────────────────────────────

function VisiteList({
  visite,
  onChange,
}: {
  visite: VisitaMedica[];
  onChange: (list: VisitaMedica[]) => void;
}) {
  const [showForm, setShowForm] = useState(false);
  const [newVisita, setNewVisita] = useState<Omit<VisitaMedica, 'id'>>({
    data: new Date().toISOString().split('T')[0],
    diagnosi: '',
    terapia: '',
    note: '',
    prossima_visita: '',
  });

  const add = () => {
    if (!newVisita.diagnosi.trim()) return;
    onChange([...visite, { id: Date.now().toString(), ...newVisita }]);
    setNewVisita({ data: new Date().toISOString().split('T')[0], diagnosi: '', terapia: '', note: '', prossima_visita: '' });
    setShowForm(false);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-white font-medium text-sm">Storico Visite</h4>
        <Button size="sm" variant="outline" className="border-slate-600 text-slate-300 hover:text-white hover:bg-slate-700"
          onClick={() => setShowForm(!showForm)}>
          <Plus className="w-3 h-3 mr-1" />Aggiungi
        </Button>
      </div>

      {showForm && (
        <div className="bg-slate-900 p-3 rounded-lg border border-slate-700 space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label className="text-slate-400 text-xs">Data</Label>
              <Input type="date" value={newVisita.data}
                onChange={(e) => setNewVisita((p) => ({ ...p, data: e.target.value }))}
                className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
            </div>
            <div>
              <Label className="text-slate-400 text-xs">Prossima visita</Label>
              <Input type="date" value={newVisita.prossima_visita ?? ''}
                onChange={(e) => setNewVisita((p) => ({ ...p, prossima_visita: e.target.value }))}
                className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
            </div>
          </div>
          <div>
            <Label className="text-slate-400 text-xs">Diagnosi *</Label>
            <Input value={newVisita.diagnosi}
              onChange={(e) => setNewVisita((p) => ({ ...p, diagnosi: e.target.value }))}
              placeholder="es. Lombalgia acuta, Cefalea tensiva..."
              className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
          </div>
          <div>
            <Label className="text-slate-400 text-xs">Terapia prescritta</Label>
            <Input value={newVisita.terapia ?? ''}
              onChange={(e) => setNewVisita((p) => ({ ...p, terapia: e.target.value }))}
              placeholder="es. Fans + riposo 3gg, Fisioterapia..."
              className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
          </div>
          <div>
            <Label className="text-slate-400 text-xs">Note</Label>
            <Input value={newVisita.note ?? ''}
              onChange={(e) => setNewVisita((p) => ({ ...p, note: e.target.value }))}
              placeholder="Note aggiuntive..."
              className="bg-slate-800 border-slate-700 text-white text-sm h-8" />
          </div>
          <div className="flex gap-2 justify-end">
            <Button size="sm" variant="ghost" className="text-slate-400 h-7 text-xs" onClick={() => setShowForm(false)}>Annulla</Button>
            <Button size="sm" className="bg-red-700 hover:bg-red-600 text-white h-7 text-xs" onClick={add}>Salva visita</Button>
          </div>
        </div>
      )}

      {visite.length === 0 && !showForm && (
        <p className="text-slate-500 text-sm text-center py-4">Nessuna visita registrata</p>
      )}

      {[...visite].sort((a, b) => b.data.localeCompare(a.data)).map((v) => (
        <div key={v.id} className="bg-slate-900 rounded-lg p-3 border border-slate-700">
          <div className="flex items-start justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="text-slate-400 text-xs">{v.data}</span>
              {v.prossima_visita && (
                <span className="text-teal-400 text-xs">→ {v.prossima_visita}</span>
              )}
            </div>
            <Button size="sm" variant="ghost" className="text-slate-600 hover:text-red-400 h-6 w-6 p-0"
              onClick={() => onChange(visite.filter((x) => x.id !== v.id))}>
              <Trash2 className="w-3 h-3" />
            </Button>
          </div>
          <p className="text-white text-sm font-medium">{v.diagnosi}</p>
          {v.terapia && <p className="text-slate-400 text-xs mt-0.5">Terapia: {v.terapia}</p>}
          {v.note && <p className="text-slate-500 text-xs mt-0.5 italic">{v.note}</p>}
        </div>
      ))}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// MAIN COMPONENT: SchedaMedica
// ─────────────────────────────────────────────────────────────────────

export function SchedaMedica({ clienteId }: { clienteId: string }) {
  const { data: scheda, isLoading } = useSchedaMedica(clienteId);
  const save = useSaveSchedaMedica();

  const emptyScheda: SchedaMedicaType = {
    cliente_id: clienteId,
    allergie_farmaci: [],
    allergie_alimenti: [],
    allergie_altro: [],
    patologie_croniche: [],
    patologie_pregresse: [],
    interventi_chirurgici: [],
    farmaci_attuali: [],
    fumatore: false,
    ex_fumatore: false,
    familiari_cardiopatie: false,
    familiari_diabete: false,
    familiari_tumori: false,
    gravidanza: false,
    allattamento: false,
    menopausa: false,
    visite: [],
    esami: [],
  };

  const [form, setForm] = useState<SchedaMedicaType>(scheda ?? emptyScheda);
  const [initialized, setInitialized] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [mediaConsentGranted, setMediaConsentGranted] = useState(false);
  const clienteIdNum = parseInt(clienteId, 10);

  if (!initialized && scheda) {
    setForm(scheda);
    setInitialized(true);
  }

  const update = <K extends keyof SchedaMedicaType>(key: K, value: SchedaMedicaType[K]) => {
    setForm((p) => ({ ...p, [key]: value }));
  };

  const handleSave = async () => {
    try {
      await save.mutateAsync({ clienteId, data: form });
      toast.success('Scheda medica salvata');
    } catch {
      toast.error('Errore nel salvataggio — backend non ancora disponibile');
    }
  };

  if (isLoading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8 text-center text-slate-400">Caricamento...</CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-red-500/20 rounded-lg">
          <Stethoscope className="w-6 h-6 text-red-500" />
        </div>
        <div>
          <CardTitle className="text-white">Scheda Medica</CardTitle>
          <p className="text-sm text-slate-400">Anamnesi, patologie, farmaci e storico visite</p>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="anamnesi" className="w-full">
          <TabsList className="bg-slate-900 border border-slate-700 w-full grid grid-cols-6">
            <TabsTrigger value="anamnesi" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
              <Heart className="w-3 h-3 mr-1" />Anamnesi
            </TabsTrigger>
            <TabsTrigger value="allergie" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
              <AlertTriangle className="w-3 h-3 mr-1" />Allergie
            </TabsTrigger>
            <TabsTrigger value="farmaci" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
              <Pill className="w-3 h-3 mr-1" />Farmaci
            </TabsTrigger>
            <TabsTrigger value="visite" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
              <ClipboardList className="w-3 h-3 mr-1" />Visite
            </TabsTrigger>
            <TabsTrigger value="note" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
              <FileText className="w-3 h-3 mr-1" />Note
            </TabsTrigger>
            <TabsTrigger value="immagini" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
              <Camera className="w-3 h-3 mr-1" />Immagini
            </TabsTrigger>
          </TabsList>

          {/* TAB: Anamnesi */}
          <TabsContent value="anamnesi" className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Motivo accesso</Label>
                <Input value={form.motivo_accesso ?? ''} onChange={(e) => update('motivo_accesso', e.target.value)}
                  placeholder="es. Dolore lombare, controllo periodico..."
                  className="bg-slate-900 border-slate-700 text-white" />
              </div>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Medico curante</Label>
                <Input value={form.medico_curante ?? ''} onChange={(e) => update('medico_curante', e.target.value)}
                  placeholder="es. Dr. Mario Rossi"
                  className="bg-slate-900 border-slate-700 text-white" />
              </div>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Prima visita</Label>
                <Input type="date" value={form.data_prima_visita ?? ''} onChange={(e) => update('data_prima_visita', e.target.value)}
                  className="bg-slate-900 border-slate-700 text-white" />
              </div>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Gruppo sanguigno</Label>
                <select value={form.gruppo_sanguigno ?? ''} onChange={(e) => update('gruppo_sanguigno', e.target.value as SchedaMedicaType['gruppo_sanguigno'])}
                  className="w-full h-10 rounded-md border border-slate-700 bg-slate-900 text-white px-3">
                  <option value="">Non specificato</option>
                  {GRUPPI_SANGUIGNI.map((g) => <option key={g} value={g}>{g}</option>)}
                </select>
              </div>
            </div>

            {/* Parametri vitali */}
            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
              <h4 className="text-white text-sm font-medium mb-3">Parametri vitali</h4>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Peso (kg)</Label>
                  <Input type="number" step="0.1" value={form.peso_kg ?? ''} onChange={(e) => update('peso_kg', parseFloat(e.target.value) || undefined)}
                    placeholder="70.5" className="bg-slate-800 border-slate-700 text-white" />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Altezza (cm)</Label>
                  <Input type="number" value={form.altezza_cm ?? ''} onChange={(e) => update('altezza_cm', parseFloat(e.target.value) || undefined)}
                    placeholder="175" className="bg-slate-800 border-slate-700 text-white" />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">FC (bpm)</Label>
                  <Input type="number" value={form.frequenza_cardiaca ?? ''} onChange={(e) => update('frequenza_cardiaca', parseInt(e.target.value) || undefined)}
                    placeholder="72" className="bg-slate-800 border-slate-700 text-white" />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Sist. (mmHg)</Label>
                  <Input type="number" value={form.pressione_sistolica ?? ''} onChange={(e) => update('pressione_sistolica', parseInt(e.target.value) || undefined)}
                    placeholder="120" className="bg-slate-800 border-slate-700 text-white" />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Diast. (mmHg)</Label>
                  <Input type="number" value={form.pressione_diastolica ?? ''} onChange={(e) => update('pressione_diastolica', parseInt(e.target.value) || undefined)}
                    placeholder="80" className="bg-slate-800 border-slate-700 text-white" />
                </div>
                <div>
                  {form.peso_kg && form.altezza_cm ? (
                    <div className="mt-4">
                      <Label className="text-slate-400 text-xs mb-1 block">BMI</Label>
                      <p className="text-white font-bold text-lg">
                        {(form.peso_kg / Math.pow(form.altezza_cm / 100, 2)).toFixed(1)}
                      </p>
                    </div>
                  ) : null}
                </div>
              </div>
            </div>

            {/* Abitudini */}
            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 space-y-3">
              <h4 className="text-white text-sm font-medium">Abitudini</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center justify-between">
                  <Label className="text-slate-300 text-sm">Fumatore</Label>
                  <Switch checked={form.fumatore} onCheckedChange={(v) => update('fumatore', v)} />
                </div>
                <div className="flex items-center justify-between">
                  <Label className="text-slate-300 text-sm">Ex fumatore</Label>
                  <Switch checked={form.ex_fumatore} onCheckedChange={(v) => update('ex_fumatore', v)} />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Consumo alcol</Label>
                  <select value={form.consumo_alcol ?? ''} onChange={(e) => update('consumo_alcol', e.target.value as SchedaMedicaType['consumo_alcol'])}
                    className="w-full h-9 rounded-md border border-slate-700 bg-slate-800 text-white text-sm px-2">
                    <option value="">Non specificato</option>
                    <option value="no">No</option>
                    <option value="occasionale">Occasionale</option>
                    <option value="moderato">Moderato</option>
                    <option value="frequente">Frequente</option>
                  </select>
                </div>
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Attività fisica</Label>
                  <select value={form.attivita_fisica ?? ''} onChange={(e) => update('attivita_fisica', e.target.value as SchedaMedicaType['attivita_fisica'])}
                    className="w-full h-9 rounded-md border border-slate-700 bg-slate-800 text-white text-sm px-2">
                    <option value="">Non specificato</option>
                    <option value="sedentario">Sedentario</option>
                    <option value="leggera">Leggera</option>
                    <option value="moderata">Moderata</option>
                    <option value="intensa">Intensa</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Patologie */}
            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 space-y-3">
              <h4 className="text-white text-sm font-medium">Patologie croniche</h4>
              <TagList tags={form.patologie_croniche} onChange={(v) => update('patologie_croniche', v)}
                placeholder="es. Diabete tipo 2..." suggestions={PATOLOGIE_COMUNI} />
            </div>

            {/* Familiari */}
            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 space-y-3">
              <h4 className="text-white text-sm font-medium">Anamnesi familiare</h4>
              <div className="grid grid-cols-3 gap-3">
                <div className="flex items-center justify-between">
                  <Label className="text-slate-300 text-xs">Cardiopatie</Label>
                  <Switch checked={form.familiari_cardiopatie} onCheckedChange={(v) => update('familiari_cardiopatie', v)} />
                </div>
                <div className="flex items-center justify-between">
                  <Label className="text-slate-300 text-xs">Diabete</Label>
                  <Switch checked={form.familiari_diabete} onCheckedChange={(v) => update('familiari_diabete', v)} />
                </div>
                <div className="flex items-center justify-between">
                  <Label className="text-slate-300 text-xs">Tumori</Label>
                  <Switch checked={form.familiari_tumori} onCheckedChange={(v) => update('familiari_tumori', v)} />
                </div>
              </div>
              <Input value={form.anamnesi_familiare_note ?? ''} onChange={(e) => update('anamnesi_familiare_note', e.target.value)}
                placeholder="Note anamnesi familiare..."
                className="bg-slate-800 border-slate-700 text-white text-sm" />
            </div>
          </TabsContent>

          {/* TAB: Allergie */}
          <TabsContent value="allergie" className="mt-4 space-y-4">
            <div className="bg-slate-900 p-4 rounded-lg border border-red-500/30">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <h4 className="text-white text-sm font-medium">Allergie ai farmaci</h4>
              </div>
              <TagList tags={form.allergie_farmaci} onChange={(v) => update('allergie_farmaci', v)}
                placeholder="es. Penicillina, FANS, Aspirina..." />
            </div>

            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
              <h4 className="text-white text-sm font-medium mb-3">Allergie alimentari</h4>
              <TagList tags={form.allergie_alimenti} onChange={(v) => update('allergie_alimenti', v)}
                placeholder="es. Glutine, Lattosio, Noci..." />
            </div>

            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
              <h4 className="text-white text-sm font-medium mb-3">Altre allergie</h4>
              <TagList tags={form.allergie_altro} onChange={(v) => update('allergie_altro', v)}
                placeholder="es. Lattice, Nichel, Polline..." />
            </div>

            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 space-y-3">
              <h4 className="text-white text-sm font-medium">Patologie pregresse e interventi</h4>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Patologie pregresse</Label>
                <TagList tags={form.patologie_pregresse} onChange={(v) => update('patologie_pregresse', v)}
                  placeholder="es. Appendicectomia 2015..." />
              </div>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Interventi chirurgici</Label>
                <TagList tags={form.interventi_chirurgici} onChange={(v) => update('interventi_chirurgici', v)}
                  placeholder="es. Ernioplastica inguinale 2020..." />
              </div>
            </div>
          </TabsContent>

          {/* TAB: Farmaci */}
          <TabsContent value="farmaci" className="mt-4">
            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
              <h4 className="text-white text-sm font-medium mb-3">Farmaci in uso</h4>
              <FarmaciList farmaci={form.farmaci_attuali} onChange={(v) => update('farmaci_attuali', v)} />
            </div>
          </TabsContent>

          {/* TAB: Visite */}
          <TabsContent value="visite" className="mt-4">
            <VisiteList visite={form.visite} onChange={(v) => update('visite', v)} />
          </TabsContent>

          {/* TAB: Note */}
          <TabsContent value="note" className="mt-4 space-y-4">
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Note cliniche</Label>
              <Textarea value={form.note_cliniche ?? ''} onChange={(e) => update('note_cliniche', e.target.value)}
                placeholder="Note cliniche generali..."
                className="bg-slate-900 border-slate-700 text-white min-h-[120px]" />
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Note private (solo professionista)</Label>
              <Textarea value={form.note_private ?? ''} onChange={(e) => update('note_private', e.target.value)}
                placeholder="Note riservate al professionista..."
                className="bg-slate-900 border-slate-700 text-white min-h-[100px]" />
            </div>
          </TabsContent>

          {/* TAB: Immagini Cliniche */}
          <TabsContent value="immagini" className="mt-4 space-y-4">
            <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-700">
              <h3 className="text-sm font-medium text-white mb-1 flex items-center gap-2">
                <Camera className="w-4 h-4 text-red-400" />
                Immagini Cliniche
              </h3>
              <p className="text-xs text-slate-500 mb-4">
                Le immagini cliniche richiedono consenso GDPR esplicito (Art. 9). Accessibili solo al medico.
              </p>

              {!mediaConsentGranted ? (
                <button
                  type="button"
                  onClick={() => setShowConsentModal(true)}
                  className="w-full py-4 border-2 border-dashed border-red-700/50 rounded-xl text-red-400 text-sm hover:border-red-500 hover:bg-red-500/5 transition-all"
                >
                  Richiedi consenso GDPR per abilitare il caricamento immagini
                </button>
              ) : (
                <>
                  <MediaUploadZone
                    clienteId={clienteIdNum}
                    categoria="clinica"
                    consensoGdpr
                    label="Aggiungi immagine clinica"
                    className="mb-4"
                  />
                  <MediaGallery
                    clienteId={clienteIdNum}
                    categoria="clinica"
                    emptyMessage="Nessuna immagine clinica"
                  />
                </>
              )}
            </div>
          </TabsContent>
        </Tabs>

        <div className="flex justify-end pt-4">
          <Button onClick={handleSave} disabled={save.isPending}
            className="bg-red-700 hover:bg-red-600 text-white">
            <Save className="w-4 h-4 mr-2" />
            {save.isPending ? 'Salvataggio...' : 'Salva Scheda Medica'}
          </Button>
        </div>
      </CardContent>
      <MediaConsentModal
        open={showConsentModal}
        clienteId={clienteIdNum}
        clienteNome={`cliente #${clienteId}`}
        onConfirmed={() => {
          setMediaConsentGranted(true);
          setShowConsentModal(false);
        }}
        onCancel={() => setShowConsentModal(false)}
      />
    </Card>
  );
}
