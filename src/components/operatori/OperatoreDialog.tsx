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
                  <FormItem><FormLabel className="text-slate-300">Colore</FormLabel><FormControl><div className="flex gap-2"><Input {...field} type="color" className="w-16 h-10 bg-slate-900 border-slate-700 cursor-pointer" /><Input {...field} placeholder="#C084FC" className="flex-1 bg-slate-900 border-slate-700 text-white" /></div></FormControl><FormMessage className="text-red-400" /></FormItem>
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
