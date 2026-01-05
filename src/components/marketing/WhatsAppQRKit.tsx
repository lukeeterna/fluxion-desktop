// ═══════════════════════════════════════════════════════════════════
// FLUXION - WhatsApp QR Kit (Fase 5)
// Genera QR code per WhatsApp: Prenota, Info, Sposta appuntamento
// ═══════════════════════════════════════════════════════════════════

import { useState, useRef } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'
import { openUrl } from '@tauri-apps/plugin-opener'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Calendar,
  MessageCircle,
  Info,
  RefreshCw,
  Download,
  Copy,
  Check,
  Settings,
  Smartphone,
} from 'lucide-react'

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface QRTemplate {
  id: string
  name: string
  icon: React.ReactNode
  description: string
  defaultMessage: string
  color: string
}

// ───────────────────────────────────────────────────────────────────
// Default Templates
// ───────────────────────────────────────────────────────────────────

const DEFAULT_TEMPLATES: QRTemplate[] = [
  {
    id: 'prenota',
    name: 'Prenota Appuntamento',
    icon: <Calendar className="h-5 w-5" />,
    description: 'Per clienti che vogliono prenotare',
    defaultMessage: 'Ciao! Vorrei prenotare un appuntamento.',
    color: 'bg-green-500',
  },
  {
    id: 'info',
    name: 'Info e Prezzi',
    icon: <Info className="h-5 w-5" />,
    description: 'Per richieste informazioni',
    defaultMessage: 'Buongiorno, vorrei info su servizi e prezzi.',
    color: 'bg-blue-500',
  },
  {
    id: 'sposta',
    name: 'Sposta Appuntamento',
    icon: <RefreshCw className="h-5 w-5" />,
    description: 'Per spostare appuntamenti esistenti',
    defaultMessage: 'Salve, devo spostare il mio appuntamento.',
    color: 'bg-amber-500',
  },
]

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export function WhatsAppQRKit() {
  // State
  const [phoneNumber, setPhoneNumber] = useState('393281536308') // Default from .env
  const [customMessages, setCustomMessages] = useState<Record<string, string>>(
    DEFAULT_TEMPLATES.reduce(
      (acc, t) => ({ ...acc, [t.id]: t.defaultMessage }),
      {}
    )
  )
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [isExporting, setIsExporting] = useState(false)
  const qrRefs = useRef<Record<string, HTMLDivElement | null>>({})

  // Generate WhatsApp URL
  const generateWhatsAppUrl = (message: string): string => {
    const encodedMessage = encodeURIComponent(message)
    return `https://wa.me/${phoneNumber}?text=${encodedMessage}`
  }

  // Copy URL to clipboard
  const copyToClipboard = async (templateId: string) => {
    const message = customMessages[templateId]
    const url = generateWhatsAppUrl(message)
    try {
      await window.navigator.clipboard.writeText(url)
      setCopiedId(templateId)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (err) {
      console.error('Errore copia:', err)
      // Fallback: mostra alert con URL
      window.alert(`Copia questo link:\n\n${url}`)
    }
  }

  // Export single QR to PDF
  const exportSinglePDF = async (template: QRTemplate) => {
    const element = qrRefs.current[template.id]
    if (!element) {
      window.alert('Errore: elemento QR non trovato')
      return
    }

    setIsExporting(true)
    try {
      const canvas = await html2canvas(element, {
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

      // Add title
      pdf.setFontSize(24)
      pdf.setFont('helvetica', 'bold')
      pdf.text(template.name, 105, 30, { align: 'center' })

      // Add description
      pdf.setFontSize(14)
      pdf.setFont('helvetica', 'normal')
      pdf.text(template.description, 105, 45, { align: 'center' })

      // Add QR code
      const imgData = canvas.toDataURL('image/png')
      const qrSize = 100
      const x = (210 - qrSize) / 2
      pdf.addImage(imgData, 'PNG', x, 60, qrSize, qrSize)

      // Add instruction text
      pdf.setFontSize(16)
      pdf.text('Scansiona con il tuo telefono', 105, 175, { align: 'center' })
      pdf.setFontSize(12)
      pdf.text('per aprire WhatsApp', 105, 185, { align: 'center' })

      // Add WhatsApp icon indicator
      pdf.setFillColor(37, 211, 102) // WhatsApp green
      pdf.circle(105, 200, 8, 'F')

      // Add footer with business info
      pdf.setFontSize(10)
      pdf.setTextColor(128, 128, 128)
      pdf.text('Generato con FLUXION', 105, 280, { align: 'center' })

      // Try to save using blob download
      const filename = `QR-WhatsApp-${template.id}.pdf`
      const pdfBlob = pdf.output('blob')
      const blobUrl = window.URL.createObjectURL(pdfBlob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(blobUrl)

      window.alert(`PDF "${filename}" salvato nella cartella Download`)
    } catch (error) {
      console.error('Error exporting PDF:', error)
      window.alert('Errore durante l\'export del PDF. Verifica la console.')
    } finally {
      setIsExporting(false)
    }
  }

  // Export all QRs to single PDF
  const exportAllPDF = async () => {
    setIsExporting(true)
    try {
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
      })

      // Title page
      pdf.setFontSize(28)
      pdf.setFont('helvetica', 'bold')
      pdf.text('QR Code WhatsApp', 105, 50, { align: 'center' })

      pdf.setFontSize(14)
      pdf.setFont('helvetica', 'normal')
      pdf.text('Kit completo per la tua attività', 105, 65, { align: 'center' })

      pdf.setFontSize(12)
      pdf.setTextColor(128, 128, 128)
      pdf.text(`Numero WhatsApp: +${phoneNumber}`, 105, 85, { align: 'center' })

      // Add each QR on a new page
      for (let i = 0; i < DEFAULT_TEMPLATES.length; i++) {
        const template = DEFAULT_TEMPLATES[i]
        const element = qrRefs.current[template.id]
        if (!element) continue

        pdf.addPage()

        // Add title
        pdf.setTextColor(0, 0, 0)
        pdf.setFontSize(24)
        pdf.setFont('helvetica', 'bold')
        pdf.text(template.name, 105, 30, { align: 'center' })

        // Add description
        pdf.setFontSize(14)
        pdf.setFont('helvetica', 'normal')
        pdf.text(template.description, 105, 45, { align: 'center' })

        // Add QR code
        const canvas = await html2canvas(element, {
          scale: 2,
          backgroundColor: '#ffffff',
          useCORS: true,
          logging: false,
        })
        const imgData = canvas.toDataURL('image/png')
        const qrSize = 100
        const x = (210 - qrSize) / 2
        pdf.addImage(imgData, 'PNG', x, 60, qrSize, qrSize)

        // Add message preview
        pdf.setFontSize(11)
        pdf.setTextColor(80, 80, 80)
        const message = customMessages[template.id]
        const lines = pdf.splitTextToSize(`"${message}"`, 150)
        pdf.text(lines, 105, 175, { align: 'center' })

        // Add instruction
        pdf.setFontSize(14)
        pdf.setTextColor(0, 0, 0)
        pdf.text('Scansiona per aprire WhatsApp', 105, 200, { align: 'center' })
      }

      // Footer on last page
      pdf.setFontSize(10)
      pdf.setTextColor(128, 128, 128)
      pdf.text('Generato con FLUXION', 105, 280, { align: 'center' })

      // Save using blob download
      const filename = 'QR-WhatsApp-Kit-Completo.pdf'
      const pdfBlob = pdf.output('blob')
      const blobUrl = window.URL.createObjectURL(pdfBlob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(blobUrl)

      window.alert(`PDF "${filename}" salvato nella cartella Download`)
    } catch (error) {
      console.error('Error exporting PDF:', error)
      window.alert('Errore durante l\'export del PDF. Verifica la console.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-fluxion-navy flex items-center gap-2">
            <MessageCircle className="h-6 w-6 text-green-500" />
            WhatsApp QR Kit
          </h2>
          <p className="text-muted-foreground">
            Genera QR code per far contattare i clienti via WhatsApp
          </p>
        </div>
        <Button
          onClick={exportAllPDF}
          disabled={isExporting}
          className="bg-green-600 hover:bg-green-700"
        >
          <Download className="h-4 w-4 mr-2" />
          {isExporting ? 'Esportando...' : 'Esporta Kit PDF'}
        </Button>
      </div>

      {/* Phone Number Config */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Configurazione
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <Label htmlFor="phone">Numero WhatsApp Business</Label>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-muted-foreground">+</span>
                <Input
                  id="phone"
                  value={phoneNumber}
                  onChange={(e) =>
                    setPhoneNumber(e.target.value.replace(/\D/g, ''))
                  }
                  placeholder="393281536308"
                  className="font-mono"
                />
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Formato internazionale senza + (es: 393281536308 per
                +39&nbsp;328&nbsp;1536308)
              </p>
            </div>
            <Button
              variant="outline"
              onClick={async () => {
                const testUrl = generateWhatsAppUrl('Test FLUXION QR Kit')
                try {
                  await openUrl(testUrl)
                } catch (err) {
                  console.error('Errore apertura URL:', err)
                  // Fallback per dev
                  window.open(testUrl, '_blank')
                }
              }}
            >
              <Smartphone className="h-4 w-4 mr-2" />
              Test Link
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* QR Templates */}
      <Tabs defaultValue="prenota" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          {DEFAULT_TEMPLATES.map((template) => (
            <TabsTrigger
              key={template.id}
              value={template.id}
              className="flex items-center gap-2"
            >
              {template.icon}
              <span className="hidden sm:inline">{template.name}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        {DEFAULT_TEMPLATES.map((template) => (
          <TabsContent key={template.id} value={template.id}>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span
                    className={`p-2 rounded-lg text-white ${template.color}`}
                  >
                    {template.icon}
                  </span>
                  {template.name}
                </CardTitle>
                <CardDescription>{template.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  {/* QR Code Preview */}
                  <div className="flex flex-col items-center">
                    <div
                      ref={(el) => { qrRefs.current[template.id] = el }}
                      className="bg-white p-6 rounded-xl shadow-lg border"
                    >
                      <QRCodeSVG
                        value={generateWhatsAppUrl(customMessages[template.id])}
                        size={200}
                        level="H"
                        includeMargin
                        imageSettings={{
                          src: '/whatsapp-icon.png',
                          x: undefined,
                          y: undefined,
                          height: 40,
                          width: 40,
                          excavate: true,
                        }}
                      />
                    </div>
                    <p className="text-sm text-muted-foreground mt-3">
                      Scansiona con la fotocamera
                    </p>

                    {/* Action buttons */}
                    <div className="flex gap-2 mt-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(template.id)}
                      >
                        {copiedId === template.id ? (
                          <>
                            <Check className="h-4 w-4 mr-1 text-green-500" />
                            Copiato!
                          </>
                        ) : (
                          <>
                            <Copy className="h-4 w-4 mr-1" />
                            Copia Link
                          </>
                        )}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => exportSinglePDF(template)}
                        disabled={isExporting}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        PDF
                      </Button>
                    </div>
                  </div>

                  {/* Message Customization */}
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor={`msg-${template.id}`}>
                        Messaggio precompilato
                      </Label>
                      <Textarea
                        id={`msg-${template.id}`}
                        value={customMessages[template.id]}
                        onChange={(e) =>
                          setCustomMessages((prev) => ({
                            ...prev,
                            [template.id]: e.target.value,
                          }))
                        }
                        rows={4}
                        className="mt-1"
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Questo testo apparirà precompilato quando il cliente
                        scansiona il QR
                      </p>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        setCustomMessages((prev) => ({
                          ...prev,
                          [template.id]: template.defaultMessage,
                        }))
                      }
                    >
                      <RefreshCw className="h-3 w-3 mr-1" />
                      Ripristina testo originale
                    </Button>

                    {/* Preview URL */}
                    <div className="p-3 bg-muted rounded-lg">
                      <p className="text-xs font-medium text-muted-foreground mb-1">
                        Link generato:
                      </p>
                      <code className="text-xs break-all">
                        {generateWhatsAppUrl(customMessages[template.id])}
                      </code>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Usage Tips */}
      <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
        <CardHeader className="pb-2">
          <CardTitle className="text-base text-green-800">
            Come usare i QR Code
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-green-700 space-y-2">
          <p>
            <strong>1.</strong> Esporta il PDF e stampalo in formato A4
          </p>
          <p>
            <strong>2.</strong> Posiziona i QR in punti visibili del tuo locale
            (reception, vetrina, tavoli)
          </p>
          <p>
            <strong>3.</strong> I clienti scansionano con la fotocamera e si apre
            WhatsApp con il messaggio precompilato
          </p>
          <p>
            <strong>4.</strong> Tu ricevi il messaggio e puoi rispondere
            direttamente
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
