import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Clienti } from './pages/Clienti';
import { Calendario } from './pages/Calendario';
import { Servizi } from './pages/Servizi';
import { Operatori } from './pages/Operatori';
import { Fatture } from './pages/Fatture';
import { Impostazioni } from './pages/Impostazioni';

// ═══════════════════════════════════════════════════════════════════
// FLUXION - Main Application
// ═══════════════════════════════════════════════════════════════════

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/clienti" element={<Clienti />} />
          <Route path="/calendario" element={<Calendario />} />
          <Route path="/servizi" element={<Servizi />} />
          <Route path="/operatori" element={<Operatori />} />
          <Route path="/fatture" element={<Fatture />} />
          <Route path="/impostazioni" element={<Impostazioni />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}

export default App;
