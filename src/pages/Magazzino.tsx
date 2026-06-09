// ═══════════════════════════════════════════════════════════════════
// FLUXION - Magazzino Page
// Inventario articoli + alert sottoscorta + movimenti carico/scarico
// Feature gating: "magazzino_alert" → Pro-only
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { toast } from 'sonner';
import {
  Package,
  Plus,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Loader2,
  Pencil,
  Trash2,
  Lock,
  Sparkles,
  Search,
  ChevronDown,
  ChevronUp,
  BarChart2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import {
  useArticoli,
  useSottoscorta,
  useCreaArticolo,
  useAggiornaArticolo,
  useEliminaArticolo,
  useSetSoglia,
  useRegistraMovimento,
  useRecomputeAlerts,
} from '@/hooks/use-magazzino';
import { useFeatureAccessEd25519, useLicenseStatusEd25519 } from '@/hooks/use-license-ed25519';
import type { Articolo, CreaArticoloInput, AggiornaArticoloInput } from '@/types/magazzino';

// ───────────────────────────────────────────────────────────────────
// Lock screen — feature non disponibile (Base tier)
// ───────────────────────────────────────────────────────────────────

const MagazzinoBloccato: FC<{ tier: string }> = ({ tier }) => (
  <div className="h-full flex items-center justify-center p-6">
    <Card className="bg-slate-800 border-slate-700 max-w-md w-full p-0 overflow-hidden">
      <div className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-amber-500/20 rounded-lg">
            <Lock className="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <p className="text-white font-semibold text-base">Magazzino non disponibile</p>
            <p className="text-sm text-slate-400">Aggiorna la tua licenza per sbloccare</p>
          </div>
        </div>
        <div className="bg-slate-900 p-4 rounded-lg text-center mb-4">
          <p className="text-slate-300 mb-2">
            La gestione del <span className="text-amber-400 font-medium">Magazzino</span> e degli{' '}
            <span className="text-amber-400 font-medium">Alert Sottoscorta</span> è disponibile
            nel piano <span className="text-cyan-400 font-medium">Pro</span>.
          </p>
          <p className="text-slate-500 text-sm">
            Piano attuale: <span className="text-cyan-400">{tier}</span>
          </p>
        </div>
        <div className="flex justify-center">
          <Button className="bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700">
            <Sparkles className="w-4 h-4 mr-2" />
            Aggiorna Licenza
          </Button>
        </div>
      </div>
    </Card>
  </div>
);

// ───────────────────────────────────────────────────────────────────
// Form Dialog — crea / modifica articolo
// ───────────────────────────────────────────────────────────────────

interface ArticoloFormState {
  nome: string;
  categoria: string;
  sogliaMinima: string;
  prezzoAcquisto: string;
  prezzoVendita: string;
  ean: string;
  fornitoreId: string;
}

const emptyForm = (): ArticoloFormState => ({
  nome: '',
  categoria: '',
  sogliaMinima: '0',
  prezzoAcquisto: '',
  prezzoVendita: '',
  ean: '',
  fornitoreId: '',
});

const formFromArticolo = (a: Articolo): ArticoloFormState => ({
  nome: a.nome,
  categoria: a.categoria ?? '',
  sogliaMinima: String(a.soglia_minima),
  prezzoAcquisto: a.prezzo_acquisto != null ? String(a.prezzo_acquisto) : '',
  prezzoVendita: a.prezzo_vendita != null ? String(a.prezzo_vendita) : '',
  ean: a.ean ?? '',
  fornitoreId: a.fornitore_id ?? '',
});

interface ArticoloDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  articolo?: Articolo;
  isSubmitting: boolean;
  onSubmit: (data: CreaArticoloInput | AggiornaArticoloInput) => void;
}

