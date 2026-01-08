// ═══════════════════════════════════════════════════════════════════
// FLUXION - Error Boundary Component
// Cattura errori React e mostra fallback UI
// ═══════════════════════════════════════════════════════════════════

import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-slate-800 rounded-lg p-6 border border-red-500/50">
            <h1 className="text-2xl font-bold text-red-400 mb-4">
              Qualcosa e' andato storto
            </h1>
            <p className="text-slate-300 mb-4">
              Si e' verificato un errore nell'applicazione. Prova a ricaricare la pagina.
            </p>

            {this.state.error && (
              <div className="bg-slate-900 rounded p-3 mb-4">
                <p className="text-red-300 font-mono text-sm break-all">
                  {this.state.error.message}
                </p>
              </div>
            )}

            {this.state.errorInfo && (
              <details className="mb-4">
                <summary className="text-slate-400 cursor-pointer hover:text-slate-200">
                  Dettagli tecnici
                </summary>
                <pre className="mt-2 text-xs text-slate-500 overflow-auto max-h-40 bg-slate-900 p-2 rounded">
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <button
              onClick={() => window.location.reload()}
              className="w-full py-2 px-4 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors"
            >
              Ricarica Applicazione
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
