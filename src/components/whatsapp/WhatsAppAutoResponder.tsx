// ═══════════════════════════════════════════════════════════════════
// FLUXION - WhatsApp Auto-Responder UI
// Gestione servizio WhatsApp con risposte automatiche
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect, type FC } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  MessageCircle,
  Power,
  PowerOff,
  RefreshCw,
  Send,
  Bot,
  Smartphone,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  QrCode,
} from 'lucide-react'

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface WhatsAppStatus {
  status: string
  timestamp?: string
  phone?: string
  name?: string
  error?: string
  qr?: string
  autoResponderEnabled?: boolean
  faqCategory?: string
}

interface WhatsAppMessage {
  from?: string
  to?: string
  name?: string
  body: string
  timestamp: string
  type: 'received' | 'sent'
  inReplyTo?: string
}

interface WhatsAppConfig {
  autoResponderEnabled: boolean
  faqCategory: string
  welcomeMessage: string
  businessName: string
  responseDelay: number
  maxResponsesPerHour: number
}

// ───────────────────────────────────────────────────────────────────
// Hooks
// ───────────────────────────────────────────────────────────────────

function useWhatsAppStatus() {
  return useQuery({
    queryKey: ['whatsapp-status'],
    queryFn: () => invoke<WhatsAppStatus>('get_whatsapp_status'),
    refetchInterval: 3000, // Poll every 3 seconds
  })
}

function useWhatsAppMessages(limit = 20) {
  return useQuery({
    queryKey: ['whatsapp-messages', limit],
    queryFn: () => invoke<WhatsAppMessage[]>('get_received_messages', { limit }),
    refetchInterval: 5000,
  })
}

function useWhatsAppConfig() {
  return useQuery({
    queryKey: ['whatsapp-config'],
    queryFn: () => invoke<WhatsAppConfig>('get_whatsapp_config'),
  })
}

function useUpdateWhatsAppConfig() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (config: Partial<WhatsAppConfig>) =>
      invoke('update_whatsapp_config', { config }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['whatsapp-config'] })
      queryClient.invalidateQueries({ queryKey: ['whatsapp-status'] })
    },
  })
}

// ───────────────────────────────────────────────────────────────────
// Status Badge Component
// ───────────────────────────────────────────────────────────────────

const StatusBadge: FC<{ status: string }> = ({ status }) => {
  switch (status) {
    case 'ready':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">
          <CheckCircle className="h-3 w-3" />
          Connesso
        </span>
      )
    case 'waiting_qr':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm">
          <QrCode className="h-3 w-3" />
          Scansiona QR
        </span>
      )
    case 'initializing':
    case 'loading':
    case 'authenticated':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
          <Clock className="h-3 w-3 animate-spin" />
          Connessione...
        </span>
      )
    case 'disconnected':
    case 'stopped':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-slate-500/20 text-slate-400 rounded-full text-sm">
          <PowerOff className="h-3 w-3" />
          Disconnesso
        </span>
      )
    case 'error':
    case 'auth_failed':
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-500/20 text-red-400 rounded-full text-sm">
          <XCircle className="h-3 w-3" />
          Errore
        </span>
      )
    default:
      return (
        <span className="inline-flex items-center gap-1 px-2 py-1 bg-slate-500/20 text-slate-400 rounded-full text-sm">
          <AlertTriangle className="h-3 w-3" />
          Non inizializzato
        </span>
      )
  }
}

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

