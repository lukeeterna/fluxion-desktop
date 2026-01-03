import { type FC } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createGiornoFestivoSchema, type CreateGiornoFestivoInput } from '@/types/orari';
import { useCreateGiornoFestivo } from '@/hooks/use-orari';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface FestivoDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const FestivoDialog: FC<FestivoDialogProps> = ({ open, onOpenChange, onSuccess }) => {
  const createMutation = useCreateGiornoFestivo();

  const form = useForm<CreateGiornoFestivoInput>({
    resolver: zodResolver(createGiornoFestivoSchema),
    defaultValues: {
      data: '',
      descrizione: '',
      ricorrente: 0,
    },
  });

  const onSubmit = async (data: CreateGiornoFestivoInput) => {
    try {
      await createMutation.mutateAsync(data);
      onSuccess();
      form.reset();
    } catch (error) {
      console.error('Errore creazione festività:', error);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-950 border-slate-800">
        <DialogHeader>
          <DialogTitle className="text-white">Aggiungi Festività</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="descrizione"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Descrizione</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="es. Santo Patrono, Chiusura aziendale..."
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="data"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Data</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      type="date"
                      className="bg-slate-900 border-slate-700 text-white"
                    />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="ricorrente"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Tipo</FormLabel>
                  <Select
                    onValueChange={(value) => field.onChange(parseInt(value))}
                    defaultValue={field.value?.toString()}
                  >
                    <FormControl>
                      <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                        <SelectValue placeholder="Seleziona tipo" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="0">Singola (solo quest'anno)</SelectItem>
                      <SelectItem value="1">Ricorrente (ogni anno)</SelectItem>
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
                className="flex-1 bg-purple-500 hover:bg-purple-600 text-white"
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
