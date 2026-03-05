// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Parrucchiere — World-Class Redesign 2026
// Fresha-inspired · Glassmorphism · Visual hierarchy · CoVe 2026
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
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
  CheckCircle2,
  Clock,
  Sparkles,
  ChevronRight,
  Loader2,
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

const SERVIZI_COMUNI = [
  'Taglio', 'Colore', 'Highlights', 'Piega',
  'Trattamento', 'Permanente', 'Stiratura', 'Extension', 'Barba', 'Shampoo',
];

const COLOR_TIPO_MAP: Record<string, string> = {
  tinta: 'bg-purple-500',
  highlights: 'bg-amber-400',
  decolorazione: 'bg-yellow-200',
  balayage: 'bg-orange-300',
  permanente: 'bg-pink-400',
  stiratura: 'bg-slate-400',
};

interface Colorazione {
  id: string;
  data: string;
  colore: string;
  tipo: string;
}

// ─────────────────────────────────────────────────────────────────────
// SUB: Stat Chip
// ─────────────────────────────────────────────────────────────────────

function StatChip({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-white/5 border border-white/10 rounded-full backdrop-blur-sm">
      <span className="text-purple-300 w-3.5 h-3.5">{icon}</span>
      <span className="text-slate-400 text-xs">{label}</span>
      <span className="text-white text-xs font-semibold">{value}</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB: Color Timeline Entry
// ─────────────────────────────────────────────────────────────────────

function ColorTimelineEntry({
  colorazione,
  onRemove,
  isLast,
}: {
  colorazione: Colorazione;
  onRemove: () => void;
  isLast: boolean;
}) {
  const dotColor = COLOR_TIPO_MAP[colorazione.tipo] ?? 'bg-slate-400';
  return (
    <div className="relative flex gap-4">
      {/* Timeline line */}
      {!isLast && (
        <div className="absolute left-[18px] top-8 bottom-0 w-px bg-slate-700" />
      )}
      {/* Color dot */}
      <div className={`w-9 h-9 rounded-full ${dotColor} shrink-0 flex items-center justify-center shadow-lg mt-0.5`}>
        <Palette className="w-4 h-4 text-white/80" />
      </div>
      {/* Content */}
      <div className="flex-1 pb-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-white font-medium text-sm">{colorazione.colore}</p>
            <div className="flex items-center gap-2 mt-0.5">
              <Badge
                variant="secondary"
                className="capitalize text-xs px-2 py-0 bg-slate-700 text-slate-300 border-slate-600"
              >
                {colorazione.tipo}
              </Badge>
              <span className="text-slate-500 text-xs flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {colorazione.data}
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={onRemove}
            className="text-slate-600 hover:text-red-400 transition-colors mt-0.5"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB: Hair Property Pill
// ─────────────────────────────────────────────────────────────────────

function HairPill({
  label,
  value,
  color = 'purple',
}: {
  label: string;
  value?: string;
  color?: string;
}) {
  if (!value) return null;
  const colors: Record<string, string> = {
    purple: 'bg-purple-500/10 border-purple-500/30 text-purple-300',
    teal: 'bg-teal-500/10 border-teal-500/30 text-teal-300',
    amber: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
  };
  return (
    <div className={`flex flex-col items-center px-4 py-3 rounded-xl border ${colors[color] ?? colors.purple}`}>
      <span className="text-[10px] uppercase tracking-widest opacity-60 mb-0.5">{label}</span>
      <span className="font-semibold text-sm capitalize">{value}</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB: Service Tag
// ─────────────────────────────────────────────────────────────────────

function ServiceTag({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all
        ${active
          ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/20'
          : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-purple-500/50 hover:text-slate-200'
        }
      `}
    >
      {active && <CheckCircle2 className="w-3 h-3" />}
      {label}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB: Section Card
// ─────────────────────────────────────────────────────────────────────

function SectionCard({
  title,
  subtitle,
  icon,
  children,
  accent = 'purple',
}: {
  title: string;
  subtitle?: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  accent?: string;
}) {
  const accents: Record<string, string> = {
    purple: 'text-purple-400',
    red: 'text-red-400',
    teal: 'text-teal-400',
    amber: 'text-amber-400',
  };
  return (
    <div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-5">
      <div className="flex items-center gap-2.5 mb-4">
        <span className={accents[accent] ?? accents.purple}>{icon}</span>
        <div>
          <h4 className="text-white font-semibold text-sm">{title}</h4>
          {subtitle && <p className="text-slate-500 text-xs">{subtitle}</p>}
        </div>
      </div>
      {children}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB: Add Prodotto Row
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
        className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500"
      />
      <Input
        placeholder="Marca (es: Kérastase)"
        value={brand}
        onChange={(e) => setBrand(e.target.value)}
        className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500"
      />
      <Button type="button" onClick={handleAdd} className="bg-purple-600 hover:bg-purple-700 shrink-0">
        <Plus className="w-4 h-4" />
      </Button>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// MAIN COMPONENT
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

  if (scheda && !formData.id) setFormData(scheda);

  const handleSave = async () => {
    await saveScheda.mutateAsync({ clienteId, data: formData as SchedaParrucchiereType });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="flex flex-col items-center gap-3 text-slate-500">
          <Loader2 className="w-8 h-8 animate-spin" />
          <p className="text-sm">Caricamento scheda...</p>
        </div>
      </div>
    );
  }

  const colorazioni = (formData.colorazioni_precedenti ?? []) as Colorazione[];
  const serviziAbituali = formData.servizi_abituali ?? [];
  const prodottiCasa = formData.prodotti_casa ?? {};
  const hasAllergie = formData.allergia_tinta || formData.allergia_ammoniaca;

  return (
    <div className="rounded-2xl overflow-hidden border border-slate-700/60 shadow-2xl bg-slate-900">

      {/* ── HEADER con glassmorphism ── */}
      <div className="relative overflow-hidden bg-gradient-to-br from-purple-950/60 via-slate-900 to-slate-900 border-b border-purple-500/10 px-6 py-5">
        {/* Ambient blur circles */}
        <div className="absolute -top-10 -right-10 w-48 h-48 bg-purple-500/8 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-8 left-20 w-32 h-32 bg-purple-400/5 rounded-full blur-2xl pointer-events-none" />

        <div className="relative flex items-start justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-500/15 rounded-2xl border border-purple-500/25 shadow-lg shadow-purple-500/10">
              <Scissors className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white">Scheda Parrucchiere</h2>
                {hasAllergie && (
                  <span className="flex items-center gap-1 px-2 py-0.5 bg-red-500/15 border border-red-500/30 rounded-full text-red-400 text-xs font-medium">
                    <AlertTriangle className="w-3 h-3" /> Allergie
                  </span>
                )}
              </div>
              <p className="text-slate-500 text-xs mt-0.5">Capelli · Colorazioni · Allergie · Preferenze</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Quick stats */}
            <StatChip
              icon={<Palette className="w-3.5 h-3.5" />}
              label="Colorazioni"
              value={String(colorazioni.length)}
            />
            <StatChip
              icon={<CheckCircle2 className="w-3.5 h-3.5" />}
              label="Servizi"
              value={String(serviziAbituali.length)}
            />
            <Button
              onClick={handleSave}
              disabled={saveScheda.isPending}
              className="bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-900/40 ml-2"
            >
              {saveScheda.isPending ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              {saveScheda.isPending ? 'Salvataggio...' : 'Salva'}
            </Button>
          </div>
        </div>
      </div>

      {/* ── BODY ── */}
      <div className="p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-slate-800/80 border border-slate-700/50 p-1 rounded-xl mb-6 h-auto flex flex-wrap gap-1">
            {[
              { value: 'capelli', icon: <Scissors className="w-3.5 h-3.5" />, label: 'Capelli' },
              { value: 'colorazioni', icon: <Palette className="w-3.5 h-3.5" />, label: 'Colorazioni', badge: colorazioni.length },
              { value: 'allergie', icon: <AlertTriangle className="w-3.5 h-3.5" />, label: 'Allergie', alert: hasAllergie },
              { value: 'preferenze', icon: <Heart className="w-3.5 h-3.5" />, label: 'Preferenze' },
              { value: 'prodotti', icon: <ShoppingBag className="w-3.5 h-3.5" />, label: 'Prodotti' },
            ].map((tab) => (
              <TabsTrigger
                key={tab.value}
                value={tab.value}
                className="flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-lg
                  data-[state=active]:bg-slate-700 data-[state=active]:text-white data-[state=active]:shadow
                  text-slate-500 hover:text-slate-300 transition-colors"
              >
                <span className={tab.alert ? 'text-red-400' : ''}>{tab.icon}</span>
                {tab.label}
                {tab.badge !== undefined && tab.badge > 0 && (
                  <span className="ml-0.5 px-1.5 py-0.5 bg-purple-500/20 text-purple-300 text-[10px] rounded-full font-bold">
                    {tab.badge}
                  </span>
                )}
                {tab.alert && (
                  <span className="ml-0.5 w-1.5 h-1.5 bg-red-400 rounded-full" />
                )}
              </TabsTrigger>
            ))}
          </TabsList>

          {/* ── TAB CAPELLI ── */}
          <TabsContent value="capelli" className="space-y-4">
            {/* Hair Passport Visual */}
            {(formData.tipo_capello || formData.porosita || formData.lunghezza_attuale || formData.colore_attuale) && (
              <div className="flex gap-3 p-4 bg-slate-800/40 rounded-xl border border-slate-700/40">
                <div className="flex items-center gap-1 text-purple-400 text-xs font-medium uppercase tracking-wider">
                  <Sparkles className="w-3.5 h-3.5" />
                  Passaporto Capello
                </div>
                <ChevronRight className="w-4 h-4 text-slate-600 self-center" />
                <div className="flex flex-wrap gap-2">
                  <HairPill label="Tipo" value={formData.tipo_capello} color="purple" />
                  <HairPill label="Porosità" value={formData.porosita} color="teal" />
                  <HairPill label="Lunghezza" value={formData.lunghezza_attuale} color="amber" />
                  {formData.colore_attuale && (
                    <HairPill label="Colore attuale" value={formData.colore_attuale} color="purple" />
                  )}
                </div>
              </div>
            )}

            <div className="grid grid-cols-3 gap-4">
              {[
                {
                  key: 'tipo_capello' as const,
                  label: 'Tipo Capello',
                  options: ['fino', 'medio', 'spesso', 'crepo', 'riccio', 'liscio'],
                },
                {
                  key: 'porosita' as const,
                  label: 'Porosità',
                  options: ['bassa', 'media', 'alta'],
                },
                {
                  key: 'lunghezza_attuale' as const,
                  label: 'Lunghezza',
                  options: ['corto', 'medio', 'lungo'],
                },
              ].map(({ key, label, options }) => (
                <div key={key} className="space-y-1.5">
                  <Label className="text-slate-400 text-xs uppercase tracking-wider">{label}</Label>
                  <select
                    value={(formData[key] as string) ?? ''}
                    onChange={(e) =>
                      setFormData({ ...formData, [key]: e.target.value || undefined })
                    }
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:border-purple-500/50 focus:outline-none transition-colors"
                  >
                    <option value="">Seleziona...</option>
                    {options.map((o) => (
                      <option key={o} value={o} className="capitalize">{o.charAt(0).toUpperCase() + o.slice(1)}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label className="text-slate-400 text-xs uppercase tracking-wider">Base Naturale (tono 1-10)</Label>
                <Input
                  placeholder="Es: 5 — castano medio"
                  value={formData.base_naturale ?? ''}
                  onChange={(e) => setFormData({ ...formData, base_naturale: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-600 focus:border-purple-500/50"
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-slate-400 text-xs uppercase tracking-wider">Colore Attuale</Label>
                <Input
                  placeholder="Es: Biondo 8 con highlights"
                  value={formData.colore_attuale ?? ''}
                  onChange={(e) => setFormData({ ...formData, colore_attuale: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-600 focus:border-purple-500/50"
                />
              </div>
            </div>

            {/* Trattamenti chimici */}
            <SectionCard
              title="Trattamenti Chimici"
              subtitle="Procedure con impatto strutturale"
              icon={<Sparkles className="w-4 h-4" />}
            >
              <div className="grid grid-cols-3 gap-3">
                {[
                  { key: 'decolorazioni' as const, label: 'Decolorazioni' },
                  { key: 'permanente' as const, label: 'Permanente' },
                  { key: 'stirature_chimiche' as const, label: 'Stirature Chimiche' },
                ].map(({ key, label }) => (
                  <div
                    key={key}
                    className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                      formData[key] === 1
                        ? 'bg-purple-500/10 border-purple-500/30'
                        : 'bg-slate-700/30 border-slate-700'
                    }`}
                  >
                    <Label className="text-slate-300 text-sm cursor-pointer">{label}</Label>
                    <Switch
                      checked={formData[key] === 1}
                      onCheckedChange={(checked) =>
                        setFormData({ ...formData, [key]: checked ? 1 : 0 })
                      }
                    />
                  </div>
                ))}
              </div>
            </SectionCard>
          </TabsContent>

          {/* ── TAB COLORAZIONI ── */}
          <TabsContent value="colorazioni" className="space-y-4">
            {/* Add form */}
            <AddColorazioneRow
              onAdd={(c) => setFormData({ ...formData, colorazioni_precedenti: [...colorazioni, c] })}
            />

            {/* Timeline */}
            {colorazioni.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-slate-600">
                <Palette className="w-10 h-10 mb-3 opacity-40" />
                <p className="text-sm">Nessuna colorazione registrata</p>
                <p className="text-xs mt-1 opacity-60">Aggiungi la prima tramite il form sopra</p>
              </div>
            ) : (
              <div className="pl-2 pt-2">
                {[...colorazioni].reverse().map((c, i) => (
                  <ColorTimelineEntry
                    key={c.id}
                    colorazione={c}
                    onRemove={() =>
                      setFormData({
                        ...formData,
                        colorazioni_precedenti: colorazioni.filter((x) => x.id !== c.id),
                      })
                    }
                    isLast={i === colorazioni.length - 1}
                  />
                ))}
              </div>
            )}
          </TabsContent>

          {/* ── TAB ALLERGIE ── */}
          <TabsContent value="allergie" className="space-y-4">
            {/* Alert banner se allergie presenti */}
            {hasAllergie && (
              <div className="flex items-start gap-3 p-4 bg-red-950/30 border border-red-500/30 rounded-xl">
                <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-red-300 font-semibold text-sm">Cliente con allergie note</p>
                  <p className="text-red-400/70 text-xs mt-0.5">
                    Usare prodotti senza ammoniaca / formula ultra-delicata. Verificare test cute aggiornato.
                  </p>
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              {[
                {
                  key: 'allergia_tinta' as const,
                  label: 'Allergia Tinta',
                  sub: 'Reazione a coloranti chimici',
                },
                {
                  key: 'allergia_ammoniaca' as const,
                  label: 'Allergia Ammoniaca',
                  sub: 'Sensibile a prodotti con ammoniaca',
                },
              ].map(({ key, label, sub }) => (
                <div
                  key={key}
                  className={`flex items-center justify-between p-4 rounded-xl border transition-all ${
                    formData[key]
                      ? 'bg-red-950/20 border-red-500/30'
                      : 'bg-slate-800/50 border-slate-700'
                  }`}
                >
                  <div>
                    <p className={`font-medium text-sm ${formData[key] ? 'text-red-300' : 'text-slate-300'}`}>
                      {label}
                    </p>
                    <p className="text-slate-500 text-xs mt-0.5">{sub}</p>
                  </div>
                  <Switch
                    checked={formData[key] ?? false}
                    onCheckedChange={(checked) => setFormData({ ...formData, [key]: checked })}
                  />
                </div>
              ))}
            </div>

            <SectionCard
              title="Test Cute"
              subtitle="Patch test per tinte e coloranti"
              icon={<CheckCircle2 className="w-4 h-4" />}
              accent="teal"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${formData.test_pelle_eseguito ? 'text-teal-300' : 'text-slate-400'}`}>
                    {formData.test_pelle_eseguito ? '✓ Test eseguito' : 'Test non ancora eseguito'}
                  </p>
                </div>
                <Switch
                  checked={formData.test_pelle_eseguito ?? false}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, test_pelle_eseguito: checked })
                  }
                />
              </div>
              {formData.test_pelle_eseguito && (
                <div className="mt-3 pt-3 border-t border-slate-700 space-y-1.5">
                  <Label className="text-slate-400 text-xs uppercase tracking-wider">Data Ultimo Test</Label>
                  <Input
                    type="date"
                    value={formData.data_test_pelle ?? ''}
                    onChange={(e) => setFormData({ ...formData, data_test_pelle: e.target.value })}
                    className="bg-slate-700/50 border-slate-600 text-white max-w-[200px]"
                  />
                </div>
              )}
            </SectionCard>
          </TabsContent>

          {/* ── TAB PREFERENZE ── */}
          <TabsContent value="preferenze" className="space-y-5">
            <SectionCard
              title="Servizi Abituali"
              subtitle="Tocca per selezionare i servizi del cliente"
              icon={<Heart className="w-4 h-4" />}
            >
              <div className="flex flex-wrap gap-2">
                {SERVIZI_COMUNI.map((servizio) => (
                  <ServiceTag
                    key={servizio}
                    label={servizio}
                    active={serviziAbituali.includes(servizio)}
                    onClick={() => {
                      const nuovi = serviziAbituali.includes(servizio)
                        ? serviziAbituali.filter((s) => s !== servizio)
                        : [...serviziAbituali, servizio];
                      setFormData({ ...formData, servizi_abituali: nuovi });
                    }}
                  />
                ))}
              </div>
            </SectionCard>

            <div className="grid grid-cols-2 gap-4">
              {[
                {
                  key: 'frequenza_taglio' as const,
                  label: 'Frequenza Taglio',
                  options: [
                    { value: 'settimanale', label: 'Settimanale' },
                    { value: '2settimane', label: 'Ogni 2 settimane' },
                    { value: 'mensile', label: 'Mensile' },
                    { value: '2mesi', label: 'Ogni 2 mesi' },
                    { value: '3mesi', label: 'Ogni 3 mesi' },
                  ],
                },
                {
                  key: 'frequenza_colore' as const,
                  label: 'Frequenza Colore',
                  options: [
                    { value: 'settimanale', label: 'Settimanale' },
                    { value: 'mensile', label: 'Mensile' },
                    { value: '2mesi', label: 'Ogni 2 mesi' },
                    { value: '3mesi', label: 'Ogni 3 mesi' },
                    { value: '6mesi', label: 'Ogni 6 mesi' },
                  ],
                },
              ].map(({ key, label, options }) => (
                <div key={key} className="space-y-1.5">
                  <Label className="text-slate-400 text-xs uppercase tracking-wider">{label}</Label>
                  <select
                    value={(formData[key] as string) ?? ''}
                    onChange={(e) => setFormData({ ...formData, [key]: e.target.value || undefined })}
                    className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 text-sm focus:border-purple-500/50 focus:outline-none"
                  >
                    <option value="">Non specificata</option>
                    {options.map((o) => (
                      <option key={o.value} value={o.value}>{o.label}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>

            <div className="space-y-1.5">
              <Label className="text-slate-400 text-xs uppercase tracking-wider">Preferenze Colore</Label>
              <Textarea
                placeholder="Es: Preferisce toni caldi, naturali. Evita il rosso intenso..."
                value={formData.preferenze_colore ?? ''}
                onChange={(e) => setFormData({ ...formData, preferenze_colore: e.target.value })}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-600 min-h-[80px] resize-none focus:border-purple-500/50"
              />
            </div>
          </TabsContent>

          {/* ── TAB PRODOTTI ── */}
          <TabsContent value="prodotti" className="space-y-4">
            <SectionCard
              title="Prodotti a Casa"
              subtitle="Shampoo, balsami e trattamenti del cliente"
              icon={<ShoppingBag className="w-4 h-4" />}
            >
              {Object.keys(prodottiCasa).length === 0 ? (
                <p className="text-slate-600 text-sm text-center py-4">Nessun prodotto registrato</p>
              ) : (
                <div className="space-y-2 mb-2">
                  {Object.entries(prodottiCasa).map(([nome, brand]) => (
                    <div
                      key={nome}
                      className="flex items-center justify-between px-3 py-2 bg-slate-700/40 rounded-lg border border-slate-700"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-slate-500 text-xs w-20 shrink-0">{nome}</span>
                        <span className="text-white text-sm font-medium">{String(brand)}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          const nuovi = { ...prodottiCasa };
                          delete nuovi[nome];
                          setFormData({ ...formData, prodotti_casa: nuovi });
                        }}
                        className="text-slate-600 hover:text-red-400 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
              <AddProdottoRow
                onAdd={(nome, brand) =>
                  setFormData({
                    ...formData,
                    prodotti_casa: { ...prodottiCasa, [nome]: brand },
                  })
                }
              />
            </SectionCard>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB: Add Colorazione Row
// ─────────────────────────────────────────────────────────────────────

function AddColorazioneRow({ onAdd }: { onAdd: (c: Colorazione) => void }) {
  const [data, setData] = useState(new Date().toISOString().split('T')[0]);
  const [colore, setColore] = useState('');
  const [tipo, setTipo] = useState('');

  const handleAdd = () => {
    if (!colore || !tipo) return;
    onAdd({
      id: `${Date.now()}-${Math.random().toString(36).substring(2, 8)}`,
      data,
      colore,
      tipo,
    });
    setColore('');
    setTipo('');
    setData(new Date().toISOString().split('T')[0]);
  };

  return (
    <div className="flex gap-2 p-4 bg-slate-800/40 border border-slate-700/40 rounded-xl">
      <Input
        type="date"
        value={data}
        onChange={(e) => setData(e.target.value)}
        className="bg-slate-700/50 border-slate-600 text-white w-36 shrink-0"
      />
      <Input
        placeholder="Colore (es: Castano 5)"
        value={colore}
        onChange={(e) => setColore(e.target.value)}
        className="bg-slate-700/50 border-slate-600 text-white placeholder:text-slate-500"
      />
      <select
        value={tipo}
        onChange={(e) => setTipo(e.target.value)}
        className="bg-slate-700/50 border border-slate-600 text-white rounded-lg px-3 text-sm focus:border-purple-500/50 focus:outline-none shrink-0"
      >
        <option value="">Tipo...</option>
        {['tinta', 'highlights', 'decolorazione', 'balayage', 'permanente', 'stiratura'].map((t) => (
          <option key={t} value={t} className="capitalize">{t.charAt(0).toUpperCase() + t.slice(1)}</option>
        ))}
      </select>
      <Button
        type="button"
        onClick={handleAdd}
        disabled={!colore || !tipo}
        className="bg-purple-600 hover:bg-purple-500 disabled:opacity-40 shrink-0"
      >
        <Plus className="w-4 h-4 mr-1" /> Aggiungi
      </Button>
    </div>
  );
}
