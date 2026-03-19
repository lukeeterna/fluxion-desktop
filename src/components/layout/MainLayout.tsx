import { type FC, type ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { usePhoneHome } from '../../hooks/use-phone-home';
import { SaraTrialBanner } from '../license/SaraTrialBanner';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface MainLayoutProps {
  children: ReactNode;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const MainLayout: FC<MainLayoutProps> = ({ children }) => {
  const phoneHomeState = usePhoneHome();

  return (
    <div className="flex min-h-screen h-screen bg-slate-950 text-slate-100" style={{ minHeight: '100vh' }}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Header */}
        <Header />

        {/* Sara Trial Banner */}
        <SaraTrialBanner phoneHome={phoneHomeState} />

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
