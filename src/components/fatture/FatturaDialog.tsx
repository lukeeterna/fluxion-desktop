// ═══════════════════════════════════════════════════════════════════
// FLUXION - FatturaDialog (Fase 6)
// Dialog per creare nuova fattura
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react'
import { useCreateFattura, useCodiciPagamento } from '@/hooks/use-fatture'
import { useClienti } from '@/hooks/use-clienti'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { FileText } from 'lucide-react'

interface FatturaDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export function FatturaDialog({
  open,
  onOpenChange,
  onSuccess,
}: FatturaDialogProps) {
  const today = new Date().toISOString().split('T')[0]

  // State
  const [clienteId, setClienteId] = useState('')
  const [tipoDocumento, setTipoDocumento] = useState('TD01')
  const [dataEmissione, setDataEmissione] = useState(today)
  const [dataScadenza, setDataScadenza] = useState('')
  const [modalitaPagamento, setModalitaPagamento] = useState('MP05')
  const [causale, setCausale] = useState('')
  const [noteInterne, setNoteInterne] = useState('')

  // Queries
  const { data: clienti } = useClienti()
  const { data: codiciPagamento } = useCodiciPagamento()

  // Mutations
  const createFattura = useCreateFattura()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!clienteId) {
      return
    }

    try {
      await createFattura.mutateAsync({
        cliente_id: clienteId,
        tipo_documento: tipoDocumento,
        data_emissione: dataEmissione,
        data_scadenza: dataScadenza || undefined,
        modalita_pagamento: modalitaPagamento,
        causale: causale || undefined,
        note_interne: noteInterne || undefined,
      })

      // Reset form
      setClienteId('')
      setTipoDocumento('TD01')
      setDataEmissione(today)
      setDataScadenza('')
      setModalitaPagamento('MP05')
      setCausale('')
      setNoteInterne('')

      onSuccess()
    } catch (err) {
      console.error('Errore creazione fattura:', err)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-slate-900 border-slate-800">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-white">
            <FileText className="h-5 w-5 text-cyan-400" />
            Nuova Fattura
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Crea una nuova fattura in bozza. Potrai aggiungere le righe dopo.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Cliente */}
          <div>
            <Label htmlFor="cliente" className="text-slate-300">
              Cliente *
            </Label>
            <Select value={clienteId} onValueChange={setClienteId}>
              <SelectTrigger className="mt-1 bg-slate-950 border-slate-700">
                <SelectValue placeholder="Seleziona cliente..." />
              </SelectTrigger>
              <SelectContent>
                {(clienti || []).map((c) => (
                  <SelectItem key={c.id} value={c.id}>
                    {c.nome} {c.cognome}
                    {c.partita_iva && ` - P.IVA ${c.partita_iva}`}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Tipo Documento */}
          <div>
            <Label htmlFor="tipo" className="text-slate-300">
              Tipo Documento
            </Label>
            <Select value={tipoDocumento} onValueChange={setTipoDocumento}>
              <SelectTrigger className="mt-1 bg-slate-950 border-slate-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="TD01">TD01 - Fattura</SelectItem>
                <SelectItem value="TD04">TD04 - Nota di Credito</SelectItem>
                <SelectItem value="TD06">TD06 - Parcella</SelectItem>
                <SelectItem value="TD24">TD24 - Fattura Differita</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Date */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="data" className="text-slate-300">
                Data Emissione *
              </Label>
              <Input
                id="data"
                type="date"
                value={dataEmissione}
                onChange={(e) => setDataEmissione(e.target.value)}
                className="mt-1 bg-slate-950 border-slate-700"
                required
              />
            </div>
            <div>
              <Label htmlFor="scadenza" className="text-slate-300">
                Data Scadenza
              </Label>
              <Input
                id="scadenza"
                type="date"
                value={dataScadenza}
                onChange={(e) => setDataScadenza(e.target.value)}
                className="mt-1 bg-slate-950 border-slate-700"
              />
            </div>
          </div>

          {/* Modalità Pagamento */}
          <div>
            <Label htmlFor="pagamento" className="text-slate-300">
              Modalità Pagamento
            </Label>
            <Select
              value={modalitaPagamento}
              onValueChange={setModalitaPagamento}
            >
              <SelectTrigger className="mt-1 bg-slate-950 border-slate-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {(codiciPagamento || []).map((c) => (
                  <SelectItem key={c.codice} value={c.codice}>
                    {c.codice} - {c.descrizione}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Causale */}
          <div>
            <Label htmlFor="causale" className="text-slate-300">
              Causale
            </Label>
            <Textarea
              id="causale"
              value={causale}
              onChange={(e) => setCausale(e.target.value)}
              placeholder="Descrizione del documento..."
              className="mt-1 bg-slate-950 border-slate-700"
              rows={2}
            />
          </div>

          {/* Note Interne */}
          <div>
            <Label htmlFor="note" className="text-slate-300">
              Note Interne
            </Label>
            <Textarea
              id="note"
              value={noteInterne}
              onChange={(e) => setNoteInterne(e.target.value)}
              placeholder="Note visibili solo a te..."
              className="mt-1 bg-slate-950 border-slate-700"
              rows={2}
            />
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="border-slate-700"
            >
              Annulla
            </Button>
            <Button
              type="submit"
              disabled={!clienteId || createFattura.isPending}
              className="bg-cyan-500 hover:bg-cyan-600"
            >
              {createFattura.isPending ? 'Creazione...' : 'Crea Bozza'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