export const WhatsAppAutoResponder: FC = () => {
  const { data: status, refetch: refetchStatus } = useWhatsAppStatus()
  const { data: messages } = useWhatsAppMessages()
  const { data: config } = useWhatsAppConfig()
  const updateConfig = useUpdateWhatsAppConfig()

  const [isStarting, setIsStarting] = useState(false)
  const [localAutoResponder, setLocalAutoResponder] = useState(true)
  const [localCategory, setLocalCategory] = useState('salone')

  // Sync local state with server config
  useEffect(() => {
    if (config) {
      setLocalAutoResponder(config.autoResponderEnabled)
      setLocalCategory(config.faqCategory)
    }
  }, [config])

  const handleStartService = async () => {
    setIsStarting(true)
    try {
      await invoke('start_whatsapp_service')
      // Open terminal instruction
      window.alert(
        `Per avviare il servizio WhatsApp, apri il Terminale ed esegui:\n\n` +
        `cd "${window.location.pathname.split('/').slice(0, -1).join('/')}"\n` +
        `npm run whatsapp:start\n\n` +
        `Poi scansiona il QR code con WhatsApp.`
      )
    } catch (error) {
      console.error('Failed to start:', error)
    } finally {
      setIsStarting(false)
      refetchStatus()
    }
  }

  const handleToggleAutoResponder = async (enabled: boolean) => {
    setLocalAutoResponder(enabled)
    try {
      await updateConfig.mutateAsync({ autoResponderEnabled: enabled })
    } catch (error) {
      setLocalAutoResponder(!enabled) // Revert on error
    }
  }

  const handleCategoryChange = async (category: string) => {
    setLocalCategory(category)
    try {
      await updateConfig.mutateAsync({ faqCategory: category })
    } catch (error) {
      setLocalCategory(config?.faqCategory || 'salone') // Revert on error
    }
  }

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <Card className="bg-gradient-to-br from-green-900/30 to-emerald-900/20 border-green-800/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-500/20 rounded-lg">
                <MessageCircle className="h-8 w-8 text-green-400" />
              </div>
              <div>
                <CardTitle className="text-2xl text-white flex items-center gap-2">
                  WhatsApp Auto-Responder
                  <Bot className="h-5 w-5 text-cyan-400" />
                </CardTitle>
                <CardDescription className="text-slate-400">
                  Risposte automatiche intelligenti con FLUXION IA
                </CardDescription>
              </div>
            </div>
            <StatusBadge status={status?.status || 'not_initialized'} />
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Connection Status */}
          {status?.status === 'ready' && (
            <div className="flex items-center gap-4 p-4 bg-green-500/10 rounded-lg border border-green-500/30">
              <Smartphone className="h-10 w-10 text-green-400" />
              <div>
                <p className="text-white font-medium">
                  {status.name || 'WhatsApp Business'}
                </p>
                <p className="text-sm text-slate-400">
                  +{status.phone}
                </p>
              </div>
            </div>
          )}

          {/* QR Code Waiting */}
          {status?.status === 'waiting_qr' && status.qr && (
            <div className="p-4 bg-slate-800 rounded-lg text-center">
              <p className="text-yellow-400 mb-4">
                Scansiona il QR code con WhatsApp per connettere
              </p>
              <div className="inline-block p-4 bg-white rounded-lg">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(status.qr)}`}
                  alt="WhatsApp QR Code"
                  className="w-48 h-48"
                />
              </div>
              <p className="text-sm text-slate-400 mt-4">
                WhatsApp &gt; Impostazioni &gt; Dispositivi collegati &gt; Collega un dispositivo
              </p>
            </div>
          )}

          {/* Not Connected */}
          {(!status?.status || status.status === 'not_initialized' || status.status === 'stopped' || status.status === 'disconnected') && (
            <div className="p-4 bg-slate-800 rounded-lg text-center">
              <PowerOff className="h-12 w-12 text-slate-500 mx-auto mb-4" />
              <p className="text-slate-400 mb-4">
                Il servizio WhatsApp non è attivo
              </p>
              <Button
                onClick={handleStartService}
                disabled={isStarting}
                className="bg-green-600 hover:bg-green-500"
              >
                {isStarting ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Avvio...
                  </>
                ) : (
                  <>
                    <Power className="h-4 w-4 mr-2" />
                    Avvia Servizio
                  </>
                )}
              </Button>
              <p className="text-xs text-slate-500 mt-4">
                Esegui nel terminale: <code className="bg-slate-700 px-2 py-1 rounded">npm run whatsapp:start</code>
              </p>
            </div>
          )}

          {/* Controls (only show when ready) */}
          {status?.status === 'ready' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Auto-Responder Toggle */}
              <div className="p-4 bg-slate-800 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Bot className="h-5 w-5 text-cyan-400" />
                    <div>
                      <Label className="text-white">Auto-Responder</Label>
                      <p className="text-xs text-slate-400">
                        Risposte automatiche con IA
                      </p>
                    </div>
                  </div>
                  <Switch
                    checked={localAutoResponder}
                    onCheckedChange={handleToggleAutoResponder}
                    disabled={updateConfig.isPending}
                  />
                </div>
              </div>

              {/* FAQ Category Select */}
              <div className="p-4 bg-slate-800 rounded-lg">
                <Label className="text-white mb-2 block">Categoria FAQ</Label>
                <Select value={localCategory} onValueChange={handleCategoryChange}>
                  <SelectTrigger className="bg-slate-700 border-slate-600">
                    <SelectValue placeholder="Seleziona categoria" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="salone">Salone / Parrucchiere</SelectItem>
                    <SelectItem value="auto">Officina / Carrozzeria</SelectItem>
                    <SelectItem value="wellness">Palestra / Wellness</SelectItem>
                    <SelectItem value="medical">Studio Medico</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-400 mt-2">
                  Solo "Salone" disponibile al momento
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Messages Log */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Send className="h-5 w-5 text-cyan-400" />
            Messaggi Recenti
          </CardTitle>
          <CardDescription>
            Ultimi messaggi ricevuti e inviati
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!messages?.length ? (
            <div className="text-center py-8 text-slate-500">
              <MessageCircle className="h-10 w-10 mx-auto mb-2 opacity-50" />
              <p>Nessun messaggio ancora</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg ${
                    msg.type === 'received'
                      ? 'bg-slate-800 border-l-4 border-green-500'
                      : 'bg-cyan-900/30 border-l-4 border-cyan-500'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-sm font-medium ${
                      msg.type === 'received' ? 'text-green-400' : 'text-cyan-400'
                    }`}>
                      {msg.type === 'received' ? (
                        <>{msg.name || msg.from} →</>
                      ) : (
                        <>→ {msg.to}</>
                      )}
                    </span>
                    <span className="text-xs text-slate-500">
                      {formatTime(msg.timestamp)}
                    </span>
                  </div>
                  <p className="text-slate-300 text-sm">
                    {msg.body.length > 150 ? msg.body.slice(0, 150) + '...' : msg.body}
                  </p>
                  {msg.inReplyTo && (
                    <p className="text-xs text-slate-500 mt-1">
                      In risposta a: "{msg.inReplyTo}..."
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="pt-6">
          <h3 className="text-white font-semibold mb-4">Come funziona</h3>
          <ol className="space-y-2 text-sm text-slate-400">
            <li className="flex items-start gap-2">
              <span className="bg-cyan-500/20 text-cyan-400 w-5 h-5 rounded-full flex items-center justify-center text-xs flex-shrink-0">1</span>
              Avvia il servizio WhatsApp dal terminale con <code className="bg-slate-700 px-1 rounded">npm run whatsapp:start</code>
            </li>
            <li className="flex items-start gap-2">
              <span className="bg-cyan-500/20 text-cyan-400 w-5 h-5 rounded-full flex items-center justify-center text-xs flex-shrink-0">2</span>
              Scansiona il QR code con il tuo WhatsApp Business
            </li>
            <li className="flex items-start gap-2">
              <span className="bg-cyan-500/20 text-cyan-400 w-5 h-5 rounded-full flex items-center justify-center text-xs flex-shrink-0">3</span>
              I messaggi ricevuti verranno automaticamente elaborati da FLUXION IA
            </li>
            <li className="flex items-start gap-2">
              <span className="bg-cyan-500/20 text-cyan-400 w-5 h-5 rounded-full flex items-center justify-center text-xs flex-shrink-0">4</span>
              Le risposte sono generate in base alle FAQ della categoria selezionata
            </li>
          </ol>
        </CardContent>
      </Card>
    </div>
  )
}
