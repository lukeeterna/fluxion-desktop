// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Parrucchiere Component (W2-A)
// Scheda cliente per saloni: capelli, colorazioni, allergie, preferenze
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
import { useSchedaParrucchiere, useSaveSchedaParrucchiere } from '../../hooks/use-schede-cliente';
import type { SchedaParrucchiere as SchedaParrucchiereType } from '../../types/scheda-cliente';
import {
  Scissors,
  Palette,
  AlertTriangle,
  Heart,
  ShoppingBag,
  Save,
  Plus,
  Trash2,
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

const SERVIZI_COMUNI = [
  'Taglio',
  'Colore',
  'Highlights/Colpi di sole',
  'Piega',
  'Trattamento',
  'Permanente',
  'Stiratura',
  'Extension',
  'Barba',
  'Shampoo',
];

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Tabella Colorazioni
// ─────────────────────────────────────────────────────────────────────

interface Colorazione {
  id: string;
  data: string;
  colore: string;
  tipo: string;
}

function TabellaColorazioni({
  colorazioni,
  onChange,
}: {
  colorazioni: Colorazione[];
  onChange: (colorazioni: Colorazione[]) => void;
}) {
  const [nuova, setNuova] = useState<Partial<Colorazione>>({
    data: new Date().toISOString().split('T')[0],
    colore: '',
    tipo: '',
  });

  const aggiungi = () => {
    if (!nuova.colore || !nuova.tipo) return;
    const entry: Colorazione = {
      id: `${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
      data: nuova.data ?? new Date().toISOString().split('T')[0],
      colore: nuova.colore,
      tipo: nuova.tipo,
    };
    onChange([...colorazioni, entry]);
    setNuova({ data: new Date().toISOString().split('T')[0], colore: '', tipo: '' });
  };

  const rimuovi = (id: string) => onChange(colorazioni.filter((c) => c.id !== id));

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-4 gap-2 bg-slate-800 p-3 rounded-lg">
        <Input
          type="date"
          value={nuova.data ?? ''}
          onChange={(e) => setNuova({ ...nuova, data: e.target.value })}
          className="bg-slate-700 border-slate-600 text-white"
        />
        <Input
          placeholder="Colore (es. Castano 5)"
          value={nuova.colore ?? ''}
          onChange={(e) => setNuova({ ...nuova, colore: e.target.value })}
          className="bg-slate-700 border-slate-600 text-white"
        />
        <select
          value={nuova.tipo ?? ''}
          onChange={(e) => setNuova({ ...nuova, tipo: e.target.value })}
          className="bg-slate-700 border-slate-600 text-white rounded-md px-2 text-sm"
        >
          <option value="">Tipo...</option>
          <option value="tinta">Tinta</option>
          <option value="highlights">Highlights</option>
          <option value="decolorazione">Decolorazione</option>
          <option value="balayage">Balayage</option>
          <option value="permanente">Permanente</option>
          <option value="stiratura">Stiratura</option>
        </select>
        <Button type="button" onClick={aggiungi} className="bg-purple-600 hover:bg-purple-700">
          <Plus className="w-4 h-4 mr-1" />
          Aggiungi
        </Button>
      </div>

      <table className="w-full text-sm">
        <thead className="bg-slate-800 text-slate-400">
          <tr>
            <th className="p-3 text-left">Data</th>
            <th className="p-3 text-left">Colore</th>
            <th className="p-3 text-left">Tipo</th>
            <th className="p-3 text-left">Azioni</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700">
          {colorazioni.length === 0 ? (
            <tr>
              <td colSpan={4} className="p-4 text-center text-slate-500">
                Nessuna colorazione registrata
              </td>
            </tr>
          ) : (
            colorazioni.map((c) => (
              <tr key={c.id} className="bg-slate-800/50">
                <td className="p-3 text-slate-300">{c.data}</td>
                <td className="p-3 text-white font-medium">{c.colore}</td>
                <td className="p-3">
                  <Badge variant="secondary" className="capitalize">
                    {c.tipo}
                  </Badge>
                </td>
                <td className="p-3">
                  <Button
                    type="button"
                    size="sm"
                    variant="destructive"
                    onClick={() => rimuovi(c.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// MAIN COMPONENT: SchedaParrucchiere
// ─────────────────────────────────────────────────────────────────────

export function SchedaParrucchiere({ clienteId }: { clienteId: string }) {
  const { data: scheda, isLoading } = useSchedaParrucchiere(clienteId);
  const saveScheda = useSaveSchedaParrucchiere();
  const [activeTab, setActiveTab] = useState('capelli');

  const [formData, setFormData] = useState<Partial<SchedaParrucchiereType>>({
    colorazioni_precedenti: [],
    decolorazioni: 0,
    permanente: 0,
    stirature_chimiche: 0,
    allergia_tinta: false,
    allergia_ammoniaca: false,
    test_pelle_eseguito: false,
    servizi_abituali: [],
    prodotti_casa: {},
    non_vuole: [],
  });

  // Carica dati esistenti (pattern da SchedaOdontoiatrica)
  if (scheda && !formData.id) {
    setFormData(scheda);
  }

  const handleSave = async () => {
    await saveScheda.mutateAsync({
      clienteId,
      data: formData as SchedaParrucchiereType,
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

  const colorazioni = (formData.colorazioni_precedenti ?? []) as Colorazione[];
  const serviziAbituali = formData.servizi_abituali ?? [];
  const prodottiCasa = formData.prodotti_casa ?? {};

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-500/20 rounded-lg">
            <Scissors className="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <CardTitle className="text-white">Scheda Parrucchiere</CardTitle>
            <p className="text-sm text-slate-400">Capelli, colorazioni e preferenze</p>
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
            <TabsTrigger value="capelli" className="data-[state=active]:bg-slate-700">
              <Scissors className="w-4 h-4 mr-2" />
              Capelli
            </TabsTrigger>
            <TabsTrigger value="colorazioni" className="data-[state=active]:bg-slate-700">
              <Palette className="w-4 h-4 mr-2" />
              Colorazioni
            </TabsTrigger>
            <TabsTrigger value="allergie" className="data-[state=active]:bg-slate-700">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Allergie
            </TabsTrigger>
            <TabsTrigger value="preferenze" className="data-[state=active]:bg-slate-700">
              <Heart className="w-4 h-4 mr-2" />
              Preferenze
            </TabsTrigger>
            <TabsTrigger value="prodotti" className="data-[state=active]:bg-slate-700">
              <ShoppingBag className="w-4 h-4 mr-2" />
              Prodotti
            </TabsTrigger>
          </TabsList>

          {/* ── TAB CAPELLI ── */}
          <TabsContent value="capelli" className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Tipo Capello</Label>
                <select
                  value={formData.tipo_capello ?? ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      tipo_capello:
                        (e.target.value as SchedaParrucchiereType['tipo_capello']) || undefined,
                    })
                  }
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md p-2 text-sm"
                >
                  <option value="">Seleziona...</option>
                  <option value="fino">Fino</option>
                  <option value="medio">Medio</option>
                  <option value="spesso">Spesso</option>
                  <option value="crepo">Crespo</option>
                  <option value="riccio">Riccio</option>
                  <option value="liscio">Liscio</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Porosità</Label>
                <select
                  value={formData.porosita ?? ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      porosita:
                        (e.target.value as SchedaParrucchiereType['porosita']) || undefined,
                    })
                  }
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md p-2 text-sm"
                >
                  <option value="">Seleziona...</option>
                  <option value="bassa">Bassa</option>
                  <option value="media">Media</option>
                  <option value="alta">Alta</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Lunghezza Attuale</Label>
                <select
                  value={formData.lunghezza_attuale ?? ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      lunghezza_attuale:
                        (e.target.value as SchedaParrucchiereType['lunghezza_attuale']) ||
                        undefined,
                    })
                  }
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md p-2 text-sm"
                >
                  <option value="">Seleziona...</option>
                  <option value="corto">Corto</option>
                  <option value="medio">Medio</option>
                  <option value="lungo">Lungo</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Base Naturale (tono 1-10)</Label>
                <Input
                  placeholder="Es: 5 (castano medio)"
                  value={formData.base_naturale ?? ''}
                  onChange={(e) => setFormData({ ...formData, base_naturale: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-slate-300">Colore Attuale</Label>
                <Input
                  placeholder="Es: Biondo 8 con highlights"
                  value={formData.colore_attuale ?? ''}
                  onChange={(e) => setFormData({ ...formData, colore_attuale: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                />
              </div>
            </div>
          </TabsContent>

          {/* ── TAB COLORAZIONI ── */}
          <TabsContent value="colorazioni" className="space-y-6">
            <div>
              <Label className="text-slate-300 text-base font-semibold">Storico Colorazioni</Label>
              <p className="text-xs text-slate-500 mb-3">
                Registra ogni trattamento chimico per tenere traccia della storia del capello.
              </p>
              <TabellaColorazioni
                colorazioni={colorazioni}
                onChange={(c) => setFormData({ ...formData, colorazioni_precedenti: c })}
              />
            </div>

            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-700">
              <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                <Label className="text-slate-300">Decolorazioni</Label>
                <Switch
                  checked={formData.decolorazioni === 1}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, decolorazioni: checked ? 1 : 0 })
                  }
                />
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                <Label className="text-slate-300">Permanente</Label>
                <Switch
                  checked={formData.permanente === 1}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, permanente: checked ? 1 : 0 })
                  }
                />
              </div>
              <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg">
                <Label className="text-slate-300">Stirature Chimiche</Label>
                <Switch
                  checked={formData.stirature_chimiche === 1}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, stirature_chimiche: checked ? 1 : 0 })
                  }
                />
              </div>
            </div>
          </TabsContent>

          {/* ── TAB ALLERGIE ── */}
          <TabsContent value="allergie" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div>
                  <Label className="text-slate-300 font-medium">Allergia Tinta</Label>
                  <p className="text-xs text-slate-500 mt-0.5">Reazione a coloranti chimici</p>
                </div>
                <Switch
                  checked={formData.allergia_tinta ?? false}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, allergia_tinta: checked })
                  }
                />
              </div>

              <div className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div>
                  <Label className="text-slate-300 font-medium">Allergia Ammoniaca</Label>
                  <p className="text-xs text-slate-500 mt-0.5">Sensibile a prodotti con ammoniaca</p>
                </div>
                <Switch
                  checked={formData.allergia_ammoniaca ?? false}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, allergia_ammoniaca: checked })
                  }
                />
              </div>
            </div>

            <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <Label className="text-slate-300 font-medium">Test Cute Eseguito</Label>
                  <p className="text-xs text-slate-500 mt-0.5">Patch test per tinte e coloranti</p>
                </div>
                <Switch
                  checked={formData.test_pelle_eseguito ?? false}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, test_pelle_eseguito: checked })
                  }
                />
              </div>

              {formData.test_pelle_eseguito && (
                <div className="space-y-2 mt-3 pt-3 border-t border-slate-600">
                  <Label className="text-slate-300">Data Ultimo Test</Label>
                  <Input
                    type="date"
                    value={formData.data_test_pelle ?? ''}
                    onChange={(e) =>
                      setFormData({ ...formData, data_test_pelle: e.target.value })
                    }
                    className="bg-slate-700 border-slate-600 text-white max-w-[200px]"
                  />
                </div>
              )}
            </div>

            {(formData.allergia_tinta || formData.allergia_ammoniaca) && (
              <div className="p-3 bg-amber-900/20 border border-amber-700/50 rounded-lg">
                <p className="text-amber-400 text-sm flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                  Cliente con allergie note. Utilizzare prodotti senza ammoniaca / formula delicata.
                </p>
              </div>
            )}
          </TabsContent>

          {/* ── TAB PREFERENZE ── */}
          <TabsContent value="preferenze" className="space-y-4">
            <div>
              <Label className="text-slate-300 font-medium mb-3 block">Servizi Abituali</Label>
              <div className="grid grid-cols-2 gap-2">
                {SERVIZI_COMUNI.map((servizio) => {
                  const attivo = serviziAbituali.includes(servizio);
                  return (
                    <button
                      key={servizio}
                      type="button"
                      onClick={() => {
                        const nuovi = attivo
                          ? serviziAbituali.filter((s) => s !== servizio)
                          : [...serviziAbituali, servizio];
                        setFormData({ ...formData, servizi_abituali: nuovi });
                      }}
                      className={`p-2 rounded-lg text-sm text-left transition-colors border ${
                        attivo
                          ? 'bg-purple-500/20 border-purple-500 text-purple-300'
                          : 'bg-slate-700/50 border-slate-600 text-slate-400 hover:bg-slate-700'
                      }`}
                    >
                      {servizio}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Frequenza Taglio</Label>
                <select
                  value={formData.frequenza_taglio ?? ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      frequenza_taglio:
                        (e.target.value as SchedaParrucchiereType['frequenza_taglio']) || undefined,
                    })
                  }
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md p-2 text-sm"
                >
                  <option value="">Non specificata</option>
                  <option value="settimanale">Settimanale</option>
                  <option value="2settimane">Ogni 2 settimane</option>
                  <option value="mensile">Mensile</option>
                  <option value="2mesi">Ogni 2 mesi</option>
                  <option value="3mesi">Ogni 3 mesi</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label className="text-slate-300">Frequenza Colore</Label>
                <select
                  value={formData.frequenza_colore ?? ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      frequenza_colore:
                        (e.target.value as SchedaParrucchiereType['frequenza_colore']) ||
                        undefined,
                    })
                  }
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md p-2 text-sm"
                >
                  <option value="">Non specificata</option>
                  <option value="settimanale">Settimanale</option>
                  <option value="2settimane">Ogni 2 settimane</option>
                  <option value="mensile">Mensile</option>
                  <option value="2mesi">Ogni 2 mesi</option>
                  <option value="3mesi">Ogni 3 mesi</option>
                  <option value="6mesi">Ogni 6 mesi</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-slate-300">Preferenze Colore</Label>
              <Textarea
                placeholder="Es: Preferisce toni caldi, naturali, evita il rosso..."
                value={formData.preferenze_colore ?? ''}
                onChange={(e) => setFormData({ ...formData, preferenze_colore: e.target.value })}
                className="bg-slate-700 border-slate-600 text-white min-h-[80px]"
              />
            </div>
          </TabsContent>

          {/* ── TAB PRODOTTI ── */}
          <TabsContent value="prodotti" className="space-y-4">
            <div>
              <Label className="text-slate-300 font-medium mb-1 block">Prodotti a Casa</Label>
              <p className="text-xs text-slate-500 mb-3">
                Registra shampoo, balsamo e trattamenti usati dal cliente a casa.
              </p>

              <div className="space-y-2">
                {Object.entries(prodottiCasa).map(([nome, brand]) => (
                  <div key={nome} className="flex items-center gap-2">
                    <span className="text-slate-400 text-sm w-28 shrink-0">{nome}:</span>
                    <span className="text-white text-sm flex-1">{String(brand)}</span>
                    <Button
                      type="button"
                      size="sm"
                      variant="destructive"
                      onClick={() => {
                        const nuovi = { ...prodottiCasa };
                        delete nuovi[nome];
                        setFormData({ ...formData, prodotti_casa: nuovi });
                      }}
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                ))}
              </div>

              <AddProdottoRow
                onAdd={(nome, brand) => {
                  setFormData({
                    ...formData,
                    prodotti_casa: { ...prodottiCasa, [nome]: brand },
                  });
                }}
              />
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Add Prodotto Row
// ─────────────────────────────────────────────────────────────────────

function AddProdottoRow({ onAdd }: { onAdd: (nome: string, brand: string) => void }) {
  const [nome, setNome] = useState('');
  const [brand, setBrand] = useState('');

  const handleAdd = () => {
    if (!nome.trim() || !brand.trim()) return;
    onAdd(nome.trim(), brand.trim());
    setNome('');
    setBrand('');
  };

  return (
    <div className="flex gap-2 mt-3 pt-3 border-t border-slate-700">
      <Input
        placeholder="Prodotto (es: Shampoo)"
        value={nome}
        onChange={(e) => setNome(e.target.value)}
        className="bg-slate-700 border-slate-600 text-white"
      />
      <Input
        placeholder="Marca/Nome (es: Kérastase)"
        value={brand}
        onChange={(e) => setBrand(e.target.value)}
        className="bg-slate-700 border-slate-600 text-white"
      />
      <Button type="button" onClick={handleAdd} className="bg-purple-600 hover:bg-purple-700 shrink-0">
        <Plus className="w-4 h-4 mr-1" />
        Aggiungi
      </Button>
    </div>
  );
}
