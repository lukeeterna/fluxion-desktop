// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Estetica Component
// Scheda cliente specifica per centri estetici
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

import { Textarea } from '../ui/textarea';
import { Switch } from '../ui/switch';
import { useSchedaEstetica, useSaveSchedaEstetica } from '../../hooks/use-schede-cliente';
import type { SchedaEstetica as SchedaEsteticaType } from '../../types/scheda-cliente';
import { 
  Sparkles, 
  Sun, 
  AlertTriangle,
  Save,
  Plus,
  Trash2,
  Droplets,
  Scale
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

interface SchedaEsteticaProps {
  clienteId: string;
}

const TIPI_PELLE = ['secca', 'mista', 'grassa', 'sensibile', 'normale'];
const OBIETTIVI = ['dimagrimento', 'tonificazione', 'rilassamento', 'anticellulite'];
const METODI_DEPILAZIONE = ['ceretta', 'laser', 'filo', 'crema'];

const PROBLEMATICHE_VISO = [
  'acne', 'macchie', 'rughe', 'rossori', 'couperose', 
  'pelle_opaca', 'pori_dilatati', 'occhiaie'
];

const ALLERGENI_COMUNI = [
  'nickel', 'profumi', 'parabeni', 'siliconi', 
  'lanolina', 'glicole', 'resina', 'henné'
];

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: SchedaEstetica Principale
// ─────────────────────────────────────────────────────────────────────

export function SchedaEstetica({ clienteId }: SchedaEsteticaProps) {
  const { data: scheda, isLoading } = useSchedaEstetica(clienteId);
  const saveScheda = useSaveSchedaEstetica();
  const [activeTab, setActiveTab] = useState('pelle');

  const [formData, setFormData] = useState<Partial<SchedaEsteticaType>>({
    fototipo: 3,
    tipo_pelle: 'normale',
    allergie_prodotti: [],
    allergie_profumi: false,
    allergie_henne: false,
    trattamenti_precedenti: [],
    unghie_naturali: true,
    problematiche_viso: [],
    gravidanza: false,
    allattamento: false,
    patologie_attive: [],
  });

  if (scheda && !formData.id) {
    setFormData(scheda);
  }

  const handleSave = async () => {
    await saveScheda.mutateAsync({
      clienteId,
      data: formData as SchedaEsteticaType,
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
          <div className="p-2 bg-pink-500/20 rounded-lg">
            <Sparkles className="w-6 h-6 text-pink-500" />
          </div>
          <div>
            <CardTitle className="text-white">Scheda Estetica</CardTitle>
            <p className="text-sm text-slate-400">Gestione trattamenti estetici</p>
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
            <TabsTrigger value="pelle" className="data-[state=active]:bg-slate-700">
              <Droplets className="w-4 h-4 mr-2" />
              Pelle
            </TabsTrigger>
            <TabsTrigger value="allergie" className="data-[state=active]:bg-slate-700">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Allergie
            </TabsTrigger>
            <TabsTrigger value="trattamenti" className="data-[state=active]:bg-slate-700">
              <Sparkles className="w-4 h-4 mr-2" />
              Trattamenti
            </TabsTrigger>
            <TabsTrigger value="corpo" className="data-[state=active]:bg-slate-700">
              <Scale className="w-4 h-4 mr-2" />
              Corpo
            </TabsTrigger>
          </TabsList>

          {/* Pelle */}
          <TabsContent value="pelle" className="space-y-6">
            {/* Fototipo */}
            <div className="space-y-3">
              <Label className="text-slate-300 flex items-center gap-2">
                <Sun className="w-4 h-4" />
                Fototipo (Scala Fitzpatrick)
              </Label>
              <div className="grid grid-cols-6 gap-2">
                {[1, 2, 3, 4, 5, 6].map((tipo) => (
                  <button
                    key={tipo}
                    type="button"
                    onClick={() => setFormData({ ...formData, fototipo: tipo })}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      formData.fototipo === tipo
                        ? 'border-pink-500 bg-pink-500/20'
                        : 'border-slate-600 bg-slate-700 hover:bg-slate-600'
                    }`}
                  >
                    <div className={`w-6 h-6 rounded-full mx-auto mb-1 ${
                      tipo <= 2 ? 'bg-amber-100' :
                      tipo <= 4 ? 'bg-amber-300' :
                      'bg-amber-700'
                    }`} />
                    <span className="text-xs text-slate-300">Tipo {tipo}</span>
                  </button>
                ))}
              </div>
              <p className="text-xs text-slate-500">
                {formData.fototipo === 1 && "Pelle molto chiara, sempre scotta, non si abbronza"}
                {formData.fototipo === 2 && "Pelle chiara, scotta facilmente, si abbronza poco"}
                {formData.fototipo === 3 && "Pelle intermedia, scotta moderatamente, abbronzatura progressiva"}
                {formData.fototipo === 4 && "Pelle olivastra, scotta raramente, abbronzatura buona"}
                {formData.fototipo === 5 && "Pelle scura, scolla difficilmente, abbronzatura intensa"}
                {formData.fototipo === 6 && "Pelle molto scura, non scotta mai, abbronzatura permanente"}
              </p>
            </div>

            {/* Tipo Pelle */}
            <div className="space-y-3">
              <Label className="text-slate-300">Tipo di Pelle</Label>
              <div className="grid grid-cols-5 gap-2">
                {TIPI_PELLE.map(tipo => (
                  <button
                    key={tipo}
                    type="button"
                    onClick={() => setFormData({ ...formData, tipo_pelle: tipo as SchedaEsteticaType['tipo_pelle'] })}
                    className={`p-2 rounded-lg border-2 capitalize transition-all ${
                      formData.tipo_pelle === tipo
                        ? 'border-pink-500 bg-pink-500/20 text-white'
                        : 'border-slate-600 bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                  >
                    {tipo}
                  </button>
                ))}
              </div>
            </div>

            {/* Problematiche Viso */}
            <div className="space-y-3">
              <Label className="text-slate-300">Problematiche Viso</Label>
              <div className="grid grid-cols-4 gap-2">
                {PROBLEMATICHE_VISO.map(prob => (
                  <label key={prob} className="flex items-center gap-2 p-2 bg-slate-700 rounded cursor-pointer hover:bg-slate-600">
                    <input
                      type="checkbox"
                      checked={formData.problematiche_viso?.includes(prob) || false}
                      onChange={(e) => {
                        const current = formData.problematiche_viso || [];
                        if (e.target.checked) {
                          setFormData({ ...formData, problematiche_viso: [...current, prob] });
                        } else {
                          setFormData({ ...formData, problematiche_viso: current.filter(p => p !== prob) });
                        }
                      }}
                      className="rounded border-slate-500"
                    />
                    <span className="text-sm text-slate-300 capitalize">{prob.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Routine Skincare */}
            <div className="space-y-2">
              <Label className="text-slate-300">Routine Skincare Attuale</Label>
              <Textarea
                value={formData.routine_skincare || ''}
                onChange={(e) => setFormData({ ...formData, routine_skincare: e.target.value })}
                placeholder="Descrivi la routine di skincare quotidiana..."
                className="bg-slate-700 border-slate-600 text-white min-h-[100px]"
              />
            </div>
          </TabsContent>

          {/* Allergie */}
          <TabsContent value="allergie" className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3 bg-slate-900 p-4 rounded-lg">
                <Switch
                  checked={formData.allergie_profumi || false}
                  onCheckedChange={(checked) => setFormData({ ...formData, allergie_profumi: checked })}
                />
                <div>
                  <Label className="text-white">Allergia ai Profumi</Label>
                  <p className="text-sm text-slate-400">Sensibilità a fragranze</p>
                </div>
              </div>

              <div className="flex items-center gap-3 bg-slate-900 p-4 rounded-lg">
                <Switch
                  checked={formData.allergie_henne || false}
                  onCheckedChange={(checked) => setFormData({ ...formData, allergie_henne: checked })}
                />
                <div>
                  <Label className="text-white">Allergia all'Henné</Label>
                  <p className="text-sm text-slate-400">Per tinture e decorative</p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <Label className="text-slate-300">Allergie a Prodotti/Ingredienti</Label>
              <div className="grid grid-cols-4 gap-2">
                {ALLERGENI_COMUNI.map(allergene => (
                  <label key={allergene} className="flex items-center gap-2 p-2 bg-slate-700 rounded cursor-pointer hover:bg-slate-600">
                    <input
                      type="checkbox"
                      checked={formData.allergie_prodotti?.includes(allergene) || false}
                      onChange={(e) => {
                        const current = formData.allergie_prodotti || [];
                        if (e.target.checked) {
                          setFormData({ ...formData, allergie_prodotti: [...current, allergene] });
                        } else {
                          setFormData({ ...formData, allergie_prodotti: current.filter(a => a !== allergene) });
                        }
                      }}
                      className="rounded border-slate-500"
                    />
                    <span className="text-sm text-slate-300 capitalize">{allergene}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <Label className="text-slate-300">Altre Allergie o Intolleranze</Label>
              <Textarea
                value={formData.allergie_prodotti?.filter(a => !ALLERGENI_COMUNI.includes(a)).join(', ') || ''}
                onChange={(e) => {
                  const custom = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
                  const common = formData.allergie_prodotti?.filter(a => ALLERGENI_COMUNI.includes(a)) || [];
                  setFormData({ ...formData, allergie_prodotti: [...common, ...custom] });
                }}
                placeholder="Specifica altre allergie separate da virgola..."
                className="bg-slate-700 border-slate-600 text-white min-h-[80px]"
              />
            </div>

            {/* Controindicazioni */}
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center gap-3 bg-rose-900/30 p-4 rounded-lg border border-rose-700">
                <Switch
                  checked={formData.gravidanza || false}
                  onCheckedChange={(checked) => setFormData({ ...formData, gravidanza: checked })}
                />
                <div>
                  <Label className="text-rose-200">Gravidanza</Label>
                  <p className="text-sm text-rose-400">Limita alcuni trattamenti</p>
                </div>
              </div>

              <div className="flex items-center gap-3 bg-rose-900/30 p-4 rounded-lg border border-rose-700">
                <Switch
                  checked={formData.allattamento || false}
                  onCheckedChange={(checked) => setFormData({ ...formData, allattamento: checked })}
                />
                <div>
                  <Label className="text-rose-200">Allattamento</Label>
                  <p className="text-sm text-rose-400">Limita alcuni trattamenti</p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <Label className="text-slate-300">Patologie Attive</Label>
              <Textarea
                value={formData.patologie_attive?.join(', ') || ''}
                onChange={(e) => setFormData({ ...formData, patologie_attive: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                placeholder="Diabete, ipertensione, problemi circolatori, ecc..."
                className="bg-slate-700 border-slate-600 text-white min-h-[80px]"
              />
            </div>
          </TabsContent>

          {/* Trattamenti */}
          <TabsContent value="trattamenti" className="space-y-6">
            {/* Trattamenti Precedenti */}
            <div className="space-y-3">
              <Label className="text-slate-300">Trattamenti Precedenti</Label>
              <div className="bg-slate-900 p-4 rounded-lg space-y-2">
                {(formData.trattamenti_precedenti || []).map((tratt, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-slate-800 rounded">
                    <div>
                      <span className="text-white font-medium">{tratt.tipo}</span>
                      <span className="text-slate-400 text-sm ml-2">({tratt.data})</span>
                      {tratt.note && <p className="text-slate-500 text-sm">{tratt.note}</p>}
                    </div>
                    <Button
                      type="button"
                      size="sm"
                      variant="destructive"
                      onClick={() => {
                        const updated = [...(formData.trattamenti_precedenti || [])];
                        updated.splice(idx, 1);
                        setFormData({ ...formData, trattamenti_precedenti: updated });
                      }}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
                
                <div className="grid grid-cols-3 gap-2 mt-4">
                  <Input
                    placeholder="Tipo trattamento"
                    id="new-tratt-tipo"
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                  <Input
                    type="date"
                    id="new-tratt-data"
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                  <Button
                    type="button"
                    onClick={() => {
                      const tipo = (document.getElementById('new-tratt-tipo') as HTMLInputElement)?.value;
                      const data = (document.getElementById('new-tratt-data') as HTMLInputElement)?.value;
                      if (tipo && data) {
                        setFormData({
                          ...formData,
                          trattamenti_precedenti: [...(formData.trattamenti_precedenti || []), { tipo, data }]
                        });
                        (document.getElementById('new-tratt-tipo') as HTMLInputElement).value = '';
                        (document.getElementById('new-tratt-data') as HTMLInputElement).value = '';
                      }
                    }}
                    className="bg-pink-600 hover:bg-pink-700"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Aggiungi
                  </Button>
                </div>
              </div>
            </div>

            {/* Epilazione */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Ultima Depilazione</Label>
                <Input
                  type="date"
                  value={formData.ultima_depilazione || ''}
                  onChange={(e) => setFormData({ ...formData, ultima_depilazione: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Metodo Depilazione</Label>
                <select
                  value={formData.metodo_depilazione || ''}
                  onChange={(e) => setFormData({ ...formData, metodo_depilazione: e.target.value as SchedaEsteticaType['metodo_depilazione'] })}
                  className="w-full bg-slate-700 border-slate-600 text-white rounded-md p-2"
                >
                  <option value="">Seleziona...</option>
                  {METODI_DEPILAZIONE.map(m => (
                    <option key={m} value={m} className="capitalize">{m}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Unghie */}
            <div className="bg-slate-900 p-4 rounded-lg space-y-3">
              <div className="flex items-center gap-3">
                <Switch
                  checked={formData.unghie_naturali || true}
                  onCheckedChange={(checked) => setFormData({ ...formData, unghie_naturali: checked })}
                />
                <Label className="text-white">Unghie Naturali</Label>
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Problematiche Unghie</Label>
                <Textarea
                  value={formData.problematiche_unghie || ''}
                  onChange={(e) => setFormData({ ...formData, problematiche_unghie: e.target.value })}
                  placeholder="Onicofagia, fragilità, micosi, ecc..."
                  className="bg-slate-700 border-slate-600 text-white min-h-[80px]"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Note Trattamenti</Label>
              <Textarea
                value={formData.note_trattamenti || ''}
                onChange={(e) => setFormData({ ...formData, note_trattamenti: e.target.value })}
                placeholder="Note generali sui trattamenti effettuati..."
                className="bg-slate-700 border-slate-600 text-white min-h-[100px]"
              />
            </div>
          </TabsContent>

          {/* Corpo */}
          <TabsContent value="corpo" className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300 flex items-center gap-2">
                  <Scale className="w-4 h-4" />
                  Peso Attuale (kg)
                </Label>
                <Input
                  type="number"
                  step="0.1"
                  value={formData.peso_attuale || ''}
                  onChange={(e) => setFormData({ ...formData, peso_attuale: parseFloat(e.target.value) })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Obiettivo</Label>
                <select
                  value={formData.obiettivo || ''}
                  onChange={(e) => setFormData({ ...formData, obiettivo: e.target.value as SchedaEsteticaType['obiettivo'] })}
                  className="w-full bg-slate-700 border-slate-600 text-white rounded-md p-2"
                >
                  <option value="">Seleziona...</option>
                  {OBIETTIVI.map(o => (
                    <option key={o} value={o} className="capitalize">{o.replace('_', ' ')}</option>
                  ))}
                </select>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
