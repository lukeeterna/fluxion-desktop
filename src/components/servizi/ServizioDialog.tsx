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
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

// Palette colori predefiniti per servizi
const COLOR_PALETTE = [
  '#EF4444', '#F97316', '#F59E0B', '#EAB308', '#84CC16', '#22C55E',
  '#10B981', '#14B8A6', '#06B6D4', '#0EA5E9', '#3B82F6', '#6366F1',
  '#8B5CF6', '#A855F7', '#D946EF', '#EC4899', '#F43F5E', '#78716C',
];

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
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="25.00"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          value={field.value === 0 ? '' : field.value}
                          onChange={(e) => {
                            const value = e.target.value === '' ? 0 : parseFloat(e.target.value);
                            field.onChange(isNaN(value) ? 0 : value);
                          }}
                          onBlur={field.onBlur}
                          name={field.name}
                          ref={field.ref}
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
                          type="number"
                          step="1"
                          min="0"
                          max="100"
                          placeholder="22"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          value={field.value ?? ''}
                          onChange={(e) => {
                            const value = e.target.value === '' ? 22 : parseFloat(e.target.value);
                            field.onChange(isNaN(value) ? 22 : value);
                          }}
                          onBlur={field.onBlur}
                          name={field.name}
                          ref={field.ref}
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
                          type="number"
                          step="5"
                          min="5"
                          placeholder="30"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          value={field.value === 0 ? '' : field.value}
                          onChange={(e) => {
                            const value = e.target.value === '' ? 0 : parseInt(e.target.value);
                            field.onChange(isNaN(value) ? 0 : value);
                          }}
                          onBlur={field.onBlur}
                          name={field.name}
                          ref={field.ref}
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
                          type="number"
                          step="5"
                          min="0"
                          placeholder="0"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          value={field.value === 0 ? '' : field.value}
                          onChange={(e) => {
                            const value = e.target.value === '' ? 0 : parseInt(e.target.value);
                            field.onChange(isNaN(value) ? 0 : value);
                          }}
                          onBlur={field.onBlur}
                          name={field.name}
                          ref={field.ref}
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
                          <Popover>
                            <PopoverTrigger asChild>
                              <button
                                type="button"
                                className="w-16 h-10 rounded-md border border-slate-700 cursor-pointer"
                                style={{ backgroundColor: field.value }}
                              />
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-3 bg-slate-900 border-slate-700" align="start">
                              <div className="grid grid-cols-6 gap-2">
                                {COLOR_PALETTE.map((color) => (
                                  <button
                                    key={color}
                                    type="button"
                                    className={`w-8 h-8 rounded-md border-2 transition-all ${
                                      field.value === color ? 'border-white scale-110' : 'border-transparent hover:border-slate-500'
                                    }`}
                                    style={{ backgroundColor: color }}
                                    onClick={() => field.onChange(color)}
                                  />
                                ))}
                              </div>
                            </PopoverContent>
                          </Popover>
                          <Input
                            value={field.value}
                            onChange={(e) => field.onChange(e.target.value)}
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
                          type="number"
                          min="0"
                          placeholder="0"
                          className="bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
                          value={field.value === 0 ? '' : field.value}
                          onChange={(e) => {
                            const value = e.target.value === '' ? 0 : parseInt(e.target.value);
                            field.onChange(isNaN(value) ? 0 : value);
                          }}
                          onBlur={field.onBlur}
                          name={field.name}
                          ref={field.ref}
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
