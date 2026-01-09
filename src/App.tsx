import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { SetupWizard } from './components/setup';
import { ErrorBoundary } from './components/ErrorBoundary';
import { useSetupStatus } from './hooks/use-setup';
import { Dashboard } from './pages/Dashboard';
import { Clienti } from './pages/Clienti';
import { Calendario } from './pages/Calendario';
import { Servizi } from './pages/Servizi';
import { Operatori } from './pages/Operatori';
import { Fatture } from './pages/Fatture';
import { Cassa } from './pages/Cassa';
import { VoiceAgent } from './pages/VoiceAgent';
import { Impostazioni } from './pages/Impostazioni';

// ═══════════════════════════════════════════════════════════════════
// FLUXION - Main Application
// ═══════════════════════════════════════════════════════════════════

function AppContent() {
  const { data: setupStatus, isLoading, isError, error, refetch } = useSetupStatus();
  const [showWizard, setShowWizard] = useState<boolean | null>(null);

  useEffect(() => {
    if (setupStatus) {
      setShowWizard(!setupStatus.is_completed);
    }
  }, [setupStatus]);

  // Se c'e' un errore, logga e prosegui mostrando l'app principale
  // (il setup wizard sara' mostrato la prossima volta)
  useEffect(() => {
    if (isError) {
      console.error('Errore caricamento setup status:', error);
      // Fallback: mostra l'app principale se c'e' un errore
      setShowWizard(false);
    }
  }, [isError, error]);

  // Loading state - ma solo per max 3 secondi, poi fallback
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (showWizard === null) {
        console.warn('Setup check timeout - mostrando app principale');
        setShowWizard(false);
      }
    }, 3000);
    return () => window.clearTimeout(timeout);
  }, [showWizard]);

  // Loading state
  if (isLoading && showWizard === null) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent mb-4">
            FLUXION
          </div>
          <div className="text-slate-400">Caricamento...</div>
        </div>
      </div>
    );
  }

  // Fallback se showWizard e' ancora null dopo il timeout
  if (showWizard === null) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-teal-400 bg-clip-text text-transparent mb-4">
            FLUXION
          </div>
          <div className="text-slate-400">Inizializzazione...</div>
        </div>
      </div>
    );
  }

  // Setup Wizard
  if (showWizard) {
    return (
      <SetupWizard
        onComplete={() => {
          refetch();
          setShowWizard(false);
        }}
      />
    );
  }

  // Main Application
  console.log('Rendering MainLayout with routes');
  return (
    <MainLayout>
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clienti" element={<Clienti />} />
          <Route path="/calendario" element={<Calendario />} />
          <Route path="/servizi" element={<Servizi />} />
          <Route path="/operatori" element={<Operatori />} />
          <Route path="/fatture" element={<Fatture />} />
          <Route path="/cassa" element={<Cassa />} />
          <Route path="/voice" element={<VoiceAgent />} />
          <Route path="/impostazioni" element={<Impostazioni />} />
        </Routes>
      </ErrorBoundary>
    </MainLayout>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
