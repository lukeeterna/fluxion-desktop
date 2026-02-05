// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Odontoiatrica Component
// Scheda cliente specifica per studi dentistici
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
import { useSchedaOdontoiatrica } from '../../hooks/use-schede-cliente';
import { useSaveSchedaOdontoiatrica } from '../../hooks/use-schede-cliente';
import type { SchedaOdontoiatrica as SchedaOdontoiatricaType } from '../../types/scheda-cliente';
import { 
  Stethoscope, 
  Calendar, 
  AlertTriangle, 
  Smile,
  Save,
  Plus,
  Trash2
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

interface SchedaOdontoiatricaProps {
  clienteId: string;
}

// Mappa denti FDI (World Dental Federation notation)
// Quadrante 1 (superiore destro): 11-18
// Quadrante 2 (superiore sinistro): 21-28
// Quadrante 3 (inferiore sinistro): 31-38
// Quadrante 4 (inferiore destro): 41-48

const DENTI_QUADRANTE_1 = [18, 17, 16, 15, 14, 13, 12, 11];
const DENTI_QUADRANTE_2 = [21, 22, 23, 24, 25, 26, 27, 28];
const DENTI_QUADRANTE_3 = [31, 32, 33, 34, 35, 36, 37, 38];
const DENTI_QUADRANTE_4 = [48, 47, 46, 45, 44, 43, 42, 41];

type ToothStatus = 'sano' | 'otturato' | 'devitalizzato' | 'corona' | 'impianto' | 'mancante' | 'carie';

const TOOTH_COLORS: Record<ToothStatus, string> = {
  sano: 'bg-emerald-500 hover:bg-emerald-600',
  otturato: 'bg-blue-500 hover:bg-blue-600',
  devitalizzato: 'bg-amber-500 hover:bg-amber-600',
  corona: 'bg-purple-500 hover:bg-purple-600',
  impianto: 'bg-cyan-500 hover:bg-cyan-600',
  mancante: 'bg-slate-700 hover:bg-slate-600 border-2 border-red-500',
  carie: 'bg-red-500 hover:bg-red-600',
};

const TOOTH_LABELS: Record<ToothStatus, string> = {
  sano: 'Sano',
  otturato: 'Otturato',
  devitalizzato: 'Devitalizzato',
  corona: 'Corona',
  impianto: 'Impianto',
  mancante: 'Mancante',
  carie: 'Carie',
};

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Odontogramma
// ─────────────────────────────────────────────────────────────────────

interface OdontogrammaProps {
  odontogramma: Record<string, { stato: ToothStatus; note?: string }>;
  onChange: (odontogramma: Record<string, { stato: ToothStatus; note?: string }>) => void;
  readOnly?: boolean;
}

function Odontogramma({ odontogramma, onChange, readOnly = false }: OdontogrammaProps) {
  const [selectedTooth, setSelectedTooth] = useState<string | null>(null);

  const getToothState = (numero: number): ToothStatus => {
    return odontogramma[numero.toString()]?.stato || 'sano';
  };

  const setToothState = (numero: number, stato: ToothStatus) => {
    if (readOnly) return;
    const newOdontogramma = { ...odontogramma };
    newOdontogramma[numero.toString()] = { 
      ...newOdontogramma[numero.toString()],
      stato 
    };
    onChange(newOdontogramma);
  };

  const renderTooth = (numero: number) => {
    const stato = getToothState(numero);
    const isSelected = selectedTooth === numero.toString();

    return (
      <button
        key={numero}
        type="button"
        onClick={() => !readOnly && setSelectedTooth(numero.toString())}
        className={`
          w-10 h-10 rounded-lg flex items-center justify-center text-white text-sm font-medium
          transition-all duration-200 ${TOOTH_COLORS[stato]}
          ${isSelected ? 'ring-2 ring-white ring-offset-2 ring-offset-slate-800 scale-110' : ''}
          ${readOnly ? 'cursor-default' : 'cursor-pointer'}
        `}
        title={`Dente ${numero} - ${TOOTH_LABELS[stato]}`}
      >
        {numero}
      </button>
    );
  };

  return (
    <div className="space-y-4">
      <div className="bg-slate-900 p-6 rounded-xl">
        {/* Quadranti superiori */}
        <div className="flex justify-center gap-8 mb-6">
          {/* Q2 - Superiore sinistro */}
          <div className="flex gap-1">
            {DENTI_QUADRANTE_2.map(renderTooth)}
          </div>
          {/* Q1 - Superiore destro */}
          <div className="flex gap-1">
            {DENTI_QUADRANTE_1.map(renderTooth)}
          </div>
        </div>

        {/* Linea mediana */}
        <div className="h-px bg-slate-600 mb-6" />

        {/* Quadranti inferiori */}
        <div className="flex justify-center gap-8">
          {/* Q3 - Inferiore sinistro */}
          <div className="flex gap-1">
            {DENTI_QUADRANTE_3.map(renderTooth)}
          </div>
          {/* Q4 - Inferiore destro */}
          <div className="flex gap-1">
            {DENTI_QUADRANTE_4.map(renderTooth)}
          </div>
        </div>
      </div>

      {/* Legenda e Modifica stato */}
      <div className="grid grid-cols-2 gap-4">
        {/* Legenda */}
        <div className="bg-slate-800 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-white mb-3">Legenda</h4>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(TOOTH_LABELS).map(([stato, label]) => (
              <div key={stato} className="flex items-center gap-2">
                <div className={`w-4 h-4 rounded ${TOOTH_COLORS[stato as ToothStatus]}`} />
                <span className="text-xs text-slate-300">{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Modifica stato */}
        {!readOnly && selectedTooth && (
          <div className="bg-slate-800 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-white mb-3">
              Modifica Dente {selectedTooth}
            </h4>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(TOOTH_LABELS).map(([stato, label]) => (
                <Button
                  key={stato}
                  type="button"
                  size="sm"
                  variant={getToothState(parseInt(selectedTooth)) === stato ? 'default' : 'outline'}
                  onClick={() => setToothState(parseInt(selectedTooth), stato as ToothStatus)}
                  className="text-xs"
                >
                  {label}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Tabella Trattamenti
// ─────────────────────────────────────────────────────────────────────

interface Trattamento {
  id: string;
  data: string;
  tipo: string;
  dente?: string;
  descrizione: string;
  costo?: number;
}

interface TabellaTrattamentiProps {
  trattamenti: Trattamento[];
  onChange: (trattamenti: Trattamento[]) => void;
  readOnly?: boolean;
}

function TabellaTrattamenti({ trattamenti, onChange, readOnly = false }: TabellaTrattamentiProps) {
  const [newTrattamento, setNewTrattamento] = useState<Partial<Trattamento>>({
    data: new Date().toISOString().split('T')[0],
    tipo: '',
    descrizione: '',
  });

  const addTrattamento = () => {
    if (!newTrattamento.tipo || !newTrattamento.descrizione) return;
    
    const trattamento: Trattamento = {
      id: crypto.randomUUID(),
      data: newTrattamento.data || new Date().toISOString().split('T')[0],
      tipo: newTrattamento.tipo,
      dente: newTrattamento.dente,
      descrizione: newTrattamento.descrizione,
      costo: newTrattamento.costo,
    };
    
    onChange([...trattamenti, trattamento]);
    setNewTrattamento({
      data: new Date().toISOString().split('T')[0],
      tipo: '',
      descrizione: '',
    });
  };

  const removeTrattamento = (id: string) => {
    onChange(trattamenti.filter(t => t.id !== id));
  };

  return (
    <div className="space-y-4">
      {!readOnly && (
        <div className="grid grid-cols-5 gap-2 bg-slate-800 p-4 rounded-lg">
          <Input
            type="date"
            value={newTrattamento.data}
            onChange={(e) => setNewTrattamento({ ...newTrattamento, data: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Input
            placeholder="Tipo"
            value={newTrattamento.tipo}
            onChange={(e) => setNewTrattamento({ ...newTrattamento, tipo: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Input
            placeholder="Dente"
            value={newTrattamento.dente || ''}
            onChange={(e) => setNewTrattamento({ ...newTrattamento, dente: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Input
            placeholder="Descrizione"
            value={newTrattamento.descrizione}
            onChange={(e) => setNewTrattamento({ ...newTrattamento, descrizione: e.target.value })}
            className="bg-slate-700 border-slate-600 text-white"
          />
          <Button type="button" onClick={addTrattamento} className="bg-cyan-600 hover:bg-cyan-700">
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
              <th className="p-3 text-left">Tipo</th>
              <th className="p-3 text-left">Dente</th>
              <th className="p-3 text-left">Descrizione</th>
              {!readOnly && <th className="p-3 text-left">Azioni</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {trattamenti.length === 0 ? (
              <tr>
                <td colSpan={readOnly ? 4 : 5} className="p-4 text-center text-slate-500">
                  Nessun trattamento registrato
                </td>
              </tr>
            ) : (
              trattamenti.map((t) => (
                <tr key={t.id} className="bg-slate-800/50">
                  <td className="p-3 text-white">{t.data}</td>
                  <td className="p-3">
                    <Badge variant="secondary">{t.tipo}</Badge>
                  </td>
                  <td className="p-3 text-slate-300">{t.dente || '-'}</td>
                  <td className="p-3 text-slate-300">{t.descrizione}</td>
                  {!readOnly && (
                    <td className="p-3">
                      <Button
                        type="button"
                        size="sm"
                        variant="destructive"
                        onClick={() => removeTrattamento(t.id)}
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
// COMPONENT: SchedaOdontoiatrica Principale
// ─────────────────────────────────────────────────────────────────────

export function SchedaOdontoiatrica({ clienteId }: SchedaOdontoiatricaProps) {
  const { data: scheda, isLoading } = useSchedaOdontoiatrica(clienteId);
  const saveScheda = useSaveSchedaOdontoiatrica();
  const [activeTab, setActiveTab] = useState('odontogramma');

  // Form state
  const [formData, setFormData] = useState<Partial<SchedaOdontoiatricaType>>({
    odontogramma: {},
    allergia_lattice: false,
    allergia_anestesia: false,
    filo_interdentale: false,
    collutorio: false,
    ortodonzia_in_corso: false,
    trattamenti: [],
  });

  // Carica dati esistenti
  if (scheda && !formData.id) {
    setFormData(scheda);
  }

  const handleSave = async () => {
    await saveScheda.mutateAsync({
      clienteId,
      data: formData as SchedaOdontoiatricaType,
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

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-500/20 rounded-lg">
            <Stethoscope className="w-6 h-6 text-red-500" />
          </div>
          <div>
            <CardTitle className="text-white">Scheda Odontoiatrica</CardTitle>
            <p className="text-sm text-slate-400">Gestione clinica dentale</p>
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
            <TabsTrigger value="odontogramma" className="data-[state=active]:bg-slate-700">
              <Smile className="w-4 h-4 mr-2" />
              Odontogramma
            </TabsTrigger>
            <TabsTrigger value="anamnesi" className="data-[state=active]:bg-slate-700">
              <Calendar className="w-4 h-4 mr-2" />
              Anamnesi
            </TabsTrigger>
            <TabsTrigger value="allergie" className="data-[state=active]:bg-slate-700">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Allergie
            </TabsTrigger>
            <TabsTrigger value="trattamenti" className="data-[state=active]:bg-slate-700">
              <Stethoscope className="w-4 h-4 mr-2" />
              Trattamenti
            </TabsTrigger>
          </TabsList>

          {/* Odontogramma */}
          <TabsContent value="odontogramma" className="space-y-4">
            <Odontogramma
              odontogramma={formData.odontogramma || {}}
              onChange={(odontogramma) => setFormData({ ...formData, odontogramma })}
            />
          </TabsContent>

          {/* Anamnesi */}
          <TabsContent value="anamnesi" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Prima Visita</Label>
                <Input
                  type="date"
                  value={formData.prima_visita || ''}
                  onChange={(e) => setFormData({ ...formData, prima_visita: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Ultima Visita</Label>
                <Input
                  type="date"
                  value={formData.ultima_visita || ''}
                  onChange={(e) => setFormData({ ...formData, ultima_visita: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Tipo Spazzolino</Label>
              <select
                value={formData.spazzolino || ''}
                onChange={(e) => setFormData({ ...formData, spazzolino: e.target.value as SchedaOdontoiatricaType['spazzolino'] })}
                className="w-full bg-slate-700 border-slate-600 text-white rounded-md p-2"
              >
                <option value="">Seleziona...</option>
                <option value="manuale">Manuale</option>
                <option value="elettrico">Elettrico</option>
                <option value="ultrasuoni">Ultrasuoni</option>
              </select>
            </div>

            <div className="flex gap-6">
              <div className="flex items-center gap-2">
                <Switch
                  checked={formData.filo_interdentale || false}
                  onCheckedChange={(checked) => setFormData({ ...formData, filo_interdentale: checked })}
                />
                <Label className="text-slate-300">Usa Filo Interdentale</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={formData.collutorio || false}
                  onCheckedChange={(checked) => setFormData({ ...formData, collutorio: checked })}
                />
                <Label className="text-slate-300">Usa Collutorio</Label>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Note Cliniche</Label>
              <Textarea
                value={formData.note_cliniche || ''}
                onChange={(e) => setFormData({ ...formData, note_cliniche: e.target.value })}
                placeholder="Inserisci note cliniche..."
                className="bg-slate-700 border-slate-600 text-white min-h-[100px]"
              />
            </div>
          </TabsContent>

          {/* Allergie */}
          <TabsContent value="allergie" className="space-y-4">
            <div className="bg-slate-900 p-6 rounded-lg space-y-4">
              <div className="flex items-center gap-3">
                <Switch
                  checked={formData.allergia_lattice || false}
                  onCheckedChange={(checked) => setFormData({ ...formData, allergia_lattice: checked })}
                />
                <div>
                  <Label className="text-white">Allergia al Lattice</Label>
                  <p className="text-sm text-slate-400">Reazione allergica ai guanti in lattice</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Switch
                  checked={formData.allergia_anestesia || false}
                  onCheckedChange={(checked) => setFormData({ ...formData, allergia_anestesia: checked })}
                />
                <div>
                  <Label className="text-white">Allergia all'Anestesia</Label>
                  <p className="text-sm text-slate-400">Reazione a anestetici locali</p>
                </div>
              </div>

              <div className="space-y-2 pt-4">
                <Label className="text-slate-300">Altre Allergie</Label>
                <Textarea
                  value={formData.allergie_altre || ''}
                  onChange={(e) => setFormData({ ...formData, allergie_altre: e.target.value })}
                  placeholder="Specifica altre allergie..."
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
            </div>
          </TabsContent>

          {/* Trattamenti */}
          <TabsContent value="trattamenti" className="space-y-4">
            <TabellaTrattamenti
              trattamenti={formData.trattamenti || []}
              onChange={(trattamenti) => setFormData({ ...formData, trattamenti })}
            />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
