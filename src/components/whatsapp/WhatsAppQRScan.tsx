// =============================================================================
// FLUXION - WhatsApp QR Scan Component
// Displays QR code for WhatsApp Web login and shows connection status
// =============================================================================

import { type FC, useState, useEffect, useCallback } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { invoke } from '@tauri-apps/api/core';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  MessageCircle,
  RefreshCw,
  CheckCircle,
  XCircle,
  Loader2,
  Smartphone,
  Power,
  PowerOff,
} from 'lucide-react';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

type WhatsAppStatus =
  | 'disconnected'
  | 'waiting_qr'
  | 'connecting'
  | 'ready'
  | 'error';

interface WhatsAppState {
  status: WhatsAppStatus;
  qr?: string;
  phone?: string;
  error?: string;
  lastUpdate?: string;
}

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------

export const WhatsAppQRScan: FC = () => {
  const [state, setState] = useState<WhatsAppState>({ status: 'disconnected' });
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);

  // Fetch current status from backend
  const fetchStatus = useCallback(async () => {
    try {
      const result = await invoke<WhatsAppState>('get_whatsapp_status');
      // Map backend status to our status type
      const statusMap: Record<string, WhatsAppStatus> = {
        'not_initialized': 'disconnected',
        'waiting_qr': 'waiting_qr',
        'connecting': 'connecting',
        'ready': 'ready',
        'error': 'error',
      };
      setState({
        ...result,
        status: statusMap[result.status] || 'disconnected',
      });
    } catch (error) {
      console.error('Failed to get WhatsApp status:', error);
      setState({ status: 'disconnected', error: String(error) });
    }
  }, []);

  // Start WhatsApp service
  const startService = async () => {
    setIsStarting(true);
    try {
      await invoke('start_whatsapp_service');
      // Poll for QR code
      setTimeout(fetchStatus, 2000);
    } catch (error) {
      console.error('Failed to start WhatsApp:', error);
      setState({ status: 'error', error: String(error) });
    } finally {
      setIsStarting(false);
    }
  };

  // Stop WhatsApp service - reset status file
  const stopService = async () => {
    setIsStopping(true);
    try {
      // For now, just reset state (full stop would kill the process)
      setState({ status: 'disconnected' });
    } catch (error) {
      console.error('Failed to stop WhatsApp:', error);
    } finally {
      setIsStopping(false);
    }
  };

  // Poll status when waiting for QR or connecting
  useEffect(() => {
    const shouldPoll = state.status === 'waiting_qr' || state.status === 'connecting';

    if (shouldPoll) {
      const interval = setInterval(fetchStatus, 2000);
      return () => clearInterval(interval);
    }
  }, [state.status, fetchStatus]);

  // Initial status fetch
  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Render status badge
  const renderStatusBadge = () => {
    switch (state.status) {
      case 'ready':
        return (
          <Badge className="bg-green-600 text-white">
            <CheckCircle className="w-3 h-3 mr-1" />
            Connesso
          </Badge>
        );
      case 'waiting_qr':
        return (
          <Badge className="bg-yellow-600 text-white">
            <Smartphone className="w-3 h-3 mr-1" />
            Scansiona QR
          </Badge>
        );
      case 'connecting':
        return (
          <Badge className="bg-blue-600 text-white">
            <Loader2 className="w-3 h-3 mr-1 animate-spin" />
            Connessione...
          </Badge>
        );
      case 'error':
        return (
          <Badge className="bg-red-600 text-white">
            <XCircle className="w-3 h-3 mr-1" />
            Errore
          </Badge>
        );
      default:
        return (
          <Badge className="bg-slate-600 text-white">
            <PowerOff className="w-3 h-3 mr-1" />
            Disconnesso
          </Badge>
        );
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-600/20 rounded-lg">
              <MessageCircle className="w-6 h-6 text-green-500" />
            </div>
            <div>
              <CardTitle className="text-white">WhatsApp Business</CardTitle>
              <CardDescription>
                Connetti il tuo account WhatsApp
              </CardDescription>
            </div>
          </div>
          {renderStatusBadge()}
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Disconnected State */}
        {state.status === 'disconnected' && (
          <div className="text-center py-8">
            <MessageCircle className="w-16 h-16 mx-auto text-slate-600 mb-4" />
            <p className="text-slate-400 mb-6">
              Connetti WhatsApp Business per ricevere prenotazioni automatiche
            </p>
            <Button
              onClick={startService}
              disabled={isStarting}
              className="bg-green-600 hover:bg-green-700"
            >
              {isStarting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Avvio in corso...
                </>
              ) : (
                <>
                  <Power className="w-4 h-4 mr-2" />
                  Connetti WhatsApp
                </>
              )}
            </Button>
          </div>
        )}

        {/* QR Code Display */}
        {state.status === 'waiting_qr' && state.qr && (
          <div className="flex flex-col items-center py-4">
            <div className="bg-white p-4 rounded-xl shadow-lg mb-4">
              <QRCodeSVG
                value={state.qr}
                size={200}
                level="M"
                includeMargin
              />
            </div>

            <div className="text-center space-y-2">
              <p className="text-white font-medium">
                Scansiona con WhatsApp
              </p>
              <p className="text-slate-400 text-sm max-w-xs">
                Apri WhatsApp sul telefono → Menu → Dispositivi collegati → Collega un dispositivo
              </p>
            </div>

            <Button
              variant="outline"
              onClick={fetchStatus}
              className="mt-4 border-slate-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Aggiorna
            </Button>
          </div>
        )}

        {/* Connecting State */}
        {state.status === 'connecting' && (
          <div className="text-center py-8">
            <Loader2 className="w-12 h-12 mx-auto text-cyan-500 animate-spin mb-4" />
            <p className="text-white">Connessione in corso...</p>
            <p className="text-slate-400 text-sm mt-2">
              Attendi qualche secondo
            </p>
          </div>
        )}

        {/* Connected State */}
        {state.status === 'ready' && (
          <div className="space-y-4">
            <div className="flex items-center justify-center gap-3 py-4">
              <CheckCircle className="w-8 h-8 text-green-500" />
              <div>
                <p className="text-white font-medium">WhatsApp Connesso</p>
                {state.phone && (
                  <p className="text-slate-400 text-sm">{state.phone}</p>
                )}
              </div>
            </div>

            <div className="bg-green-950/30 border border-green-900/50 rounded-lg p-4">
              <p className="text-green-200 text-sm">
                I messaggi WhatsApp verranno gestiti automaticamente da Sara,
                l'assistente vocale di FLUXION.
              </p>
            </div>

            <div className="flex justify-center">
              <Button
                variant="outline"
                onClick={stopService}
                disabled={isStopping}
                className="border-red-800 text-red-400 hover:bg-red-950"
              >
                {isStopping ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Disconnessione...
                  </>
                ) : (
                  <>
                    <PowerOff className="w-4 h-4 mr-2" />
                    Disconnetti
                  </>
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Error State */}
        {state.status === 'error' && (
          <div className="text-center py-6">
            <XCircle className="w-12 h-12 mx-auto text-red-500 mb-4" />
            <p className="text-white font-medium mb-2">Errore di connessione</p>
            <p className="text-slate-400 text-sm mb-4">
              {state.error || 'Impossibile connettersi a WhatsApp'}
            </p>
            <Button
              onClick={startService}
              disabled={isStarting}
              variant="outline"
              className="border-slate-700"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Riprova
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
