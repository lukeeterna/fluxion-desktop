// ═══════════════════════════════════════════════════════════════════
// FLUXION - License Manager Component
// UI completa per gestione licenze Ed25519
// ═══════════════════════════════════════════════════════════════════

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { Separator } from '../ui/separator';
import { 
  useLicenseStatusEd25519, 
  useActivateLicenseEd25519, 
  useDeactivateLicenseEd25519,
  useTierInfoEd25519,
  useMachineFingerprint,
  useIsTrial,
  useIsTrialExpiring
} from '../../hooks/use-license-ed25519';
import { 
  getLicenseExpiryMessage, 
  getTierDisplayName,
  getTierColor,
  LICENSE_TIERS_ED25519
} from '../../types/license-ed25519';
import { 
  Key, 
  Shield, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle,
  Copy,
  Download,
  Upload,
  Sparkles,
  Cpu,
  Unlock,
  Lock
} from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════
// COMPONENT: Status Badge
// ═══════════════════════════════════════════════════════════════════

function StatusBadge({ status, isValid }: { status: string; isValid: boolean }) {
  if (!isValid) {
    return (
      <Badge variant="destructive" className="flex items-center gap-1">
        <XCircle className="w-3 h-3" />
        Non Valida
      </Badge>
    );
  }
  
  if (status === 'trial') {
    return (
      <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-400 flex items-center gap-1">
        <Clock className="w-3 h-3" />
        Trial
      </Badge>
    );
  }
  
  return (
    <Badge variant="default" className="bg-green-500/20 text-green-400 flex items-center gap-1">
      <CheckCircle2 className="w-3 h-3" />
      Attiva
    </Badge>
  );
}

// ═══════════════════════════════════════════════════════════════════
// COMPONENT: Tier Card
// ═══════════════════════════════════════════════════════════════════

