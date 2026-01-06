// ═══════════════════════════════════════════════════════════════════
// FLUXION - Setup Wizard Component
// Configurazione iniziale all'installazione
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { useSaveSetupConfig } from '../../hooks/use-setup';
import {
  SetupConfigSchema,
  REGIMI_FISCALI,
  CATEGORIE_ATTIVITA,
  defaultSetupConfig,
  type SetupConfig,
} from '../../types/setup';

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

interface SetupWizardProps {
  onComplete: () => void;
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────

export function SetupWizard({ onComplete }: SetupWizardProps) {
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const saveConfig = useSaveSetupConfig();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<SetupConfig>({
    resolver: zodResolver(SetupConfigSchema),
    defaultValues: defaultSetupConfig,
  });

  const formData = watch();

  const onSubmit = async (data: SetupConfig) => {
    try {
      await saveConfig.mutateAsync(data);
      onComplete();
    } catch (error) {
      console.error('Errore salvataggio setup:', error);
    }
  };

  const nextStep = () => {
    if (step < totalSteps) setStep(step + 1);
  };

  const prevStep = () => {
    if (step > 1) setStep(step - 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl bg-slate-800/50 border-slate-700">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 text-4xl font-bold bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent">
            FLUXION
          </div>
          <CardTitle className="text-2xl text-white">Configurazione Iniziale</CardTitle>
          <CardDescription className="text-slate-400">
            Step {step} di {totalSteps}
          </CardDescription>
          {/* Progress bar */}
          <div className="flex gap-2 mt-4">
            {Array.from({ length: totalSteps }).map((_, i) => (
              <div
                key={i}
                className={`h-2 flex-1 rounded-full transition-colors ${
                  i < step ? 'bg-cyan-500' : 'bg-slate-700'
                }`}
              />
            ))}
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* STEP 1: Dati Azienda Base */}
            {step === 1 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Dati Attività</h3>

                <div className="space-y-2">
                  <Label htmlFor="nome_attivita" className="text-slate-300">
                    Nome Attività *
                  </Label>
                  <Input
                    id="nome_attivita"
                    {...register('nome_attivita')}
                    placeholder="Es: Salone Maria"
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                  {errors.nome_attivita && (
                    <p className="text-red-400 text-sm">{errors.nome_attivita.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="partita_iva" className="text-slate-300">
                      Partita IVA
                    </Label>
                    <Input
                      id="partita_iva"
                      {...register('partita_iva')}
                      placeholder="12345678901"
                      maxLength={11}
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                    {errors.partita_iva && (
                      <p className="text-red-400 text-sm">{errors.partita_iva.message}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="codice_fiscale" className="text-slate-300">
                      Codice Fiscale
                    </Label>
                    <Input
                      id="codice_fiscale"
                      {...register('codice_fiscale')}
                      placeholder="RSSMRA80A01H501Z"
                      className="bg-slate-700 border-slate-600 text-white uppercase"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="telefono" className="text-slate-300">
                    Telefono
                  </Label>
                  <Input
                    id="telefono"
                    {...register('telefono')}
                    placeholder="+39 333 1234567"
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-slate-300">
                    Email
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    {...register('email')}
                    placeholder="info@tuodominio.it"
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                  {errors.email && (
                    <p className="text-red-400 text-sm">{errors.email.message}</p>
                  )}
                </div>
              </div>
            )}

            {/* STEP 2: Indirizzo */}
            {step === 2 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Sede Legale</h3>

                <div className="space-y-2">
                  <Label htmlFor="indirizzo" className="text-slate-300">
                    Indirizzo
                  </Label>
                  <Input
                    id="indirizzo"
                    {...register('indirizzo')}
                    placeholder="Via Roma 123"
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="cap" className="text-slate-300">
                      CAP
                    </Label>
                    <Input
                      id="cap"
                      {...register('cap')}
                      placeholder="00100"
                      maxLength={5}
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="citta" className="text-slate-300">
                      Città
                    </Label>
                    <Input
                      id="citta"
                      {...register('citta')}
                      placeholder="Roma"
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="provincia" className="text-slate-300">
                      Provincia
                    </Label>
                    <Input
                      id="provincia"
                      {...register('provincia')}
                      placeholder="RM"
                      maxLength={2}
                      className="bg-slate-700 border-slate-600 text-white uppercase"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pec" className="text-slate-300">
                    PEC (per fatturazione elettronica)
                  </Label>
                  <Input
                    id="pec"
                    type="email"
                    {...register('pec')}
                    placeholder="tuazienda@pec.it"
                    className="bg-slate-700 border-slate-600 text-white"
                  />
                </div>
              </div>
            )}

            {/* STEP 3: Configurazione */}
            {step === 3 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Configurazione</h3>

                <div className="space-y-2">
                  <Label className="text-slate-300">Categoria Attività</Label>
                  <Select
                    value={formData.categoria_attivita}
                    onValueChange={(value) => setValue('categoria_attivita', value as SetupConfig['categoria_attivita'])}
                  >
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue placeholder="Seleziona categoria" />
                    </SelectTrigger>
                    <SelectContent>
                      {CATEGORIE_ATTIVITA.map((cat) => (
                        <SelectItem key={cat.value} value={cat.value}>
                          {cat.icon} {cat.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label className="text-slate-300">Regime Fiscale</Label>
                  <Select
                    value={formData.regime_fiscale}
                    onValueChange={(value) => setValue('regime_fiscale', value as SetupConfig['regime_fiscale'])}
                  >
                    <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                      <SelectValue placeholder="Seleziona regime" />
                    </SelectTrigger>
                    <SelectContent>
                      {REGIMI_FISCALI.map((regime) => (
                        <SelectItem key={regime.value} value={regime.value}>
                          {regime.label} - {regime.description}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fluxion_ia_key" className="text-slate-300">
                    FLUXION IA Key (opzionale - per assistente intelligente)
                  </Label>
                  <Input
                    id="fluxion_ia_key"
                    type="password"
                    {...register('fluxion_ia_key')}
                    placeholder="Inserisci la chiave ricevuta"
                    className="bg-slate-700 border-slate-600 text-white font-mono"
                  />
                  <p className="text-xs text-slate-500">
                    Chiave fornita con la licenza FLUXION per funzionalità AI avanzate
                  </p>
                </div>
              </div>
            )}

            {/* STEP 4: Riepilogo */}
            {step === 4 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Riepilogo</h3>

                <div className="bg-slate-700/50 rounded-lg p-4 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Nome Attività</span>
                    <span className="text-white font-medium">{formData.nome_attivita || '-'}</span>
                  </div>
                  {formData.partita_iva && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">P.IVA</span>
                      <span className="text-white">{formData.partita_iva}</span>
                    </div>
                  )}
                  {formData.citta && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Sede</span>
                      <span className="text-white">
                        {formData.citta} ({formData.provincia})
                      </span>
                    </div>
                  )}
                  {formData.email && (
                    <div className="flex justify-between">
                      <span className="text-slate-400">Email</span>
                      <span className="text-white">{formData.email}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-slate-400">Categoria</span>
                    <span className="text-white">
                      {CATEGORIE_ATTIVITA.find((c) => c.value === formData.categoria_attivita)?.label || '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Regime Fiscale</span>
                    <span className="text-white">
                      {REGIMI_FISCALI.find((r) => r.value === formData.regime_fiscale)?.label || '-'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">FLUXION IA</span>
                    <span className="text-white">
                      {formData.fluxion_ia_key ? '✓ Configurata' : 'Non configurata'}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-slate-400 text-center">
                  Puoi modificare queste impostazioni in qualsiasi momento dalla pagina Impostazioni.
                </p>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                disabled={step === 1}
                className="border-slate-600 text-slate-300 hover:bg-slate-700"
              >
                Indietro
              </Button>

              {step < totalSteps ? (
                <Button
                  type="button"
                  onClick={nextStep}
                  disabled={step === 1 && !formData.nome_attivita}
                  className="bg-cyan-600 hover:bg-cyan-700"
                >
                  Avanti
                </Button>
              ) : (
                <Button
                  type="submit"
                  disabled={saveConfig.isPending}
                  className="bg-teal-600 hover:bg-teal-700"
                >
                  {saveConfig.isPending ? 'Salvataggio...' : 'Completa Setup'}
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
