// ═══════════════════════════════════════════════════════════════════
// FLUXION - FatturaDetail (Fase 6)
// Sheet per visualizzare/modificare fattura con righe e pagamenti
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react'
import {
  useFattura,
  useAddRigaFattura,
  useDeleteRigaFattura,
  useEmettiFattura,
  useRegistraPagamento,
  useImpostazioniFatturazione,
} from '@/hooks/use-fatture'
import { useServizi } from '@/hooks/use-servizi'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
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
  Trash2,
  Send,
  Download,
  CreditCard,
} from 'lucide-react'
import {
  getStatoFatturaBadge,
  formatCurrency,
  formatDate,
} from '@/types/fatture'

interface FatturaDetailProps {
  fatturaId: string
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function FatturaDetail({
  fatturaId,
  open,
  onOpenChange,
}: FatturaDetailProps) {
  // State for new line
  const [newRiga, setNewRiga] = useState({
    descrizione: '',
    quantita: 1,
    prezzo_unitario: 0,
    sconto_percentuale: 0,
    aliquota_iva: 0,
    natura: 'N2.2',
    servizio_id: '',
  })

  // State for payment
  const [showPaymentForm, setShowPaymentForm] = useState(false)
  const [payment, setPayment] = useState({
    importo: 0,
    metodo: 'bonifico',
    riferimento: '',
  })

  // Queries
  const { data: fatturaCompleta, isLoading } = useFattura(fatturaId)
  const { data: impostazioni } = useImpostazioniFatturazione()
  const { data: servizi } = useServizi()

  // Mutations
  const addRiga = useAddRigaFattura()
  const deleteRiga = useDeleteRigaFattura()
  const emettiFattura = useEmettiFattura()
  const registraPagamento = useRegistraPagamento()

  if (isLoading || !fatturaCompleta) {
    return null
  }

  const { fattura, righe, pagamenti } = fatturaCompleta
  const isBozza = fattura.stato === 'bozza'
  const isEmessa = fattura.stato === 'emessa' || fattura.stato === 'accettata'
  const isPagata = fattura.stato === 'pagata'
  const isForfettario = impostazioni?.regime_fiscale === 'RF19'

  const badge = getStatoFatturaBadge(fattura.stato)

  const handleAddRiga = async () => {
    if (!newRiga.descrizione || newRiga.prezzo_unitario <= 0) return

    await addRiga.mutateAsync({
      fattura_id: fatturaId,
      descrizione: newRiga.descrizione,
      quantita: newRiga.quantita,
      prezzo_unitario: newRiga.prezzo_unitario,
      sconto_percentuale: newRiga.sconto_percentuale,
      aliquota_iva: newRiga.aliquota_iva,
      natura: isForfettario ? newRiga.natura : undefined,
      servizio_id: newRiga.servizio_id || undefined,
    })

    // Reset form
    setNewRiga({
      descrizione: '',
      quantita: 1,
      prezzo_unitario: 0,
      sconto_percentuale: 0,
      aliquota_iva: 0,
      natura: 'N2.2',
      servizio_id: '',
    })
  }

  const handleSelectServizio = (servizioId: string) => {
    const servizio = servizi?.find((s) => s.id === servizioId)
    if (servizio) {
      setNewRiga({
        ...newRiga,
        descrizione: servizio.nome,
        prezzo_unitario: servizio.prezzo,
        aliquota_iva: isForfettario ? 0 : servizio.iva_percentuale || 22,
        servizio_id: servizioId,
      })
    }
  }

  const handleEmetti = async () => {
    if (window.confirm('Vuoi emettere questa fattura? Verrà generato l\'XML.')) {
      await emettiFattura.mutateAsync(fatturaId)
    }
  }

  const handleAddPayment = async () => {
    if (payment.importo <= 0) return

    await registraPagamento.mutateAsync({
      fattura_id: fatturaId,
      data_pagamento: new Date().toISOString().split('T')[0],
      importo: payment.importo,
      metodo: payment.metodo,
      riferimento: payment.riferimento || undefined,
    })

    setPayment({ importo: 0, metodo: 'bonifico', riferimento: '' })
    setShowPaymentForm(false)
  }

  const handleDownloadXml = () => {
    if (!fattura.xml_content) return
    const blob = new window.Blob([fattura.xml_content], { type: 'application/xml' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fattura.xml_filename || 'fattura.xml'
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const totalePagato = pagamenti.reduce((sum, p) => sum + p.importo, 0)
  const residuo = fattura.totale_documento - totalePagato

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="right"
        className="w-full sm:max-w-2xl bg-slate-900 border-slate-800 overflow-y-auto"
      >
        <SheetHeader>
          <SheetTitle className="flex items-center gap-3 text-white">
            <FileText className="h-6 w-6 text-cyan-400" />
            Fattura {fattura.numero_completo}
            <Badge variant={badge.variant}>{badge.label}</Badge>
          </SheetTitle>
          <SheetDescription className="text-slate-400">
            {fattura.cliente_denominazione} - {formatDate(fattura.data_emissione)}
          </SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Dati Cliente */}
          <Card className="p-4 bg-slate-950 border-slate-800">
            <h3 className="font-semibold text-white mb-2">Dati Cliente</h3>
            <div className="text-sm text-slate-400 space-y-1">
              <p>{fattura.cliente_denominazione}</p>
              {fattura.cliente_partita_iva && (
                <p>P.IVA: {fattura.cliente_partita_iva}</p>
              )}
              {fattura.cliente_codice_fiscale && (
                <p>CF: {fattura.cliente_codice_fiscale}</p>
              )}
              {fattura.cliente_indirizzo && (
                <p>
                  {fattura.cliente_indirizzo}, {fattura.cliente_cap}{' '}
                  {fattura.cliente_comune} ({fattura.cliente_provincia})
                </p>
              )}
              <p>Codice SDI: {fattura.cliente_codice_sdi}</p>
            </div>
          </Card>

          {/* Righe Fattura */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-white">Righe Documento</h3>
            </div>

            {righe.length > 0 && (
              <Table>
                <TableHeader>
                  <TableRow className="border-slate-800">
                    <TableHead className="text-slate-400">#</TableHead>
                    <TableHead className="text-slate-400">Descrizione</TableHead>
                    <TableHead className="text-slate-400 text-right">Qtà</TableHead>
                    <TableHead className="text-slate-400 text-right">Prezzo</TableHead>
                    <TableHead className="text-slate-400 text-right">Totale</TableHead>
                    {isBozza && <TableHead className="w-10"></TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {righe.map((riga) => (
                    <TableRow key={riga.id} className="border-slate-800">
                      <TableCell className="text-slate-500">{riga.numero_linea}</TableCell>
                      <TableCell className="text-slate-300">{riga.descrizione}</TableCell>
                      <TableCell className="text-right text-slate-300">
                        {riga.quantita} {riga.unita_misura}
                      </TableCell>
                      <TableCell className="text-right text-slate-300">
                        {formatCurrency(riga.prezzo_unitario)}
                      </TableCell>
                      <TableCell className="text-right font-mono text-cyan-400">
                        {formatCurrency(riga.prezzo_totale)}
                      </TableCell>
                      {isBozza && (
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-red-400"
                            onClick={() => deleteRiga.mutate(riga.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      )}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {/* Add new line - only for bozza */}
            {isBozza && (
              <Card className="p-4 mt-4 bg-slate-950 border-slate-800 border-dashed">
                <h4 className="text-sm font-medium text-slate-400 mb-3">
                  Aggiungi Riga
                </h4>
                <div className="space-y-3">
                  {/* Quick select from servizi */}
                  <Select onValueChange={handleSelectServizio}>
                    <SelectTrigger className="bg-slate-900 border-slate-700">
                      <SelectValue placeholder="Seleziona da servizi..." />
                    </SelectTrigger>
                    <SelectContent>
                      {(servizi || []).map((s) => (
                        <SelectItem key={s.id} value={s.id}>
                          {s.nome} - {formatCurrency(s.prezzo)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <div className="grid grid-cols-4 gap-2">
                    <div className="col-span-2">
                      <Input
                        placeholder="Descrizione"
                        value={newRiga.descrizione}
                        onChange={(e) =>
                          setNewRiga({ ...newRiga, descrizione: e.target.value })
                        }
                        className="bg-slate-900 border-slate-700"
                      />
                    </div>
                    <div>
                      <Input
                        type="number"
                        placeholder="Qtà"
                        value={newRiga.quantita}
                        onChange={(e) =>
                          setNewRiga({
                            ...newRiga,
                            quantita: parseFloat(e.target.value) || 1,
                          })
                        }
                        className="bg-slate-900 border-slate-700"
                        min={1}
                      />
                    </div>
                    <div>
                      <Input
                        type="number"
                        placeholder="Prezzo"
                        value={newRiga.prezzo_unitario || ''}
                        onChange={(e) =>
                          setNewRiga({
                            ...newRiga,
                            prezzo_unitario: parseFloat(e.target.value) || 0,
                          })
                        }
                        className="bg-slate-900 border-slate-700"
                        min={0}
                        step={0.01}
                      />
                    </div>
                  </div>

                  <Button
                    onClick={handleAddRiga}
                    disabled={!newRiga.descrizione || addRiga.isPending}
                    className="w-full bg-cyan-600 hover:bg-cyan-700"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Aggiungi Riga
                  </Button>
                </div>
              </Card>
            )}
          </div>

          {/* Totali */}
          <Card className="p-4 bg-slate-950 border-slate-800">
            <div className="space-y-2">
              <div className="flex justify-between text-slate-400">
                <span>Imponibile</span>
                <span className="font-mono">
                  {formatCurrency(fattura.imponibile_totale)}
                </span>
              </div>
              {!isForfettario && (
                <div className="flex justify-between text-slate-400">
                  <span>IVA</span>
                  <span className="font-mono">
                    {formatCurrency(fattura.iva_totale)}
                  </span>
                </div>
              )}
              {fattura.bollo_virtuale === 1 && (
                <div className="flex justify-between text-slate-400">
                  <span>Bollo</span>
                  <span className="font-mono">
                    {formatCurrency(fattura.bollo_importo)}
                  </span>
                </div>
              )}
              <div className="flex justify-between text-lg font-bold text-white border-t border-slate-700 pt-2 mt-2">
                <span>Totale</span>
                <span className="font-mono text-cyan-400">
                  {formatCurrency(fattura.totale_documento)}
                </span>
              </div>
            </div>
          </Card>

          {/* Pagamenti */}
          {isEmessa && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-white">Pagamenti</h3>
                {!isPagata && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setShowPaymentForm(!showPaymentForm)}
                    className="border-slate-700"
                  >
                    <CreditCard className="h-4 w-4 mr-2" />
                    Registra Pagamento
                  </Button>
                )}
              </div>

              {pagamenti.length > 0 && (
                <div className="space-y-2 mb-4">
                  {pagamenti.map((p) => (
                    <Card
                      key={p.id}
                      className="p-3 bg-slate-950 border-slate-800 flex justify-between items-center"
                    >
                      <div>
                        <p className="text-slate-300">{formatDate(p.data_pagamento)}</p>
                        <p className="text-sm text-slate-500">
                          {p.metodo} {p.riferimento && `- ${p.riferimento}`}
                        </p>
                      </div>
                      <p className="font-mono text-emerald-400">
                        +{formatCurrency(p.importo)}
                      </p>
                    </Card>
                  ))}
                </div>
              )}

              {!isPagata && (
                <Card className="p-3 bg-amber-500/10 border-amber-500/30">
                  <div className="flex justify-between items-center">
                    <span className="text-amber-400">Residuo da incassare</span>
                    <span className="font-mono text-amber-400 font-bold">
                      {formatCurrency(residuo)}
                    </span>
                  </div>
                </Card>
              )}

              {showPaymentForm && (
                <Card className="p-4 mt-4 bg-slate-950 border-slate-800">
                  <div className="space-y-3">
                    <div>
                      <Label className="text-slate-400">Importo</Label>
                      <Input
                        type="number"
                        value={payment.importo || ''}
                        onChange={(e) =>
                          setPayment({
                            ...payment,
                            importo: parseFloat(e.target.value) || 0,
                          })
                        }
                        className="mt-1 bg-slate-900 border-slate-700"
                        min={0}
                        step={0.01}
                        max={residuo}
                      />
                    </div>
                    <div>
                      <Label className="text-slate-400">Metodo</Label>
                      <Select
                        value={payment.metodo}
                        onValueChange={(v) =>
                          setPayment({ ...payment, metodo: v })
                        }
                      >
                        <SelectTrigger className="mt-1 bg-slate-900 border-slate-700">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="contanti">Contanti</SelectItem>
                          <SelectItem value="bonifico">Bonifico</SelectItem>
                          <SelectItem value="carta">Carta</SelectItem>
                          <SelectItem value="satispay">Satispay</SelectItem>
                          <SelectItem value="assegno">Assegno</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label className="text-slate-400">Riferimento (CRO, etc.)</Label>
                      <Input
                        value={payment.riferimento}
                        onChange={(e) =>
                          setPayment({ ...payment, riferimento: e.target.value })
                        }
                        className="mt-1 bg-slate-900 border-slate-700"
                      />
                    </div>
                    <Button
                      onClick={handleAddPayment}
                      disabled={payment.importo <= 0 || registraPagamento.isPending}
                      className="w-full bg-emerald-600 hover:bg-emerald-700"
                    >
                      Registra Pagamento
                    </Button>
                  </div>
                </Card>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            {isBozza && righe.length > 0 && (
              <Button
                onClick={handleEmetti}
                disabled={emettiFattura.isPending}
                className="flex-1 bg-green-600 hover:bg-green-700"
              >
                <Send className="h-4 w-4 mr-2" />
                {emettiFattura.isPending ? 'Emissione...' : 'Emetti Fattura'}
              </Button>
            )}
            {fattura.xml_content && (
              <Button
                onClick={handleDownloadXml}
                variant="outline"
                className="flex-1 border-slate-700"
              >
                <Download className="h-4 w-4 mr-2" />
                Scarica XML
              </Button>
            )}
          </div>

          {/* Regime forfettario notice */}
          {isForfettario && (
            <p className="text-xs text-slate-500 text-center">
              Operazione effettuata ai sensi dell'art. 1, commi 54-89, L. 190/2014
              - Regime forfettario. Operazione senza applicazione dell'IVA.
            </p>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}
