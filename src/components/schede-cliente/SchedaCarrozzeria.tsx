// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Carrozzeria Component (W2-D)
// Scheda cliente per carrozzerie — preventivi, sinistri, lavorazioni
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Badge } from '../ui/badge';
import { Switch } from '../ui/switch';
import { Textarea } from '../ui/textarea';
import { useSchedaCarrozzeria, useSaveSchedaCarrozzeria } from '../../hooks/use-schede-cliente';
import type { SchedaCarrozzeria as SchedaCarrozzeriaType } from '../../types/scheda-cliente';
import { toast } from 'sonner';
import { MediaUploadZone } from '../media/MediaUploadZone';
import { MediaGallery } from '../media/MediaGallery';
import { ImageAnnotator } from '../media/ImageAnnotator';
import type { Annotation } from '../media/ImageAnnotator';
import { readMediaAsDataUrl, useUpdateMediaNote, useExportMediaPdf } from '../../hooks/use-media';
import type { MediaRecord } from '../../types/media';
import {
  Car,
  FileText,
  Calendar,
  Shield,
  Save,
  Plus,
  Trash2,
  CheckCircle,
  Clock,
  Wrench,
  Camera,
  FileOutput,
  X,
} from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

const STATI_PRATICA = [
  { value: 'preventivo', label: 'Preventivo', color: 'text-slate-400' },
  { value: 'approvato', label: 'Approvato', color: 'text-amber-400' },
  { value: 'in_lavorazione', label: 'In lavorazione', color: 'text-blue-400' },
  { value: 'completato', label: 'Completato', color: 'text-teal-400' },
  { value: 'consegnato', label: 'Consegnato', color: 'text-green-400' },
] as const;

const TIPI_DANNO = [
  { value: 'ammaccatura', label: 'Ammaccatura' },
  { value: 'graffio', label: 'Graffio / Graffiatura' },
  { value: 'urto', label: 'Urto / Collisione' },
  { value: 'corrosione', label: 'Corrosione / Ruggine' },
  { value: 'rottura', label: 'Rottura vetro / specchio' },
] as const;

const ENTITA_DANNO = [
  { value: 'lieve', label: 'Lieve', color: 'text-green-400' },
  { value: 'media', label: 'Media', color: 'text-amber-400' },
  { value: 'grave', label: 'Grave', color: 'text-red-400' },
] as const;

const POSIZIONI_DANNO = [
  'Paraurti anteriore',
  'Paraurti posteriore',
  'Cofano',
  'Tetto',
  'Porta anteriore sx',
  'Porta anteriore dx',
  'Porta posteriore sx',
  'Porta posteriore dx',
  'Fiancata sinistra',
  'Fiancata destra',
  'Portellone',
  'Parafango ant. sx',
  'Parafango ant. dx',
  'Parafango post. sx',
  'Parafango post. dx',
  'Specchio sx',
  'Specchio dx',
  'Parabrezza',
  'Lunotto',
];

const LAVORAZIONI_COMUNI = [
  'Raddrizzatura',
  'Verniciatura',
  'Stuccatura',
  'Lucidatura',
  'Sostituzione pezzo',
  'Riparazione vetreria',
  'Smontaggio/rimontaggio',
  'Rimozione ruggine',
  'Trattamento antiruggine',
];

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Stato Badge
// ─────────────────────────────────────────────────────────────────────

