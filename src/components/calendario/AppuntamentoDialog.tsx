import { type FC, useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createAppuntamentoSchema, type CreateAppuntamentoInput } from '@/types/appuntamento';
import { useCreateAppuntamento } from '@/hooks/use-appuntamenti';
import { useClienti } from '@/hooks/use-clienti';
import { useServizi } from '@/hooks/use-servizi';
import { useOperatori } from '@/hooks/use-operatori';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

interface AppuntamentoDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  initialDate?: string;
  onSuccess: () => void;
}

export const AppuntamentoDialog: FC<AppuntamentoDialogProps> = ({ open, onOpenChange, initialDate, onSuccess }) => {
  const createMutation = useCreateAppuntamento();
  const { data: clienti } = useClienti();
  const { data: servizi } = useServizi();
  const { data: operatori } = useOperatori();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const form = useForm<CreateAppuntamentoInput>({
    resolver: zodResolver(createAppuntamentoSchema),
    defaultValues: {
      cliente_id: '',
      servizio_id: '',
      operatore_id: '',
      data_ora_inizio: initialDate || new Date().toISOString().slice(0, 16),
      durata_minuti: 30,
      stato: 'confermato',
      prezzo: 0,
      sconto_percentuale: 0,
      note: '',
      note_interne: '',
      fonte_prenotazione: 'manuale',
    },
  });

  const watchServizio = form.watch('servizio_id');

  useEffect(() => {
    if (watchServizio && servizi) {
      const servizio = servizi.find((s) => s.id === watchServizio);
      if (servizio) {
        form.setValue('durata_minuti', servizio.durata_minuti);
        form.setValue('prezzo', servizio.prezzo);
      }
    }
  }, [watchServizio, servizi, form]);

  const onSubmit = async (data: CreateAppuntamentoInput) => {
    try {
      setErrorMessage(null);
      await createMutation.mutateAsync(data);
      onSuccess();
      form.reset();
      onOpenChange(false);
    } catch (error) {
      const err = error as Error;
      if (err.message.includes('Conflitto')) {
        setErrorMessage('⚠️ ' + err.message);
      } else {
        setErrorMessage('Errore durante la creazione: ' + err.message);
      }
    }
  };

  const isSubmitting = createMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white">Nuovo Appuntamento</DialogTitle>
          <DialogDescription className="text-slate-400">Prenota un nuovo appuntamento</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {errorMessage && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
                <p className="text-red-400 text-sm">{errorMessage}</p>
              </div>
            )}

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">CLIENTE E SERVIZIO</h3>
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="cliente_id" render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Cliente *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                          <SelectValue placeholder="Seleziona cliente" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-slate-900 border-slate-700">
                        {clienti?.map((c) => (
                          <SelectItem key={c.id} value={c.id}>{c.nome} {c.cognome}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )} />

                <FormField control={form.control} name="servizio_id" render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Servizio *</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                          <SelectValue placeholder="Seleziona servizio" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-slate-900 border-slate-700">
                        {servizi?.map((s) => (
                          <SelectItem key={s.id} value={s.id}>{s.nome} - €{s.prezzo} ({s.durata_minuti}min)</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )} />
              </div>

              <FormField control={form.control} name="operatore_id" render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Operatore</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value || ''}>
                    <FormControl>
                      <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                        <SelectValue placeholder="Seleziona operatore (opzionale)" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      {operatori?.map((o) => (
                        <SelectItem key={o.id} value={o.id}>{o.nome} {o.cognome} ({o.ruolo})</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )} />
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">DATA E ORA</h3>
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="data_ora_inizio" render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Data e Ora *</FormLabel>
                    <FormControl>
                      <Input {...field} type="datetime-local" className="bg-slate-900 border-slate-700 text-white" />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )} />

                <FormField control={form.control} name="durata_minuti" render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Durata (min)</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" step="5" className="bg-slate-900 border-slate-700 text-white" onChange={(e) => field.onChange(parseInt(e.target.value))} />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )} />
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">PREZZI</h3>
              <div className="grid grid-cols-2 gap-4">
                <FormField control={form.control} name="prezzo" render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Prezzo (€) *</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" step="0.01" className="bg-slate-900 border-slate-700 text-white" onChange={(e) => field.onChange(parseFloat(e.target.value))} />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )} />

                <FormField control={form.control} name="sconto_percentuale" render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Sconto (%)</FormLabel>
                    <FormControl>
                      <Input {...field} type="number" step="1" placeholder="0" className="bg-slate-900 border-slate-700 text-white" onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)} />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )} />
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">NOTE</h3>
              <FormField control={form.control} name="note" render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Note Cliente</FormLabel>
                  <FormControl>
                    <Textarea {...field} placeholder="Note visibili al cliente..." rows={2} className="bg-slate-900 border-slate-700 text-white resize-none" />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )} />

              <FormField control={form.control} name="note_interne" render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Note Interne</FormLabel>
                  <FormControl>
                    <Textarea {...field} placeholder="Note visibili solo allo staff..." rows={2} className="bg-slate-900 border-slate-700 text-white resize-none" />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )} />
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)} className="border-slate-700 text-slate-300 hover:bg-slate-800" disabled={isSubmitting}>Annulla</Button>
              <Button type="submit" disabled={isSubmitting} className="bg-cyan-500 hover:bg-cyan-600 text-white">{isSubmitting ? 'Creazione...' : 'Crea Appuntamento'}</Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
