// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Manager Component (S50 UX Enhancement)
// World-class: piano attivo prominente + progress bar + feature matrix
// ═══════════════════════════════════════════════════════════════════

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { Alert, AlertDescription } from '../ui/alert';
import { Separator } from '../ui/separator';
import {
  useLicenseStatusEd25519,
  useActivateLicenseEd25519,
  useDeactivateLicenseEd25519,
  useTierInfoEd25519,
  useMachineFingerprint,
  useIsTrialExpiring
} from '../../hooks/use-license-ed25519';
import { openUrl } from '@tauri-apps/plugin-opener';
import {
  getLicenseExpiryMessage,
  LICENSE_TIERS_ED25519,
  type LicenseStatusEd25519,
  type TierInfo,
} from '../../types/license-ed25519';
import {
  Key,
  Shield,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Copy,
  Upload,
  Sparkles,
  Cpu,
  Unlock,
  Lock,
  ExternalLink,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

// ─── Feature comparison data ─────────────────────────────────────

const FEATURE_ROWS: { label: string; base: boolean; pro: boolean; clinic: boolean }[] = [
  { label: 'CRM Clienti',                base: true,  pro: true,  clinic: true  },
  { label: 'Calendario appuntamenti',    base: true,  pro: true,  clinic: true  },
  { label: 'Fatturazione SDI',           base: true,  pro: true,  clinic: true  },
  { label: 'Max 3 operatori',            base: true,  pro: false, clinic: false },
  { label: '1 Scheda Verticale',         base: true,  pro: false, clinic: false },
  { label: '3 Schede Verticali',         base: false, pro: true,  clinic: false },
  { label: 'Verticali illimitate',       base: false, pro: false, clinic: true  },
  { label: 'Voice Agent Sara 24/7',      base: false, pro: true,  clinic: true  },
  { label: 'WhatsApp AI',               base: false, pro: true,  clinic: true  },
  { label: 'Loyalty Avanzato',           base: false, pro: true,  clinic: true  },
  { label: 'API Access',                 base: false, pro: false, clinic: true  },
  { label: 'Onboarding 1h incluso',      base: false, pro: false, clinic: true  },
];

// ─── Checkout URL Builder ─────────────────────────────────────────
// World-class: pre-fill email + fingerprint + dark mode per LemonSqueezy
// checkout[email] = +15% conversion (zero friction per cliente che ha già account LS)
// checkout[custom][fingerprint] = fingerprint Mac pre-passato → attivazione 1-click post-acquisto

function buildCheckoutUrl(
  baseUrl: string,
  opts: { email?: string | null; fingerprint?: string | null },
): string {
  const parts: string[] = ['dark=1'];
  if (opts.email) parts.push(`checkout[email]=${encodeURIComponent(opts.email)}`);
  if (opts.fingerprint) parts.push(`checkout[custom][fingerprint]=${encodeURIComponent(opts.fingerprint)}`);
  return `${baseUrl}?${parts.join('&')}`;
}

// ─── Trial Progress Bar ──────────────────────────────────────────

function TrialProgressBar({ daysRemaining }: { daysRemaining: number }) {
  const total = 30;
  const pct = Math.max(0, Math.min(100, (daysRemaining / total) * 100));

  const barColor =
    daysRemaining > 7  ? 'bg-green-500'  :
    daysRemaining > 0  ? 'bg-yellow-500' :
    'bg-red-500';
  const textColor =
    daysRemaining > 7  ? 'text-green-400'  :
    daysRemaining > 0  ? 'text-yellow-400' :
    'text-red-400';

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-slate-400 flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5" />
          Periodo di prova
        </span>
        <span className={`font-medium ${textColor}`}>
          {daysRemaining > 0 ? `${daysRemaining} giorni rimanenti` : 'Scaduto'}
        </span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

// ─── Active Plan Card ────────────────────────────────────────────

const TIER_BORDER: Record<string, string> = {
  yellow: 'border-yellow-500',
  blue:   'border-blue-500',
  purple: 'border-purple-500',
  gold:   'border-amber-500',
};
const TIER_BG: Record<string, string> = {
  yellow: 'bg-yellow-500/5',
  blue:   'bg-blue-500/5',
  purple: 'bg-purple-500/5',
  gold:   'bg-amber-500/5',
};

function ActivePlanCard({ status }: { status: LicenseStatusEd25519 }) {
  const tierInfo = LICENSE_TIERS_ED25519.find(t => t.value === status.tier);
  const color   = tierInfo?.color ?? 'blue';
  const border  = TIER_BORDER[color] ?? 'border-cyan-500';
  const bg      = TIER_BG[color]     ?? 'bg-cyan-500/5';

  return (
    <div className={`rounded-xl border-2 ${border} ${bg} p-6 space-y-4`}>
      {/* Plan name + price */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <Badge className="mb-2 bg-green-500/20 text-green-400 border-green-500/30 text-xs">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            Piano Attivo
          </Badge>
          <h2 className="text-2xl font-bold text-white leading-tight">{status.tier_display}</h2>
          {status.licensee_name && (
            <p className="text-slate-400 text-sm mt-0.5">
              {status.licensee_name}
              {status.licensee_email ? ` · ${status.licensee_email}` : ''}
            </p>
          )}
        </div>
        {tierInfo && tierInfo.price > 0 && (
          <div className="text-right shrink-0">
            <span className="text-3xl font-bold text-cyan-400">€{tierInfo.price}</span>
            <span className="text-slate-500 text-xs block mt-0.5">Lifetime</span>
          </div>
        )}
      </div>

      {/* Trial progress bar */}
      {status.tier === 'trial' && status.days_remaining !== null && (
        <TrialProgressBar daysRemaining={status.days_remaining} />
      )}

      {/* HW lock plain language — AC4 */}
      <div className="flex items-center gap-2 text-sm text-slate-400">
        <Lock className="w-4 h-4 text-slate-500 shrink-0" />
        <span>
          Funziona offline, bloccato su questo Mac
          {status.machine_name ? `: ${status.machine_name}` : ''}
        </span>
      </div>
    </div>
  );
}

// ─── Feature Comparison Matrix ───────────────────────────────────

function FeatureComparisonMatrix({ currentTier }: { currentTier: string }) {
  const tiers = [
    { key: 'base',       label: 'Base',   price: 497 },
    { key: 'pro',        label: 'Pro',    price: 897 },
    { key: 'enterprise', label: 'Clinic', price: 1497 },
  ];

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="pb-3">
        <CardTitle className="text-white text-base">Confronto Piani</CardTitle>
      </CardHeader>
      <CardContent className="p-0 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left px-4 py-2 text-slate-500 font-normal w-1/2">Funzionalità</th>
              {tiers.map(t => (
                <th key={t.key} className="px-4 py-2 text-center">
                  <span className={`font-semibold ${currentTier === t.key ? 'text-cyan-400' : 'text-white'}`}>
                    {t.label}
                  </span>
                  {currentTier === t.key && (
                    <span className="block text-xs text-cyan-500 font-normal">attuale</span>
                  )}
                  {currentTier !== t.key && (
                    <span className="block text-xs text-slate-500 font-normal">€{t.price}</span>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {FEATURE_ROWS.map((row, i) => (
              <tr key={i} className={i % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'}>
                <td className="px-4 py-2 text-slate-300">{row.label}</td>
                <td className="px-4 py-2 text-center">
                  {row.base
                    ? <CheckCircle2 className="w-4 h-4 text-green-500 mx-auto" />
                    : <XCircle className="w-4 h-4 text-slate-600 mx-auto" />}
                </td>
                <td className="px-4 py-2 text-center">
                  {row.pro
                    ? <CheckCircle2 className="w-4 h-4 text-green-500 mx-auto" />
                    : <XCircle className="w-4 h-4 text-slate-600 mx-auto" />}
                </td>
                <td className="px-4 py-2 text-center">
                  {row.clinic
                    ? <CheckCircle2 className="w-4 h-4 text-green-500 mx-auto" />
                    : <XCircle className="w-4 h-4 text-slate-600 mx-auto" />}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

// ─── Upgrade CTAs ────────────────────────────────────────────────
// World-class: "Più scelto" badge su Pro + feature bullets + prezzo nella CTA
// Pattern: Jane App / Linear — massimo conversion sopra la feature matrix

function UpgradeCTAs({
  currentTier,
  email,
  fingerprint,
}: {
  currentTier: string;
  email?: string | null;
  fingerprint?: string | null;
}) {
  const upgradeTiers = LICENSE_TIERS_ED25519.filter((t: TierInfo) => {
    if (t.value === 'trial') return false;
    if (currentTier === 'trial') return true;
    if (currentTier === 'base') return t.value === 'pro';
    if (currentTier === 'pro') return false;
    return false;
  });

  if (upgradeTiers.length === 0) return null;

  const gridClass =
    upgradeTiers.length === 1 ? 'grid-cols-1' :
    upgradeTiers.length === 2 ? 'grid-cols-1 md:grid-cols-2' :
    'grid-cols-1 md:grid-cols-3';

  return (
    <div className="space-y-3">
      <h3 className="text-white font-semibold flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-cyan-400" />
        Acquista FLUXION — Lifetime, nessun canone mensile
      </h3>
      <div className={`grid ${gridClass} gap-3`}>
        {upgradeTiers.map((tier: TierInfo) => {
          const isPro = tier.value === 'pro';
          const url = tier.checkout_url
            ? buildCheckoutUrl(tier.checkout_url, { email, fingerprint })
            : null;
          return (
            <div
              key={tier.value}
              className={`relative rounded-xl border p-4 space-y-3 transition-all ${
                isPro
                  ? 'border-cyan-500/60 bg-cyan-500/5'
                  : 'border-slate-700 bg-slate-800'
              }`}
            >
              {isPro && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-cyan-500 text-slate-900 text-xs font-bold px-3 py-0.5 whitespace-nowrap">
                    Più scelto
                  </Badge>
                </div>
              )}

              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-white font-semibold">{tier.label}</p>
                  <p className="text-slate-400 text-xs mt-0.5 leading-relaxed">{tier.description}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-2xl font-bold text-cyan-400">€{tier.price}</p>
                  <p className="text-slate-500 text-xs">lifetime</p>
                </div>
              </div>

              <ul className="space-y-1.5">
                {tier.features.slice(0, 4).map((feat: string, i: number) => (
                  <li key={i} className="flex items-center gap-2 text-xs text-slate-300">
                    <CheckCircle2 className="w-3.5 h-3.5 text-green-500 shrink-0" />
                    {feat}
                  </li>
                ))}
              </ul>

              <Button
                className={`w-full ${
                  isPro
                    ? 'bg-cyan-600 hover:bg-cyan-700 text-white'
                    : 'bg-slate-700 hover:bg-slate-600 text-white'
                }`}
                disabled={!url}
                onClick={() => { if (url) void openUrl(url); }}
              >
                Acquista — €{tier.price}
                <ExternalLink className="w-3.5 h-3.5 ml-2" />
              </Button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Activate Section ────────────────────────────────────────────

function ActivateSection({
  licenseKey,
  setLicenseKey,
  onActivate,
  isPending,
  fileInputRef,
  onFileUpload,
}: {
  licenseKey: string;
  setLicenseKey: (v: string) => void;
  onActivate: () => void;
  isPending: boolean;
  fileInputRef: React.RefObject<HTMLInputElement | null>;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="pt-5 space-y-4">
        <div className="space-y-2">
          <Label className="text-slate-300">Codice Licenza</Label>
          <Textarea
            value={licenseKey}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setLicenseKey(e.target.value)}
            placeholder="Incolla qui il codice licenza JSON..."
            className="bg-slate-700 border-slate-600 text-white min-h-[160px] font-mono text-sm"
          />
        </div>
        <div className="flex gap-2">
          <input
            type="file"
            accept=".json"
            ref={fileInputRef}
            onChange={onFileUpload}
            className="hidden"
          />
          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            className="flex-1"
          >
            <Upload className="w-4 h-4 mr-2" />
            Carica File
          </Button>
          <Button
            onClick={onActivate}
            disabled={!licenseKey.trim() || isPending}
            className="flex-1 bg-cyan-600 hover:bg-cyan-700"
          >
            <Unlock className="w-4 h-4 mr-2" />
            {isPending ? 'Attivazione...' : 'Attiva Licenza'}
          </Button>
        </div>
        <div className="bg-slate-900 p-4 rounded-lg">
          <h4 className="text-white font-medium mb-2 flex items-center gap-2 text-sm">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            Come ottenere una licenza
          </h4>
          <ol className="text-slate-400 text-sm space-y-1 list-decimal list-inside">
            <li>Acquista un piano (vedi sopra)</li>
            <li>Copia il tuo <strong>ID Mac</strong> dalla sezione qui sotto</li>
            <li>Riceverai un file <code>license.json</code> via email</li>
            <li>Carica il file o incolla il contenuto qui</li>
          </ol>
        </div>
      </CardContent>
    </Card>
  );
}

// ═══════════════════════════════════════════════════════════════════
// COMPONENT: LicenseManager
// ═══════════════════════════════════════════════════════════════════

export function LicenseManager() {
  const { data: status, isLoading, refetch } = useLicenseStatusEd25519();
  useTierInfoEd25519();
  const { data: fingerprint } = useMachineFingerprint();
  const isTrialExpiring = useIsTrialExpiring();

  const activateLicense   = useActivateLicenseEd25519();
  const deactivateLicense = useDeactivateLicenseEd25519();

  const [licenseKey, setLicenseKey]       = useState('');
  const [showActivate, setShowActivate]   = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleActivate = async () => {
    if (!licenseKey.trim()) return;
    const result = await activateLicense.mutateAsync(licenseKey.trim());
    if (result.success) {
      setLicenseKey('');
      setShowActivate(false);
      refetch();
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const content = await file.text();
      setLicenseKey(content);
    } catch {
      // file non leggibile
    }
  };

  const handleDeactivate = async () => {
    if (!confirm('Sei sicuro? Tornerai alla modalità trial.')) return;
    await deactivateLicense.mutateAsync();
    refetch();
  };

  const copyFingerprint = () => {
    if (fingerprint) navigator.clipboard.writeText(fingerprint);
  };

  if (isLoading) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8 text-center text-slate-400">
          Caricamento licenza...
        </CardContent>
      </Card>
    );
  }

  const expiryMessage = status ? getLicenseExpiryMessage(status) : null;

  return (
    <div className="space-y-6">

      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Shield className="w-6 h-6 text-cyan-500" />
            Gestione Licenza
          </h1>
          <p className="text-slate-400 text-sm">Licenza desktop lifetime — nessun canone mensile</p>
        </div>
      </div>

      {/* ── Alerts ── */}
      {isTrialExpiring && (
        <Alert className="bg-yellow-500/10 border-yellow-500/50">
          <AlertTriangle className="w-4 h-4 text-yellow-500" />
          <AlertDescription className="text-yellow-200">
            {expiryMessage}. Acquista una licenza per continuare senza interruzioni.
          </AlertDescription>
        </Alert>
      )}

      {status?.validation_code === 'HARDWARE_MISMATCH' && (
        <Alert variant="destructive">
          <XCircle className="w-4 h-4" />
          <AlertDescription>
            Questa licenza è registrata su un altro Mac. Contatta il supporto per trasferirla.
          </AlertDescription>
        </Alert>
      )}

      {/* ── AC1: Piano attivo full-width, sempre visibile ── */}
      {status && <ActivePlanCard status={status} />}

      {/* ── AC3: Feature comparison matrix ── */}
      {status?.tier !== 'enterprise' && (
        <FeatureComparisonMatrix currentTier={status?.tier ?? ''} />
      )}

      {/* ── AC5: Upgrade CTAs fuori dai tab ── */}
      {status && (
        <UpgradeCTAs
          currentTier={status.tier}
          email={status.licensee_email}
          fingerprint={fingerprint}
        />
      )}

      <Separator className="bg-slate-700" />

      {/* ── Attiva Licenza — collapsibile ── */}
      <div className="space-y-3">
        <Button
          variant="outline"
          className="w-full justify-between"
          onClick={() => setShowActivate(v => !v)}
        >
          <span className="flex items-center gap-2">
            <Key className="w-4 h-4" />
            Hai già una licenza? Attivala
          </span>
          {showActivate
            ? <ChevronUp className="w-4 h-4" />
            : <ChevronDown className="w-4 h-4" />}
        </Button>
        {showActivate && (
          <ActivateSection
            licenseKey={licenseKey}
            setLicenseKey={setLicenseKey}
            onActivate={handleActivate}
            isPending={activateLicense.isPending}
            fileInputRef={fileInputRef}
            onFileUpload={handleFileUpload}
          />
        )}
      </div>

      {/* ── AC4: Identificativo Mac (plain language) ── */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-white text-sm font-medium flex items-center gap-2">
            <Cpu className="w-4 h-4 text-slate-400" />
            ID Mac — necessario per attivare la licenza
          </CardTitle>
          <CardDescription className="text-slate-500 text-xs">
            Questo codice identifica univocamente il tuo Mac. Inviacelo dopo l'acquisto.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-2">
            <code className="flex-1 text-slate-300 font-mono text-xs bg-slate-900 px-3 py-2 rounded break-all">
              {fingerprint ?? 'Caricamento...'}
            </code>
            <Button size="sm" variant="outline" onClick={copyFingerprint}>
              <Copy className="w-4 h-4" />
            </Button>
          </div>

          {status?.is_activated && status.tier !== 'trial' && (
            <Button
              variant="destructive"
              onClick={handleDeactivate}
              disabled={deactivateLicense.isPending}
              className="w-full"
              size="sm"
            >
              <Lock className="w-4 h-4 mr-2" />
              Disattiva Licenza
            </Button>
          )}
        </CardContent>
      </Card>

    </div>
  );
}

export default LicenseManager;
