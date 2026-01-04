// ═══════════════════════════════════════════════════════════════════
// FLUXION - Pacchetti List Component (Fase 5)
// Lista pacchetti cliente con progress e azioni
// ═══════════════════════════════════════════════════════════════════

import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  useClientePacchetti,
  usePacchetti,
  useProponiPacchetto,
  useConfermaAcquistoPacchetto,
  useUsaServizioPacchetto,
} from '@/hooks/use-loyalty'
import { getPacchettoStatoBadge, formatRisparmio } from '@/types/loyalty'
import type { ClientePacchetto, Pacchetto } from '@/types/loyalty'
import { Package, Plus, Check, ShoppingCart } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { useState } from 'react'

interface PacchettiListProps {
  clienteId: string
}

export function PacchettiList({ clienteId }: PacchettiListProps) {
  const { data: clientePacchetti, isLoading } = useClientePacchetti(clienteId)
  const { data: pacchetti } = usePacchetti()
  const proponi = useProponiPacchetto()
  const conferma = useConfermaAcquistoPacchetto()
  const usaServizio = useUsaServizioPacchetto()
  const [showProponiDialog, setShowProponiDialog] = useState(false)

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-2">
        <div className="h-16 bg-muted rounded" />
        <div className="h-16 bg-muted rounded" />
      </div>
    )
  }

  const activePacchetti = clientePacchetti?.filter(
    (p) => p.stato !== 'completato' && p.stato !== 'annullato' && p.stato !== 'scaduto'
  )
  const historyPacchetti = clientePacchetti?.filter(
    (p) => p.stato === 'completato' || p.stato === 'annullato' || p.stato === 'scaduto'
  )

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Package className="h-5 w-5 text-primary" />
          <span className="font-medium">Pacchetti</span>
        </div>

        <Dialog open={showProponiDialog} onOpenChange={setShowProponiDialog}>
          <DialogTrigger asChild>
            <Button size="sm" variant="outline">
              <Plus className="h-4 w-4 mr-1" />
              Proponi Pacchetto
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Proponi Pacchetto</DialogTitle>
            </DialogHeader>
            <div className="space-y-3">
              {pacchetti?.map((p) => (
                <PacchettoCard
                  key={p.id}
                  pacchetto={p}
                  onSelect={() => {
                    proponi.mutate(
                      { clienteId, pacchettoId: p.id },
                      { onSuccess: () => setShowProponiDialog(false) }
                    )
                  }}
                  isLoading={proponi.isPending}
                />
              ))}
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Active Pacchetti */}
      {activePacchetti && activePacchetti.length > 0 ? (
        <div className="space-y-2">
          {activePacchetti.map((cp) => (
            <ClientePacchettoCard
              key={cp.id}
              clientePacchetto={cp}
              onConferma={() =>
                conferma.mutate({
                  clientePacchettoId: cp.id,
                  metodoPagamento: 'contanti',
                  validitaGiorni: 365,
                })
              }
              onUsaServizio={() => usaServizio.mutate(cp.id)}
              isLoading={conferma.isPending || usaServizio.isPending}
            />
          ))}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground text-center py-4">
          Nessun pacchetto attivo
        </p>
      )}

      {/* History */}
      {historyPacchetti && historyPacchetti.length > 0 && (
        <div className="pt-2 border-t">
          <p className="text-xs text-muted-foreground mb-2">Storico</p>
          <div className="space-y-1">
            {historyPacchetti.slice(0, 3).map((cp) => (
              <div
                key={cp.id}
                className="flex items-center justify-between text-sm text-muted-foreground"
              >
                <span>{cp.pacchetto_nome}</span>
                <Badge variant="outline" className="text-xs">
                  {getPacchettoStatoBadge(cp.stato).label}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ───────────────────────────────────────────────────────────────────
// Sub-components
// ───────────────────────────────────────────────────────────────────

function PacchettoCard({
  pacchetto,
  onSelect,
  isLoading,
}: {
  pacchetto: Pacchetto
  onSelect: () => void
  isLoading: boolean
}) {
  const risparmio = formatRisparmio(pacchetto)

  return (
    <Card className="cursor-pointer hover:bg-muted/50 transition-colors">
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium">{pacchetto.nome}</h4>
            {pacchetto.descrizione && (
              <p className="text-sm text-muted-foreground">
                {pacchetto.descrizione}
              </p>
            )}
            <div className="flex items-center gap-2 mt-1">
              <span className="text-lg font-bold">€{pacchetto.prezzo}</span>
              {risparmio && (
                <Badge variant="secondary" className="text-green-600">
                  {risparmio}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              {pacchetto.servizi_inclusi} servizi • Valido {pacchetto.validita_giorni} giorni
            </p>
          </div>
          <Button onClick={onSelect} disabled={isLoading} size="sm">
            <ShoppingCart className="h-4 w-4 mr-1" />
            Proponi
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function ClientePacchettoCard({
  clientePacchetto,
  onConferma,
  onUsaServizio,
  isLoading,
}: {
  clientePacchetto: ClientePacchetto
  onConferma: () => void
  onUsaServizio: () => void
  isLoading: boolean
}) {
  const badge = getPacchettoStatoBadge(clientePacchetto.stato)

  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h4 className="font-medium">{clientePacchetto.pacchetto_nome}</h4>
          <Badge variant={badge.variant}>{badge.label}</Badge>
        </div>

        <Progress value={clientePacchetto.progress_percent} className="h-2 mb-2" />

        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {clientePacchetto.servizi_usati} / {clientePacchetto.servizi_totali} usati
          </span>

          {clientePacchetto.stato === 'proposto' && (
            <Button size="sm" onClick={onConferma} disabled={isLoading}>
              <Check className="h-4 w-4 mr-1" />
              Conferma Acquisto
            </Button>
          )}

          {(clientePacchetto.stato === 'venduto' ||
            clientePacchetto.stato === 'in_uso') && (
            <Button
              size="sm"
              variant="secondary"
              onClick={onUsaServizio}
              disabled={isLoading}
            >
              Usa Servizio
            </Button>
          )}
        </div>

        {clientePacchetto.data_scadenza && (
          <p className="text-xs text-muted-foreground mt-2">
            Scade: {clientePacchetto.data_scadenza}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