function TierCard({ 
  tier, 
  isCurrent,
  onSelect 
}: { 
  tier: typeof LICENSE_TIERS_ED25519[0]; 
  isCurrent: boolean;
  onSelect?: () => void;
}) {
  const colorClasses: Record<string, string> = {
    yellow: 'border-yellow-500/50 bg-yellow-500/10',
    blue: 'border-blue-500/50 bg-blue-500/10',
    purple: 'border-purple-500/50 bg-purple-500/10',
    gold: 'border-amber-500/50 bg-amber-500/10',
  };

  return (
    <div 
      className={`
        relative p-4 rounded-lg border-2 transition-all
        ${isCurrent ? colorClasses[tier.color] || 'border-cyan-500 bg-cyan-500/10' : 'border-slate-700 bg-slate-800'}
        ${onSelect ? 'cursor-pointer hover:border-slate-500' : ''}
      `}
      onClick={onSelect}
    >
      {isCurrent && (
        <div className="absolute -top-2 -right-2">
          <Badge className="bg-green-500 text-white">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            Attuale
          </Badge>
        </div>
      )}
      
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-white font-semibold">{tier.label}</h3>
          <p className="text-slate-400 text-sm">{tier.description}</p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold text-cyan-400">
            {tier.price === 0 ? 'Gratis' : `€${tier.price}`}
          </span>
          {tier.price > 0 && <span className="text-slate-500 text-sm block">Lifetime</span>}
        </div>
      </div>
      
      <ul className="space-y-1">
        {tier.features.map((feature, idx) => (
          <li key={idx} className="flex items-center gap-2 text-sm text-slate-300">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            {feature}
          </li>
        ))}
      </ul>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// COMPONENT: LicenseManager
// ═══════════════════════════════════════════════════════════════════

export function LicenseManager() {
  const { data: status, isLoading: isLoadingStatus, refetch } = useLicenseStatusEd25519();
  const { data: tierInfo } = useTierInfoEd25519();
  const { data: fingerprint } = useMachineFingerprint();
  const isTrial = useIsTrial();
  const isTrialExpiring = useIsTrialExpiring();
  
  const activateLicense = useActivateLicenseEd25519();
  const deactivateLicense = useDeactivateLicenseEd25519();
  
  const [licenseKey, setLicenseKey] = useState('');
  const [activeTab, setActiveTab] = useState('status');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleActivate = async () => {
    if (!licenseKey.trim()) return;
    
    const result = await activateLicense.mutateAsync(licenseKey.trim());
    
    if (result.success) {
      setLicenseKey('');
      refetch();
    }
    
    alert(result.message);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      const content = await file.text();
      setLicenseKey(content);
    } catch (error) {
      alert('Errore nella lettura del file');
    }
  };

  const handleDeactivate = async () => {
    if (!confirm('Sei sicuro di voler disattivare la licenza? Tornerai alla modalità trial.')) {
      return;
    }
    
    await deactivateLicense.mutateAsync();
    refetch();
  };

  const copyFingerprint = () => {
    if (fingerprint) {
      navigator.clipboard.writeText(fingerprint);
      alert('Fingerprint copiato negli appunti!');
    }
  };

  if (isLoadingStatus) {
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Shield className="w-6 h-6 text-cyan-500" />
            Gestione Licenza
          </h1>
          <p className="text-slate-400">Gestisci la tua licenza FLUXION</p>
        </div>
        <StatusBadge status={status?.status || 'none'} isValid={status?.is_valid || false} />
      </div>

      {/* Alerts */}
      {isTrialExpiring && (
        <Alert className="bg-yellow-500/10 border-yellow-500/50">
          <AlertTriangle className="w-4 h-4 text-yellow-500" />
          <AlertDescription className="text-yellow-200">
            {expiryMessage}. Attiva una licenza per continuare a usare FLUXION senza interruzioni.
          </AlertDescription>
        </Alert>
      )}

      {status?.validation_code === 'HARDWARE_MISMATCH' && (
        <Alert variant="destructive">
          <XCircle className="w-4 h-4" />
          <AlertDescription>
            Questa licenza è valida per un'altra macchina. Contatta il supporto per trasferire la licenza.
          </AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-900">
          <TabsTrigger value="status" className="data-[state=active]:bg-slate-700">
            <Shield className="w-4 h-4 mr-2" />
            Stato
          </TabsTrigger>
          <TabsTrigger value="activate" className="data-[state=active]:bg-slate-700">
            <Key className="w-4 h-4 mr-2" />
            Attiva Licenza
          </TabsTrigger>
          <TabsTrigger value="tiers" className="data-[state=active]:bg-slate-700">
            <Sparkles className="w-4 h-4 mr-2" />
            Piani
          </TabsTrigger>
        </TabsList>

        {/* Tab: Stato */}
        <TabsContent value="status" className="space-y-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Stato Licenza</CardTitle>
              <CardDescription className="text-slate-400">
                Informazioni sulla licenza attuale
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900 p-4 rounded-lg">
                  <Label className="text-slate-500 text-sm">Piano</Label>
                  <p className="text-white text-lg font-medium">{status?.tier_display || 'Nessuna'}</p>
                </div>
                <div className="bg-slate-900 p-4 rounded-lg">
                  <Label className="text-slate-500 text-sm">Stato</Label>
                  <p className={`text-lg font-medium ${status?.is_valid ? 'text-green-400' : 'text-red-400'}`}>
                    {status?.is_valid ? 'Valida' : 'Non Valida'}
                  </p>
                </div>
              </div>

              {status?.license_id && (
                <div className="bg-slate-900 p-4 rounded-lg">
                  <Label className="text-slate-500 text-sm">ID Licenza</Label>
                  <p className="text-slate-300 font-mono">{status.license_id}</p>
                </div>
              )}

              {status?.licensee_name && (
                <div className="bg-slate-900 p-4 rounded-lg">
                  <Label className="text-slate-500 text-sm">Licenziatario</Label>
                  <p className="text-white">{status.licensee_name}</p>
                  {status.licensee_email && (
                    <p className="text-slate-400 text-sm">{status.licensee_email}</p>
                  )}
                </div>
              )}

              {status?.expiry_date && (
                <div className="bg-slate-900 p-4 rounded-lg">
                  <Label className="text-slate-500 text-sm">Scadenza</Label>
                  <p className={`text-lg font-medium ${isTrialExpiring ? 'text-yellow-400' : 'text-slate-300'}`}>
                    {new Date(status.expiry_date).toLocaleDateString('it-IT')}
                  </p>
                  {expiryMessage && (
                    <p className={`text-sm ${isTrialExpiring ? 'text-yellow-400' : 'text-slate-500'}`}>
                      {expiryMessage}
                    </p>
                  )}
                </div>
              )}

              <Separator className="bg-slate-700" />

              {/* Hardware Fingerprint */}
              <div className="bg-slate-900 p-4 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <Label className="text-slate-500 text-sm flex items-center gap-2">
                    <Cpu className="w-4 h-4" />
                    Hardware Fingerprint
                  </Label>
                  <Button size="sm" variant="outline" onClick={copyFingerprint}>
                    <Copy className="w-4 h-4 mr-1" />
                    Copia
                  </Button>
                </div>
                <p className="text-slate-300 font-mono text-sm break-all">{fingerprint || 'Caricamento...'}</p>
                <p className="text-slate-500 text-xs mt-2">
                  Questo codice identifica univocamente questa macchina. 
                  Servono per generare una licenza personalizzata.
                </p>
              </div>

              {/* Verticali abilitate */}
              {status?.enabled_verticals && status.enabled_verticals.length > 0 && (
                <div className="bg-slate-900 p-4 rounded-lg">
                  <Label className="text-slate-500 text-sm">Verticali Abilitate</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {status.enabled_verticals.map(v => (
                      <Badge key={v} variant="secondary" className="capitalize">
                        {v.replace('_', ' ')}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Pulsante disattiva */}
              {status?.is_activated && status.tier !== 'trial' && (
                <Button 
                  variant="destructive" 
                  onClick={handleDeactivate}
                  disabled={deactivateLicense.isPending}
                  className="w-full"
                >
                  <Lock className="w-4 h-4 mr-2" />
                  Disattiva Licenza
                </Button>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Attiva */}
        <TabsContent value="activate" className="space-y-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Attiva Licenza</CardTitle>
              <CardDescription className="text-slate-400">
                Inserisci il codice licenza ricevuto o carica il file
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label className="text-slate-300">Codice Licenza</Label>
                <Textarea
                  value={licenseKey}
                  onChange={(e) => setLicenseKey(e.target.value)}
                  placeholder="Incolla qui il codice licenza JSON..."
                  className="bg-slate-700 border-slate-600 text-white min-h-[200px] font-mono text-sm"
                />
              </div>

              <div className="flex gap-2">
                <input
                  type="file"
                  accept=".json"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
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
                  onClick={handleActivate}
                  disabled={!licenseKey.trim() || activateLicense.isPending}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                >
                  <Unlock className="w-4 h-4 mr-2" />
                  {activateLicense.isPending ? 'Attivazione...' : 'Attiva Licenza'}
                </Button>
              </div>

              <div className="bg-slate-900 p-4 rounded-lg">
                <h4 className="text-white font-medium mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500" />
                  Come ottenere una licenza
                </h4>
                <ol className="text-slate-400 text-sm space-y-2 list-decimal list-inside">
                  <li>Copia il tuo <strong>Hardware Fingerprint</strong> dalla scheda Stato</li>
                  <li>Invialo al venditore autorizzato FLUXION</li>
                  <li>Riceverai un file <code>license.json</code> personalizzato</li>
                  <li>Carica il file qui o incolla il contenuto</li>
                  <li>Clicca "Attiva Licenza"</li>
                </ol>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab: Piani */}
        <TabsContent value="tiers" className="space-y-6">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Piani Disponibili</CardTitle>
              <CardDescription className="text-slate-400">
                Scegli il piano più adatto alle tue esigenze
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {LICENSE_TIERS_ED25519.map((tier) => (
                  <TierCard
                    key={tier.value}
                    tier={tier}
                    isCurrent={status?.tier === tier.value}
                  />
                ))}
              </div>

              <div className="mt-6 bg-slate-900 p-4 rounded-lg">
                <h4 className="text-white font-medium mb-2">Note</h4>
                <ul className="text-slate-400 text-sm space-y-1">
                  <li>• Tutte le licenze sono <strong>LIFETIME</strong> (a vita)</li>
                  <li>• Una licenza è valida per una sola macchina (hardware-locked)</li>
                  <li>• Il trial di 30 giorni include tutte le funzionalità</li>
                  <li>• Per acquistare contatta un rivenditore autorizzato FLUXION</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default LicenseManager;