function StatoBadge({ stato }: { stato: SchedaCarrozzeriaType['stato'] }) {
  const config = STATI_PRATICA.find((s) => s.value === stato);
  const icons: Record<string, React.ReactNode> = {
    preventivo: <FileText className="w-3 h-3" />,
    approvato: <CheckCircle className="w-3 h-3" />,
    in_lavorazione: <Wrench className="w-3 h-3" />,
    completato: <CheckCircle className="w-3 h-3" />,
    consegnato: <CheckCircle className="w-3 h-3" />,
  };
  return (
    <Badge variant="outline" className={`border-slate-600 ${config?.color ?? 'text-slate-400'} gap-1`}>
      {icons[stato]}
      {config?.label ?? stato}
    </Badge>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Pratica Form
// ─────────────────────────────────────────────────────────────────────

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Foto Fase Section (Entrata / Lavorazione / Uscita)
// ─────────────────────────────────────────────────────────────────────

type FaseCategoria = 'danno_veicolo' | 'lavorazione' | 'post_intervento';

function FaseFotoSection({
  clienteId,
  categoria,
  label,
}: {
  clienteId: number;
  categoria: FaseCategoria;
  label: string;
}) {
  const [selectedRecord, setSelectedRecord] = useState<MediaRecord | null>(null);
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const updateNote = useUpdateMediaNote(clienteId);

  useEffect(() => {
    if (!selectedRecord) { setImageSrc(null); return; }
    readMediaAsDataUrl(selectedRecord.media_path).then(setImageSrc).catch(() => setImageSrc(null));
    // Parse existing annotations from note field
    try {
      const parsed = JSON.parse(selectedRecord.note ?? '[]');
      setAnnotations(Array.isArray(parsed) ? parsed : []);
    } catch {
      setAnnotations([]);
    }
  }, [selectedRecord]);

  const handleAnnotationsChange = async (anns: Annotation[]) => {
    setAnnotations(anns);
    if (!selectedRecord) return;
    try {
      await updateNote.mutateAsync({ mediaId: selectedRecord.id, note: JSON.stringify(anns) });
    } catch {
      // silent — annotations saved on next reload
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-slate-300 text-sm font-medium">{label}</h4>
        <span className="text-slate-500 text-xs">Fase {label}</span>
      </div>

      <MediaUploadZone
        clienteId={clienteId}
        categoria={categoria}
        label={`Aggiungi foto ${label.toLowerCase()}`}
      />

      <MediaGallery
        clienteId={clienteId}
        tipo="foto"
        categoria={categoria}
        emptyMessage={`Nessuna foto ${label.toLowerCase()}`}
        onRecordClick={(record) => {
          setSelectedRecord(record === selectedRecord ? null : record);
        }}
      />

      {/* ImageAnnotator panel */}
      {selectedRecord && imageSrc && (
        <div className="border border-slate-700 rounded-lg p-3 bg-slate-950 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-medium">Annotazioni danno</span>
            <button
              type="button"
              onClick={() => setSelectedRecord(null)}
              className="text-slate-600 hover:text-slate-400"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
          <ImageAnnotator
            imageSrc={imageSrc}
            annotations={annotations}
            onChange={handleAnnotationsChange}
          />
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// SUB-COMPONENT: Tab Foto (Entrata / Lavorazione / Uscita)
// ─────────────────────────────────────────────────────────────────────

function TabFoto({ clienteId }: { clienteId: number }) {
  const exportPdf = useExportMediaPdf();

  const handleExport = async () => {
    try {
      const path = await exportPdf.mutateAsync({ clienteId, tipoReport: 'veicolo' });
      toast.success(`PDF salvato: ${path}`);
    } catch (e) {
      toast.error(`Errore export PDF: ${String(e)}`);
    }
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="entrata" className="w-full">
        <TabsList className="bg-slate-900 border border-slate-700 w-full grid grid-cols-3">
          <TabsTrigger value="entrata" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            Entrata
          </TabsTrigger>
          <TabsTrigger value="lavorazione" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            Lavorazione
          </TabsTrigger>
          <TabsTrigger value="uscita" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            Uscita
          </TabsTrigger>
        </TabsList>

        <TabsContent value="entrata" className="mt-3">
          <FaseFotoSection clienteId={clienteId} categoria="danno_veicolo" label="Entrata" />
        </TabsContent>
        <TabsContent value="lavorazione" className="mt-3">
          <FaseFotoSection clienteId={clienteId} categoria="lavorazione" label="Lavorazione" />
        </TabsContent>
        <TabsContent value="uscita" className="mt-3">
          <FaseFotoSection clienteId={clienteId} categoria="post_intervento" label="Uscita" />
        </TabsContent>
      </Tabs>

      {/* Export PDF */}
      <div className="pt-2 border-t border-slate-700/50 flex justify-end">
        <Button
          size="sm"
          variant="outline"
          className="border-slate-600 text-slate-300 hover:text-white hover:bg-slate-700 gap-1.5"
          onClick={handleExport}
          disabled={exportPdf.isPending}
        >
          <FileOutput className="w-3.5 h-3.5" />
          {exportPdf.isPending ? 'Generazione...' : 'Rapporto PDF'}
        </Button>
      </div>
    </div>
  );
}

function PraticaForm({
  pratica,
  clienteId,
  onSaved,
}: {
  pratica: SchedaCarrozzeriaType;
  clienteId: string;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<SchedaCarrozzeriaType>(pratica);
  const save = useSaveSchedaCarrozzeria();

  const update = <K extends keyof SchedaCarrozzeriaType>(key: K, value: SchedaCarrozzeriaType[K]) => {
    setForm((p) => ({ ...p, [key]: value }));
  };

  const toggleLavorazione = (lav: string) => {
    const curr = form.lavorazioni;
    update('lavorazioni', curr.includes(lav) ? curr.filter((l) => l !== lav) : [...curr, lav]);
  };

  const handleSave = async () => {
    try {
      await save.mutateAsync({ clienteId, data: form });
      toast.success('Pratica salvata');
      onSaved();
    } catch {
      toast.error('Errore nel salvataggio');
    }
  };

  return (
    <div className="space-y-4">
      <Tabs defaultValue="pratica" className="w-full">
        <TabsList className="bg-slate-900 border border-slate-700 w-full grid grid-cols-5">
          <TabsTrigger value="pratica" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <Car className="w-3 h-3 mr-1" />
            Danno
          </TabsTrigger>
          <TabsTrigger value="preventivo" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <FileText className="w-3 h-3 mr-1" />
            Prev.
          </TabsTrigger>
          <TabsTrigger value="consegna" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <Calendar className="w-3 h-3 mr-1" />
            Date
          </TabsTrigger>
          <TabsTrigger value="assicurazione" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <Shield className="w-3 h-3 mr-1" />
            Assic.
          </TabsTrigger>
          <TabsTrigger value="foto" className="text-xs data-[state=active]:bg-slate-700 data-[state=active]:text-white">
            <Camera className="w-3 h-3 mr-1" />
            Foto
          </TabsTrigger>
        </TabsList>

        {/* TAB: Danno */}
        <TabsContent value="pratica" className="mt-4 space-y-4">
          <div>
            <Label className="text-slate-400 text-xs mb-2 block">Stato pratica</Label>
            <div className="flex flex-wrap gap-2">
              {STATI_PRATICA.map((s) => (
                <button
                  key={s.value}
                  onClick={() => update('stato', s.value)}
                  className={`px-3 py-1.5 rounded-lg border text-sm transition-colors ${
                    form.stato === s.value
                      ? 'bg-slate-700 border-slate-500 text-white'
                      : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Tipo danno</Label>
              <select
                value={form.tipo_danno ?? ''}
                onChange={(e) => update('tipo_danno', e.target.value as SchedaCarrozzeriaType['tipo_danno'])}
                className="w-full h-10 rounded-md border border-slate-700 bg-slate-900 text-white px-3"
              >
                <option value="">Seleziona...</option>
                {TIPI_DANNO.map((t) => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Entità</Label>
              <select
                value={form.entita_danno ?? ''}
                onChange={(e) => update('entita_danno', e.target.value as SchedaCarrozzeriaType['entita_danno'])}
                className="w-full h-10 rounded-md border border-slate-700 bg-slate-900 text-white px-3"
              >
                <option value="">Seleziona...</option>
                {ENTITA_DANNO.map((e) => (
                  <option key={e.value} value={e.value}>{e.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <Label className="text-slate-400 text-xs mb-1 block">Posizione danno</Label>
            <select
              value={form.posizione_danno ?? ''}
              onChange={(e) => update('posizione_danno', e.target.value)}
              className="w-full h-10 rounded-md border border-slate-700 bg-slate-900 text-white px-3"
            >
              <option value="">Seleziona...</option>
              {POSIZIONI_DANNO.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div>
            <Label className="text-slate-400 text-xs mb-1 block">Descrizione danno</Label>
            <Textarea
              value={form.descrizione_danno ?? ''}
              onChange={(e) => update('descrizione_danno', e.target.value)}
              placeholder="Descrivere il danno in dettaglio..."
              className="bg-slate-900 border-slate-700 text-white min-h-[100px]"
            />
          </div>
        </TabsContent>

        {/* TAB: Preventivo */}
        <TabsContent value="preventivo" className="mt-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Numero preventivo</Label>
              <Input
                value={form.preventivo_numero ?? ''}
                onChange={(e) => update('preventivo_numero', e.target.value)}
                placeholder="es. PREV-2026-001"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-400 text-xs mb-1 block">Importo preventivo (€)</Label>
              <Input
                type="number"
                step="0.01"
                value={form.importo_preventivo ?? ''}
                onChange={(e) => update('importo_preventivo', parseFloat(e.target.value) || undefined)}
                placeholder="es. 850.00"
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-900 rounded-lg border border-slate-700">
            <div>
              <p className="text-white text-sm font-medium">Preventivo approvato</p>
              <p className="text-slate-500 text-xs">Cliente ha accettato il preventivo</p>
            </div>
            <Switch
              checked={form.approvato}
              onCheckedChange={(v) => update('approvato', v)}
            />
          </div>

          <div>
            <Label className="text-slate-400 text-xs mb-2 block">Lavorazioni incluse</Label>
            <div className="flex flex-wrap gap-2">
              {LAVORAZIONI_COMUNI.map((lav) => (
                <button
                  key={lav}
                  onClick={() => toggleLavorazione(lav)}
                  className={`px-2.5 py-1 rounded-full text-xs border transition-colors ${
                    form.lavorazioni.includes(lav)
                      ? 'bg-blue-600/20 border-blue-500 text-blue-400'
                      : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500'
                  }`}
                >
                  {lav}
                </button>
              ))}
            </div>
            {/* Lavorazioni custom */}
            <div className="mt-2">
              {form.lavorazioni.filter((l) => !LAVORAZIONI_COMUNI.includes(l)).map((l) => (
                <Badge key={l} variant="outline" className="border-blue-500/50 text-blue-400 text-xs mr-1 gap-1">
                  {l}
                  <button onClick={() => toggleLavorazione(l)}>
                    <Trash2 className="w-2.5 h-2.5" />
                  </button>
                </Badge>
              ))}
            </div>
          </div>

          <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 space-y-3">
            <h4 className="text-white text-sm font-medium">Verniciatura</h4>
            <div className="flex items-center justify-between">
              <p className="text-slate-400 text-sm">Richiede verniciatura</p>
              <Switch
                checked={form.verniciatura}
                onCheckedChange={(v) => update('verniciatura', v)}
              />
            </div>
            {form.verniciatura && (
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Codice colore</Label>
                <Input
                  value={form.codice_colore ?? ''}
                  onChange={(e) => update('codice_colore', e.target.value.toUpperCase())}
                  placeholder="es. LB9A (VW Bianco Puro)"
                  className="bg-slate-800 border-slate-700 text-white font-mono"
                />
              </div>
            )}
          </div>
        </TabsContent>

        {/* TAB: Date */}
        <TabsContent value="consegna" className="mt-4 space-y-4">
          <div className="space-y-3">
            <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
              <div className="flex items-center gap-2 mb-3">
                <Clock className="w-4 h-4 text-blue-400" />
                <h4 className="text-white text-sm font-medium">Date pratica</h4>
              </div>
              <div className="space-y-3">
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Data ingresso veicolo</Label>
                  <Input
                    type="date"
                    value={form.data_ingresso ?? ''}
                    onChange={(e) => update('data_ingresso', e.target.value)}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Consegna prevista</Label>
                  <Input
                    type="date"
                    value={form.data_consegna_prevista ?? ''}
                    onChange={(e) => update('data_consegna_prevista', e.target.value)}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-400 text-xs mb-1 block">Consegna effettiva</Label>
                  <Input
                    type="date"
                    value={form.data_consegna_effettiva ?? ''}
                    onChange={(e) => update('data_consegna_effettiva', e.target.value)}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
              </div>
            </div>

            {/* Riepilogo tempistiche */}
            {form.data_ingresso && form.data_consegna_prevista && (
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                <p className="text-blue-400 text-sm">
                  Durata prevista:{' '}
                  <span className="font-medium">
                    {Math.round(
                      (new Date(form.data_consegna_prevista).getTime() -
                        new Date(form.data_ingresso).getTime()) /
                        (1000 * 60 * 60 * 24)
                    )}{' '}
                    giorni
                  </span>
                </p>
              </div>
            )}
          </div>
        </TabsContent>

        {/* TAB: Assicurazione */}
        <TabsContent value="assicurazione" className="mt-4 space-y-4">
          <div className="flex items-center justify-between p-3 bg-slate-900 rounded-lg border border-slate-700">
            <div>
              <p className="text-white text-sm font-medium">Sinistro assicurativo</p>
              <p className="text-slate-500 text-xs">La pratica è coperta da assicurazione</p>
            </div>
            <Switch
              checked={form.sinistro_assicurativo}
              onCheckedChange={(v) => update('sinistro_assicurativo', v)}
            />
          </div>

          {form.sinistro_assicurativo && (
            <div className="space-y-3">
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Compagnia assicurativa</Label>
                <Input
                  value={form.compagnia ?? ''}
                  onChange={(e) => update('compagnia', e.target.value)}
                  placeholder="es. Generali, AXA, Unipol..."
                  className="bg-slate-900 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-400 text-xs mb-1 block">Numero sinistro</Label>
                <Input
                  value={form.numero_sinistro ?? ''}
                  onChange={(e) => update('numero_sinistro', e.target.value)}
                  placeholder="es. SIN-2026-00123"
                  className="bg-slate-900 border-slate-700 text-white font-mono"
                />
              </div>
              <div className="bg-teal-500/10 border border-teal-500/30 rounded-lg p-3">
                <div className="flex items-center gap-2 text-teal-400 text-sm">
                  <Shield className="w-4 h-4" />
                  <span>Pratica assicurativa attiva</span>
                </div>
              </div>
            </div>
          )}

          {!form.sinistro_assicurativo && (
            <div className="text-center py-6 text-slate-500">
              <Shield className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Nessun sinistro assicurativo</p>
              <p className="text-xs">Attiva l'interruttore sopra per aggiungere i dati</p>
            </div>
          )}
        </TabsContent>

        {/* TAB: Foto — Workflow Entrata / Lavorazione / Uscita */}
        <TabsContent value="foto" className="mt-4">
          {pratica.id ? (
            <TabFoto clienteId={parseInt(clienteId, 10)} />
          ) : (
            <div className="text-center py-8 text-slate-500">
              <Camera className="w-10 h-10 mx-auto mb-2 opacity-30" />
              <p className="text-sm">Salva prima la pratica per aggiungere foto</p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      <div className="flex justify-end pt-2">
        <Button
          onClick={handleSave}
          disabled={save.isPending}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Save className="w-4 h-4 mr-2" />
          {save.isPending ? 'Salvataggio...' : 'Salva Pratica'}
        </Button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// MAIN COMPONENT: SchedaCarrozzeria
// ─────────────────────────────────────────────────────────────────────

export function SchedaCarrozzeria({ clienteId }: { clienteId: string }) {
  const { data: pratiche, isLoading } = useSchedaCarrozzeria(clienteId);
  const [selectedId, setSelectedId] = useState<string | 'new' | null>(null);

  const newPratica: SchedaCarrozzeriaType = {
    cliente_id: clienteId,
    foto_pre: [],
    foto_post: [],
    lavorazioni: [],
    approvato: false,
    verniciatura: false,
    sinistro_assicurativo: false,
    stato: 'preventivo',
  };

  if (isLoading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8 text-center text-slate-400">Caricamento...</CardContent>
      </Card>
    );
  }

  const praticheLista = pratiche ?? [];
  const selectedPratica =
    selectedId === 'new'
      ? newPratica
      : praticheLista.find((p) => p.id === selectedId) ?? null;

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/20 rounded-lg">
            <Car className="w-6 h-6 text-indigo-500" />
          </div>
          <div>
            <CardTitle className="text-white">Scheda Carrozzeria</CardTitle>
            <p className="text-sm text-slate-400">
              {praticheLista.length} {praticheLista.length === 1 ? 'pratica' : 'pratiche'} registrate
            </p>
          </div>
        </div>
        <Button
          size="sm"
          variant="outline"
          className="border-slate-600 text-slate-300 hover:text-white hover:bg-slate-700"
          onClick={() => setSelectedId('new')}
        >
          <Plus className="w-4 h-4 mr-1" />
          Nuova Pratica
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Lista pratiche */}
        {praticheLista.length > 0 && (
          <div className="space-y-2">
            {praticheLista.map((p) => (
              <button
                key={p.id}
                onClick={() => setSelectedId(p.id ?? null)}
                className={`w-full flex items-center justify-between p-3 rounded-lg border transition-colors text-left ${
                  selectedId === p.id
                    ? 'bg-indigo-600/20 border-indigo-500'
                    : 'bg-slate-900 border-slate-700 hover:border-slate-500'
                }`}
              >
                <div className="flex items-center gap-3">
                  <StatoBadge stato={p.stato} />
                  <div>
                    <p className="text-white text-sm">
                      {p.tipo_danno ? TIPI_DANNO.find((t) => t.value === p.tipo_danno)?.label : 'Pratica'}
                      {p.posizione_danno ? ` — ${p.posizione_danno}` : ''}
                    </p>
                    {p.data_ingresso && (
                      <p className="text-slate-500 text-xs">Ingresso: {p.data_ingresso}</p>
                    )}
                  </div>
                </div>
                {p.importo_preventivo !== undefined && (
                  <span className="text-teal-400 text-sm font-medium">
                    € {p.importo_preventivo.toFixed(2)}
                  </span>
                )}
              </button>
            ))}
          </div>
        )}

        {/* Nessuna pratica */}
        {praticheLista.length === 0 && !selectedPratica && (
          <div className="text-center py-8 text-slate-500">
            <Car className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p className="text-sm">Nessuna pratica registrata</p>
            <p className="text-xs mt-1">Clicca "Nuova Pratica" per creare</p>
          </div>
        )}

        {/* Form pratica selezionata */}
        {selectedPratica && (
          <div className="border border-slate-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <h3 className="text-white font-medium">
                  {selectedId === 'new' ? 'Nuova Pratica' : 'Modifica Pratica'}
                </h3>
                {selectedId !== 'new' && <StatoBadge stato={selectedPratica.stato} />}
              </div>
              <Button
                size="sm"
                variant="ghost"
                className="text-slate-500 hover:text-slate-300 text-xs h-7"
                onClick={() => setSelectedId(null)}
              >
                Chiudi
              </Button>
            </div>
            <PraticaForm
              pratica={selectedPratica}
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
