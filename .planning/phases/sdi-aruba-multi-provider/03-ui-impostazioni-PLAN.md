---
phase: sdi-aruba-multi-provider
plan: 03
type: execute
wave: 2
depends_on:
  - sdi-aruba-01
  - sdi-aruba-02
files_modified:
  - src/types/fatture.ts
  - src/hooks/use-fatture.ts
  - src/components/impostazioni/SdiProviderSettings.tsx
  - src/pages/Impostazioni.tsx
autonomous: true

must_haves:
  truths:
    - "L'utente vede una sezione SDI in Impostazioni con un radio group per scegliere provider"
    - "Selezionando Aruba appare il campo API key Aruba; selezionando OpenAPI appare API key OpenAPI; selezionando Fattura24 appare il campo esistente"
    - "Il bottone Salva persiste il provider scelto e la API key nel DB"
    - "npm run type-check non produce errori TypeScript"
  artifacts:
    - path: "src/types/fatture.ts"
      provides: "ImpostazioniFatturazione type aggiornato con 3 nuovi campi"
      contains: "sdi_provider: z.string()"
    - path: "src/hooks/use-fatture.ts"
      provides: "useUpdateImpostazioniFatturazione aggiornato con 3 parametri"
      contains: "sdi_provider"
    - path: "src/components/impostazioni/SdiProviderSettings.tsx"
      provides: "Componente UI per selezione provider SDI"
      exports: ["SdiProviderSettings"]
    - path: "src/pages/Impostazioni.tsx"
      provides: "SdiProviderSettings integrata nella pagina Impostazioni"
      contains: "SdiProviderSettings"
  key_links:
    - from: "src/components/impostazioni/SdiProviderSettings.tsx"
      to: "useImpostazioniFatturazione + useUpdateImpostazioniFatturazione"
      via: "hooks importati dal componente"
      pattern: "useImpostazioniFatturazione|useUpdateImpostazioniFatturazione"
    - from: "src/pages/Impostazioni.tsx"
      to: "SdiProviderSettings"
      via: "import e rendering con ErrorBoundary"
      pattern: "SdiProviderSettings"
---

<objective>
Creare il componente `SdiProviderSettings.tsx` che permette all'utente di scegliere il provider SDI
(Aruba / OpenAPI.com / Fattura24) e configurare la relativa API key. Aggiornare i tipi TypeScript e
il hook `use-fatture.ts` per supportare i 3 nuovi campi. Integrare il componente in Impostazioni.tsx.

Purpose: Senza questa UI l'utente non può switchare da Fattura24 ad Aruba. Il componente mostra
info di costo per ogni provider (€29.90/anno Aruba vs pay-per-use OpenAPI vs legacy Fattura24).

Output: Componente SdiProviderSettings funzionante + type-check OK.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/sdi-aruba-multi-provider/
@.planning/phases/sdi-aruba-multi-provider/sdi-aruba-01-SUMMARY.md
@.planning/phases/sdi-aruba-multi-provider/sdi-aruba-02-SUMMARY.md

# File esistenti da leggere prima di modificare
@src/types/fatture.ts
@src/hooks/use-fatture.ts
@src/pages/Impostazioni.tsx

# Convenzioni UI del progetto
@src/components/impostazioni/SmtpSettings.tsx
</context>

<tasks>

<task type="auto">
  <name>Task 1: TypeScript — aggiorna ImpostazioniFatturazione e hook</name>
  <files>
    src/types/fatture.ts
    src/hooks/use-fatture.ts
  </files>
  <action>
**FILE 1: src/types/fatture.ts**

Nell'`ImpostazioniFatturazioneSchema` (Zod), aggiungi dopo `fattura24_api_key`:
```typescript
sdi_provider: z.string().default('fattura24'),
aruba_api_key: z.string().nullable(),
openapi_api_key: z.string().nullable(),
```

Il tipo `ImpostazioniFatturazione` viene già derivato automaticamente da `z.infer<typeof ImpostazioniFatturazioneSchema>`.

**FILE 2: src/hooks/use-fatture.ts**

