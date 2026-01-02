import { type FC, useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createAppuntamentoSchema, updateAppuntamentoSchema, type CreateAppuntamentoInput, type UpdateAppuntamentoInput, type AppuntamentoDettagliato } from '@/types/appuntamento';
import { useCreateAppuntamento, useUpdateAppuntamento, useDeleteAppuntamento } from '@/hooks/use-appuntamenti';
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
  editingAppuntamento?: AppuntamentoDettagliato | null;
  onSuccess: () => void;
}

export const AppuntamentoDialog: FC<AppuntamentoDialogProps> = ({ open, onOpenChange, initialDate, editingAppuntamento, onSuccess }) => {
  const isEditMode = !!editingAppuntamento;
  const createMutation = useCreateAppuntamento();
  const updateMutation = useUpdateAppuntamento();
  const deleteMutation = useDeleteAppuntamento();
  const { data: clienti } = useClienti();
  const { data: servizi } = useServizi();
  const { data: operatori } = useOperatori();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Helper function to format date in LOCAL timezone (not UTC)
  const getLocalDateTimeString = (date: Date = new Date()): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  const form = useForm<CreateAppuntamentoInput | UpdateAppuntamentoInput>({
    resolver: zodResolver(isEditMode ? updateAppuntamentoSchema : createAppuntamentoSchema),
    defaultValues: {
      cliente_id: undefined,
      servizio_id: undefined,
      operatore_id: undefined,
      data_ora_inizio: initialDate || getLocalDateTimeString(), // YYYY-MM-DDTHH:mm (datetime-local format, LOCAL timezone)
      durata_minuti: 30,
      stato: 'confermato',
      prezzo: 0,
      sconto_percentuale: 0,
      note: '',
      note_interne: '',
      fonte_prenotazione: 'manuale',
    },
  });

  // Populate form when editing
  useEffect(() => {
    if (editingAppuntamento) {
      // Convert UTC datetime to local datetime-local format (YYYY-MM-DDTHH:mm)
      const utcDate = new Date(editingAppuntamento.data_ora_inizio);
      const year = utcDate.getFullYear();
      const month = String(utcDate.getMonth() + 1).padStart(2, '0');
      const day = String(utcDate.getDate()).padStart(2, '0');
      const hours = String(utcDate.getHours()).padStart(2, '0');
      const minutes = String(utcDate.getMinutes()).padStart(2, '0');
      const dataOraInizio = `${year}-${month}-${day}T${hours}:${minutes}`;

      form.reset({
        cliente_id: editingAppuntamento.cliente_id,
        servizio_id: editingAppuntamento.servizio_id,
        operatore_id: editingAppuntamento.operatore_id || undefined,
        data_ora_inizio: dataOraInizio,
        durata_minuti: editingAppuntamento.durata_minuti,
        stato: editingAppuntamento.stato,
        prezzo: editingAppuntamento.prezzo,
        sconto_percentuale: editingAppuntamento.sconto_percentuale,
        note: editingAppuntamento.note || '',
        note_interne: editingAppuntamento.note_interne || '',
      });
    } else {
      // Format current date/time in LOCAL timezone (not UTC)
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const defaultDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;

      form.reset({
        cliente_id: undefined,
        servizio_id: undefined,
        operatore_id: undefined,
        data_ora_inizio: initialDate || defaultDateTime,
        durata_minuti: 30,
        stato: 'confermato',
        prezzo: 0,
        sconto_percentuale: 0,
        note: '',
        note_interne: '',
        fonte_prenotazione: 'manuale',
      });
    }
  }, [editingAppuntamento, initialDate, form]);

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

  const onSubmit = async (data: CreateAppuntamentoInput | UpdateAppuntamentoInput) => {
    try {
      setErrorMessage(null);

      // Convert datetime-local to RFC3339 format WITHOUT timezone conversion
      let dataOraInizio = data.data_ora_inizio;
      if (dataOraInizio) {
        // datetime-local format: "YYYY-MM-DDTHH:mm" (no timezone, treated as local)
        // CRITICAL FIX: Keep local time, do NOT convert to UTC
        // This prevents the "+1 day bug" when creating appointments at midnight

        // Validate format
        const [datePart, timePart] = dataOraInizio.split('T');
        if (!datePart || !timePart) {
          throw new Error('Data/ora non valida');
        }

        const [year, month, day] = datePart.split('-').map(Number);
        const [hours, minutes] = timePart.split(':').map(Number);

        // Validate components
        const localDate = new Date(year, month - 1, day, hours, minutes, 0, 0);
        if (isNaN(localDate.getTime())) {
          throw new Error('Data/ora non valida');
        }

        // Keep local time in RFC3339 format WITHOUT timezone (no Z suffix)
        // Format: "YYYY-MM-DDTHH:mm:ss" (interpreted as local by backend)
        dataOraInizio = `${datePart}T${timePart}:00`;
      }

      const payload = {
        ...data,
        data_ora_inizio: dataOraInizio,
      };

      if (isEditMode && editingAppuntamento) {
        // Update existing appuntamento
        await updateMutation.mutateAsync({ id: editingAppuntamento.id, input: payload as UpdateAppuntamentoInput });
      } else {
        // Create new appuntamento
        await createMutation.mutateAsync(payload as CreateAppuntamentoInput);
      }

      onSuccess();
      form.reset();
      onOpenChange(false);
    } catch (error) {
      // Robust error handling for Tauri errors (may be string or Error object)
      let errorMsg = 'Errore sconosciuto';

      if (typeof error === 'string') {
        errorMsg = error;
      } else if (error && typeof error === 'object') {
        const err = error as any;
        errorMsg = err.message || err.toString();
      }

      if (errorMsg.includes('Conflitto')) {
        setErrorMessage('⚠️ ' + errorMsg);
      } else {
        const action = isEditMode ? 'modifica' : 'creazione';
        setErrorMessage(`Errore durante la ${action}: ${errorMsg}`);
      }

      console.error('Appuntamento error:', error);
    }
  };

  const handleDelete = async () => {
    if (!editingAppuntamento?.id) return;

    if (!confirm('Sei sicuro di voler eliminare questo appuntamento?')) {
      return;
    }

    try {
      await deleteMutation.mutateAsync(editingAppuntamento.id);
      onOpenChange(false);
      onSuccess();
    } catch (error) {
      const errorMsg = typeof error === 'string' ? error : (error as any)?.message || 'Errore sconosciuto';
      setErrorMessage(`Errore durante l'eliminazione: ${errorMsg}`);
    }
  };

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-white">
            {isEditMode ? 'Modifica Appuntamento' : 'Nuovo Appuntamento'}
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            {isEditMode ? 'Modifica i dettagli dell\'appuntamento' : 'Prenota un nuovo appuntamento'}
          </DialogDescription>
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

            <div className="flex items-center justify-between gap-3 pt-4 border-t border-slate-800">
              {/* Bottone Elimina (solo in modalità edit) */}
              {isEditMode && (
                <Button
                  type="button"
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={deleteMutation.isPending || isSubmitting}
                  className="bg-red-600 hover:bg-red-700 text-white"
                >
                  {deleteMutation.isPending ? 'Eliminazione...' : 'Elimina'}
                </Button>
              )}

              {/* Spacer per allineare a destra quando non c'è delete button */}
              {!isEditMode && <div />}

              {/* Bottoni Annulla e Salva */}
              <div className="flex gap-3">
                <Button type="button" variant="outline" onClick={() => onOpenChange(false)} className="border-slate-700 text-slate-300 hover:bg-slate-800" disabled={isSubmitting}>Annulla</Button>
                <Button type="submit" disabled={isSubmitting} className="bg-cyan-500 hover:bg-cyan-600 text-white">
                  {isSubmitting
                    ? (isEditMode ? 'Salvataggio...' : 'Creazione...')
                    : (isEditMode ? 'Salva Modifiche' : 'Crea Appuntamento')
                  }
                </Button>
              </div>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
