// ═══════════════════════════════════════════════════════════════════
// FLUXION - Scheda Cliente Dynamic Component
// Switcher che carica la scheda corretta in base alla micro categoria
// ═══════════════════════════════════════════════════════════════════

import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { useSetupConfig } from '../../hooks/use-setup';
import { useLicenseStatusEd25519 } from '../../hooks/use-license-ed25519';
import { SchedaOdontoiatrica } from './SchedaOdontoiatrica';
import { SchedaFisioterapia } from './SchedaFisioterapia';
import { SchedaEstetica } from './SchedaEstetica';
import { 
  Stethoscope, 
  Sparkles, 
  Scissors, 
  Car, 
  Dumbbell,
  User,
  Lock
} from 'lucide-react';
import { Button } from '../ui/button';

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

export interface SchedaClienteDynamicProps {
  clienteId: string;
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Scheda Base (Fallback)
// ─────────────────────────────────────────────────────────────────────

function SchedaBase({ clienteId }: { clienteId: string }) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <User className="w-5 h-5" />
          Scheda Cliente
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-slate-400">
          Nessuna scheda specifica disponibile per questa categoria.
        </p>
        <p className="text-slate-500 text-sm mt-2">
          Cliente ID: {clienteId}
        </p>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Scheda Bloccata (Licenza insufficiente)
// ─────────────────────────────────────────────────────────────────────

function SchedaBloccata({ 
  vertical, 
  tier 
}: { 
  vertical: string; 
  tier: string;
}) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-amber-500/20 rounded-lg">
          <Lock className="w-6 h-6 text-amber-500" />
        </div>
        <div>
          <CardTitle className="text-white">Scheda Non Disponibile</CardTitle>
          <p className="text-sm text-slate-400">Aggiorna la tua licenza per sbloccare</p>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="bg-slate-900 p-4 rounded-lg text-center">
          <p className="text-slate-300 mb-2">
            La scheda <span className="text-amber-400 font-medium">{vertical}</span> non è inclusa nel tuo piano attuale.
          </p>
          <p className="text-slate-500 text-sm">
            Piano attuale: <span className="text-cyan-400">{tier}</span>
          </p>
        </div>
        <div className="flex justify-center">
          <Button className="bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700">
            <Sparkles className="w-4 h-4 mr-2" />
            Aggiorna Licenza
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Scheda Parrucchiere
// ─────────────────────────────────────────────────────────────────────

function SchedaParrucchiere({ clienteId }: { clienteId: string }) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-purple-500/20 rounded-lg">
          <Scissors className="w-6 h-6 text-purple-500" />
        </div>
        <div>
          <CardTitle className="text-white">Scheda Parrucchiere</CardTitle>
          <p className="text-sm text-slate-400">Gestione capelli e colorazioni</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="bg-slate-900 p-4 rounded-lg">
            <h4 className="text-white font-medium mb-2">📝 In Sviluppo</h4>
            <p className="text-slate-400 text-sm">
              La scheda parrucchiere completa è in fase di sviluppo.
              <br />Cliente ID: {clienteId}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Scheda Veicoli
// ─────────────────────────────────────────────────────────────────────

function SchedaVeicoli({ clienteId }: { clienteId: string }) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-blue-500/20 rounded-lg">
          <Car className="w-6 h-6 text-blue-500" />
        </div>
        <div>
          <CardTitle className="text-white">Scheda Veicoli</CardTitle>
          <p className="text-sm text-slate-400">Gestione veicoli e manutenzioni</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="bg-slate-900 p-4 rounded-lg">
            <h4 className="text-white font-medium mb-2">📝 In Sviluppo</h4>
            <p className="text-slate-400 text-sm">
              La scheda veicoli completa è in fase di sviluppo.
              <br />Cliente ID: {clienteId}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Scheda Carrozzeria
// ─────────────────────────────────────────────────────────────────────

function SchedaCarrozzeria({ clienteId }: { clienteId: string }) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-indigo-500/20 rounded-lg">
          <Car className="w-6 h-6 text-indigo-500" />
        </div>
        <div>
          <CardTitle className="text-white">Scheda Carrozzeria</CardTitle>
          <p className="text-sm text-slate-400">Gestione lavorazioni carrozzeria</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="bg-slate-900 p-4 rounded-lg">
            <h4 className="text-white font-medium mb-2">📝 In Sviluppo</h4>
            <p className="text-slate-400 text-sm">
              La scheda carrozzeria completa è in fase di sviluppo.
              <br />Cliente ID: {clienteId}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Scheda Medica
// ─────────────────────────────────────────────────────────────────────

function SchedaMedica({ clienteId }: { clienteId: string }) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-red-500/20 rounded-lg">
          <Stethoscope className="w-6 h-6 text-red-500" />
        </div>
        <div>
          <CardTitle className="text-white">Scheda Medica</CardTitle>
          <p className="text-sm text-slate-400">Gestione pazienti medici</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="bg-slate-900 p-4 rounded-lg">
            <h4 className="text-white font-medium mb-2">📝 In Sviluppo</h4>
            <p className="text-slate-400 text-sm">
              La scheda medica completa è in fase di sviluppo.
              <br />Cliente ID: {clienteId}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: Scheda Fitness
// ─────────────────────────────────────────────────────────────────────

function SchedaFitness({ clienteId }: { clienteId: string }) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-green-500/20 rounded-lg">
          <Dumbbell className="w-6 h-6 text-green-500" />
        </div>
        <div>
          <CardTitle className="text-white">Scheda Fitness</CardTitle>
          <p className="text-sm text-slate-400">Gestione allenamenti e palestre</p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="bg-slate-900 p-4 rounded-lg">
            <h4 className="text-white font-medium mb-2">📝 In Sviluppo</h4>
            <p className="text-slate-400 text-sm">
              La scheda fitness completa è in fase di sviluppo.
              <br />Cliente ID: {clienteId}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────
// MAPPING TIPO SCHEDA → VERTICALE
// ─────────────────────────────────────────────────────────────────────

const VERTICALE_PER_MICRO_CATEGORIA: Record<string, string> = {
  'odontoiatra': 'odontoiatrica',
  'fisioterapia': 'fisioterapia',
  'osteopata': 'fisioterapia',
  'podologo': 'fisioterapia',
  'medico_generico': 'medica',
  'specialista': 'medica',
  'psicologo': 'medica',
  'nutrizionista': 'medica',
  'estetista_viso': 'estetica',
  'estetista_corpo': 'estetica',
  'nail_specialist': 'estetica',
  'epilazione_laser': 'estetica',
  'centro_abbronzatura': 'estetica',
  'spa': 'estetica',
  'salone_donna': 'parrucchiere',
  'barbiere': 'parrucchiere',
  'salone_unisex': 'parrucchiere',
  'extension_specialist': 'parrucchiere',
  'color_specialist': 'parrucchiere',
  'tricologo': 'parrucchiere',
  'officina_meccanica': 'veicoli',
  'carrozzeria': 'carrozzeria',
  'elettrauto': 'veicoli',
  'gommista': 'veicoli',
  'detailing': 'veicoli',
  'palestra': 'fitness',
  'personal_trainer': 'fitness',
  'yoga_pilates': 'fitness',
  'crossfit': 'fitness',
  'piscina': 'fitness',
  'arti_marziali': 'fitness',
};

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: SchedaClienteDynamic (Switcher)
// ═══════════════════════════════════════════════════════════════════

export function SchedaClienteDynamic({ clienteId }: SchedaClienteDynamicProps) {
  const { data: config, isLoading: isLoadingConfig } = useSetupConfig();
  const { data: licenseStatus, isLoading: isLoadingLicense } = useLicenseStatusEd25519();

  if (isLoadingConfig || isLoadingLicense) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-8 text-center text-slate-400">
          Caricamento configurazione...
        </CardContent>
      </Card>
    );
  }

  const microCategoria = config?.micro_categoria;
  const verticale = microCategoria ? VERTICALE_PER_MICRO_CATEGORIA[microCategoria] : null;

  // Se non c'è micro categoria, mostra scheda base
  if (!microCategoria || !verticale) {
    return <SchedaBase clienteId={clienteId} />;
  }

  // Verifica licenza (se non enterprise, controlla verticali abilitate)
  const hasAccess = licenseStatus?.tier === 'enterprise' || 
                    licenseStatus?.enabled_verticals?.includes(verticale) ||
                    licenseStatus?.tier === 'trial';

  if (!hasAccess && licenseStatus?.tier !== 'trial') {
    return <SchedaBloccata vertical={verticale} tier={licenseStatus?.tier_display || 'Base'} />;
  }

  // Renderizza la scheda corretta in base alla micro categoria
  switch (microCategoria) {
    case 'odontoiatra':
      return <SchedaOdontoiatrica clienteId={clienteId} />;
    
    case 'fisioterapia':
    case 'osteopata':
    case 'podologo':
      return <SchedaFisioterapia clienteId={clienteId} />;
    
    case 'estetista_viso':
    case 'estetista_corpo':
    case 'nail_specialist':
    case 'epilazione_laser':
    case 'centro_abbronzatura':
    case 'spa':
      return <SchedaEstetica clienteId={clienteId} />;
    
    case 'salone_donna':
    case 'barbiere':
    case 'salone_unisex':
    case 'extension_specialist':
    case 'color_specialist':
    case 'tricologo':
      return <SchedaParrucchiere clienteId={clienteId} />;
    
    case 'officina_meccanica':
    case 'elettrauto':
    case 'gommista':
    case 'detailing':
      return <SchedaVeicoli clienteId={clienteId} />;
    
    case 'carrozzeria':
      return <SchedaCarrozzeria clienteId={clienteId} />;
    
    case 'medico_generico':
    case 'specialista':
    case 'psicologo':
    case 'nutrizionista':
      return <SchedaMedica clienteId={clienteId} />;
    
    case 'palestra':
    case 'personal_trainer':
    case 'yoga_pilates':
    case 'crossfit':
    case 'piscina':
    case 'arti_marziali':
      return <SchedaFitness clienteId={clienteId} />;
    
    default:
      return <SchedaBase clienteId={clienteId} />;
  }
}

// ─────────────────────────────────────────────────────────────────────
// EXPORTS
// ═══════════════════════════════════════════════════════════════════

export {
  SchedaBase,
  SchedaOdontoiatrica,
  SchedaFisioterapia,
  SchedaEstetica,
  SchedaParrucchiere,
  SchedaVeicoli,
  SchedaCarrozzeria,
  SchedaMedica,
  SchedaFitness,
  SchedaBloccata,
  VERTICALE_PER_MICRO_CATEGORIA,
};

export default SchedaClienteDynamic;
