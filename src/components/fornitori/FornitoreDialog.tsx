// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fornitore Dialog Component
// Create/Edit supplier dialog with form
// ═══════════════════════════════════════════════════════════════════

import { type FC, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2 } from 'lucide-react';
import type { Supplier, CreateSupplierInput, UpdateSupplierInput } from '@/types/supplier';

interface FornitoreDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fornitore?: Supplier;
  onSubmit: (data: CreateSupplierInput | UpdateSupplierInput) => Promise<void>;
  isSubmitting: boolean;
}

interface FormData {
  nome: string;
  email: string;
  telefono: string;
  partita_iva: string;
  indirizzo: string;
  citta: string;
  cap: string;
  provincia: string;
  paese: string;
  iban: string;
  note: string;
  categoria: string;
  status: 'active' | 'inactive' | 'blocked';
}

const CATEGORIE_FORNITORE = [
  'Prodotti',
  'Attrezzature',
  'Servizi',
  'Materiali',
  'Software',
  'Consulenza',
  'Altro',
];

export const FornitoreDialog: FC<FornitoreDialogProps> = ({
  open,
  onOpenChange,
  fornitore,
  onSubmit,
  isSubmitting,
}) => {
  const isEdit = !!fornitore;

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      nome: '',
      email: '',
      telefono: '',
      partita_iva: '',
      indirizzo: '',
      citta: '',
      cap: '',
      provincia: '',
      paese: 'Italia',
      iban: '',
      note: '',
      categoria: '',
      status: 'active',
    },
  });

  const status = watch('status');
  const categoria = watch('categoria');

  // Reset form when dialog opens/closes or fornitore changes
  useEffect(() => {
    if (open) {
      if (fornitore) {
        reset({
          nome: fornitore.nome,
          email: fornitore.email || '',
          telefono: fornitore.telefono || '',
          partita_iva: fornitore.partita_iva || '',
          indirizzo: fornitore.indirizzo || '',
          citta: fornitore.citta || '',
          cap: fornitore.cap || '',
          provincia: fornitore.provincia || '',
          paese: fornitore.paese || 'Italia',
          iban: fornitore.iban || '',
          note: fornitore.note || '',
          categoria: fornitore.categoria || '',
          status: fornitore.status,
        });
      } else {
        reset({
          nome: '',
          email: '',
          telefono: '',
          partita_iva: '',
          indirizzo: '',
          citta: '',
          cap: '',
          provincia: '',
          paese: 'Italia',
          iban: '',
          note: '',
          categoria: '',
          status: 'active',
        });
      }
    }
  }, [open, fornitore, reset]);

  const onFormSubmit = async (data: FormData) => {
    if (isEdit && fornitore) {
      await onSubmit({
        id: fornitore.id,
        nome: data.nome,
        email: data.email || undefined,
        telefono: data.telefono || undefined,
        partita_iva: data.partita_iva || undefined,
        indirizzo: data.indirizzo || undefined,
        citta: data.citta || undefined,
        cap: data.cap || undefined,
        provincia: data.provincia || undefined,
        paese: data.paese || undefined,
        iban: data.iban || undefined,
        note: data.note || undefined,
        categoria: data.categoria || undefined,
        status: data.status,
      });
    } else {
      await onSubmit({
        nome: data.nome,
        email: data.email || undefined,
        telefono: data.telefono || undefined,
        partita_iva: data.partita_iva || undefined,
        indirizzo: data.indirizzo || undefined,
        citta: data.citta || undefined,
        cap: data.cap || undefined,
        provincia: data.provincia || undefined,
        paese: data.paese || undefined,
        iban: data.iban || undefined,
        note: data.note || undefined,
        categoria: data.categoria || undefined,
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-950 border-slate-800 max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-white">
            {isEdit ? 'Modifica Fornitore' : 'Nuovo Fornitore'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
          {/* Dati Principali */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-slate-400">Dati Principali</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <Label htmlFor="nome" className="text-slate-300">
                  Nome / Ragione Sociale *
                </Label>
                <Input
                  id="nome"
                  {...register('nome', { required: 'Nome obbligatorio' })}
                  className="bg-slate-900 border-slate-700 text-white"
                  placeholder="Es: Forniture Italia Srl"
                />
                {errors.nome && (
                  <span className="text-red-400 text-sm">{errors.nome.message}</span>
                )}
              </div>

              <div>
                <Label htmlFor="telefono" className="text-slate-300">
                  Telefono
                </Label>
                <Input
                  id="telefono"
                  {...register('telefono')}
                  className="bg-slate-900 border-slate-700 text-white"
                  placeholder="Es: +39 02 1234567"
                />
              </div>

              <div>
                <Label htmlFor="email" className="text-slate-300">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  {...register('email')}
                  className="bg-slate-900 border-slate-700 text-white"
                  placeholder="Es: ordini@fornitore.it"
                />
              </div>

              <div>
                <Label htmlFor="partita_iva" className="text-slate-300">
                  Partita IVA
                </Label>
                <Input
                  id="partita_iva"
                  {...register('partita_iva')}
                  className="bg-slate-900 border-slate-700 text-white font-mono"
                  placeholder="Es: IT12345678901"
                />
              </div>

              <div>
                <Label htmlFor="categoria" className="text-slate-300">
                  Categoria
                </Label>
                <Select
                  value={categoria}
                  onValueChange={(value) => setValue('categoria', value)}
                >
                  <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                    <SelectValue placeholder="Seleziona categoria" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-700">
                    {CATEGORIE_FORNITORE.map((cat) => (
                      <SelectItem key={cat} value={cat} className="text-white">
                        {cat}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Indirizzo */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-slate-400">Indirizzo</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <Label htmlFor="indirizzo" className="text-slate-300">
                  Via / Indirizzo
                </Label>
                <Input
                  id="indirizzo"
                  {...register('indirizzo')}
                  className="bg-slate-900 border-slate-700 text-white"
                  placeholder="Es: Via Roma 123"
                />
              </div>

              <div>
                <Label htmlFor="citta" className="text-slate-300">
                  Citta
                </Label>
                <Input
                  id="citta"
                  {...register('citta')}
                  className="bg-slate-900 border-slate-700 text-white"
                  placeholder="Es: Milano"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <Label htmlFor="cap" className="text-slate-300">
                    CAP
                  </Label>
                  <Input
                    id="cap"
                    {...register('cap')}
                    className="bg-slate-900 border-slate-700 text-white"
                    placeholder="20100"
                  />
                </div>
                <div>
                  <Label htmlFor="provincia" className="text-slate-300">
                    Prov.
                  </Label>
                  <Input
                    id="provincia"
                    {...register('provincia')}
                    className="bg-slate-900 border-slate-700 text-white"
                    placeholder="MI"
                    maxLength={2}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Pagamento */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-slate-400">Pagamento</h3>
            <div>
              <Label htmlFor="iban" className="text-slate-300">
                IBAN
              </Label>
              <Input
                id="iban"
                {...register('iban')}
                className="bg-slate-900 border-slate-700 text-white font-mono"
                placeholder="IT60X0542811101000000123456"
              />
            </div>
          </div>

          {/* Status (solo in edit) */}
          {isEdit && (
            <div className="space-y-4">
              <h3 className="text-sm font-medium text-slate-400">Stato</h3>
              <Select
                value={status}
                onValueChange={(value: 'active' | 'inactive' | 'blocked') =>
                  setValue('status', value)
                }
              >
                <SelectTrigger className="bg-slate-900 border-slate-700 text-white w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-700">
                  <SelectItem value="active" className="text-white">
                    Attivo
                  </SelectItem>
                  <SelectItem value="inactive" className="text-white">
                    Inattivo
                  </SelectItem>
                  <SelectItem value="blocked" className="text-white">
                    Bloccato
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* Note */}
          <div>
            <Label htmlFor="note" className="text-slate-300">
              Note
            </Label>
            <Textarea
              id="note"
              {...register('note')}
              className="bg-slate-900 border-slate-700 text-white resize-none"
              rows={3}
              placeholder="Note interne sul fornitore..."
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="border-slate-700 text-slate-300 hover:bg-slate-800"
            >
              Annulla
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-cyan-500 hover:bg-cyan-600 text-white"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              {isEdit ? 'Salva Modifiche' : 'Crea Fornitore'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
