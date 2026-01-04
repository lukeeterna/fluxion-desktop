import { type FC, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { type Operatore, type CreateOperatoreInput, createOperatoreSchema } from '@/types/operatore';
import { useCreateOperatore, useUpdateOperatore } from '@/hooks/use-operatori';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';

// Palette colori predefiniti per operatori
const COLOR_PALETTE = [
  '#EF4444', '#F97316', '#F59E0B', '#EAB308', '#84CC16', '#22C55E',
  '#10B981', '#14B8A6', '#06B6D4', '#0EA5E9', '#3B82F6', '#6366F1',
  '#8B5CF6', '#A855F7', '#D946EF', '#EC4899', '#F43F5E', '#78716C',
];

interface OperatoreDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  operatore?: Operatore;
  onSubmit: () => void;
}

export const OperatoreDialog: FC<OperatoreDialogProps> = ({ open, onOpenChange, operatore, onSubmit: onSubmitCallback }) => {
  const isEditMode = !!operatore;
  const createMutation = useCreateOperatore();
  const updateMutation = useUpdateOperatore();

  const form = useForm<CreateOperatoreInput>({
    resolver: zodResolver(createOperatoreSchema),
    defaultValues: { nome: '', cognome: '', email: '', telefono: '', ruolo: 'operatore', colore: '#C084FC', avatar_url: '', attivo: 1 },
  });

  useEffect(() => {
    if (operatore) {
      form.reset({ nome: operatore.nome, cognome: operatore.cognome, email: operatore.email || '', telefono: operatore.telefono || '', ruolo: operatore.ruolo as any, colore: operatore.colore, avatar_url: operatore.avatar_url || '', attivo: operatore.attivo });
    } else {
      form.reset({ nome: '', cognome: '', email: '', telefono: '', ruolo: 'operatore', colore: '#C084FC', avatar_url: '', attivo: 1 });
    }
  }, [operatore, form]);

  const onSubmit = async (data: CreateOperatoreInput) => {
    try {
      if (isEditMode) {
        await updateMutation.mutateAsync({ id: operatore.id, input: data });
      } else {
        await createMutation.mutateAsync(data);
      }
      onSubmitCallback();
      form.reset();
    } catch (error) {
      console.error('Failed to save operatore:', error);
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white">{isEditMode ? 'Modifica Operatore' : 'Nuovo Operatore'}</DialogTitle>
          <DialogDescription className="text-slate-400">{isEditMode ? 'Modifica i dati dell\'operatore.' : 'Inserisci i dati del nuovo operatore.'}</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">ANAGRAFICA</h3>
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="nome" render={({ field }) => (
                  <FormItem><FormLabel className="text-slate-300">Nome *</FormLabel><FormControl><Input {...field} placeholder="Mario" className="bg-slate-900 border-slate-700 text-white" /></FormControl><FormMessage className="text-red-400" /></FormItem>
                )} />
                <FormField control={form.control} name="cognome" render={({ field }) => (
                  <FormItem><FormLabel className="text-slate-300">Cognome *</FormLabel><FormControl><Input {...field} placeholder="Rossi" className="bg-slate-900 border-slate-700 text-white" /></FormControl><FormMessage className="text-red-400" /></FormItem>
                )} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="email" render={({ field }) => (
                  <FormItem><FormLabel className="text-slate-300">Email</FormLabel><FormControl><Input {...field} type="email" placeholder="mario@example.com" className="bg-slate-900 border-slate-700 text-white" /></FormControl><FormMessage className="text-red-400" /></FormItem>
                )} />
                <FormField control={form.control} name="telefono" render={({ field }) => (
                  <FormItem><FormLabel className="text-slate-300">Telefono</FormLabel><FormControl><Input {...field} placeholder="+39 333 1234567" className="bg-slate-900 border-slate-700 text-white" /></FormControl><FormMessage className="text-red-400" /></FormItem>
                )} />
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">RUOLO E UI</h3>
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="ruolo" render={({ field }) => (
                  <FormItem><FormLabel className="text-slate-300">Ruolo</FormLabel><Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl><SelectTrigger className="bg-slate-900 border-slate-700 text-white"><SelectValue placeholder="Seleziona ruolo" /></SelectTrigger></FormControl>
                    <SelectContent className="bg-slate-900 border-slate-700"><SelectItem value="admin">Admin</SelectItem><SelectItem value="operatore">Operatore</SelectItem><SelectItem value="reception">Reception</SelectItem></SelectContent>
                  </Select><FormMessage className="text-red-400" /></FormItem>
                )} />
                <FormField control={form.control} name="colore" render={({ field }) => (
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
                          placeholder="#C084FC"
                          className="flex-1 bg-slate-900 border-slate-700 text-white"
                        />
                      </div>
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )} />
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)} className="border-slate-700 text-slate-300 hover:bg-slate-800" disabled={isSubmitting}>Annulla</Button>
              <Button type="submit" disabled={isSubmitting} className="bg-cyan-500 hover:bg-cyan-600 text-white">{isSubmitting ? 'Salvataggio...' : isEditMode ? 'Aggiorna' : 'Crea Operatore'}</Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
