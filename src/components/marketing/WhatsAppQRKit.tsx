// ═══════════════════════════════════════════════════════════════════
// FLUXION - WhatsApp QR Kit (Semplificato)
// Un solo QR "Contattaci su WhatsApp"
// ═══════════════════════════════════════════════════════════════════

import { useState, useRef, useEffect } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'
import { openUrl } from '@tauri-apps/plugin-opener'
import { useSetupConfig } from '@/hooks/use-setup'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  MessageCircle,
  Copy,
  Check,
  Smartphone,
  Printer,
} from 'lucide-react'

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export function WhatsAppQRKit() {
  // Load config from settings
  const { data: config } = useSetupConfig()

  // State - initialized with config values when available
  const [phoneNumber, setPhoneNumber] = useState('393281536308')
  const [message, setMessage] = useState('Ciao! Vorrei informazioni.')
  const [businessName, setBusinessName] = useState('')
  const [copied, setCopied] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const qrRef = useRef<HTMLDivElement | null>(null)

  // Update state when config loads
  useEffect(() => {
    if (config) {
      if (config.nome_attivita && config.nome_attivita !== 'La Mia Attività') {
        setBusinessName(config.nome_attivita)
      }
      if (config.telefono) {
        // Remove + and spaces from phone number
        const cleanPhone = config.telefono.replace(/[+\s]/g, '')
        setPhoneNumber(cleanPhone)
      }
    }
  }, [config])

  // Generate WhatsApp URL
  const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`

  // Copy URL to clipboard
  const copyToClipboard = async () => {
    try {
      await window.navigator.clipboard.writeText(whatsappUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      window.alert(`Copia questo link:\n\n${whatsappUrl}`)
    }
  }

  // Test link
  const testLink = async () => {
    try {
      await openUrl(whatsappUrl)
    } catch {
      window.open(whatsappUrl, '_blank')
    }
  }

  // Export PDF
  const exportPDF = async () => {
    if (!qrRef.current) return

    setIsExporting(true)
    try {
      const canvas = await html2canvas(qrRef.current, {
        scale: 2,
        backgroundColor: '#ffffff',
        useCORS: true,
        logging: false,
      })

      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
      })

      // Title
      pdf.setFontSize(28)
      pdf.setFont('helvetica', 'bold')
      pdf.text(businessName, 105, 35, { align: 'center' })

      // Subtitle
      pdf.setFontSize(18)
      pdf.setFont('helvetica', 'normal')
      pdf.text('Contattaci su WhatsApp', 105, 50, { align: 'center' })

      // QR code
      const imgData = canvas.toDataURL('image/png')
      const qrSize = 120
      const x = (210 - qrSize) / 2
      pdf.addImage(imgData, 'PNG', x, 65, qrSize, qrSize)

      // Instructions
      pdf.setFontSize(16)
      pdf.text('Scansiona con il tuo telefono', 105, 200, { align: 'center' })

      pdf.setFontSize(12)
      pdf.setTextColor(100, 100, 100)
      pdf.text('Apri la fotocamera e inquadra il QR code', 105, 210, { align: 'center' })

      // WhatsApp green circle
      pdf.setFillColor(37, 211, 102)
      pdf.circle(105, 230, 10, 'F')

      // Footer
      pdf.setFontSize(10)
      pdf.setTextColor(150, 150, 150)
      pdf.text('Generato con FLUXION', 105, 280, { align: 'center' })

      // Save PDF - viene scaricato nella cartella Downloads
      const filename = `QR-WhatsApp-${businessName.replace(/\s+/g, '-')}.pdf`
      pdf.save(filename)

      window.alert(
        `PDF "${filename}" salvato!\n\n` +
        `Controlla la cartella "Download" del tuo computer.`
      )
    } catch (error) {
      console.error('Errore export PDF:', error)
      window.alert('Errore durante l\'export del PDF')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
          <MessageCircle className="h-7 w-7 text-green-500" />
          Contattaci su WhatsApp
        </h2>
        <p className="text-slate-400 mt-1">
          Un QR code per far contattare i clienti
        </p>
      </div>

      {/* Config Card */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-base text-white">Configurazione</CardTitle>
          <CardDescription>Personalizza il tuo QR code</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Business Name */}
          <div>
            <Label htmlFor="business" className="text-slate-300">Nome Attività</Label>
            <Input
              id="business"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
              placeholder="Es: Salone Mario"
              className="mt-1 bg-slate-950 border-slate-700"
            />
          </div>

          {/* Phone */}
          <div>
            <Label htmlFor="phone" className="text-slate-300">Numero WhatsApp</Label>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-slate-500">+</span>
              <Input
                id="phone"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value.replace(/\D/g, ''))}
                placeholder="393281536308"
                className="font-mono bg-slate-950 border-slate-700"
              />
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Formato: 39 + numero (es: 393281536308)
            </p>
          </div>

          {/* Message */}
          <div>
            <Label htmlFor="message" className="text-slate-300">Messaggio Precompilato</Label>
            <Textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={2}
              className="mt-1 bg-slate-950 border-slate-700"
              placeholder="Ciao! Vorrei informazioni."
            />
          </div>
        </CardContent>
      </Card>

      {/* QR Preview Card */}
      <Card className="bg-slate-900 border-slate-800">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center">
            {/* QR Code */}
            <div
              ref={qrRef}
              className="bg-white p-6 rounded-2xl shadow-lg"
            >
              <QRCodeSVG
                value={whatsappUrl}
                size={200}
                level="H"
                includeMargin
              />
            </div>

            <p className="text-slate-400 text-sm mt-4">
              Scansiona per aprire WhatsApp
            </p>

            {/* Actions */}
            <div className="flex gap-3 mt-6">
              <Button
                variant="outline"
                onClick={testLink}
                className="border-slate-700"
              >
                <Smartphone className="h-4 w-4 mr-2" />
                Test
              </Button>

              <Button
                variant="outline"
                onClick={copyToClipboard}
                className="border-slate-700"
              >
                {copied ? (
                  <>
                    <Check className="h-4 w-4 mr-2 text-green-500" />
                    Copiato!
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4 mr-2" />
                    Copia Link
                  </>
                )}
              </Button>

              <Button
                onClick={exportPDF}
                disabled={isExporting}
                className="bg-green-600 hover:bg-green-700"
              >
                <Printer className="h-4 w-4 mr-2" />
                {isExporting ? 'Esporto...' : 'Stampa PDF'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tips */}
      <Card className="bg-green-950/30 border-green-900/50">
        <CardContent className="pt-4 text-sm text-green-200/80 space-y-2">
          <p><strong>1.</strong> Stampa il PDF in formato A4</p>
          <p><strong>2.</strong> Posiziona in reception, vetrina o bancone</p>
          <p><strong>3.</strong> I clienti scansionano → si apre WhatsApp</p>
          <p><strong>4.</strong> Tu ricevi il messaggio e rispondi</p>
        </CardContent>
      </Card>
    </div>
  )
}
