// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fatture Page (Fase 6)
// Lista fatture con filtri, creazione, emissione, download XML
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react'
import { toast } from 'sonner'
import {
  useFatture,
  useEmettiFattura,
  useDeleteFattura,
  useImpostazioniFatturazione,
} from '@/hooks/use-fatture'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  FileText,
  Plus,
  Send,
  Download,
  Trash2,
  Eye,
  Settings,
  Search,
  CheckCircle,
  XCircle,
  Clock,
} from 'lucide-react'
import {
  getStatoFatturaBadge,
  getTipoDocumentoLabel,
  formatCurrency,
  formatDate,
  type Fattura,
  type StatoFattura,
} from '@/types/fatture'
import { FatturaDialog } from '@/components/fatture/FatturaDialog'
import { FatturaDetail } from '@/components/fatture/FatturaDetail'
import { ImpostazioniFatturazioneDialog } from '@/components/fatture/ImpostazioniFatturazioneDialog'

export const Fatture: FC = () => {
  // State
  const [anno, setAnno] = useState<number>(new Date().getFullYear())
  const [statoFilter, setStatoFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [detailFatturaId, setDetailFatturaId] = useState<string | null>(null)
  const [impostazioniOpen, setImpostazioniOpen] = useState(false)

  // Queries
  const {
    data: fatture,
    isLoading,
    error,
  } = useFatture({
    anno,
    stato: statoFilter === 'all' ? undefined : statoFilter,
  })
  const { data: impostazioni } = useImpostazioniFatturazione()

  // Mutations
  const emettiFattura = useEmettiFattura()
  const deleteFattura = useDeleteFattura()

  // Filter by search
  const filteredFatture = (fatture || []).filter((f) => {
    if (!searchQuery) return true
    const q = searchQuery.toLowerCase()
    return (
      f.numero_completo.toLowerCase().includes(q) ||
      f.cliente_denominazione.toLowerCase().includes(q)
    )
  })

  // Stats
  const stats = {
    totale: filteredFatture.length,
    bozze: filteredFatture.filter((f) => f.stato === 'bozza').length,
    emesse: filteredFatture.filter(
      (f) => f.stato === 'emessa' || f.stato === 'inviata_sdi'
    ).length,
    pagate: filteredFatture.filter((f) => f.stato === 'pagata').length,
    importoTotale: filteredFatture
      .filter((f) => f.stato !== 'annullata')
      .reduce((sum, f) => sum + f.totale_documento, 0),
    importoPagato: filteredFatture
      .filter((f) => f.stato === 'pagata')
      .reduce((sum, f) => sum + f.totale_documento, 0),
  }

  const handleEmetti = async (fattura: Fattura) => {
    if (
      window.confirm(
        `Vuoi emettere la fattura ${fattura.numero_completo}? Verrà generato l'XML.`
      )
    ) {
      try {
        const result = await emettiFattura.mutateAsync(fattura.id)
        toast.success('Fattura Emessa!', {
          description: `XML generato: ${result.xml_filename || fattura.numero_completo + '.xml'}. Clicca sul pulsante Download per scaricarlo.`,
          duration: 8000,
        })
      } catch (err) {
        console.error('Errore emissione:', err)
        toast.error('Errore emissione fattura', {
          description: String(err),
        })
      }
    }
  }

  const handleDelete = async (fattura: Fattura) => {
    if (
      window.confirm(
        `Vuoi eliminare la bozza ${fattura.numero_completo}? L'azione è irreversibile.`
      )
    ) {
      try {
        await deleteFattura.mutateAsync(fattura.id)
      } catch (err) {
        console.error('Errore eliminazione:', err)
      }
    }
  }

  const getStatoIcon = (stato: StatoFattura) => {
    switch (stato) {
      case 'pagata':
        return <CheckCircle className="h-4 w-4 text-emerald-500" />
      case 'annullata':
      case 'rifiutata':
      case 'scartata':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'bozza':
        return <Clock className="h-4 w-4 text-gray-500" />
      default:
        return <FileText className="h-4 w-4 text-blue-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <FileText className="h-8 w-8 text-cyan-400" />
            Fatturazione Elettronica
          </h1>
          <p className="text-slate-400 mt-1">
            {impostazioni?.denominazione} - P.IVA {impostazioni?.partita_iva} -{' '}
            {impostazioni?.regime_fiscale === 'RF19'
              ? 'Regime Forfettario'
              : 'Regime Ordinario'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setImpostazioniOpen(true)}
            className="border-slate-700"
          >
            <Settings className="h-4 w-4 mr-2" />
            Impostazioni
          </Button>
          <Button
            data-testid="new-invoice"
            onClick={() => setCreateDialogOpen(true)}
            className="bg-cyan-500 hover:bg-cyan-600"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nuova Fattura
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 bg-slate-900 border-slate-800">
          <div className="text-sm text-slate-400">Fatture {anno}</div>
          <div className="text-2xl font-bold text-white">{stats.totale}</div>
          <div className="text-xs text-slate-500 mt-1">
            {stats.bozze} bozze, {stats.emesse} emesse, {stats.pagate} pagate
          </div>
        </Card>
        <Card className="p-4 bg-slate-900 border-slate-800">
          <div className="text-sm text-slate-400">Fatturato</div>
          <div className="text-2xl font-bold text-cyan-400">
            {formatCurrency(stats.importoTotale)}
          </div>
        </Card>
        <Card className="p-4 bg-slate-900 border-slate-800">
          <div className="text-sm text-slate-400">Incassato</div>
          <div className="text-2xl font-bold text-emerald-400">
            {formatCurrency(stats.importoPagato)}
          </div>
        </Card>
        <Card className="p-4 bg-slate-900 border-slate-800">
          <div className="text-sm text-slate-400">Da incassare</div>
          <div className="text-2xl font-bold text-amber-400">
            {formatCurrency(stats.importoTotale - stats.importoPagato)}
          </div>
        </Card>
      </div>

      {/* Filters */}
      <Card className="p-4 bg-slate-900 border-slate-800">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <Label className="text-slate-400">Cerca</Label>
            <div className="relative mt-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
              <Input
                placeholder="Numero, cliente..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-slate-950 border-slate-700"
              />
            </div>
          </div>
          <div className="w-32">
            <Label className="text-slate-400">Anno</Label>
            <Select
              value={anno.toString()}
              onValueChange={(v) => setAnno(parseInt(v))}
            >
              <SelectTrigger className="mt-1 bg-slate-950 border-slate-700">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {[2026, 2025, 2024].map((y) => (
                  <SelectItem key={y} value={y.toString()}>
                    {y}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="w-40">
            <Label className="text-slate-400">Stato</Label>
            <Select value={statoFilter} onValueChange={setStatoFilter}>
              <SelectTrigger className="mt-1 bg-slate-950 border-slate-700">
                <SelectValue placeholder="Tutti" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tutti</SelectItem>
                <SelectItem value="bozza">Bozze</SelectItem>
                <SelectItem value="emessa">Emesse</SelectItem>
                <SelectItem value="pagata">Pagate</SelectItem>
                <SelectItem value="annullata">Annullate</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Table */}
      <Card className="bg-slate-900 border-slate-800 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-slate-400">
            Caricamento fatture...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-red-400">
            Errore: {String(error)}
          </div>
        ) : filteredFatture.length === 0 ? (
          <div className="p-8 text-center text-slate-400">
            Nessuna fattura trovata
          </div>
        ) : (
          <Table data-testid="invoices-list">
            <TableHeader>
              <TableRow className="border-slate-800 hover:bg-slate-800/50">
                <TableHead className="text-slate-400">Numero</TableHead>
                <TableHead className="text-slate-400">Data</TableHead>
                <TableHead className="text-slate-400">Cliente</TableHead>
                <TableHead className="text-slate-400">Tipo</TableHead>
                <TableHead className="text-slate-400 text-right">
                  Importo
                </TableHead>
                <TableHead className="text-slate-400">Stato</TableHead>
                <TableHead className="text-slate-400 text-right">
                  Azioni
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredFatture.map((fattura) => {
                const badge = getStatoFatturaBadge(fattura.stato)
                return (
                  <TableRow
                    key={fattura.id}
                    className="border-slate-800 hover:bg-slate-800/50 cursor-pointer"
                    onClick={() => setDetailFatturaId(fattura.id)}
                  >
                    <TableCell className="font-mono text-white">
                      {fattura.numero_completo}
                    </TableCell>
                    <TableCell className="text-slate-300">
                      {formatDate(fattura.data_emissione)}
                    </TableCell>
                    <TableCell className="text-slate-300">
                      {fattura.cliente_denominazione}
                    </TableCell>
                    <TableCell className="text-slate-400">
                      {getTipoDocumentoLabel(fattura.tipo_documento)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-cyan-400">
                      {formatCurrency(fattura.totale_documento)}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatoIcon(fattura.stato)}
                        <Badge variant={badge.variant}>{badge.label}</Badge>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div
                        className="flex justify-end gap-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setDetailFatturaId(fattura.id)}
                          className="h-8 w-8 p-0"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        {fattura.stato === 'bozza' && (
                          <>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEmetti(fattura)}
                              className="h-8 w-8 p-0 text-green-400 hover:text-green-300"
                              disabled={emettiFattura.isPending}
                            >
                              <Send className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDelete(fattura)}
                              className="h-8 w-8 p-0 text-red-400 hover:text-red-300"
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                        {fattura.xml_filename && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              // Download XML
                              const blob = new window.Blob(
                                [fattura.xml_content || ''],
                                { type: 'application/xml' }
                              )
                              const url = window.URL.createObjectURL(blob)
                              const a = document.createElement('a')
                              a.href = url
                              a.download = fattura.xml_filename || 'fattura.xml'
                              a.click()
                              window.URL.revokeObjectURL(url)
                            }}
                            className="h-8 w-8 p-0 text-cyan-400 hover:text-cyan-300"
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        )}
      </Card>

      {/* Dialogs */}
      <FatturaDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
        onSuccess={() => setCreateDialogOpen(false)}
      />

      {detailFatturaId && (
        <FatturaDetail
          fatturaId={detailFatturaId}
          open={!!detailFatturaId}
          onOpenChange={(open) => !open && setDetailFatturaId(null)}
        />
      )}

      <ImpostazioniFatturazioneDialog
        open={impostazioniOpen}
        onOpenChange={setImpostazioniOpen}
      />
    </div>
  )
}
