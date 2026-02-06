// ═══════════════════════════════════════════════════════════════════
// FLUXION - Pacchetti Admin Component (Fase 5 v3)
// Gestione pacchetti: crea con servizi, modifica, elimina
// Prezzo calcolato automaticamente da servizi + sconto
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  usePacchetti,
  useCreatePacchetto,
  useDeletePacchetto,
  usePacchettoServizi,
  useAddServizioToPacchetto,
  useRemoveServizioFromPacchetto,
} from '@/hooks/use-loyalty'
import { useServizi } from '@/hooks/use-servizi'
import type { Pacchetto } from '@/types/loyalty'
import type { Servizio } from '@/types/servizio'
import { Package, Plus, Edit, Trash2, Euro, Calendar, Layers, X, Percent, MessageCircle, Send, Users, Star } from 'lucide-react'
import { useState as useReactState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { toast } from 'sonner'

// ═══════════════════════════════════════════════════════════════════
// WhatsApp Pacchetti Sender Component
// Invio selettivo pacchetti via WhatsApp con filtri
// ═══════════════════════════════════════════════════════════════════

interface ClienteWhatsAppInfo {
  id: string
  nome: string
  cognome: string
  telefono: string
  is_vip: boolean
  loyalty_visits: number
}

interface InvioResult {
  success: boolean
  total_clienti: number
  messaggi_inviati: number
  messaggi_falliti: number
}

type FiltroTipo = 'tutti' | 'vip' | 'vip_3_plus'

function WhatsAppPacchettiSender({ pacchetti }: { pacchetti: Pacchetto[] }) {
  const [selectedPacchetto, setSelectedPacchetto] = useReactState<string>('')
  const [filtro, setFiltro] = useReactState<FiltroTipo>('tutti')
  const [messaggio, setMessaggio] = useReactState<string>('')
  const [clientiPreview, setClientiPreview] = useReactState<ClienteWhatsAppInfo[]>([])
  const [isLoading, setIsLoading] = useReactState(false)
  const [isSending, setIsSending] = useReactState(false)
  const [dialogOpen, setDialogOpen] = useReactState(false)
  const [result, setResult] = useReactState<InvioResult | null>(null)

  // Template messaggio predefinito
  const templateMessaggio = `Ciao {{nome}}! 🎁

Abbiamo pensato a te: {{pacchetto}}
✨ {{servizi}} servizi inclusi
💰 Solo €{{prezzo}} invece di €{{prezzo_originale}}
⏰ Valido per {{giorni}} giorni

Prenota ora rispondendo a questo messaggio!

{{nome_attivita}}`

  // Genera messaggio personalizzato quando cambia il pacchetto
  const updateMessaggio = (pacchettoId: string) => {
    const p = pacchetti.find((p) => p.id === pacchettoId)
    if (!p) return

    const newMessaggio = templateMessaggio
      .replace('{{pacchetto}}', p.nome)
      .replace('{{servizi}}', p.servizi_inclusi.toString())
      .replace('{{prezzo}}', p.prezzo.toFixed(2))
      .replace('{{prezzo_originale}}', (p.prezzo_originale || p.prezzo).toFixed(2))
      .replace('{{giorni}}', p.validita_giorni.toString())
      .replace('{{nome_attivita}}', 'Il tuo centro estetico')

    setMessaggio(newMessaggio)
  }

  // Carica preview clienti quando cambia il filtro
  const loadClientiPreview = async (f: FiltroTipo) => {
    setIsLoading(true)
    try {
      const clienti = await invoke<ClienteWhatsAppInfo[]>('get_clienti_per_invio_whatsapp', {
        filtro: f,
      })
      setClientiPreview(clienti)
    } catch (error) {
      console.error('Error loading clienti:', error)
      toast.error('Errore caricamento clienti')
    } finally {
      setIsLoading(false)
    }
  }

  // Invia messaggi
  const handleSend = async () => {
    if (!selectedPacchetto) {
      toast.error('Seleziona un pacchetto')
      return
    }
    if (!messaggio.trim()) {
      toast.error('Inserisci un messaggio')
      return
    }

    setIsSending(true)
    try {
      const res = await invoke<InvioResult>('invia_pacchetto_whatsapp_bulk', {
        pacchettoId: selectedPacchetto,
        filtro: filtro,
        messaggio: messaggio,
      })
      setResult(res)
      if (res.success) {
        toast.success(`Invio completato! ${res.messaggi_inviati} messaggi in coda`)
      } else {
        toast.error(`Invio parziale: ${res.messaggi_falliti} falliti`)
      }
    } catch (error) {
      console.error('Error sending:', error)
      toast.error('Errore invio messaggi')
    } finally {
      setIsSending(false)
    }
  }

  const getFiltroLabel = (f: FiltroTipo) => {
    switch (f) {
      case 'tutti':
        return 'Tutti i clienti (con consenso)'
      case 'vip':
        return 'Solo VIP'
      case 'vip_3_plus':
        return 'VIP 3+ stelle'
    }
  }

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => {
          setDialogOpen(true)
          loadClientiPreview('tutti')
        }}
        className="border-green-600 text-green-400 hover:bg-green-900/30"
      >
        <MessageCircle className="h-4 w-4 mr-1" />
        Invia WhatsApp
      </Button>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="bg-slate-950 border-slate-800 max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <MessageCircle className="h-5 w-5 text-green-400" />
              Invia Pacchetto via WhatsApp
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Selezione Pacchetto */}
            <div className="space-y-2">
              <Label className="text-slate-300">Seleziona Pacchetto</Label>
              <select
                value={selectedPacchetto}
                onChange={(e) => {
                  setSelectedPacchetto(e.target.value)
                  updateMessaggio(e.target.value)
                }}
                className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-white text-sm"
              >
                <option value="">-- Scegli un pacchetto --</option>
                {pacchetti.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.nome} - €{p.prezzo.toFixed(2)} ({p.servizi_inclusi} servizi)
                  </option>
                ))}
              </select>
            </div>

            {/* Filtro Destinatari */}
            <div className="space-y-2">
              <Label className="text-slate-300">Filtro Destinatari</Label>
              <div className="grid grid-cols-3 gap-2">
                {(['tutti', 'vip', 'vip_3_plus'] as FiltroTipo[]).map((f) => (
                  <button
                    key={f}
                    onClick={() => {
                      setFiltro(f)
                      loadClientiPreview(f)
                    }}
                    className={`p-3 rounded-lg border text-sm transition-all ${
                      filtro === f
                        ? 'bg-green-900/50 border-green-500 text-green-300'
                        : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:bg-slate-800'
                    }`}
                  >
                    {f === 'tutti' && <Users className="h-4 w-4 mx-auto mb-1" />}
                    {f === 'vip' && <Star className="h-4 w-4 mx-auto mb-1" />}
                    {f === 'vip_3_plus' && <span className="text-xs">⭐⭐⭐</span>}
                    <span className="text-xs">{getFiltroLabel(f)}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Preview Clienti */}
            <div className="space-y-2">
              <Label className="text-slate-300 flex items-center justify-between">
                <span>Destinatari ({clientiPreview.length})</span>
                {isLoading && <span className="text-xs text-slate-500">Caricamento...</span>}
              </Label>
              <div className="max-h-32 overflow-y-auto rounded-lg border border-slate-700 bg-slate-900/50 p-2">
                {clientiPreview.length === 0 ? (
                  <p className="text-sm text-slate-500 text-center py-4">
                    Nessun cliente trovato con questo filtro
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-1">
                    {clientiPreview.slice(0, 20).map((c) => (
                      <Badge
                        key={c.id}
                        variant="outline"
                        className={`text-xs ${
                          c.is_vip ? 'border-yellow-600 text-yellow-400' : 'border-slate-600 text-slate-400'
                        }`}
                      >
                        {c.nome} {c.is_vip && '⭐'}
                      </Badge>
                    ))}
                    {clientiPreview.length > 20 && (
                      <Badge variant="outline" className="text-xs border-slate-600 text-slate-500">
                        +{clientiPreview.length - 20} altri
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Messaggio Personalizzato */}
            <div className="space-y-2">
              <Label className="text-slate-300">
                Messaggio WhatsApp
                <span className="text-xs text-slate-500 ml-2">
                  (Variabili: {'{'}nome{'}'}, {'{'}pacchetto{'}'}, {'{'}prezzo{'}'}...)
                </span>
              </Label>
              <Textarea
                value={messaggio}
                onChange={(e) => setMessaggio(e.target.value)}
                rows={6}
                className="bg-slate-900 border-slate-700 text-white text-sm"
                placeholder="Ciao {nome}! Abbiamo pensato a te..."
              />
            </div>

            {/* Info Rate Limiting */}
            <div className="p-3 rounded-lg bg-blue-900/20 border border-blue-800/50">
              <p className="text-xs text-blue-300">
                ℹ️ I messaggi verranno inviati con rate limiting (max 60/ora) per evitare blocchi WhatsApp.
                I clienti riceveranno il messaggio dalla coda del servizio WhatsApp.
              </p>
            </div>

            {/* Risultato */}
            {result && (
              <div
                className={`p-4 rounded-lg border ${
                  result.success
                    ? 'bg-green-900/20 border-green-800 text-green-300'
                    : 'bg-yellow-900/20 border-yellow-800 text-yellow-300'
                }`}
              >
                <p className="font-medium">Esito Invio:</p>
                <p className="text-sm">
                  ✅ {result.messaggi_inviati} messaggi in coda
                  {result.messaggi_falliti > 0 && <span> | ❌ {result.messaggi_falliti} falliti</span>}
                </p>
              </div>
            )}

            {/* Azioni */}
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Chiudi
              </Button>
              <Button
                onClick={handleSend}
                disabled={isSending || !selectedPacchetto || clientiPreview.length === 0}
                className="bg-green-600 hover:bg-green-700"
              >
                {isSending ? (
                  'Invio in corso...'
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Invia a {clientiPreview.length} clienti
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

export function PacchettiAdmin() {
  const { data: pacchetti, isLoading } = usePacchetti()
  const deletePacchetto = useDeletePacchetto()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingPacchetto, setEditingPacchetto] = useState<Pacchetto | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [pacchettoToDelete, setPacchettoToDelete] = useState<Pacchetto | null>(null)

  const handleDelete = () => {
    if (pacchettoToDelete) {
      deletePacchetto.mutate(pacchettoToDelete.id, {
        onSuccess: () => {
          setDeleteDialogOpen(false)
          setPacchettoToDelete(null)
        },
        onError: (error) => {
          console.error('Delete error:', error instanceof Error ? error.message : 'Errore eliminazione')
        },
      })
    }
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-muted rounded w-48" />
        <div className="h-32 bg-muted rounded" />
      </div>
    )
  }

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-2">
          <Package className="h-5 w-5 text-primary" />
          <CardTitle className="text-white">Gestione Pacchetti</CardTitle>
        </div>

        <div className="flex items-center gap-2">
          {/* WhatsApp Sender Button */}
          {pacchetti && pacchetti.length > 0 && (
            <WhatsAppPacchettiSender pacchetti={pacchetti} />
          )}

        <Dialog open={dialogOpen} onOpenChange={(open) => {
          setDialogOpen(open)
          if (!open) setEditingPacchetto(null)
        }}>
          <DialogTrigger asChild>
            <Button
              size="sm"
              onClick={() => setEditingPacchetto(null)}
              className="bg-cyan-500 hover:bg-cyan-600"
            >
              <Plus className="h-4 w-4 mr-1" />
              Nuovo Pacchetto
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-950 border-slate-800 max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-white">
                {editingPacchetto ? 'Modifica Pacchetto' : 'Nuovo Pacchetto'}
              </DialogTitle>
            </DialogHeader>
            <PacchettoForm
              pacchetto={editingPacchetto}
              onClose={() => setDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
        </div>
      </CardHeader>

      <CardContent>
        {pacchetti && pacchetti.length > 0 ? (
          <div className="space-y-3">
            {pacchetti.map((p) => (
              <PacchettoRow
                key={p.id}
                pacchetto={p}
                onEdit={() => {
                  setEditingPacchetto(p)
                  setDialogOpen(true)
                }}
                onDelete={() => {
                  setPacchettoToDelete(p)
                  setDeleteDialogOpen(true)
                }}
              />
            ))}
          </div>
        ) : (
          <p className="text-slate-400 text-center py-8">
            Nessun pacchetto configurato. Crea il primo!
          </p>
        )}
      </CardContent>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-slate-950 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Elimina Pacchetto</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Sei sicuro di voler eliminare il pacchetto{' '}
              <span className="font-semibold text-white">{pacchettoToDelete?.nome}</span>?
              <br />
              Il pacchetto verrà disattivato e non sarà più proponibile ai clienti.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Annulla
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deletePacchetto.isPending}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {deletePacchetto.isPending ? 'Eliminazione...' : 'Elimina'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  )
}

// ───────────────────────────────────────────────────────────────────
// Sub-components
// ───────────────────────────────────────────────────────────────────

function PacchettoRow({
  pacchetto,
  onEdit,
  onDelete,
}: {
  pacchetto: Pacchetto
  onEdit: () => void
  onDelete: () => void
}) {
  const { data: servizi } = usePacchettoServizi(pacchetto.id)
  const risparmio =
    pacchetto.prezzo_originale && pacchetto.prezzo_originale > pacchetto.prezzo
      ? Math.round(
          ((pacchetto.prezzo_originale - pacchetto.prezzo) /
            pacchetto.prezzo_originale) *
            100
        )
      : null

  return (
    <div className="flex items-center justify-between p-4 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <h4 className="font-medium text-white">{pacchetto.nome}</h4>
          {risparmio && (
            <Badge variant="secondary" className="bg-green-900 text-green-300">
              -{risparmio}%
            </Badge>
          )}
          {!pacchetto.attivo && (
            <Badge variant="outline" className="text-slate-500">
              Disattivo
            </Badge>
          )}
        </div>
        {pacchetto.descrizione && (
          <p className="text-sm text-slate-400 mt-1">{pacchetto.descrizione}</p>
        )}

        {/* Servizi inclusi */}
        {servizi && servizi.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {servizi.map((s) => (
              <Badge key={s.id} variant="outline" className="text-xs text-slate-300 border-slate-600">
                {s.servizio_nome} {s.quantita > 1 && `x${s.quantita}`}
              </Badge>
            ))}
          </div>
        )}

        <div className="flex items-center gap-4 mt-2 text-sm text-slate-400">
          <span className="flex items-center gap-1">
            <Euro className="h-3 w-3" />
            <span className="text-green-400 font-medium">{pacchetto.prezzo.toFixed(2)}</span>
            {pacchetto.prezzo_originale && (
              <span className="line-through text-slate-600 ml-1">
                {pacchetto.prezzo_originale.toFixed(2)}
              </span>
            )}
          </span>
          <span className="flex items-center gap-1">
            <Layers className="h-3 w-3" />
            {pacchetto.servizi_inclusi} servizi
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {pacchetto.validita_giorni} giorni
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={onEdit}
          className="text-slate-400 hover:text-cyan-400"
        >
          <Edit className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onDelete}
          className="text-slate-400 hover:text-red-400"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

// Servizio selezionato localmente (prima di salvare)
interface SelectedServizio {
  servizio: Servizio
  quantita: number
}

function PacchettoForm({
  pacchetto,
  onClose,
}: {
  pacchetto: Pacchetto | null
  onClose: () => void
}) {
  const { data: serviziDisponibili } = useServizi()
  const { data: serviziPacchetto, refetch: refetchServizi } = usePacchettoServizi(pacchetto?.id)
  const createPacchetto = useCreatePacchetto()
  const addServizio = useAddServizioToPacchetto()
  const removeServizio = useRemoveServizioFromPacchetto()

  // Form state
  const [nome, setNome] = useState(pacchetto?.nome ?? '')
  const [descrizione, setDescrizione] = useState(pacchetto?.descrizione ?? '')
  const [sconto, setSconto] = useState(10) // Sconto percentuale
  const [validitaGiorni, setValiditaGiorni] = useState(pacchetto?.validita_giorni ?? 365)

  // Servizi selezionati (per nuovo pacchetto)
  const [selectedServizi, setSelectedServizi] = useState<SelectedServizio[]>([])

  // Loading state
  const [isSaving, setIsSaving] = useState(false)

  // Calcola totale servizi
  const totalFromServices = pacchetto
    ? serviziPacchetto?.reduce((sum, s) => sum + s.servizio_prezzo * s.quantita, 0) ?? 0
    : selectedServizi.reduce((sum, s) => sum + s.servizio.prezzo * s.quantita, 0)

  // Calcola prezzo scontato
  const prezzoOriginale = totalFromServices
  const prezzoScontato = totalFromServices * (1 - sconto / 100)
  const risparmio = prezzoOriginale - prezzoScontato

  // Numero servizi totali
  const serviziCount = pacchetto
    ? serviziPacchetto?.reduce((sum, s) => sum + s.quantita, 0) ?? 0
    : selectedServizi.reduce((sum, s) => sum + s.quantita, 0)

  // Init sconto da pacchetto esistente
  useEffect(() => {
    if (pacchetto && pacchetto.prezzo_originale && pacchetto.prezzo_originale > 0) {
      const scontoCalcolato = Math.round(
        ((pacchetto.prezzo_originale - pacchetto.prezzo) / pacchetto.prezzo_originale) * 100
      )
      setSconto(scontoCalcolato > 0 ? scontoCalcolato : 10)
    }
  }, [pacchetto])

  // Aggiungi servizio (locale per nuovo, DB per esistente)
  const handleAddServizio = (servizio: Servizio) => {
    if (pacchetto) {
      // Edit mode: aggiungi direttamente al DB
      addServizio.mutate(
        { pacchettoId: pacchetto.id, servizioId: servizio.id, quantita: 1 },
        { onSuccess: () => refetchServizi() }
      )
    } else {
      // Create mode: aggiungi localmente
      const existing = selectedServizi.find((s) => s.servizio.id === servizio.id)
      if (existing) {
        setSelectedServizi(
          selectedServizi.map((s) =>
            s.servizio.id === servizio.id ? { ...s, quantita: s.quantita + 1 } : s
          )
        )
      } else {
        setSelectedServizi([...selectedServizi, { servizio, quantita: 1 }])
      }
    }
  }

  // Rimuovi servizio
  const handleRemoveServizio = (servizioId: string) => {
    if (pacchetto) {
      removeServizio.mutate(
        { pacchettoId: pacchetto.id, servizioId },
        { onSuccess: () => refetchServizi() }
      )
    } else {
      setSelectedServizi(selectedServizi.filter((s) => s.servizio.id !== servizioId))
    }
  }

  // Cambia quantità (solo per nuovo)
  const handleChangeQuantity = (servizioId: string, delta: number) => {
    setSelectedServizi(
      selectedServizi
        .map((s) =>
          s.servizio.id === servizioId
            ? { ...s, quantita: Math.max(0, s.quantita + delta) }
            : s
        )
        .filter((s) => s.quantita > 0)
    )
  }

  // Salva pacchetto
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!nome.trim()) return
    if (serviziCount === 0) return

    setIsSaving(true)

    try {
      if (pacchetto) {
        // Edit mode: già salvato, chiudi
        onClose()
      } else {
        // Create mode: crea pacchetto e aggiungi servizi
        const newPacchetto = await createPacchetto.mutateAsync({
          nome,
          descrizione: descrizione || undefined,
          prezzo: prezzoScontato,
          prezzo_originale: prezzoOriginale,
          servizi_inclusi: serviziCount,
          validita_giorni: validitaGiorni,
        })

        // Aggiungi tutti i servizi selezionati
        for (const sel of selectedServizi) {
          await addServizio.mutateAsync({
            pacchettoId: newPacchetto.id,
            servizioId: sel.servizio.id,
            quantita: sel.quantita,
          })
        }

        onClose()
      }
    } catch (error) {
      console.error('Save error:', error)
    } finally {
      setIsSaving(false)
    }
  }

  // Lista servizi da mostrare
  const serviziDaMostrare = pacchetto ? serviziPacchetto : null
  const serviziSelezionati = pacchetto
    ? serviziPacchetto?.map((s) => s.servizio_id) ?? []
    : selectedServizi.map((s) => s.servizio.id)

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Nome */}
      <div className="space-y-2">
        <Label htmlFor="nome" className="text-slate-300">
          Nome Pacchetto *
        </Label>
        <Input
          id="nome"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          placeholder="es. Pacchetto 5 Massaggi"
          required
          className="bg-slate-900 border-slate-700 text-white"
        />
      </div>

      {/* Descrizione */}
      <div className="space-y-2">
        <Label htmlFor="descrizione" className="text-slate-300">
          Descrizione
        </Label>
        <Textarea
          id="descrizione"
          value={descrizione}
          onChange={(e) => setDescrizione(e.target.value)}
          placeholder="Descrizione opzionale del pacchetto"
          className="bg-slate-900 border-slate-700 text-white"
          rows={2}
        />
      </div>

      {/* Servizi Composizione */}
      <div className="space-y-3 p-4 rounded-lg bg-slate-800/50 border border-slate-700">
        <Label className="text-slate-300 flex items-center gap-2">
          <Layers className="h-4 w-4" />
          Componi con Servizi *
        </Label>

        {/* Servizi già aggiunti (edit mode) */}
        {pacchetto && serviziDaMostrare && serviziDaMostrare.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {serviziDaMostrare.map((s) => (
              <Badge
                key={s.id}
                variant="secondary"
                className="flex items-center gap-1 pr-1 bg-cyan-900/50 text-cyan-300"
              >
                {s.servizio_nome} (€{s.servizio_prezzo.toFixed(0)})
                {s.quantita > 1 && ` x${s.quantita}`}
                <button
                  type="button"
                  onClick={() => handleRemoveServizio(s.servizio_id)}
                  className="ml-1 hover:bg-cyan-800 rounded p-0.5"
                  disabled={removeServizio.isPending}
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}

        {/* Servizi selezionati (create mode) */}
        {!pacchetto && selectedServizi.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {selectedServizi.map((s) => (
              <Badge
                key={s.servizio.id}
                variant="secondary"
                className="flex items-center gap-2 pr-1 bg-cyan-900/50 text-cyan-300"
              >
                <span>{s.servizio.nome} (€{s.servizio.prezzo.toFixed(0)})</span>
                <div className="flex items-center gap-1 ml-1">
                  <button
                    type="button"
                    onClick={() => handleChangeQuantity(s.servizio.id, -1)}
                    className="hover:bg-cyan-800 rounded px-1"
                  >
                    -
                  </button>
                  <span className="min-w-[16px] text-center">{s.quantita}</span>
                  <button
                    type="button"
                    onClick={() => handleChangeQuantity(s.servizio.id, 1)}
                    className="hover:bg-cyan-800 rounded px-1"
                  >
                    +
                  </button>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveServizio(s.servizio.id)}
                  className="ml-1 hover:bg-red-800 rounded p-0.5"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}

        {/* Servizi disponibili da aggiungere */}
        <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
          {serviziDisponibili
            ?.filter((s) => s.attivo && !serviziSelezionati.includes(s.id))
            .map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => handleAddServizio(s)}
                disabled={addServizio.isPending}
                className="flex items-center justify-between p-2 rounded bg-slate-700/50 hover:bg-slate-700 text-left text-sm"
              >
                <span className="text-slate-200 truncate">{s.nome}</span>
                <span className="text-slate-400 text-xs ml-2">€{s.prezzo}</span>
              </button>
            ))}
        </div>

        {serviziCount === 0 && (
          <p className="text-xs text-yellow-400 mt-2">
            Seleziona almeno un servizio per creare il pacchetto
          </p>
        )}
      </div>

      {/* Sconto + Validità */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="sconto" className="text-slate-300 flex items-center gap-1">
            <Percent className="h-3 w-3" />
            Sconto (%)
          </Label>
          <Input
            id="sconto"
            type="number"
            min="0"
            max="100"
            value={sconto}
            onChange={(e) => setSconto(parseInt(e.target.value) || 0)}
            className="bg-slate-900 border-slate-700 text-white"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="validita" className="text-slate-300 flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            Validità (giorni)
          </Label>
          <Input
            id="validita"
            type="number"
            min="1"
            value={validitaGiorni}
            onChange={(e) => setValiditaGiorni(parseInt(e.target.value) || 365)}
            className="bg-slate-900 border-slate-700 text-white"
          />
        </div>
      </div>

      {/* Riepilogo Prezzi */}
      {serviziCount > 0 && (
        <div className="p-4 rounded-lg bg-gradient-to-r from-green-900/30 to-cyan-900/30 border border-green-800/50">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-slate-400 uppercase">Prezzo Singoli</p>
              <p className="text-lg font-bold text-slate-300 line-through">
                €{prezzoOriginale.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase">Sconto</p>
              <p className="text-lg font-bold text-yellow-400">
                -{sconto}% (€{risparmio.toFixed(2)})
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-400 uppercase">Prezzo Pacchetto</p>
              <p className="text-2xl font-bold text-green-400">
                €{prezzoScontato.toFixed(2)}
              </p>
            </div>
          </div>
          <p className="text-center text-xs text-slate-400 mt-2">
            {serviziCount} servizi inclusi • Valido {validitaGiorni} giorni
          </p>
        </div>
      )}

      {/* Submit */}
      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onClose}>
          Annulla
        </Button>
        <Button
          type="submit"
          disabled={isSaving || !nome.trim() || serviziCount === 0}
          className="bg-cyan-500 hover:bg-cyan-600"
        >
          {isSaving ? 'Salvataggio...' : pacchetto ? 'Chiudi' : 'Crea Pacchetto'}
        </Button>
      </div>
    </form>
  )
}
