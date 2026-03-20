// ═══════════════════════════════════════════════════════════════════
// FLUXION - Setup Wizard Component
// Configurazione iniziale all'installazione
// ═══════════════════════════════════════════════════════════════════

import { useState, type CSSProperties } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { useSaveSetupConfig } from '../../hooks/use-setup';
import {
  SetupConfigSchema,
  REGIMI_FISCALI,
  CATEGORIE_ATTIVITA,
  MACRO_CATEGORIE,
  MICRO_CATEGORIE,
  LICENSE_TIERS,
  defaultSetupConfig,
  type SetupConfig,
} from '../../types/setup';
import { Check, Sparkles, Building2, Car, Heart, Dumbbell, Briefcase, PenLine, Shield } from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

const FIRMA_FONTS: CSSProperties[] = [
  { fontStyle: 'italic', fontSize: '22px', fontFamily: 'Georgia, "Times New Roman", serif' },
  { fontStyle: 'italic', fontSize: '20px', fontFamily: 'Palatino, "Palatino Linotype", serif', letterSpacing: '1px' },
  { fontStyle: 'italic', fontSize: '18px', fontFamily: '"Book Antiqua", Garamond, serif', letterSpacing: '2px' },
];

const CONTRATTO_TESTO = `CONTRATTO DI CONCESSIONE DI LICENZA SOFTWARE — FLUXION

Il presente contratto è stipulato tra il Concedente (sviluppatore di FLUXION) e il Licenziatario (l'utente che accetta i presenti termini).

1. OGGETTO. Il Concedente concede al Licenziatario una licenza perpetua, non esclusiva e non trasferibile per l'utilizzo del software FLUXION su un singolo dispositivo identificato dall'hardware fingerprint generato dall'applicazione.

2. LIMITAZIONI. È vietata la copia, redistribuzione, sublicenza o reverse engineering del software. La licenza è valida per una sola installazione.

3. AGGIORNAMENTI. Gli aggiornamenti potranno essere inclusi o richiedere aggiornamento della licenza, a discrezione del Concedente.

4. LIMITAZIONE DI RESPONSABILITÀ. Il software è fornito "così com'è". Il Concedente non è responsabile per danni diretti o indiretti derivanti dall'uso del software.

5. PRIVACY E GDPR. I dati sono conservati esclusivamente sul dispositivo locale del Licenziatario. Nessun dato viene trasmesso a server remoti senza esplicito consenso. Il Licenziatario è responsabile del trattamento dei dati dei propri clienti ai sensi del Regolamento UE 2016/679 (GDPR).

6. LEGGE APPLICABILE. Il presente contratto è regolato dalla legge italiana.`;

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
  const totalSteps = 7;

  // Step 7: Firma contratto
  const [firmatarioNome, setFirmatarioNome] = useState('');
  const [firmatarioEmail, setFirmatarioEmail] = useState('');
  const [firmaFont, setFirmaFont] = useState(0);
  const [termsAccepted, setTermsAccepted] = useState(false);

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
      // Salva accettazione contratto (Firma Elettronica Semplice — eIDAS art. 25)
      window.localStorage.setItem('fluxion_contratto', JSON.stringify({
        firmatario_nome: firmatarioNome,
        firmatario_email: firmatarioEmail,
        firma_font: firmaFont,
        accepted_at: new Date().toISOString(),
        app_version: '1.0.0',
        contract_version: '1.0',
      }));
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

  // Helper per icona macro categoria
  const getMacroIcon = (value: string) => {
    switch (value) {
      case 'medico': return <Heart className="w-6 h-6 text-red-500" />;
      case 'beauty': return <Sparkles className="w-6 h-6 text-pink-500" />;
      case 'hair': return <Sparkles className="w-6 h-6 text-purple-500" />;
      case 'auto': return <Car className="w-6 h-6 text-blue-500" />;
      case 'wellness': return <Dumbbell className="w-6 h-6 text-green-500" />;
      case 'professionale': return <Briefcase className="w-6 h-6 text-gray-500" />;
      default: return <Building2 className="w-6 h-6" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl bg-slate-800/50 border-slate-700">
        <CardHeader className="text-center">
          <img
            src="/logo_fluxion.jpg"
            alt="Fluxion"
            style={{ width: 64, height: 64, borderRadius: 12, objectFit: 'cover' }}
            className="mx-auto mb-4 flex-shrink-0"
          />
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
                    placeholder="Es: Studio Dentistico Rossi"
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

            {/* STEP 3: Macro Categoria */}
            {step === 3 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Tipo di Attività</h3>
                <p className="text-slate-400 text-sm">
                  Seleziona la categoria principale della tua attività
                </p>

                <RadioGroup
                  value={formData.macro_categoria || ''}
                  onValueChange={(value: string) => {
                    setValue('macro_categoria', value as SetupConfig['macro_categoria']);
                    setValue('micro_categoria', undefined); // Reset micro quando cambia macro
                  }}
                  className="grid grid-cols-2 gap-3"
                >
                  {MACRO_CATEGORIE.map((cat) => (
                    <div key={cat.value}>
                      <RadioGroupItem
                        value={cat.value}
                        id={`macro-${cat.value}`}
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor={`macro-${cat.value}`}
                        className="flex flex-col items-center justify-center p-4 bg-slate-700 border-2 border-slate-600 rounded-lg cursor-pointer transition-all hover:bg-slate-600 peer-data-[state=checked]:border-cyan-500 peer-data-[state=checked]:bg-cyan-500/10"
                      >
                        <div className="mb-2">{getMacroIcon(cat.value)}</div>
                        <span className="text-white font-medium text-center">{cat.label}</span>
                        <span className="text-slate-400 text-xs text-center mt-1">{cat.description}</span>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            )}

            {/* STEP 4: Micro Categoria */}
            {step === 4 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Specializzazione</h3>
                <p className="text-slate-400 text-sm">
                  Seleziona la tua specifica attività
                </p>

                {formData.macro_categoria ? (
                  <RadioGroup
                    value={formData.micro_categoria || ''}
                    onValueChange={(value: string) => setValue('micro_categoria', value)}
                    className="grid grid-cols-1 gap-2"
                  >
                    {MICRO_CATEGORIE[formData.macro_categoria]?.map((micro) => (
                      <div key={micro.value}>
                        <RadioGroupItem
                          value={micro.value}
                          id={`micro-${micro.value}`}
                          className="peer sr-only"
                        />
                        <Label
                          htmlFor={`micro-${micro.value}`}
                          className="flex items-center justify-between p-3 bg-slate-700 border-2 border-slate-600 rounded-lg cursor-pointer transition-all hover:bg-slate-600 peer-data-[state=checked]:border-cyan-500 peer-data-[state=checked]:bg-cyan-500/10"
                        >
                          <span className="text-white">{micro.label}</span>
                          {micro.hasScheda && (
                            <span className="text-xs bg-cyan-500/20 text-cyan-400 px-2 py-1 rounded">
                              Scheda digitale
                            </span>
                          )}
                        </Label>
                      </div>
                    ))}
                  </RadioGroup>
                ) : (
                  <div className="text-center p-8 text-slate-400">
                    Seleziona prima una categoria principale
                  </div>
                )}
              </div>
            )}

            {/* STEP 5: Licenza */}
            {step === 5 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Seleziona la tua Licenza</h3>
                <p className="text-slate-400 text-sm">
                  Scegli il piano più adatto alle tue esigenze
                </p>

                <RadioGroup
                  value={formData.license_tier || 'trial'}
                  onValueChange={(value: string) => setValue('license_tier', value as SetupConfig['license_tier'])}
                  className="grid grid-cols-1 gap-3"
                >
                  {LICENSE_TIERS.map((tier) => (
                    <div key={tier.value}>
                      <RadioGroupItem
                        value={tier.value}
                        id={`tier-${tier.value}`}
                        className="peer sr-only"
                      />
                      <Label
                        htmlFor={`tier-${tier.value}`}
                        className="flex flex-col p-4 bg-slate-700 border-2 border-slate-600 rounded-lg cursor-pointer transition-all hover:bg-slate-600 peer-data-[state=checked]:border-cyan-500 peer-data-[state=checked]:bg-cyan-500/10"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <span className="text-white font-semibold text-lg">{tier.label}</span>
                            <p className="text-slate-400 text-sm">{tier.description}</p>
                          </div>
                          <span className="text-cyan-400 font-bold text-xl">
                            {tier.price === 0 ? 'Gratis' : `€${tier.price}`}
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {tier.features.map((feature, idx) => (
                            <span key={idx} className="text-xs bg-slate-600 text-slate-300 px-2 py-1 rounded flex items-center gap-1">
                              <Check className="w-3 h-3" />
                              {feature}
                            </span>
                          ))}
                        </div>
                      </Label>
                    </div>
                  ))}
                </RadioGroup>

                <div className="space-y-2 pt-4 border-t border-slate-700">
                  <Label htmlFor="fluxion_ia_key" className="text-slate-300">
                    Chiave Licenza FLUXION (opzionale per attivazione)
                  </Label>
                  <Input
                    id="fluxion_ia_key"
                    type="password"
                    {...register('fluxion_ia_key')}
                    placeholder="Inserisci la chiave di licenza ricevuta"
                    className="bg-slate-700 border-slate-600 text-white font-mono"
                  />
                  <p className="text-xs text-slate-500">
                    Puoi anche attivare la licenza successivamente dalle Impostazioni
                  </p>
                </div>
              </div>
            )}

            {/* STEP 6: Configurazione Fiscale + Riepilogo */}
            {step === 6 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Configurazione Finale</h3>

                <div className="space-y-2">
                  <Label className="text-slate-300">Categoria Attività (legacy)</Label>
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

                {/* NUOVO: Configurazione Comunicazioni */}
                <div className="border-t border-slate-700 pt-4 space-y-4">
                  <h4 className="text-white font-medium flex items-center gap-2">
                    <span>📱</span> Configurazione Comunicazioni
                  </h4>
                  <p className="text-xs text-slate-500">
                    Questi dati servono per WhatsApp e l'assistente vocale. Puoi anche configurarli dopo.
                  </p>

                  <div className="space-y-2">
                    <Label htmlFor="whatsapp_number" className="text-slate-300">
                      Numero WhatsApp Business
                    </Label>
                    <Input
                      id="whatsapp_number"
                      {...register('whatsapp_number')}
                      placeholder="Es: 3391234567 (senza prefisso +39)"
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                    <p className="text-xs text-slate-500">
                      Per inviare notifiche e reminder ai clienti
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="ehiweb_number" className="text-slate-300">
                      Numero Linea Fissa EhiWeb (opzionale)
                    </Label>
                    <Input
                      id="ehiweb_number"
                      {...register('ehiweb_number')}
                      placeholder="Es: 0835123456"
                      className="bg-slate-700 border-slate-600 text-white"
                    />
                    <p className="text-xs text-slate-500">
                      Numero fisso o dedicato della tua attività (opzionale)
                    </p>
                  </div>
                </div>

                {/* Riepilogo */}
                <div className="bg-slate-700/50 rounded-lg p-4 space-y-3 mt-4">
                  <h4 className="text-white font-medium">Riepilogo</h4>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Attività</span>
                    <span className="text-white">{formData.nome_attivita || '-'}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Categoria</span>
                    <span className="text-white">
                      {MACRO_CATEGORIE.find(c => c.value === formData.macro_categoria)?.label || '-'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Specializzazione</span>
                    <span className="text-white">
                      {formData.macro_categoria && formData.micro_categoria
                        ? MICRO_CATEGORIE[formData.macro_categoria]?.find(m => m.value === formData.micro_categoria)?.label
                        : '-'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Licenza</span>
                    <span className="text-white">
                      {LICENSE_TIERS.find(t => t.value === formData.license_tier)?.label || 'Trial'}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-slate-400 text-center">
                  Puoi modificare queste impostazioni in qualsiasi momento dalla pagina Impostazioni.
                </p>
              </div>
            )}

            {/* STEP 7: Firma Contratto */}
            {step === 7 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <PenLine className="w-5 h-5 text-cyan-400" />
                  Contratto di Licenza
                </h3>
                <p className="text-slate-400 text-sm">
                  Leggi i termini e apponi la tua firma digitale per procedere.
                </p>

                {/* Testo contratto */}
                <div className="bg-slate-900 rounded-lg p-4 max-h-36 overflow-y-auto border border-slate-700">
                  <pre className="text-xs text-slate-400 whitespace-pre-wrap leading-relaxed font-sans">
                    {CONTRATTO_TESTO}
                  </pre>
                </div>

                {/* Nome firmatario */}
                <div className="space-y-2">
                  <label className="text-slate-300 text-sm font-medium">Nome e Cognome *</label>
                  <input
                    type="text"
                    value={firmatarioNome}
                    onChange={(e) => setFirmatarioNome(e.target.value)}
                    placeholder="Mario Rossi"
                    className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>

                {/* Email */}
                <div className="space-y-2">
                  <label className="text-slate-300 text-sm font-medium">Email *</label>
                  <input
                    type="email"
                    value={firmatarioEmail}
                    onChange={(e) => setFirmatarioEmail(e.target.value)}
                    placeholder="mario@azienda.it"
                    className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  />
                </div>

                {/* Firma visiva */}
                {firmatarioNome.trim() && (
                  <div className="space-y-2">
                    <label className="text-slate-300 text-sm font-medium">Stile firma</label>
                    <div className="grid grid-cols-3 gap-2">
                      {FIRMA_FONTS.map((font, idx) => (
                        <button
                          key={idx}
                          type="button"
                          onClick={() => setFirmaFont(idx)}
                          className={`p-3 rounded-lg border-2 bg-slate-900 transition-all text-center ${
                            firmaFont === idx
                              ? 'border-cyan-500 bg-cyan-500/10'
                              : 'border-slate-700 hover:border-slate-500'
                          }`}
                        >
                          <span style={{ ...font, color: firmaFont === idx ? '#22d3ee' : '#94a3b8', display: 'block' }}>
                            {firmatarioNome}
                          </span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Checkbox accettazione */}
                <div className="flex items-start gap-3 p-3 bg-slate-900 rounded-lg border border-slate-700">
                  <input
                    type="checkbox"
                    id="terms-accept"
                    checked={termsAccepted}
                    onChange={(e) => setTermsAccepted(e.target.checked)}
                    className="mt-0.5 w-4 h-4 accent-cyan-500 cursor-pointer flex-shrink-0"
                  />
                  <label htmlFor="terms-accept" className="text-slate-300 text-sm cursor-pointer leading-relaxed">
                    Dichiaro di aver letto e di accettare integralmente il Contratto di Licenza Software FLUXION.
                    Questa azione costituisce <strong className="text-cyan-400">firma elettronica semplice (FES)</strong> ai
                    sensi del Regolamento UE eIDAS.
                  </label>
                </div>

                {/* Badge FES */}
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <Shield className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
                  <span>FES valida per contratti di licenza software — archiviazione locale GDPR-compliant</span>
                </div>
              </div>
            )}

            {/* Step 8-9 removed: Sara AI works via FLUXION proxy (zero config needed) */}


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
                  disabled={
                    (step === 1 && !formData.nome_attivita) ||
                    (step === 7 && (!termsAccepted || !firmatarioNome.trim() || !firmatarioEmail.trim()))
                  }
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
                  {saveConfig.isPending ? 'Salvataggio...' : '🚀 Avvia FLUXION'}
                </Button>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
