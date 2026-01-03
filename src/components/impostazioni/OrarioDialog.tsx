import { type FC } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createOrarioLavoroSchema, type CreateOrarioLavoroInput, GIORNI_SETTIMANA } from '@/types/orari';
import { useCreateOrarioLavoro } from '@/hooks/use-orari';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface OrarioDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const OrarioDialog: FC<OrarioDialogProps> = ({ open, onOpenChange, onSuccess }) => {
  const createMutation = useCreateOrarioLavoro();

  const form = useForm<CreateOrarioLavoroInput>({
    resolver: zodResolver(createOrarioLavoroSchema),
    defaultValues: {
      giorno_settimana: 1,
      ora_inizio: '09:00',
      ora_fine: '13:00',
      tipo: 'lavoro',
    },
  });

  const onSubmit = async (data: CreateOrarioLavoroInput) => {
    try {
      await createMutation.mutateAsync(data);
      onSuccess();
      form.reset();
    } catch (error) {
      console.error('Errore creazione orario:', error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-white">Aggiungi Orario</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="giorno_settimana"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Giorno</FormLabel>
                  <Select
                    onValueChange={(value) => field.onChange(parseInt(value))}
                    defaultValue={field.value?.toString()}
                  >
                    <FormControl>
                      <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                        <SelectValue placeholder="Seleziona giorno" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      {GIORNI_SETTIMANA.map((g) => (
                        <SelectItem key={g.value} value={g.value.toString()}>
                          {g.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="ora_inizio"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Ora Inizio</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="time"
                        className="bg-slate-900 border-slate-700 text-white"
                      />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="ora_fine"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-slate-300">Ora Fine</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="time"
                        className="bg-slate-900 border-slate-700 text-white"
                      />
                    </FormControl>
                    <FormMessage className="text-red-400" />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="tipo"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Tipo</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                        <SelectValue placeholder="Seleziona tipo" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="lavoro">Lavoro</SelectItem>
                      <SelectItem value="pausa">Pausa</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />

            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="flex-1 border-slate-700 text-slate-300 hover:bg-slate-800"
              >
                Annulla
              </Button>
              <Button
                type="submit"
                disabled={createMutation.isPending}
                className="flex-1 bg-cyan-500 hover:bg-cyan-600 text-white"
              >
                {createMutation.isPending ? 'Salvataggio...' : 'Salva'}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
