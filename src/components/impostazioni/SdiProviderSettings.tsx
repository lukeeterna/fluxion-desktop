// ═══════════════════════════════════════════════════════════════════
// FLUXION - SDI Provider Settings Component
// Selector UI per provider intermediario fatturazione elettronica
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useImpostazioniFatturazione, useUpdateImpostazioniFatturazione } from '@/hooks/use-fatture';
import { toast } from 'sonner';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

type SdiProviderType = 'fattura24' | 'aruba' | 'openapi';

interface ProviderInfo {
  id: SdiProviderType;
  nome: string;
  costo: string;
  descrizione: string;
  linkDoc: string;
  labelKey: string;
  placeholderKey: string;
}

// ───────────────────────────────────────────────────────────────────
// Provider definitions
// ───────────────────────────────────────────────────────────────────

const PROVIDERS: ProviderInfo[] = [
  {
    id: 'aruba',
    nome: 'Aruba Fatturazione Elettronica',
    costo: '€29.90/anno — invii ILLIMITATI',
    descrizione:
      'Conservazione decennale inclusa. Il provider più conveniente per PMI con 20+ fatture/anno.',
    linkDoc: 'https://fatturazioneelettronica.aruba.it/apidoc/docs.html',
    labelKey: 'API Key Aruba FE',
    placeholderKey: 'Aruba API Key (da Account → API)',
  },
  {
    id: 'openapi',
    nome: 'OpenAPI.com SDI',
    costo: '€0.025/fattura — pay-per-use',
    descrizione: 'Ideale per forfettari con meno di 30 fatture/anno. Nessun abbonamento fisso.',
    linkDoc: 'https://console.openapi.com/apis/sdi',
    labelKey: 'API Key OpenAPI.com',
    placeholderKey: 'OpenAPI.com API Key (da console.openapi.com)',
  },
  {
    id: 'fattura24',
    nome: 'Fattura24',
    costo: '~€96-192/anno (piano Business)',
    descrizione:
      'Provider originale FLUXION. Mantiene retrocompatibilità per chi lo usa già.',
    linkDoc: 'https://api.fattura24.com',
    labelKey: 'API Key Fattura24',
    placeholderKey: 'Fattura24 API Key',
  },
];

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const SdiProviderSettings: FC = () => {
  const { data: impostazioni, isLoading } = useImpostazioniFatturazione();
  const updateMutation = useUpdateImpostazioniFatturazione();

  const [providerSelezionato, setProviderSelezionato] = useState<SdiProviderType>('fattura24');
  const [arubaKey, setArubaKey] = useState('');
  const [openapiKey, setOpenapiKey] = useState('');
  const [fattura24Key, setFattura24Key] = useState('');
  const [salvato, setSalvato] = useState(false);

  useEffect(() => {
    if (impostazioni) {
      const p = impostazioni.sdi_provider as SdiProviderType;
      if (p === 'aruba' || p === 'openapi' || p === 'fattura24') {
        setProviderSelezionato(p);
      }
      setArubaKey(impostazioni.aruba_api_key ?? '');
      setOpenapiKey(impostazioni.openapi_api_key ?? '');
      setFattura24Key(impostazioni.fattura24_api_key ?? '');
    }
  }, [impostazioni]);

  const handleSalva = async () => {
    if (!impostazioni) return;
    try {
      await updateMutation.mutateAsync({
        ...impostazioni,
        sdi_provider: providerSelezionato,
        aruba_api_key: arubaKey || null,
        openapi_api_key: openapiKey || null,
        fattura24_api_key: fattura24Key || null,
      });
      setSalvato(true);
      toast.success('Impostazioni SDI salvate');
      setTimeout(() => setSalvato(false), 3000);
    } catch (err) {
      toast.error(`Errore salvataggio SDI: ${String(err)}`);
    }
  };

  const providerAttivo = PROVIDERS.find((p) => p.id === providerSelezionato) ?? PROVIDERS[0];

  if (isLoading) {
    return (
      <Card className="p-6 bg-slate-900 border-slate-800">
        <p className="text-slate-400">Caricamento impostazioni SDI...</p>
      </Card>
    );
  }

  return (
    <Card className="p-6 bg-slate-900 border-slate-800">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">Integrazione SDI</h2>
        <p className="text-sm text-slate-400 mt-1">
          Scegli il provider intermediario per l&apos;invio delle fatture al Sistema di
          Interscambio (AdE)
        </p>
      </div>

      {/* Provider selector cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {PROVIDERS.map((provider) => {
          const isSelected = providerSelezionato === provider.id;
          return (
            <button
              key={provider.id}
              type="button"
              onClick={() => setProviderSelezionato(provider.id)}
              className={`text-left p-4 rounded-lg border-2 transition-colors ${
                isSelected
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-slate-700 bg-slate-950 hover:border-slate-600'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <span className="font-semibold text-white text-sm">{provider.nome}</span>
                {isSelected && (
                  <span className="text-cyan-400 text-xs font-bold uppercase tracking-wide">
                    Attivo
                  </span>
                )}
              </div>
              <span
                className={`text-xs font-mono ${
                  provider.id === 'aruba'
                    ? 'text-green-400'
                    : provider.id === 'openapi'
                      ? 'text-blue-400'
                      : 'text-slate-400'
                }`}
              >
                {provider.costo}
              </span>
              <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                {provider.descrizione}
              </p>
            </button>
          );
        })}
      </div>

      {/* API Key input — dynamic based on selected provider */}
      <div className="space-y-4 mb-6">
        <div>
          <Label className="text-slate-300 mb-2 block">{providerAttivo.labelKey}</Label>
          {providerSelezionato === 'aruba' && (
            <Input
              type="password"
              value={arubaKey}
              onChange={(e) => setArubaKey(e.target.value)}
              placeholder={providerAttivo.placeholderKey}
              className="bg-slate-950 border-slate-700 text-white font-mono"
            />
          )}
          {providerSelezionato === 'openapi' && (
            <Input
              type="password"
              value={openapiKey}
              onChange={(e) => setOpenapiKey(e.target.value)}
              placeholder={providerAttivo.placeholderKey}
              className="bg-slate-950 border-slate-700 text-white font-mono"
            />
          )}
          {providerSelezionato === 'fattura24' && (
            <Input
              type="password"
              value={fattura24Key}
              onChange={(e) => setFattura24Key(e.target.value)}
              placeholder={providerAttivo.placeholderKey}
              className="bg-slate-950 border-slate-700 text-white font-mono"
            />
          )}
          <p className="text-xs text-slate-500 mt-1">
            <a
              href={providerAttivo.linkDoc}
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-500 hover:text-cyan-400"
            >
              Documentazione API →
            </a>
          </p>
        </div>
      </div>

      {/* Save button */}
      <div className="flex items-center gap-4">
        <Button
          onClick={handleSalva}
          disabled={updateMutation.isPending}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          {updateMutation.isPending ? 'Salvataggio...' : 'Salva Impostazioni SDI'}
        </Button>
        {salvato && (
          <span className="text-green-400 text-sm">Impostazioni SDI salvate con successo.</span>
        )}
      </div>
    </Card>
  );
};
