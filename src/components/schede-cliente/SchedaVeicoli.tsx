// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Veicoli Component (W2-C)
// Scheda cliente per officine, gommisti, elettrauto, detailing
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { useSchedaVeicoli, useSaveSchedaVeicoli } from '../../hooks/use-schede-cliente';
import type { SchedaVeicoli as SchedaVeicoliType, Intervento } from '../../types/scheda-cliente';
import { toast } from 'sonner';
import {
  Car,
  Wrench,
  ClipboardList,
  StickyNote,
  Save,
  Plus,
  Trash2,
  AlertCircle,
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

const TIPI_ALIMENTAZIONE = [
  { value: 'benzina', label: 'Benzina' },
  { value: 'diesel', label: 'Diesel' },
  { value: 'gpl', label: 'GPL' },
  { value: 'metano', label: 'Metano' },
  { value: 'elettrico', label: 'Elettrico' },
  { value: 'ibrido', label: 'Ibrido' },
] as const;

const TIPI_GOMME = [
  { value: 'estive', label: 'Estive' },
  { value: 'invernali', label: 'Invernali' },
  { value: 'allseason', label: 'All Season' },
] as const;

const TIPI_INTERVENTO = [
  'Tagliando',
  'Cambio olio',
  'Revisione',
  'Cambio gomme',
  'Freni',
  'Distribuzione',
  'Batteria',
  'Filtri',
  'Diagnosi',
  'Riparazione',
  'Altro',
];

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Tabella Interventi
// ─────────────────────────────────────────────────────────────────────

function TabellaInterventi({
  interventi,
  onChange,
}: {
  interventi: Intervento[];
  onChange: (list: Intervento[]) => void;
}) {
  const [showForm, setShowForm] = useState(false);
  const [newItem, setNewItem] = useState<Omit<Intervento, 'id'>>({
    data: new Date().toISOString().split('T')[0],
    km: 0,
    tipo: '',
    descrizione: '',
    costo: undefined,
  });

  const handleAdd = () => {
    if (!newItem.tipo || !newItem.descrizione) return;
    const item: Intervento = {
      id: Date.now().toString(),
      ...newItem,
    };
    onChange([...interventi, item]);
    setNewItem({ data: new Date().toISOString().split('T')[0], km: 0, tipo: '', descrizione: '', costo: undefined });
    setShowForm(false);
  };

  const handleRemove = (id: string) => {
    onChange(interventi.filter((i) => i.id !== id));
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-white font-medium text-sm">Storico Interventi</h4>
        <Button
          size="sm"
          variant="outline"
          className="border-slate-600 text-slate-300 hover:text-white hover:bg-slate-700"
          onClick={() => setShowForm(!showForm)}
        >
          <Plus className="w-3 h-3 mr-1" />
          Aggiungi
        </Button>
      </div>

      {showForm && (
        <div className="bg-slate-900 p-3 rounded-lg space-y-3 border border-slate-700">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label className="text-slate-400 text-xs">Data</Label>
              <Input
                type="date"
                value={newItem.data}
                onChange={(e) => setNewItem((p) => ({ ...p, data: e.target.value }))}
                className="bg-slate-800 border-slate-700 text-white text-sm h-8"
              />
            </div>
            <div>
              <Label className="text-slate-400 text-xs">Km</Label>
              <Input
                type="number"
                placeholder="es. 45000"
                value={newItem.km || ''}
                onChange={(e) => setNewItem((p) => ({ ...p, km: parseInt(e.target.value) || 0 }))}
                className="bg-slate-800 border-slate-700 text-white text-sm h-8"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <Label className="text-slate-400 text-xs">Tipo</Label>
              <select
                value={newItem.tipo}
                onChange={(e) => setNewItem((p) => ({ ...p, tipo: e.target.value }))}
                className="w-full h-8 rounded-md border border-slate-700 bg-slate-800 text-white text-sm px-2"
              >
                <option value="">Seleziona...</option>
                {TIPI_INTERVENTO.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <Label className="text-slate-400 text-xs">Costo (€)</Label>
              <Input
                type="number"
                step="0.01"
                placeholder="es. 89.90"
                value={newItem.costo ?? ''}
                onChange={(e) => setNewItem((p) => ({ ...p, costo: parseFloat(e.target.value) || undefined }))}
                className="bg-slate-800 border-slate-700 text-white text-sm h-8"
              />
            </div>
          </div>
          <div>
            <Label className="text-slate-400 text-xs">Descrizione</Label>
            <Input
              placeholder="es. Cambio olio + filtri"
              value={newItem.descrizione}
              onChange={(e) => setNewItem((p) => ({ ...p, descrizione: e.target.value }))}
              className="bg-slate-800 border-slate-700 text-white text-sm h-8"
            />
          </div>
          <div className="flex gap-2 justify-end">
            <Button size="sm" variant="ghost" className="text-slate-400 h-7 text-xs" onClick={() => setShowForm(false)}>
              Annulla
            </Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white h-7 text-xs" onClick={handleAdd}>
              Aggiungi
            </Button>
          </div>
        </div>
      )}

      {interventi.length === 0 ? (
        <p className="text-slate-500 text-sm text-center py-4">Nessun intervento registrato</p>
      ) : (
        <div className="space-y-2">
          {[...interventi].sort((a, b) => b.data.localeCompare(a.data)).map((item) => (
            <div
              key={item.id}
              className="flex items-start justify-between bg-slate-900 rounded-lg p-3 border border-slate-700"
            >
              <div className="space-y-1 flex-1">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="border-blue-500/50 text-blue-400 text-xs">
                    {item.tipo}
                  </Badge>
                  <span className="text-slate-400 text-xs">{item.data}</span>
                  {item.km > 0 && (
                    <span className="text-slate-500 text-xs">{item.km.toLocaleString('it-IT')} km</span>
                  )}
                </div>
                <p className="text-white text-sm">{item.descrizione}</p>
                {item.costo !== undefined && (
                  <p className="text-teal-400 text-xs font-medium">€ {item.costo.toFixed(2)}</p>
                )}
              </div>
              <Button
                size="sm"
                variant="ghost"
                className="text-slate-600 hover:text-red-400 h-7 w-7 p-0 ml-2"
                onClick={() => handleRemove(item.id)}
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Veicolo Form (singolo veicolo)
// ─────────────────────────────────────────────────────────────────────

function VeicoloForm({
  veicolo,
  clienteId,
  onSaved,
}: {
  veicolo: SchedaVeicoliType;
  clienteId: string;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<SchedaVeicoliType>(veicolo);
  const save = useSaveSchedaVeicoli();

  const update = <K extends keyof SchedaVeicoliType>(key: K, value: SchedaVeicoliType[K]) => {
    setForm((p) => ({ ...p, [key]: value }));
  };

  const handleSave = async () => {
    if (!form.targa.trim()) {
      toast.error('Inserisci la targa del veicolo');
      return;
    }
    try {
      await save.mutateAsync({ clienteId, data: form });
      toast.success('Scheda veicolo salvata');
      onSaved();
    } catch {
      toast.error('Errore nel salvataggio');
    }
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="veicolo" className="w-full">
        <TabsList className="bg-slate-900 border border-slate-700 w-full grid grid-cols-4">
          <TabsTrigger value="veicolo" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <Car className="w-3 h-3 mr-1" />
            Veicolo
          </TabsTrigger>
          <TabsTrigger value="manutenzione" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <Wrench className="w-3 h-3 mr-1" />
            Manutenzione
          </TabsTrigger>
          <TabsTrigger value="interventi" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <ClipboardList className="w-3 h-3 mr-1" />
            Interventi
          </TabsTrigger>
          <TabsTrigger value="note" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <StickyNote className="w-3 h-3 mr-1" />
            Note
          </TabsTrigger>
        </TabsList>

        {/* TAB: Veicolo */}
        <TabsContent value="veicolo" className="mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <Label className="text-slate-400 text-xs mb-1 block">Targa *</Label>
              <Input
                value={form.targa}
                onChange={(e) => update('targa', e.target.value.toUpperCase())}
                placeholder="es. AB123CD"
                className="bg-slate-900 border-slate-700 text-white font-mono text-lg tracking-widest uppercase"
              />
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Marca</Label>
              <Input
                value={form.marca ?? ''}
                onChange={(e) => update('marca', e.target.value)}
                placeholder="es. Volkswagen"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Modello</Label>
              <Input
                value={form.modello ?? ''}
                onChange={(e) => update('modello', e.target.value)}
                placeholder="es. Golf 1.6 TDI"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Anno</Label>
              <Input
                type="number"
                value={form.anno ?? ''}
                onChange={(e) => update('anno', parseInt(e.target.value) || undefined)}
                placeholder="es. 2019"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Alimentazione</Label>
              <select
                value={form.alimentazione ?? ''}
                onChange={(e) => update('alimentazione', e.target.value as SchedaVeicoliType['alimentazione'])}
                className="w-full h-10 rounded-md border border-slate-700 bg-slate-900 text-white px-3"
              >
                <option value="">Seleziona...</option>
                {TIPI_ALIMENTAZIONE.map((a) => (
                  <option key={a.value} value={a.value}>{a.label}</option>
                ))}
              </select>
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Cilindrata</Label>
              <Input
                value={form.cilindrata ?? ''}
                onChange={(e) => update('cilindrata', e.target.value)}
                placeholder="es. 1598cc"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Potenza (kW)</Label>
              <Input
                type="number"
                value={form.kw ?? ''}
                onChange={(e) => update('kw', parseInt(e.target.value) || undefined)}
                placeholder="es. 85"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div className="col-span-2">
              <Label className="text-slate-400 text-xs mb-1 block">Numero Telaio (VIN)</Label>
              <Input
                value={form.telaio ?? ''}
                onChange={(e) => update('telaio', e.target.value.toUpperCase())}
                placeholder="es. WVWZZZ1JZ3W386752"
                className="bg-slate-900 border-slate-700 text-white font-mono text-sm"
              />
            </div>
          </div>
        </TabsContent>

        {/* TAB: Manutenzione */}
        <TabsContent value="manutenzione" className="mt-4 space-y-4">
          <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
            <h4 className="text-white font-medium text-sm mb-3">Revisione</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Ultima revisione</Label>
                <Input
                  type="date"
                  value={form.ultima_revisione ?? ''}
                  onChange={(e) => update('ultima_revisione', e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Scadenza revisione</Label>
                <Input
                  type="date"
                  value={form.scadenza_revisione ?? ''}
                  onChange={(e) => update('scadenza_revisione', e.target.value)}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
            </div>
            {form.scadenza_revisione && new Date(form.scadenza_revisione) < new Date() && (
              <div className="mt-2 flex items-center gap-2 text-red-400 text-sm">
                <AlertCircle className="w-4 h-4" />
                Revisione scaduta!
              </div>
            )}
          </div>

          <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
            <h4 className="text-white font-medium text-sm mb-3">Chilometraggio</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Km attuali</Label>
                <Input
                  type="number"
                  value={form.km_attuali ?? ''}
                  onChange={(e) => update('km_attuali', parseInt(e.target.value) || undefined)}
                  placeholder="es. 87500"
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Km ultimo tagliando</Label>
                <Input
                  type="number"
                  value={form.km_ultimo_tagliando ?? ''}
                  onChange={(e) => update('km_ultimo_tagliando', parseInt(e.target.value) || undefined)}
                  placeholder="es. 75000"
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
            </div>
            {form.km_attuali && form.km_ultimo_tagliando && (form.km_attuali - form.km_ultimo_tagliando) > 15000 && (
              <div className="mt-2 flex items-center gap-2 text-amber-400 text-sm">
                <AlertCircle className="w-4 h-4" />
                Tagliando in scadenza ({(form.km_attuali - form.km_ultimo_tagliando).toLocaleString('it-IT')} km dall'ultimo)
              </div>
            )}
          </div>

          <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
            <h4 className="text-white font-medium text-sm mb-3">Gomme</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Misura</Label>
                <Input
                  value={form.misura_gomme ?? ''}
                  onChange={(e) => update('misura_gomme', e.target.value)}
                  placeholder="es. 205/55 R16"
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Tipo</Label>
                <select
                  value={form.tipo_gomme ?? ''}
                  onChange={(e) => update('tipo_gomme', e.target.value as SchedaVeicoliType['tipo_gomme'])}
                  className="w-full h-10 rounded-md border border-slate-700 bg-slate-800 text-white px-3"
                >
                  <option value="">Seleziona...</option>
                  {TIPI_GOMME.map((g) => (
                    <option key={g.value} value={g.value}>{g.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
            <h4 className="text-white font-medium text-sm mb-3">Preferenza Ricambi</h4>
            <select
              value={form.preferenza_ricambi ?? ''}
              onChange={(e) => update('preferenza_ricambi', e.target.value as SchedaVeicoliType['preferenza_ricambi'])}
              className="w-full h-10 rounded-md border border-slate-700 bg-slate-800 text-white px-3"
            >
              <option value="">Nessuna preferenza</option>
              <option value="originali">Ricambi originali</option>
              <option value="compatibili">Ricambi compatibili</option>
              <option value="entrambi">Entrambi (valuta il tecnico)</option>
            </select>
          </div>
        </TabsContent>

        {/* TAB: Interventi */}
        <TabsContent value="interventi" className="mt-4">
          <TabellaInterventi
            interventi={form.interventi}
            onChange={(list) => update('interventi', list)}
          />
        </TabsContent>

        {/* TAB: Note */}
        <TabsContent value="note" className="mt-4">
          <div>
            <Label className="text-slate-400 text-xs mb-1 block">Note tecniche / Avvertenze</Label>
            <Textarea
              value={form.note_veicolo ?? ''}
              onChange={(e) => update('note_veicolo', e.target.value)}
              placeholder="es. Olio 5W40 sintetico, frizione usurata, spia ABS intermittente..."
              className="bg-slate-900 border-slate-700 text-white min-h-[200px]"
            />
          </div>
        </TabsContent>
      </Tabs>

      <div className="flex justify-end pt-2">
        <Button
          onClick={handleSave}
          disabled={save.isPending}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Save className="w-4 h-4 mr-2" />
          {save.isPending ? 'Salvataggio...' : 'Salva Scheda'}
        </Button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// MAIN COMPONENT: SchedaVeicoli
// ─────────────────────────────────────────────────────────────────────

export function SchedaVeicoli({ clienteId }: { clienteId: string }) {
  const { data: veicoli, isLoading } = useSchedaVeicoli(clienteId);
  const save = useSaveSchedaVeicoli();
  const [selectedId, setSelectedId] = useState<string | 'new' | null>(null);

  const newVeicolo: SchedaVeicoliType = {
    cliente_id: clienteId,
    targa: '',
    interventi: [],
    is_default: false,
  };

  const handleAddNew = () => {
    setSelectedId('new');
  };

  const handleSetDefault = async (veicolo: SchedaVeicoliType) => {
    try {
      await save.mutateAsync({ clienteId, data: { ...veicolo, is_default: true } });
      toast.success('Veicolo principale impostato');
    } catch {
      toast.error('Errore');
    }
  };

  if (isLoading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8 text-center text-slate-400">Caricamento...</CardContent>
      </Card>
    );
  }

  const veicoliList = veicoli ?? [];
  const selectedVeicolo =
    selectedId === 'new'
      ? newVeicolo
      : veicoliList.find((v) => v.id === selectedId) ?? null;

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/20 rounded-lg">
            <Car className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <CardTitle className="text-white">Scheda Veicoli</CardTitle>
            <p className="text-sm text-slate-400">
              {veicoliList.length} {veicoliList.length === 1 ? 'veicolo' : 'veicoli'} registrati
            </p>
          </div>
        </div>
        <Button
          size="sm"
          variant="outline"
          className="border-slate-600 text-slate-300 hover:text-white hover:bg-slate-700"
          onClick={handleAddNew}
        >
          <Plus className="w-4 h-4 mr-1" />
          Nuovo Veicolo
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Lista veicoli */}
        {veicoliList.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {veicoliList.map((v) => (
              <button
                key={v.id}
                onClick={() => setSelectedId(v.id ?? null)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg border transition-colors text-sm ${
                  selectedId === v.id
                    ? 'bg-blue-600/20 border-blue-500 text-blue-400'
                    : 'bg-slate-900 border-slate-700 text-slate-300 hover:border-slate-500'
                }`}
              >
                <Car className="w-3 h-3" />
                <span className="font-mono font-bold">{v.targa}</span>
                {v.marca && <span className="text-slate-500">{v.marca}</span>}
                {v.is_default && (
                  <Badge className="bg-blue-600/30 text-blue-400 text-xs px-1 py-0 border-0">
                    Principale
                  </Badge>
                )}
              </button>
            ))}
          </div>
        )}

        {/* Nessun veicolo */}
        {veicoliList.length === 0 && !selectedVeicolo && (
          <div className="text-center py-8 text-slate-500">
            <Car className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">Nessun veicolo registrato</p>
            <p className="text-xs mt-1">Clicca "Nuovo Veicolo" per aggiungere</p>
          </div>
        )}

        {/* Form veicolo selezionato */}
        {selectedVeicolo && (
          <div className="border border-slate-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-medium">
                {selectedId === 'new'
                  ? 'Nuovo Veicolo'
                  : `Targa: ${selectedVeicolo.targa}`}
              </h3>
              <div className="flex gap-2">
                {selectedId !== 'new' && selectedVeicolo.id && !selectedVeicolo.is_default && (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-slate-400 hover:text-blue-400 text-xs h-7"
                    onClick={() => handleSetDefault(selectedVeicolo)}
                  >
                    Imposta principale
                  </Button>
                )}
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-slate-500 hover:text-slate-300 text-xs h-7"
                  onClick={() => setSelectedId(null)}
                >
                  Chiudi
                </Button>
              </div>
            </div>
            <VeicoloForm
              veicolo={selectedVeicolo}
              clienteId={clienteId}
              onSaved={() => {
                if (selectedId === 'new') setSelectedId(null);
              }}
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
