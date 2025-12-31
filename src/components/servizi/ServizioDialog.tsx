// ═══════════════════════════════════════════════════════════════════
// FLUXION - Servizio Dialog
// Dialog for creating and editing servizi
// ═══════════════════════════════════════════════════════════════════

import { type FC, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  type Servizio,
  type CreateServizioInput,
  type UpdateServizioInput,
  createServizioSchema,
} from '@/types/servizio';
import { useCreateServizio, useUpdateServizio } from '@/hooks/use-servizi';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface ServizioDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  servizio?: Servizio;
  onSubmit: (data: CreateServizioInput | UpdateServizioInput) => void;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const ServizioDialog: FC<ServizioDialogProps> = ({
  open,
  onOpenChange,
  servizio,
  onSubmit: onSubmitCallback,
}) => {
  const isEditMode = !!servizio;
  const createMutation = useCreateServizio();
  const updateMutation = useUpdateServizio();

  const form = useForm<CreateServizioInput>({
    resolver: zodResolver(createServizioSchema),
    defaultValues: {
      nome: '',
      descrizione: '',
      categoria: '',
      prezzo: 0,
      iva_percentuale: 22,
      durata_minuti: 30,
      buffer_minuti: 0,
      colore: '#22D3EE',
      icona: '',
      attivo: 1,
      ordine: 0,
    },
  });

  // Populate form when editing
  useEffect(() => {
    if (servizio) {
      form.reset({
        nome: servizio.nome,
        descrizione: servizio.descrizione || '',
        categoria: servizio.categoria || '',
        prezzo: servizio.prezzo,
        iva_percentuale: servizio.iva_percentuale,
        durata_minuti: servizio.durata_minuti,
        buffer_minuti: servizio.buffer_minuti,
        colore: servizio.colore,
        icona: servizio.icona || '',
        attivo: servizio.attivo,
        ordine: servizio.ordine,
      });
    } else {
      form.reset({
        nome: '',
        descrizione: '',
        categoria: '',
        prezzo: 0,
        iva_percentuale: 22,
        durata_minuti: 30,
        buffer_minuti: 0,
        colore: '#22D3EE',
        icona: '',
        attivo: 1,
        ordine: 0,
      });
    }
  }, [servizio, form]);

  const onSubmit = async (data: CreateServizioInput) => {
    try {
      if (isEditMode) {
        await updateMutation.mutateAsync({ id: servizio.id, input: data });
      } else {
        await createMutation.mutateAsync(data);
      }
      onSubmitCallback(data);
      form.reset();
    } catch (error) {
      console.error('Failed to save servizio:', error);
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white">
            {isEditMode ? 'Modifica Servizio' : 'Nuovo Servizio'}
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            {isEditMode
              ? 'Modifica i dati del servizio. I campi contrassegnati con * sono obbligatori.'
              : 'Inserisci i dati del nuovo servizio. I campi contrassegnati con * sono obbligatori.'}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Base Info */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">
                INFORMAZIONI BASE
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="nome"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Nome *</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          placeholder="es. Taglio Uomo"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500 focus:border-cyan-500"
                        />
                      </FormControl>
                      <FormMessage className="text-red-400" />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="categoria"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Categoria</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          placeholder="es. Taglio, Colore, Trattamento"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                        />
                      </FormControl>
                      <FormMessage className="text-red-400" />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="descrizione"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Descrizione</FormLabel>
                    <FormControl>
                      <Textarea
                        {...field}
                        placeholder="Descrizione dettagliata del servizio..."
                        rows={3}
                        className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500 resize-none"
                      />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )}
              />
            </div>

            {/* Pricing */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">
                PREZZI E TEMPI
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="prezzo"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Prezzo (€) *</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="number"
                          step="0.01"
                          placeholder="25.00"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          onChange={(e) => {
                            const value = parseFloat(e.target.value);
                            field.onChange(isNaN(value) ? undefined : value);
                          }}
                        />
                      </FormControl>
                      <FormMessage className="text-red-400" />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="iva_percentuale"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">IVA (%)</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="number"
                          step="1"
                          placeholder="22"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          onChange={(e) => {
                            const value = parseFloat(e.target.value);
                            field.onChange(isNaN(value) ? undefined : value);
                          }}
                        />
                      </FormControl>
                      <FormMessage className="text-red-400" />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="durata_minuti"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Durata (minuti) *</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="number"
                          step="5"
                          placeholder="30"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          onChange={(e) => {
                            const value = parseInt(e.target.value);
                            field.onChange(isNaN(value) ? undefined : value);
                          }}
                        />
                      </FormControl>
                      <FormMessage className="text-red-400" />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="buffer_minuti"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Buffer (minuti)</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="number"
                          step="5"
                          placeholder="0"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          onChange={(e) => {
                            const value = parseInt(e.target.value);
                            field.onChange(isNaN(value) ? undefined : value);
                          }}
                        />
                      </FormControl>
                      <FormMessage className="text-red-400" />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* UI Customization */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">
                PERSONALIZZAZIONE UI
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="colore"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Colore</FormLabel>
                      <FormControl>
                        <div className="flex gap-2">
                          <Input
                            {...field}
                            type="color"
                            className="w-16 h-10 bg-slate-900 border-slate-700 cursor-pointer"
                          />
                          <Input
                            {...field}
                            placeholder="#22D3EE"
                            className="flex-1 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          />
                        </div>
                      </FormControl>
                      <FormMessage className="text-red-400" />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="ordine"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="text-slate-300">Ordine</FormLabel>
                      <FormControl>
                        <Input
                          {...field}
                          type="number"
                          placeholder="0"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          onChange={(e) => {
                            const value = parseInt(e.target.value);
                            field.onChange(isNaN(value) ? undefined : value);
                          }}
                        />
                      </FormControl>
                      <FormMessage className="text-red-400" />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="border-slate-700 text-slate-300 hover:bg-slate-800"
                disabled={isSubmitting}
              >
                Annulla
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting}
                className="bg-cyan-500 hover:bg-cyan-600 text-white"
              >
                {isSubmitting
                  ? 'Salvataggio...'
                  : isEditMode
                  ? 'Aggiorna Servizio'
                  : 'Crea Servizio'}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
