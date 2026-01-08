// ═══════════════════════════════════════════════════════════════════
// FLUXION - Cliente Form
// Form for creating and editing clienti
// ═══════════════════════════════════════════════════════════════════

import { type FC } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { cn } from '@/lib/utils';
import type { Cliente, CreateClienteInput, UpdateClienteInput } from '@/types/cliente';
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
import { Checkbox } from '@/components/ui/checkbox';

// ───────────────────────────────────────────────────────────────────
// Validation Schema
// ───────────────────────────────────────────────────────────────────

const clienteSchema = z.object({
  nome: z.string().min(2, 'Nome richiesto (min 2 caratteri)'),
  cognome: z.string().min(2, 'Cognome richiesto (min 2 caratteri)'),
  soprannome: z.string().optional(), // Per identificazione WhatsApp
  telefono: z.string().min(10, 'Telefono richiesto (min 10 cifre)'),
  email: z.string().email('Email non valida').optional().or(z.literal('')),
  data_nascita: z.string().optional(),
  indirizzo: z.string().optional(),
  cap: z.string().optional(),
  citta: z.string().optional(),
  provincia: z.string().optional(),
  codice_fiscale: z.string().optional(),
  partita_iva: z.string().optional(),
  codice_sdi: z.string().optional(),
  pec: z.string().email('PEC non valida').optional().or(z.literal('')),
  note: z.string().optional(),
  fonte: z.string().optional(),
  consenso_marketing: z.boolean(),
  consenso_whatsapp: z.boolean(),
});