const ArticoloDialog: FC<ArticoloDialogProps> = ({
  open,
  onOpenChange,
  articolo,
  isSubmitting,
  onSubmit,
}) => {
  const [form, setForm] = useState<ArticoloFormState>(emptyForm);
  const isEdit = !!articolo;

  useEffect(() => {
    if (open) {
      setForm(articolo ? formFromArticolo(articolo) : emptyForm());
    }
  }, [open, articolo]);

  const set = (field: keyof ArticoloFormState) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.nome.trim()) {
      toast.error('Il nome articolo è obbligatorio');
      return;
    }
    const sogliaMinima = parseInt(form.sogliaMinima, 10);
    if (isNaN(sogliaMinima) || sogliaMinima < 0) {
      toast.error('La soglia minima deve essere un numero ≥ 0');
      return;
    }
    const base = {
      nome: form.nome.trim(),
      categoria: form.categoria.trim() || undefined,
      sogliaMinima,
      prezzoAcquisto: form.prezzoAcquisto ? parseFloat(form.prezzoAcquisto) : undefined,
      prezzoVendita: form.prezzoVendita ? parseFloat(form.prezzoVendita) : undefined,
      ean: form.ean.trim() || undefined,
      fornitoreId: form.fornitoreId.trim() || undefined,
    };

    if (isEdit && articolo) {
      onSubmit({ ...base, id: articolo.id } satisfies AggiornaArticoloInput);
    } else {
      onSubmit(base satisfies CreaArticoloInput);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-950 border-slate-800 max-w-lg">
        <DialogHeader>
          <DialogTitle className="text-white">
            {isEdit ? 'Modifica Articolo' : 'Nuovo Articolo'}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          {/* Nome */}
          <div className="space-y-1.5">
            <Label htmlFor="mag-nome" className="text-slate-300 text-sm">
              Nome <span className="text-red-400">*</span>
            </Label>
            <Input
              id="mag-nome"
              data-testid="articolo-nome"
              value={form.nome}
              onChange={set('nome')}
              placeholder="es. Shampoo professionale"
              className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
              autoFocus
            />
          </div>

          {/* Categoria + EAN */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="mag-categoria" className="text-slate-300 text-sm">Categoria</Label>
              <Input
                id="mag-categoria"
                data-testid="articolo-categoria"
                value={form.categoria}
                onChange={set('categoria')}
                placeholder="es. Cosmetici"
                className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="mag-ean" className="text-slate-300 text-sm">Codice EAN</Label>
              <Input
                id="mag-ean"
                data-testid="articolo-ean"
                value={form.ean}
                onChange={set('ean')}
                placeholder="es. 8001234567890"
                className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>
          </div>

          {/* Soglia minima */}
          <div className="space-y-1.5">
            <Label htmlFor="mag-soglia" className="text-slate-300 text-sm">
              Soglia minima (alert sottoscorta)
            </Label>
            <Input
              id="mag-soglia"
              data-testid="articolo-soglia"
              type="number"
              min={0}
              value={form.sogliaMinima}
              onChange={set('sogliaMinima')}
              className="bg-slate-900 border-slate-700 text-white"
            />
          </div>

          {/* Prezzi */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="mag-prezzo-acq" className="text-slate-300 text-sm">Prezzo acquisto (€)</Label>
              <Input
                id="mag-prezzo-acq"
                data-testid="articolo-prezzo-acquisto"
                type="number"
                min={0}
                step={0.01}
                value={form.prezzoAcquisto}
                onChange={set('prezzoAcquisto')}
                placeholder="0.00"
                className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="mag-prezzo-vend" className="text-slate-300 text-sm">Prezzo vendita (€)</Label>
              <Input
                id="mag-prezzo-vend"
                data-testid="articolo-prezzo-vendita"
                type="number"
                min={0}
                step={0.01}
                value={form.prezzoVendita}
                onChange={set('prezzoVendita')}
                placeholder="0.00"
                className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>
          </div>

          <DialogFooter className="gap-2 pt-2">
            <DialogClose asChild>
              <Button
                type="button"
                variant="outline"
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
              >
                Annulla
              </Button>
            </DialogClose>
            <Button
              type="submit"
              data-testid="articolo-submit"
              disabled={isSubmitting}
              className="bg-cyan-500 hover:bg-cyan-600 text-white"
            >
              {isSubmitting ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Salvataggio...</>
              ) : isEdit ? (
                'Salva modifiche'
              ) : (
                'Crea articolo'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// ───────────────────────────────────────────────────────────────────
// Movimento Dialog — carico / scarico
// ───────────────────────────────────────────────────────────────────

interface MovimentoDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  articolo: Articolo | null;
  tipo: 'carico' | 'scarico';
  isSubmitting: boolean;
  onSubmit: (quantita: number, causale: string) => void;
}

const MovimentoDialog: FC<MovimentoDialogProps> = ({
  open,
  onOpenChange,
  articolo,
  tipo,
  isSubmitting,
  onSubmit,
}) => {
  const [quantita, setQuantita] = useState('1');
  const [causale, setCausale] = useState('');

  useEffect(() => {
    if (open) {
      setQuantita('1');
      setCausale('');
    }
  }, [open]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const qty = parseInt(quantita, 10);
    if (isNaN(qty) || qty <= 0) {
      toast.error('La quantità deve essere maggiore di zero');
      return;
    }
    onSubmit(qty, causale.trim());
  };

  const colorAccent = tipo === 'carico' ? 'text-emerald-400' : 'text-red-400';
  const label = tipo === 'carico' ? 'Carico' : 'Scarico';

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-950 border-slate-800 max-w-sm">
        <DialogHeader>
          <DialogTitle className={cn('flex items-center gap-2', colorAccent)}>
            {tipo === 'carico' ? (
              <TrendingUp className="w-5 h-5" />
            ) : (
              <TrendingDown className="w-5 h-5" />
            )}
            {label}: {articolo?.nome}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          {articolo && (
            <p className="text-sm text-slate-400">
              Giacenza attuale:{' '}
              <span className="font-semibold text-white">{articolo.giacenza}</span>
            </p>
          )}
          <div className="space-y-1.5">
            <Label htmlFor="mov-quantita" className="text-slate-300 text-sm">
              Quantità <span className="text-red-400">*</span>
            </Label>
            <Input
              id="mov-quantita"
              data-testid="movimento-quantita"
              type="number"
              min={1}
              value={quantita}
              onChange={(e) => setQuantita(e.target.value)}
              className="bg-slate-900 border-slate-700 text-white"
              autoFocus
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="mov-causale" className="text-slate-300 text-sm">Causale</Label>
            <Input
              id="mov-causale"
              data-testid="movimento-causale"
              value={causale}
              onChange={(e) => setCausale(e.target.value)}
              placeholder="es. Acquisto fornitore, vendita..."
              className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
            />
          </div>
          <DialogFooter className="gap-2 pt-2">
            <DialogClose asChild>
              <Button
                type="button"
                variant="outline"
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
              >
                Annulla
              </Button>
            </DialogClose>
            <Button
              type="submit"
              data-testid="movimento-submit"
              disabled={isSubmitting}
              className={cn(
                'text-white',
                tipo === 'carico'
                  ? 'bg-emerald-600 hover:bg-emerald-700'
                  : 'bg-red-600 hover:bg-red-700',
              )}
            >
              {isSubmitting ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Registrazione...</>
              ) : (
                `Registra ${label}`
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// ───────────────────────────────────────────────────────────────────
// Soglia Inline Editor
// ───────────────────────────────────────────────────────────────────

interface SogliaEditorProps {
  articolo: Articolo;
  onSave: (id: string, soglia: number) => void;
  isSubmitting: boolean;
}

const SogliaEditor: FC<SogliaEditorProps> = ({ articolo, onSave, isSubmitting }) => {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(String(articolo.soglia_minima));

  const handleBlur = () => {
    const v = parseInt(value, 10);
    if (!isNaN(v) && v >= 0 && v !== articolo.soglia_minima) {
      onSave(articolo.id, v);
    }
    setEditing(false);
  };

  if (editing) {
    return (
      <Input
        data-testid={`soglia-input-${articolo.id}`}
        type="number"
        min={0}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={handleBlur}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleBlur();
          if (e.key === 'Escape') setEditing(false);
        }}
        className="w-20 h-7 text-xs bg-slate-800 border-slate-600 text-white px-2"
        autoFocus
        disabled={isSubmitting}
      />
    );
  }

  return (
    <button
      data-testid={`soglia-btn-${articolo.id}`}
      onClick={() => setEditing(true)}
      className="text-xs text-slate-400 hover:text-cyan-400 transition-colors underline-offset-2 hover:underline"
      title="Clicca per modificare la soglia"
    >
      ≥ {articolo.soglia_minima}
    </button>
  );
};

// ───────────────────────────────────────────────────────────────────
// Sottoscorta Banner
// ───────────────────────────────────────────────────────────────────

interface SottoscortaBannerProps {
  articoli: Articolo[];
  onCarico: (a: Articolo) => void;
  expanded: boolean;
  onToggle: () => void;
}

const SottoscortaBanner: FC<SottoscortaBannerProps> = ({
  articoli,
  onCarico,
  expanded,
  onToggle,
}) => {
  if (articoli.length === 0) return null;

  return (
    <Card
      className="relative overflow-hidden border-amber-500/30 bg-amber-950/20"
      data-testid="sottoscorta-banner"
    >
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-amber-500/50 to-transparent" />
      <div className="p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/15 border border-amber-500/30">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-amber-300">
                Sottoscorta — {articoli.length}{' '}
                {articoli.length === 1 ? 'articolo' : 'articoli'}
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Richiede riordino urgente
              </p>
            </div>
          </div>
          <button
            onClick={onToggle}
            data-testid="sottoscorta-toggle"
            className="p-1.5 rounded-lg hover:bg-slate-800 transition-colors text-slate-400 hover:text-white"
            aria-label={expanded ? 'Comprimi' : 'Espandi'}
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        {expanded && (
          <div className="mt-4 space-y-2">
            {articoli.map((a) => {
              const diff = a.soglia_minima - a.giacenza;
              return (
                <div
                  key={a.id}
                  data-testid={`sottoscorta-row-${a.id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-800/40 border border-amber-500/20 hover:bg-slate-800/60 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-2 h-2 rounded-full bg-amber-400 shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-white truncate">{a.nome}</p>
                      <p className="text-xs text-slate-500">
                        {a.categoria ?? 'Senza categoria'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 shrink-0 ml-3">
                    <div className="text-right">
                      <p className="text-sm font-bold text-amber-400">{a.giacenza}</p>
                      <p className="text-xs text-slate-500">giacenza</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-red-400 font-medium">−{diff} mancanti</p>
                    </div>
                    <Button
                      size="sm"
                      data-testid={`sottoscorta-carico-${a.id}`}
                      onClick={() => onCarico(a)}
                      className="h-7 px-3 text-xs bg-emerald-600 hover:bg-emerald-700 text-white"
                    >
                      <TrendingUp className="w-3 h-3 mr-1" />
                      Carico
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Card>
  );
};

// ───────────────────────────────────────────────────────────────────
// Row Articolo nella lista principale
// ───────────────────────────────────────────────────────────────────

interface ArticoloRowProps {
  articolo: Articolo;
  onEdit: (a: Articolo) => void;
  onDelete: (a: Articolo) => void;
  onCarico: (a: Articolo) => void;
  onScarico: (a: Articolo) => void;
  onSoglia: (id: string, soglia: number) => void;
  isSogliaSubmitting: boolean;
}

const ArticoloRow: FC<ArticoloRowProps> = ({
  articolo,
  onEdit,
  onDelete,
  onCarico,
  onScarico,
  onSoglia,
  isSogliaSubmitting,
}) => {
  const isSotto = articolo.giacenza <= articolo.soglia_minima;

  return (
    <div
      data-testid={`articolo-row-${articolo.id}`}
      className={cn(
        'flex items-center gap-4 p-3 rounded-lg border transition-all duration-200',
        'hover:bg-slate-800/50',
        isSotto
          ? 'bg-amber-950/10 border-amber-500/20 hover:border-amber-500/30'
          : 'bg-slate-800/20 border-slate-700/50 hover:border-slate-600',
      )}
    >
      {/* Status dot */}
      <div
        className={cn(
          'w-2 h-2 rounded-full shrink-0',
          isSotto ? 'bg-amber-400' : 'bg-emerald-400',
        )}
      />

      {/* Info articolo */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-white truncate">{articolo.nome}</p>
          {articolo.categoria && (
            <span className="text-xs px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700 shrink-0">
              {articolo.categoria}
            </span>
          )}
          {isSotto && (
            <Badge
              className="shrink-0 bg-amber-500/20 text-amber-300 border-amber-500/30 text-xs"
              data-testid={`articolo-alert-badge-${articolo.id}`}
            >
              Sottoscorta
            </Badge>
          )}
        </div>
        {articolo.ean && (
          <p className="text-xs text-slate-500 mt-0.5">EAN: {articolo.ean}</p>
        )}
      </div>

      {/* Giacenza */}
      <div className="text-right w-20 shrink-0">
        <p
          className={cn(
            'text-lg font-bold',
            isSotto ? 'text-amber-400' : 'text-white',
          )}
        >
          {articolo.giacenza}
        </p>
        <p className="text-xs text-slate-500">giacenza</p>
      </div>

      {/* Soglia */}
      <div className="text-right w-20 shrink-0">
        <SogliaEditor
          articolo={articolo}
          onSave={onSoglia}
          isSubmitting={isSogliaSubmitting}
        />
        <p className="text-xs text-slate-500">soglia</p>
      </div>

      {/* Prezzi */}
      {(articolo.prezzo_acquisto != null || articolo.prezzo_vendita != null) && (
        <div className="text-right w-24 shrink-0 hidden lg:block">
          {articolo.prezzo_vendita != null && (
            <p className="text-sm font-medium text-emerald-400">
              €{articolo.prezzo_vendita.toFixed(2)}
            </p>
          )}
          {articolo.prezzo_acquisto != null && (
            <p className="text-xs text-slate-500">
              acq. €{articolo.prezzo_acquisto.toFixed(2)}
            </p>
          )}
        </div>
      )}

      {/* Azioni */}
      <div className="flex items-center gap-1.5 shrink-0">
        <Button
          size="sm"
          data-testid={`carico-btn-${articolo.id}`}
          onClick={() => onCarico(articolo)}
          className="h-7 w-7 p-0 bg-emerald-600/20 hover:bg-emerald-600 text-emerald-400 hover:text-white border border-emerald-500/30 transition-all"
          title="Carico"
        >
          <TrendingUp className="w-3.5 h-3.5" />
        </Button>
        <Button
          size="sm"
          data-testid={`scarico-btn-${articolo.id}`}
          onClick={() => onScarico(articolo)}
          className="h-7 w-7 p-0 bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white border border-red-500/30 transition-all"
          title="Scarico"
        >
          <TrendingDown className="w-3.5 h-3.5" />
        </Button>
        <Button
          size="sm"
          data-testid={`edit-btn-${articolo.id}`}
          onClick={() => onEdit(articolo)}
          variant="ghost"
          className="h-7 w-7 p-0 text-slate-400 hover:text-white hover:bg-slate-700"
          title="Modifica"
        >
          <Pencil className="w-3.5 h-3.5" />
        </Button>
        <Button
          size="sm"
          data-testid={`delete-btn-${articolo.id}`}
          onClick={() => onDelete(articolo)}
          variant="ghost"
          className="h-7 w-7 p-0 text-slate-500 hover:text-red-400 hover:bg-red-500/10"
          title="Elimina"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </Button>
      </div>
    </div>
  );
};

// ───────────────────────────────────────────────────────────────────
// Main Page
// ───────────────────────────────────────────────────────────────────

export const Magazzino: FC = () => {
  const { data: hasAccess, isLoading: isLoadingAccess } = useFeatureAccessEd25519('magazzino_alert');
  const { data: licenseStatus, isLoading: isLoadingLicense } = useLicenseStatusEd25519();

  // Queries
  const { data: articoli = [], isLoading: isLoadingArticoli, error: articoliError } = useArticoli();
  const { data: sottoscorta = [] } = useSottoscorta();

  // Mutations
  const creaArticolo = useCreaArticolo();
  const aggiornaArticolo = useAggiornaArticolo();
  const eliminaArticolo = useEliminaArticolo();
  const setSoglia = useSetSoglia();
  const registraMovimento = useRegistraMovimento();
  const recomputeAlerts = useRecomputeAlerts();

  // Boot: ricalcola alert al mount
  useEffect(() => {
    recomputeAlerts.mutate(undefined, {
      onError: (err) => {
        // Non mostrare toast per errori di boot, solo log silenzioso
        void String(err);
      },
    });
     
  }, []);

  // UI state
  const [search, setSearch] = useState('');
  const [sottoscortaExpanded, setSottoscortaExpanded] = useState(true);

  // Dialog states
  const [articoloDialogOpen, setArticoloDialogOpen] = useState(false);
  const [selectedArticolo, setSelectedArticolo] = useState<Articolo | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [articoloToDelete, setArticoloToDelete] = useState<Articolo | undefined>();

  // Movimento dialog
  const [movimentoDialogOpen, setMovimentoDialogOpen] = useState(false);
  const [movimentoArticolo, setMovimentoArticolo] = useState<Articolo | null>(null);
  const [movimentoTipo, setMovimentoTipo] = useState<'carico' | 'scarico'>('carico');

  // Feature gate
  if (!isLoadingAccess && !isLoadingLicense && hasAccess === false) {
    return <MagazzinoBloccato tier={licenseStatus?.tier_display ?? 'Base'} />;
  }

  // Handlers — Articolo
  const handleNewArticolo = () => {
    setSelectedArticolo(undefined);
    setArticoloDialogOpen(true);
  };

  const handleEditArticolo = (a: Articolo) => {
    setSelectedArticolo(a);
    setArticoloDialogOpen(true);
  };

  const handleDeleteArticolo = (a: Articolo) => {
    setArticoloToDelete(a);
    setDeleteDialogOpen(true);
  };

  const handleArticoloSubmit = async (data: CreaArticoloInput | AggiornaArticoloInput) => {
    try {
      if ('id' in data) {
        await aggiornaArticolo.mutateAsync(data as AggiornaArticoloInput);
        toast.success('Articolo aggiornato');
      } else {
        await creaArticolo.mutateAsync(data as CreaArticoloInput);
        toast.success('Articolo creato');
      }
      setArticoloDialogOpen(false);
    } catch (err) {
      toast.error('Errore salvataggio articolo', { description: String(err) });
    }
  };

  const handleConfirmDelete = async () => {
    if (!articoloToDelete) return;
    try {
      await eliminaArticolo.mutateAsync(articoloToDelete.id);
      setDeleteDialogOpen(false);
      setArticoloToDelete(undefined);
      toast.success('Articolo eliminato');
    } catch (err) {
      toast.error('Errore eliminazione articolo', { description: String(err) });
    }
  };

  const handleSetSoglia = async (id: string, soglia: number) => {
    try {
      await setSoglia.mutateAsync({ id, sogliaMinima: soglia });
      toast.success('Soglia aggiornata');
    } catch (err) {
      toast.error('Errore aggiornamento soglia', { description: String(err) });
    }
  };

  // Handlers — Movimenti
  const openMovimento = (a: Articolo, tipo: 'carico' | 'scarico') => {
    setMovimentoArticolo(a);
    setMovimentoTipo(tipo);
    setMovimentoDialogOpen(true);
  };

  const handleMovimentoSubmit = async (quantita: number, causale: string) => {
    if (!movimentoArticolo) return;
    try {
      await registraMovimento.mutateAsync({
        articoloId: movimentoArticolo.id,
        tipo: movimentoTipo,
        quantita,
        causale: causale || undefined,
      });
      setMovimentoDialogOpen(false);
      toast.success(
        movimentoTipo === 'carico'
          ? `Carico di ${quantita} registrato`
          : `Scarico di ${quantita} registrato`,
      );
    } catch (err) {
      toast.error(
        movimentoTipo === 'carico' ? 'Errore carico' : 'Errore scarico',
        { description: String(err) },
      );
    }
  };

  // Filtro ricerca
  const filtered = articoli.filter((a) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      a.nome.toLowerCase().includes(q) ||
      (a.categoria?.toLowerCase().includes(q) ?? false) ||
      (a.ean?.includes(q) ?? false)
    );
  });

  // Statistiche header
  const totale = articoli.length;
  const totSottoscorta = sottoscorta.length;
  const totValore =
    articoli.reduce((sum, a) => {
      if (a.prezzo_acquisto != null) return sum + a.prezzo_acquisto * a.giacenza;
      return sum;
    }, 0);

  // Loading
  if (isLoadingArticoli) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
      </div>
    );
  }

  // Error
  if (articoliError) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-white">Magazzino</h1>
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
          <p className="text-red-400">
            Errore nel caricamento:{' '}
            {articoliError instanceof Error ? articoliError.message : 'Errore sconosciuto'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between" data-testid="magazzino-header">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Package className="w-8 h-8 text-cyan-500" />
            Magazzino
          </h1>
          <p className="text-slate-400 mt-1">
            {totale} {totale === 1 ? 'articolo' : 'articoli'}
            {totSottoscorta > 0 && (
              <span className="text-amber-400 ml-2">· {totSottoscorta} sottoscorta</span>
            )}
          </p>
        </div>
        <Button
          data-testid="new-articolo"
          onClick={handleNewArticolo}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          <Plus className="w-5 h-5 mr-2" />
          Nuovo Articolo
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="relative overflow-hidden p-5 border-slate-700/50 hover:border-slate-600 hover:shadow-lg hover:shadow-black/20 transition-all duration-200">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-400 mb-1.5">Totale Articoli</p>
              <p className="text-3xl font-bold text-white" data-testid="stats-totale">{totale}</p>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/50 text-cyan-400">
              <Package className="h-5 w-5" />
            </div>
          </div>
        </Card>

        <Card
          className={cn(
            'relative overflow-hidden p-5 border-slate-700/50 hover:shadow-lg hover:shadow-black/20 transition-all duration-200',
            totSottoscorta > 0
              ? 'border-amber-500/30 hover:border-amber-500/50'
              : 'hover:border-slate-600',
          )}
          data-testid="stats-sottoscorta"
        >
          <div
            className={cn(
              'absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent to-transparent',
              totSottoscorta > 0 ? 'via-amber-500/50' : 'via-slate-500/20',
            )}
          />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-400 mb-1.5">Sottoscorta</p>
              <p
                className={cn(
                  'text-3xl font-bold',
                  totSottoscorta > 0 ? 'text-amber-400' : 'text-emerald-400',
                )}
              >
                {totSottoscorta}
              </p>
              <p className="text-sm text-slate-500 mt-1.5">
                {totSottoscorta === 0 ? 'Tutto ok' : 'Richiede attenzione'}
              </p>
            </div>
            <div
              className={cn(
                'p-2.5 rounded-xl border',
                totSottoscorta > 0
                  ? 'bg-amber-500/10 border-amber-500/20 text-amber-400'
                  : 'bg-slate-800/80 border-slate-700/50 text-emerald-400',
              )}
            >
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>
        </Card>

        <Card className="relative overflow-hidden p-5 border-slate-700/50 hover:border-slate-600 hover:shadow-lg hover:shadow-black/20 transition-all duration-200">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-500/40 to-transparent" />
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-400 mb-1.5">Valore Magazzino</p>
              <p className="text-3xl font-bold text-emerald-400" data-testid="stats-valore">
                {new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(totValore)}
              </p>
              <p className="text-sm text-slate-500 mt-1.5">Prezzo acquisto</p>
            </div>
            <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/50 text-emerald-400">
              <BarChart2 className="h-5 w-5" />
            </div>
          </div>
        </Card>
      </div>

      {/* Sottoscorta Banner */}
      <SottoscortaBanner
        articoli={sottoscorta}
        onCarico={(a) => openMovimento(a, 'carico')}
        expanded={sottoscortaExpanded}
        onToggle={() => setSottoscortaExpanded((v) => !v)}
      />

      {/* Lista Articoli */}
      <div className="space-y-3">
        {/* Toolbar */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <Input
              data-testid="ricerca-articolo"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Cerca articolo..."
              className="pl-9 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
            />
          </div>
          <p className="text-sm text-slate-500">
            {filtered.length} {filtered.length === 1 ? 'risultato' : 'risultati'}
          </p>
        </div>

        {/* Header colonne */}
        <div className="flex items-center gap-4 px-3 text-xs text-slate-500 font-medium uppercase tracking-wide">
          <div className="w-2 shrink-0" />
          <div className="flex-1">Articolo</div>
          <div className="w-20 text-right shrink-0">Giacenza</div>
          <div className="w-20 text-right shrink-0">Soglia</div>
          <div className="w-24 text-right shrink-0 hidden lg:block">Prezzi</div>
          <div className="w-28 shrink-0" />
        </div>

        {/* Rows */}
        {filtered.length === 0 ? (
          <div className="text-center py-16" data-testid="articoli-empty">
            <div className="mx-auto w-14 h-14 rounded-2xl bg-slate-800/50 border border-slate-700/50 flex items-center justify-center mb-4">
              <Package className="w-7 h-7 text-slate-600" />
            </div>
            {search ? (
              <>
                <p className="text-slate-400 font-medium mb-1">Nessun articolo trovato</p>
                <p className="text-sm text-slate-500">Prova con un termine diverso</p>
              </>
            ) : (
              <>
                <p className="text-slate-400 font-medium mb-1">Magazzino vuoto</p>
                <p className="text-sm text-slate-500 mb-4">
                  Aggiungi il primo articolo cliccando il bottone in alto
                </p>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-1.5">
            {filtered.map((a) => (
              <ArticoloRow
                key={a.id}
                articolo={a}
                onEdit={handleEditArticolo}
                onDelete={handleDeleteArticolo}
                onCarico={(art) => openMovimento(art, 'carico')}
                onScarico={(art) => openMovimento(art, 'scarico')}
                onSoglia={handleSetSoglia}
                isSogliaSubmitting={setSoglia.isPending}
              />
            ))}
          </div>
        )}
      </div>

      {/* Articolo Dialog */}
      <ArticoloDialog
        open={articoloDialogOpen}
        onOpenChange={setArticoloDialogOpen}
        articolo={selectedArticolo}
        isSubmitting={creaArticolo.isPending || aggiornaArticolo.isPending}
        onSubmit={handleArticoloSubmit}
      />

      {/* Movimento Dialog */}
      <MovimentoDialog
        open={movimentoDialogOpen}
        onOpenChange={setMovimentoDialogOpen}
        articolo={movimentoArticolo}
        tipo={movimentoTipo}
        isSubmitting={registraMovimento.isPending}
        onSubmit={handleMovimentoSubmit}
      />

      {/* Delete Confirmation */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-slate-950 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Elimina Articolo</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Sei sicuro di voler eliminare{' '}
              <span className="font-semibold text-white">{articoloToDelete?.nome}</span>? Questa
              azione non può essere annullata.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Annulla
            </AlertDialogCancel>
            <AlertDialogAction
              data-testid="delete-confirm"
              onClick={handleConfirmDelete}
              disabled={eliminaArticolo.isPending}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {eliminaArticolo.isPending ? 'Eliminazione...' : 'Elimina'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