Aggiorna `useUpdateImpostazioniFatturazione`:
```typescript
export function useUpdateImpostazioniFatturazione() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<ImpostazioniFatturazione>) =>
      invoke<ImpostazioniFatturazione>('update_impostazioni_fatturazione', {
        // campi esistenti invariati:
        denominazione: data.denominazione ?? '',
        partita_iva: data.partita_iva ?? '',
        codice_fiscale: data.codice_fiscale ?? null,
        regime_fiscale: data.regime_fiscale ?? 'RF18',
        indirizzo: data.indirizzo ?? '',
        cap: data.cap ?? '',
        comune: data.comune ?? '',
        provincia: data.provincia ?? '',
        telefono: data.telefono ?? null,
        email: data.email ?? null,
        pec: data.pec ?? null,
        prefisso_numerazione: data.prefisso_numerazione ?? null,
        aliquota_iva_default: data.aliquota_iva_default ?? 22,
        natura_iva_default: data.natura_iva_default ?? null,
        iban: data.iban ?? null,
        bic: data.bic ?? null,
        nome_banca: data.nome_banca ?? null,
        fattura24_api_key: data.fattura24_api_key ?? null,
        // NUOVI campi multi-provider:
        sdi_provider: data.sdi_provider ?? null,
        aruba_api_key: data.aruba_api_key ?? null,
        openapi_api_key: data.openapi_api_key ?? null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: fattureKeys.impostazioni() })
    },
  })
}
```

NOTA: Il hook attuale usa `mutationFn: (data: Partial<ImpostazioniFatturazione>) => invoke<ImpostazioniFatturazione>('update_impostazioni_fatturazione', data)` che passa i campi direttamente. Questo NON funziona con Tauri commands che richiedono parametri espliciti. Usa la versione con mapping esplicito sopra.

Zero `any` — tutti i tipi devono essere esplicitamente tipati.
  </action>
  <verify>
```bash
npm run type-check 2>&1 | head -30
# Verifica nessun errore in src/types/fatture.ts e src/hooks/use-fatture.ts
grep -n "sdi_provider\|aruba_api_key\|openapi_api_key" src/types/fatture.ts
grep -n "sdi_provider\|aruba_api_key\|openapi_api_key" src/hooks/use-fatture.ts
```
  </verify>
  <done>
- ImpostazioniFatturazioneSchema ha sdi_provider, aruba_api_key, openapi_api_key
- useUpdateImpostazioniFatturazione mappa esplicitamente i 3 nuovi campi
- npm run type-check: 0 errori nei file modificati
  </done>
</task>

<task type="auto">
  <name>Task 2: UI — SdiProviderSettings.tsx + integrazione Impostazioni</name>
  <files>
    src/components/impostazioni/SdiProviderSettings.tsx
    src/pages/Impostazioni.tsx
  </files>
  <action>
**FILE 1: Crea `src/components/impostazioni/SdiProviderSettings.tsx`**

```typescript
// ═══════════════════════════════════════════════════════════════════
// FLUXION — SDI Provider Settings
// Selezione provider intermediario SDI: Aruba FE / OpenAPI.com / Fattura24
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useImpostazioniFatturazione, useUpdateImpostazioniFatturazione } from '@/hooks/use-fatture'
import { toast } from 'sonner'

type SdiProviderType = 'fattura24' | 'aruba' | 'openapi'

interface ProviderInfo {
  id: SdiProviderType
  nome: string
  costo: string
  descrizione: string
  linkDoc: string
  labelKey: string
  placeholderKey: string
}

const PROVIDERS: ProviderInfo[] = [
  {
    id: 'aruba',
    nome: 'Aruba Fatturazione Elettronica',
    costo: '€29.90/anno — invii ILLIMITATI',
    descrizione: 'Conservazione decennale inclusa. Il provider più conveniente per PMI con 20+ fatture/anno.',
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
    descrizione: 'Provider originale FLUXION. Mantiene retrocompatibilità per chi lo usa già.',
    linkDoc: 'https://api.fattura24.com',
    labelKey: 'API Key Fattura24',
    placeholderKey: 'Fattura24 API Key',
  },
]

export const SdiProviderSettings: FC = () => {
  const { data: impostazioni, isLoading } = useImpostazioniFatturazione()
  const updateMutation = useUpdateImpostazioniFatturazione()

  const [providerSelezionato, setProviderSelezionato] = useState<SdiProviderType>('fattura24')
  const [arubaKey, setArubaKey] = useState('')
  const [openapiKey, setOpenapiKey] = useState('')
  const [fattura24Key, setFattura24Key] = useState('')
  const [salvato, setSalvato] = useState(false)

  // Inizializza stato dal DB
  useEffect(() => {
    if (impostazioni) {
      const p = impostazioni.sdi_provider as SdiProviderType
      if (p === 'aruba' || p === 'openapi' || p === 'fattura24') {
        setProviderSelezionato(p)
      }
      setArubaKey(impostazioni.aruba_api_key ?? '')
      setOpenapiKey(impostazioni.openapi_api_key ?? '')
      setFattura24Key(impostazioni.fattura24_api_key ?? '')
    }
  }, [impostazioni])

  const handleSalva = async () => {
    if (!impostazioni) return;
    try {
      await updateMutation.mutateAsync({
        ...impostazioni,
        sdi_provider: providerSelezionato,
        aruba_api_key: arubaKey || null,
        openapi_api_key: openapiKey || null,
        fattura24_api_key: fattura24Key || null,
      })
      setSalvato(true)
      toast.success('Impostazioni SDI salvate')
      setTimeout(() => setSalvato(false), 3000)
    } catch (err) {
      toast.error(`Errore salvataggio SDI: ${String(err)}`)
    }
  }

  const providerAttivo = PROVIDERS.find((p) => p.id === providerSelezionato) ?? PROVIDERS[0]

  if (isLoading) {
    return (
      <Card className="p-6 bg-slate-900 border-slate-800">
        <p className="text-slate-400">Caricamento impostazioni SDI...</p>
      </Card>
    )
  }

  return (
    <Card className="p-6 bg-slate-900 border-slate-800">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">Integrazione SDI</h2>
        <p className="text-sm text-slate-400 mt-1">
          Scegli il provider intermediario per l'invio delle fatture al Sistema di Interscambio (AdE)
        </p>
      </div>

      {/* Selezione provider */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {PROVIDERS.map((provider) => {
          const isSelected = providerSelezionato === provider.id
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
              <p className="text-xs text-slate-500 mt-2 leading-relaxed">{provider.descrizione}</p>
            </button>
          )
        })}
      </div>

      {/* Campo API key dinamico */}
      <div className="space-y-4 mb-6">
        <div>
          <Label className="text-slate-300 mb-2 block">
            {providerAttivo.labelKey}
          </Label>
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

      {/* Azione */}
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
  )
}
```

