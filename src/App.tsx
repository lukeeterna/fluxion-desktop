import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { SetupWizard } from './components/setup';
import { useSetupStatus } from './hooks/use-setup';
import { Dashboard } from './pages/Dashboard';
import { Clienti } from './pages/Clienti';
import { Calendario } from './pages/Calendario';
import { Servizi } from './pages/Servizi';
import { Operatori } from './pages/Operatori';
import { Fatture } from './pages/Fatture';
import { Cassa } from './pages/Cassa';
import { Impostazioni } from './pages/Impostazioni';

// ═══════════════════════════════════════════════════════════════════
// FLUXION - Main Application
// ═══════════════════════════════════════════════════════════════════

function AppContent() {
  const { data: setupStatus, isLoading, refetch } = useSetupStatus();
  const [showWizard, setShowWizard] = useState<boolean | null>(null);

  useEffect(() => {
    if (setupStatus) {
      setShowWizard(!setupStatus.is_completed);
    }
  }, [setupStatus]);

  // Loading state
  if (isLoading || showWizard === null) {
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
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/clienti" element={<Clienti />} />
        <Route path="/calendario" element={<Calendario />} />
        <Route path="/servizi" element={<Servizi />} />
        <Route path="/operatori" element={<Operatori />} />
        <Route path="/fatture" element={<Fatture />} />
        <Route path="/cassa" element={<Cassa />} />
        <Route path="/impostazioni" element={<Impostazioni />} />
      </Routes>
    </MainLayout>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