type ClienteFormValues = z.infer<typeof clienteSchema>;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface ClienteFormProps {
  cliente?: Cliente; // If provided, form is in edit mode
  onSubmit: (data: CreateClienteInput | UpdateClienteInput) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
  className?: string;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const ClienteForm: FC<ClienteFormProps> = ({
  cliente,
  onSubmit,
  onCancel,
  isSubmitting = false,
  className,
}) => {
  const isEditMode = !!cliente;

  // Setup form with default values
  const form = useForm<ClienteFormValues>({
    resolver: zodResolver(clienteSchema),
    defaultValues: {
      nome: cliente?.nome || '',
      cognome: cliente?.cognome || '',
      soprannome: cliente?.soprannome || '',
      telefono: cliente?.telefono || '',
      email: cliente?.email || '',
      data_nascita: cliente?.data_nascita || '',
      indirizzo: cliente?.indirizzo || '',
      cap: cliente?.cap || '',
      citta: cliente?.citta || '',
      provincia: cliente?.provincia || '',
      codice_fiscale: cliente?.codice_fiscale || '',
      partita_iva: cliente?.partita_iva || '',
      codice_sdi: cliente?.codice_sdi || '',
      pec: cliente?.pec || '',
      note: cliente?.note || '',
      fonte: cliente?.fonte || '',
      consenso_marketing: cliente?.consenso_marketing === 1,
      consenso_whatsapp: cliente?.consenso_whatsapp === 1,
    },
  });

  const handleSubmit = (values: ClienteFormValues) => {
    const data = {
      ...values,
      soprannome: values.soprannome || undefined,
      email: values.email || undefined,
      data_nascita: values.data_nascita || undefined,
      indirizzo: values.indirizzo || undefined,
      cap: values.cap || undefined,
      citta: values.citta || undefined,
      provincia: values.provincia || undefined,
      codice_fiscale: values.codice_fiscale || undefined,
      partita_iva: values.partita_iva || undefined,
      codice_sdi: values.codice_sdi || undefined,
      pec: values.pec || undefined,
      note: values.note || undefined,
      fonte: values.fonte || undefined,
      consenso_marketing: values.consenso_marketing ? 1 : 0,
      consenso_whatsapp: values.consenso_whatsapp ? 1 : 0,
    };

    if (isEditMode) {
      onSubmit({ ...data, id: cliente.id } as UpdateClienteInput);
    } else {
      onSubmit(data as CreateClienteInput);
    }
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(handleSubmit)}
        className={cn('space-y-6', className)}
      >
        {/* Anagrafica */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
            Anagrafica
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Nome *</FormLabel>
                  <FormControl>
                    <Input {...field} className="bg-slate-900 border-slate-700 text-white" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="cognome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Cognome *</FormLabel>
                  <FormControl>
                    <Input {...field} className="bg-slate-900 border-slate-700 text-white" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <FormField
            control={form.control}
            name="soprannome"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-slate-300">Soprannome (per WhatsApp)</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="Es: Luca il biondo" className="bg-slate-900 border-slate-700 text-white" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="telefono"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Telefono *</FormLabel>
                  <FormControl>
                    <Input {...field} type="tel" className="bg-slate-900 border-slate-700 text-white" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Email</FormLabel>
                  <FormControl>
                    <Input {...field} type="email" className="bg-slate-900 border-slate-700 text-white" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <FormField
            control={form.control}
            name="data_nascita"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-slate-300">Data di Nascita</FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    type="date"
                    min="1900-01-01"
                    max={new Date().toISOString().split('T')[0]}
                    className="bg-slate-900 border-slate-700 text-white"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Indirizzo */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
            Indirizzo
          </h3>
          <FormField
            control={form.control}
            name="indirizzo"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-slate-300">Via e Numero</FormLabel>
                <FormControl>
                  <Input {...field} className="bg-slate-900 border-slate-700 text-white" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="grid grid-cols-3 gap-4">
            <FormField
              control={form.control}
              name="cap"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">CAP</FormLabel>
                  <FormControl>
                    <Input {...field} className="bg-slate-900 border-slate-700 text-white" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="citta"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Città</FormLabel>
                  <FormControl>
                    <Input {...field} className="bg-slate-900 border-slate-700 text-white" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="provincia"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Provincia</FormLabel>
                  <FormControl>
                    <Input {...field} maxLength={2} className="bg-slate-900 border-slate-700 text-white uppercase" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        {/* Dati Fiscali */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
            Dati Fiscali (opzionale)
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="codice_fiscale"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Codice Fiscale</FormLabel>
                  <FormControl>
                    <Input {...field} maxLength={16} className="bg-slate-900 border-slate-700 text-white uppercase" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="partita_iva"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Partita IVA</FormLabel>
                  <FormControl>
                    <Input {...field} maxLength={11} className="bg-slate-900 border-slate-700 text-white" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="codice_sdi"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">Codice SDI</FormLabel>
                  <FormControl>
                    <Input {...field} maxLength={7} placeholder="0000000" className="bg-slate-900 border-slate-700 text-white uppercase" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="pec"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-slate-300">PEC</FormLabel>
                  <FormControl>
                    <Input {...field} type="email" placeholder="azienda@pec.it" className="bg-slate-900 border-slate-700 text-white" />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        {/* Note */}
        <FormField
          control={form.control}
          name="note"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-slate-300">Note</FormLabel>
              <FormControl>
                <Textarea {...field} rows={3} className="bg-slate-900 border-slate-700 text-white resize-none" />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* GDPR */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide">
            Consensi
          </h3>
          <FormField
            control={form.control}
            name="consenso_marketing"
            render={({ field }) => (
              <FormItem className="flex items-center space-x-2 space-y-0">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
                <FormLabel className="text-slate-300 font-normal cursor-pointer">
                  Consenso marketing e comunicazioni
                </FormLabel>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="consenso_whatsapp"
            render={({ field }) => (
              <FormItem className="flex items-center space-x-2 space-y-0">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
                <FormLabel className="text-slate-300 font-normal cursor-pointer">
                  Consenso WhatsApp reminder
                </FormLabel>
              </FormItem>
            )}
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 pt-4 border-t border-slate-800">
          <Button
            type="submit"
            disabled={isSubmitting}
            className="bg-cyan-500 hover:bg-cyan-600 text-white"
          >
            {isSubmitting ? 'Salvataggio...' : isEditMode ? 'Aggiorna Cliente' : 'Crea Cliente'}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isSubmitting}
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
          >
            Annulla
          </Button>
        </div>
      </form>
    </Form>
  );
};