**FILE 2: Modifica `src/pages/Impostazioni.tsx`**

Aggiungi import in cima al file (dopo gli import esistenti):
```typescript
import { SdiProviderSettings } from '@/components/impostazioni/SdiProviderSettings'
```

Aggiungi il rendering del componente PRIMA della sezione `DiagnosticsPanel` (cercare `{/* SEZIONE: Diagnostica`):
```tsx
{/* ─────────────────────────────────────────────────────────────── */}
{/* SEZIONE: Integrazione SDI Multi-Provider */}
{/* ─────────────────────────────────────────────────────────────── */}
<ErrorBoundary fallback={<SectionError name="Integrazione SDI" />}>
  <SdiProviderSettings />
</ErrorBoundary>
```

NON rimuovere nessuna sezione esistente da Impostazioni.tsx.
  </action>
  <verify>
```bash
npm run type-check 2>&1
# Deve terminare con 0 errori
# Se ci sono errori, correggere prima di procedere

grep -n "SdiProviderSettings" src/pages/Impostazioni.tsx
# Deve mostrare import e rendering

grep -n "sdi_provider\|aruba_api_key" src/components/impostazioni/SdiProviderSettings.tsx | head -5
```
  </verify>
  <done>
- SdiProviderSettings.tsx creato e compilato senza errori TypeScript
- Impostazioni.tsx importa e renderizza SdiProviderSettings
- Selezionando Aruba mostra campo Aruba API Key
- Selezionando OpenAPI mostra campo OpenAPI Key
- Selezionando Fattura24 mostra campo Fattura24 Key
- npm run type-check: 0 errori
  </done>
</task>

</tasks>

<verification>
Verifica obbligatoria:
1. `npm run type-check` — 0 errori TypeScript (bloccante)
2. `grep -n "any" src/components/impostazioni/SdiProviderSettings.tsx` — zero occorrenze
3. `grep -n "SdiProviderSettings" src/pages/Impostazioni.tsx` — almeno 2 righe (import + render)
4. `grep -n "sdi_provider" src/types/fatture.ts src/hooks/use-fatture.ts` — almeno 4 occorrenze totali
</verification>

<success_criteria>
- SdiProviderSettings.tsx: componente card con 3 provider selezionabili + campo API key dinamico
- ImpostazioniFatturazioneSchema aggiornato con sdi_provider, aruba_api_key, openapi_api_key
- useUpdateImpostazioniFatturazione mappa i 3 nuovi campi verso il Tauri command
- Impostazioni.tsx mostra SdiProviderSettings wrappata in ErrorBoundary
- npm run type-check: 0 errori — OBBLIGATORIO
- Zero any, zero as unknown nel codice nuovo
</success_criteria>

<output>
Dopo completamento, crea `.planning/phases/sdi-aruba-multi-provider/sdi-aruba-03-SUMMARY.md`
</output>
