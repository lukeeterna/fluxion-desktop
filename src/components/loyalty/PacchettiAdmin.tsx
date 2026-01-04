// ═══════════════════════════════════════════════════════════════════
// FLUXION - Pacchetti Admin Component (Fase 5 v2)
// Gestione pacchetti: crea, modifica, elimina, componi con servizi
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react'
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
import type { Pacchetto, CreatePacchetto } from '@/types/loyalty'
import type { Servizio } from '@/types/servizio'
import { Package, Plus, Edit, Trash2, Euro, Calendar, Layers, X } from 'lucide-react'

export function PacchettiAdmin() {
  const { data: pacchetti, isLoading } = usePacchetti()
  const createPacchetto = useCreatePacchetto()
  const deletePacchetto = useDeletePacchetto()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingPacchetto, setEditingPacchetto] = useState<Pacchetto | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [pacchettoToDelete, setPacchettoToDelete] = useState<Pacchetto | null>(null)

  const handleCreate = (data: CreatePacchetto) => {
    createPacchetto.mutate(data, {
      onSuccess: () => {
        setDialogOpen(false)
        setEditingPacchetto(null)
      },
    })
  }

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

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
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
              onSubmit={handleCreate}
              isLoading={createPacchetto.isPending}
              onClose={() => setDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>
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
            {pacchetto.prezzo.toFixed(2)}
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

function PacchettoForm({
  pacchetto,
  onSubmit,
  isLoading,
  onClose,
}: {
  pacchetto: Pacchetto | null
  onSubmit: (data: CreatePacchetto) => void
  isLoading: boolean
  onClose: () => void
}) {
  const { data: serviziDisponibili } = useServizi()
  const { data: serviziPacchetto } = usePacchettoServizi(pacchetto?.id)
  const addServizio = useAddServizioToPacchetto()
  const removeServizio = useRemoveServizioFromPacchetto()

  const [formData, setFormData] = useState<CreatePacchetto>({
    nome: pacchetto?.nome ?? '',
    descrizione: pacchetto?.descrizione ?? '',
    prezzo: pacchetto?.prezzo ?? 0,
    prezzo_originale: pacchetto?.prezzo_originale ?? undefined,
    servizi_inclusi: pacchetto?.servizi_inclusi ?? 0,
    validita_giorni: pacchetto?.validita_giorni ?? 365,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleAddServizio = (servizio: Servizio) => {
    if (pacchetto) {
      addServizio.mutate({
        pacchettoId: pacchetto.id,
        servizioId: servizio.id,
        quantita: 1,
      })
    }
  }

  const handleRemoveServizio = (servizioId: string) => {
    if (pacchetto) {
      removeServizio.mutate({
        pacchettoId: pacchetto.id,
        servizioId,
      })
    }
  }

  // Calculate total from services
  const totalFromServices = serviziPacchetto?.reduce(
    (sum, s) => sum + s.servizio_prezzo * s.quantita,
    0
  ) ?? 0

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Nome */}
      <div className="space-y-2">
        <Label htmlFor="nome" className="text-slate-300">
          Nome Pacchetto *
        </Label>
        <Input
          id="nome"
          value={formData.nome}
          onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
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
          value={formData.descrizione ?? ''}
          onChange={(e) =>
            setFormData({ ...formData, descrizione: e.target.value })
          }
          placeholder="Descrizione opzionale del pacchetto"
          className="bg-slate-900 border-slate-700 text-white"
          rows={2}
        />
      </div>

      {/* Servizi Composizione (solo in edit mode) */}
      {pacchetto && (
        <div className="space-y-3 p-4 rounded-lg bg-slate-800/50 border border-slate-700">
          <Label className="text-slate-300 flex items-center gap-2">
            <Layers className="h-4 w-4" />
            Componi con Servizi
          </Label>

          {/* Servizi già aggiunti */}
          {serviziPacchetto && serviziPacchetto.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {serviziPacchetto.map((s) => (
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

          {/* Servizi disponibili da aggiungere */}
          <div className="grid grid-cols-2 gap-2 max-h-40 overflow-y-auto">
            {serviziDisponibili
              ?.filter(
                (s) =>
                  s.attivo &&
                  !serviziPacchetto?.some((sp) => sp.servizio_id === s.id)
              )
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

          {totalFromServices > 0 && (
            <p className="text-xs text-slate-400 mt-2">
              Valore singolo servizi: €{totalFromServices.toFixed(2)}
            </p>
          )}
        </div>
      )}

      {/* Prezzo + Prezzo Originale */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="prezzo" className="text-slate-300">
            Prezzo Pacchetto (€) *
          </Label>
          <Input
            id="prezzo"
            type="number"
            step="0.01"
            min="0"
            value={formData.prezzo}
            onChange={(e) =>
              setFormData({ ...formData, prezzo: parseFloat(e.target.value) || 0 })
            }
            required
            className="bg-slate-900 border-slate-700 text-white"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="prezzo_originale" className="text-slate-300">
            Prezzo Originale (€)
          </Label>
          <Input
            id="prezzo_originale"
            type="number"
            step="0.01"
            min="0"
            value={formData.prezzo_originale ?? (totalFromServices > 0 ? totalFromServices : '')}
            onChange={(e) =>
              setFormData({
                ...formData,
                prezzo_originale: e.target.value
                  ? parseFloat(e.target.value)
                  : undefined,
              })
            }
            placeholder={totalFromServices > 0 ? `${totalFromServices.toFixed(2)} (da servizi)` : 'Per mostrare sconto'}
            className="bg-slate-900 border-slate-700 text-white"
          />
        </div>
      </div>

      {/* Validità */}
      <div className="space-y-2">
        <Label htmlFor="validita" className="text-slate-300">
          Validità (giorni)
        </Label>
        <Input
          id="validita"
          type="number"
          min="1"
          value={formData.validita_giorni ?? 365}
          onChange={(e) =>
            setFormData({
              ...formData,
              validita_giorni: parseInt(e.target.value) || 365,
            })
          }
          className="bg-slate-900 border-slate-700 text-white"
        />
      </div>

      {/* Preview Risparmio */}
      {formData.prezzo_originale && formData.prezzo_originale > formData.prezzo && (
        <div className="p-3 rounded-lg bg-green-900/30 border border-green-800">
          <p className="text-sm text-green-300">
            Risparmio cliente:{' '}
            <strong>
              €{(formData.prezzo_originale - formData.prezzo).toFixed(2)}
            </strong>{' '}
            (
            {Math.round(
              ((formData.prezzo_originale - formData.prezzo) /
                formData.prezzo_originale) *
                100
            )}
            %)
          </p>
        </div>
      )}

      {/* Submit */}
      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onClose}>
          Annulla
        </Button>
        <Button type="submit" disabled={isLoading || !formData.nome}>
          {isLoading ? 'Salvataggio...' : pacchetto ? 'Salva Modifiche' : 'Crea Pacchetto'}
        </Button>
      </div>
    </form>
  )
}
