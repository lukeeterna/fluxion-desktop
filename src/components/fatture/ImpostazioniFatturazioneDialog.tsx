// ═══════════════════════════════════════════════════════════════════
// FLUXION - ImpostazioniFatturazioneDialog (Fase 6)
// Dialog per configurare dati azienda per fatturazione
// ═══════════════════════════════════════════════════════════════════

import { useEffect, useState } from 'react'
import {
  useImpostazioniFatturazione,
  useUpdateImpostazioniFatturazione,
} from '@/hooks/use-fatture'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Settings, Building2, CreditCard, FileText } from 'lucide-react'

interface ImpostazioniFatturazioneDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ImpostazioniFatturazioneDialog({
  open,
  onOpenChange,
}: ImpostazioniFatturazioneDialogProps) {
  const { data: impostazioni, isLoading } = useImpostazioniFatturazione()
  const updateImpostazioni = useUpdateImpostazioniFatturazione()

  // Form state
  const [form, setForm] = useState({
    denominazione: '',
    partita_iva: '',
    codice_fiscale: '',
    regime_fiscale: 'RF19',
    indirizzo: '',
    cap: '',
    comune: '',
    provincia: '',
    telefono: '',
    email: '',
    pec: '',
    prefisso_numerazione: '',
    aliquota_iva_default: 0,
    natura_iva_default: 'N2.2',
    iban: '',
    bic: '',
    nome_banca: '',
  })

  // Load data when dialog opens
  useEffect(() => {
    if (impostazioni) {
      setForm({
        denominazione: impostazioni.denominazione,
        partita_iva: impostazioni.partita_iva,
        codice_fiscale: impostazioni.codice_fiscale || '',
        regime_fiscale: impostazioni.regime_fiscale,
        indirizzo: impostazioni.indirizzo,
        cap: impostazioni.cap,
        comune: impostazioni.comune,
        provincia: impostazioni.provincia,
        telefono: impostazioni.telefono || '',
        email: impostazioni.email || '',
        pec: impostazioni.pec || '',
        prefisso_numerazione: impostazioni.prefisso_numerazione || '',
        aliquota_iva_default: impostazioni.aliquota_iva_default,
        natura_iva_default: impostazioni.natura_iva_default || 'N2.2',
        iban: impostazioni.iban || '',
        bic: impostazioni.bic || '',
        nome_banca: impostazioni.nome_banca || '',
      })
    }
  }, [impostazioni])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await updateImpostazioni.mutateAsync({
        denominazione: form.denominazione,
        partita_iva: form.partita_iva,
        codice_fiscale: form.codice_fiscale || undefined,
        regime_fiscale: form.regime_fiscale,
        indirizzo: form.indirizzo,
        cap: form.cap,
        comune: form.comune,
        provincia: form.provincia,
        telefono: form.telefono || undefined,
        email: form.email || undefined,
        pec: form.pec || undefined,
        prefisso_numerazione: form.prefisso_numerazione || undefined,
        aliquota_iva_default: form.aliquota_iva_default,
        natura_iva_default: form.natura_iva_default || undefined,
        iban: form.iban || undefined,
        bic: form.bic || undefined,
        nome_banca: form.nome_banca || undefined,
      })
      onOpenChange(false)
    } catch (err) {
      console.error('Errore aggiornamento impostazioni:', err)
    }
  }

  if (isLoading) {
    return null
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] bg-slate-900 border-slate-800 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-white">
            <Settings className="h-5 w-5 text-cyan-400" />
            Impostazioni Fatturazione
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Configura i dati aziendali per la fatturazione elettronica.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <Tabs defaultValue="azienda" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-slate-800">
              <TabsTrigger value="azienda">
                <Building2 className="h-4 w-4 mr-2" />
                Azienda
              </TabsTrigger>
              <TabsTrigger value="fiscale">
                <FileText className="h-4 w-4 mr-2" />
                Fiscale
              </TabsTrigger>
              <TabsTrigger value="banca">
                <CreditCard className="h-4 w-4 mr-2" />
                Banca
              </TabsTrigger>
            </TabsList>

            {/* Tab Azienda */}
            <TabsContent value="azienda" className="space-y-4 mt-4">
              <div>
                <Label className="text-slate-300">Denominazione *</Label>
                <Input
                  value={form.denominazione}
                  onChange={(e) =>
                    setForm({ ...form, denominazione: e.target.value })
                  }
                  className="mt-1 bg-slate-950 border-slate-700"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-300">Partita IVA *</Label>
                  <Input
                    value={form.partita_iva}
                    onChange={(e) =>
                      setForm({ ...form, partita_iva: e.target.value })
                    }
                    className="mt-1 bg-slate-950 border-slate-700"
                    maxLength={11}
                    required
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Codice Fiscale</Label>
                  <Input
                    value={form.codice_fiscale}
                    onChange={(e) =>
                      setForm({ ...form, codice_fiscale: e.target.value.toUpperCase() })
                    }
                    className="mt-1 bg-slate-950 border-slate-700"
                    maxLength={16}
                  />
                </div>
              </div>

              <div>
                <Label className="text-slate-300">Indirizzo *</Label>
                <Input
                  value={form.indirizzo}
                  onChange={(e) =>
                    setForm({ ...form, indirizzo: e.target.value })
                  }
                  className="mt-1 bg-slate-950 border-slate-700"
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label className="text-slate-300">CAP *</Label>
                  <Input
                    value={form.cap}
                    onChange={(e) => setForm({ ...form, cap: e.target.value })}
                    className="mt-1 bg-slate-950 border-slate-700"
                    maxLength={5}
                    required
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Comune *</Label>
                  <Input
                    value={form.comune}
                    onChange={(e) =>
                      setForm({ ...form, comune: e.target.value })
                    }
                    className="mt-1 bg-slate-950 border-slate-700"
                    required
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Provincia *</Label>
                  <Input
                    value={form.provincia}
                    onChange={(e) =>
                      setForm({ ...form, provincia: e.target.value.toUpperCase() })
                    }
                    className="mt-1 bg-slate-950 border-slate-700"
                    maxLength={2}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-300">Telefono</Label>
                  <Input
                    value={form.telefono}
                    onChange={(e) =>
                      setForm({ ...form, telefono: e.target.value })
                    }
                    className="mt-1 bg-slate-950 border-slate-700"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Email</Label>
                  <Input
                    type="email"
                    value={form.email}
                    onChange={(e) =>
                      setForm({ ...form, email: e.target.value })
                    }
                    className="mt-1 bg-slate-950 border-slate-700"
                  />
                </div>
              </div>

              <div>
                <Label className="text-slate-300">PEC</Label>
                <Input
                  type="email"
                  value={form.pec}
                  onChange={(e) => setForm({ ...form, pec: e.target.value })}
                  className="mt-1 bg-slate-950 border-slate-700"
                />
              </div>
            </TabsContent>

            {/* Tab Fiscale */}
            <TabsContent value="fiscale" className="space-y-4 mt-4">
              <div>
                <Label className="text-slate-300">Regime Fiscale *</Label>
                <Select
                  value={form.regime_fiscale}
                  onValueChange={(v) =>
                    setForm({ ...form, regime_fiscale: v })
                  }
                >
                  <SelectTrigger className="mt-1 bg-slate-950 border-slate-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="RF01">RF01 - Ordinario</SelectItem>
                    <SelectItem value="RF19">RF19 - Forfettario</SelectItem>
                    <SelectItem value="RF02">RF02 - Contribuenti minimi</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500 mt-1">
                  {form.regime_fiscale === 'RF19'
                    ? 'Regime forfettario: operazioni senza IVA'
                    : 'Regime ordinario: IVA applicata normalmente'}
                </p>
              </div>

              <div>
                <Label className="text-slate-300">Prefisso Numerazione</Label>
                <Input
                  value={form.prefisso_numerazione}
                  onChange={(e) =>
                    setForm({ ...form, prefisso_numerazione: e.target.value })
                  }
                  className="mt-1 bg-slate-950 border-slate-700"
                  placeholder="Es: FT- (opzionale)"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Esempio: FT-001/2026 invece di 1/2026
                </p>
              </div>

              {form.regime_fiscale !== 'RF19' && (
                <div>
                  <Label className="text-slate-300">Aliquota IVA Default</Label>
                  <Select
                    value={form.aliquota_iva_default.toString()}
                    onValueChange={(v) =>
                      setForm({ ...form, aliquota_iva_default: parseFloat(v) })
                    }
                  >
                    <SelectTrigger className="mt-1 bg-slate-950 border-slate-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="22">22%</SelectItem>
                      <SelectItem value="10">10%</SelectItem>
                      <SelectItem value="5">5%</SelectItem>
                      <SelectItem value="4">4%</SelectItem>
                      <SelectItem value="0">0% (Esente)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              {(form.regime_fiscale === 'RF19' ||
                form.aliquota_iva_default === 0) && (
                <div>
                  <Label className="text-slate-300">Natura IVA (per esenzioni)</Label>
                  <Select
                    value={form.natura_iva_default}
                    onValueChange={(v) =>
                      setForm({ ...form, natura_iva_default: v })
                    }
                  >
                    <SelectTrigger className="mt-1 bg-slate-950 border-slate-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="N2.2">N2.2 - Non soggette (altri casi)</SelectItem>
                      <SelectItem value="N4">N4 - Esenti (art. 10)</SelectItem>
                      <SelectItem value="N1">N1 - Escluse art. 15</SelectItem>
                      <SelectItem value="N3">N3 - Non imponibili</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </TabsContent>

            {/* Tab Banca */}
            <TabsContent value="banca" className="space-y-4 mt-4">
              <div>
                <Label className="text-slate-300">IBAN</Label>
                <Input
                  value={form.iban}
                  onChange={(e) =>
                    setForm({ ...form, iban: e.target.value.toUpperCase().replace(/\s/g, '') })
                  }
                  className="mt-1 bg-slate-950 border-slate-700 font-mono"
                  placeholder="IT00X0000000000000000000000"
                  maxLength={27}
                />
              </div>

              <div>
                <Label className="text-slate-300">BIC/SWIFT</Label>
                <Input
                  value={form.bic}
                  onChange={(e) =>
                    setForm({ ...form, bic: e.target.value.toUpperCase() })
                  }
                  className="mt-1 bg-slate-950 border-slate-700 font-mono"
                  maxLength={11}
                />
              </div>

              <div>
                <Label className="text-slate-300">Nome Banca</Label>
                <Input
                  value={form.nome_banca}
                  onChange={(e) =>
                    setForm({ ...form, nome_banca: e.target.value })
                  }
                  className="mt-1 bg-slate-950 border-slate-700"
                />
              </div>

              <p className="text-xs text-slate-500">
                I dati bancari verranno inseriti automaticamente nelle fatture
                per facilitare i pagamenti tramite bonifico.
              </p>
            </TabsContent>
          </Tabs>

          <DialogFooter className="mt-6">
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
              disabled={updateImpostazioni.isPending}
              className="bg-cyan-500 hover:bg-cyan-600"
            >
              {updateImpostazioni.isPending ? 'Salvataggio...' : 'Salva'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
