import { type FC, type ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

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
  return (
    <div className="flex min-h-screen h-screen bg-slate-950 text-slate-100" style={{ minHeight: '100vh' }}>
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
};
