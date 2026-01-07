// ═══════════════════════════════════════════════════════════════════
// FLUXION - Pagina Cassa
// Registrazione incassi + report giornaliero
// ═══════════════════════════════════════════════════════════════════

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  useIncassiOggi,
  useMetodiPagamento,
  useRegistraIncasso,
  useEliminaIncasso,
  useChiudiCassa,
  useCassaChiusa,
  useDataOggi,
} from '@/hooks/use-cassa';
import {
  formatImporto,
  getMetodoIcon,
  getMetodoColor,
  getCategoriaLabel,
} from '@/types/cassa';
import type { CreateIncassoInput } from '@/types/cassa';

export const Cassa = () => {
  const oggi = useDataOggi();
  const cassaChiusa = useCassaChiusa(oggi);

  const { data: report, isLoading } = useIncassiOggi();
  const { data: metodi } = useMetodiPagamento();

  const [showNuovoIncasso, setShowNuovoIncasso] = useState(false);
  const [showChiusura, setShowChiusura] = useState(false);

  // Form nuovo incasso
  const [importo, setImporto] = useState('');
  const [metodo, setMetodo] = useState('contanti');
  const [descrizione, setDescrizione] = useState('');
  const [categoria, setCategoria] = useState('servizio');

  // Form chiusura
  const [fondoFinale, setFondoFinale] = useState('');
  const [noteChiusura, setNoteChiusura] = useState('');

  const registraIncasso = useRegistraIncasso();
  const eliminaIncasso = useEliminaIncasso();
  const chiudiCassa = useChiudiCassa();

  const handleRegistraIncasso = async () => {
    const input: CreateIncassoInput = {
      importo: parseFloat(importo),
      metodo_pagamento: metodo,
      descrizione: descrizione || undefined,
      categoria,
    };

    try {
      await registraIncasso.mutateAsync(input);
      // Reset form
      setImporto('');
      setDescrizione('');
      setShowNuovoIncasso(false);
    } catch (error) {
      console.error('Errore registrazione:', error);
    }
  };

  const handleChiudiCassa = async () => {
    try {
      await chiudiCassa.mutateAsync({
        data: oggi,
        fondoCassaFinale: parseFloat(fondoFinale),
        note: noteChiusura || undefined,
      });
      setShowChiusura(false);
    } catch (error) {
      console.error('Errore chiusura:', error);
    }
  };

  const handleEliminaIncasso = async (id: string) => {
    if (window.confirm('Eliminare questo incasso?')) {
      try {
        await eliminaIncasso.mutateAsync(id);
      } catch (error) {
        console.error('Errore eliminazione:', error);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Caricamento cassa...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Cassa</h1>
          <p className="text-muted-foreground">
            {new Date().toLocaleDateString('it-IT', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </p>
        </div>
        <div className="flex gap-2">
          {!cassaChiusa && (
            <>
              <Button onClick={() => setShowNuovoIncasso(true)}>
                + Registra Incasso
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowChiusura(true)}
                disabled={!report || report.numero_transazioni === 0}
              >
                Chiudi Cassa
              </Button>
            </>
          )}
          {cassaChiusa && (
            <Badge variant="secondary" className="text-lg px-4 py-2">
              Cassa Chiusa
            </Badge>
          )}
        </div>
      </div>

      {/* Riepilogo Totali */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Totale Giornata
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">
              {formatImporto(report?.totale ?? 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {report?.numero_transazioni ?? 0} transazioni
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              💵 Contanti
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-semibold text-green-600">
              {formatImporto(report?.totale_contanti ?? 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              💳 Carte
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-semibold text-blue-600">
              {formatImporto(report?.totale_carte ?? 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              📱 Satispay
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-semibold text-red-600">
              {formatImporto(report?.totale_satispay ?? 0)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              💰 Altro
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xl font-semibold text-gray-600">
              {formatImporto(report?.totale_altro ?? 0)}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista Incassi */}
      <Card>
        <CardHeader>
          <CardTitle>Incassi di Oggi</CardTitle>
        </CardHeader>
        <CardContent>
          {report?.incassi.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              Nessun incasso registrato oggi.
              <br />
              Clicca "Registra Incasso" per iniziare.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Ora</TableHead>
                  <TableHead>Importo</TableHead>
                  <TableHead>Metodo</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Descrizione</TableHead>
                  <TableHead className="text-right">Azioni</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {report?.incassi.map((incasso) => (
                  <TableRow key={incasso.id}>
                    <TableCell className="font-mono text-sm">
                      {new Date(incasso.data_incasso).toLocaleTimeString(
                        'it-IT',
                        { hour: '2-digit', minute: '2-digit' }
                      )}
                    </TableCell>
                    <TableCell className="font-semibold">
                      {formatImporto(incasso.importo)}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="secondary"
                        className={getMetodoColor(incasso.metodo_pagamento)}
                      >
                        {getMetodoIcon(incasso.metodo_pagamento)}{' '}
                        {incasso.metodo_pagamento}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {incasso.cliente_nome || (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {incasso.descrizione ||
                        incasso.servizio_nome || (
                          <span className="text-muted-foreground">
                            {getCategoriaLabel(incasso.categoria)}
                          </span>
                        )}
                    </TableCell>
                    <TableCell className="text-right">
                      {!cassaChiusa && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEliminaIncasso(incasso.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          Elimina
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Dialog Nuovo Incasso */}
      <Dialog open={showNuovoIncasso} onOpenChange={setShowNuovoIncasso}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Registra Incasso</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label htmlFor="importo">Importo (€)</Label>
              <Input
                id="importo"
                type="number"
                step="0.01"
                min="0.01"
                value={importo}
                onChange={(e) => setImporto(e.target.value)}
                placeholder="0.00"
                className="text-2xl font-bold"
                autoFocus
              />
            </div>

            <div>
              <Label htmlFor="metodo">Metodo di Pagamento</Label>
              <Select value={metodo} onValueChange={setMetodo}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {metodi?.map((m) => (
                    <SelectItem key={m.codice} value={m.codice}>
                      {m.icona} {m.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="categoria">Categoria</Label>
              <Select value={categoria} onValueChange={setCategoria}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="servizio">Servizio</SelectItem>
                  <SelectItem value="prodotto">Prodotto</SelectItem>
                  <SelectItem value="pacchetto">Pacchetto</SelectItem>
                  <SelectItem value="altro">Altro</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="descrizione">Descrizione (opzionale)</Label>
              <Input
                id="descrizione"
                value={descrizione}
                onChange={(e) => setDescrizione(e.target.value)}
                placeholder="Es: Taglio + Piega"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNuovoIncasso(false)}>
              Annulla
            </Button>
            <Button
              onClick={handleRegistraIncasso}
              disabled={!importo || parseFloat(importo) <= 0}
            >
              Registra {importo && formatImporto(parseFloat(importo))}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Dialog Chiusura Cassa */}
      <Dialog open={showChiusura} onOpenChange={setShowChiusura}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Chiusura Cassa</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Riepilogo */}
            <Card>
              <CardContent className="pt-4">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="text-muted-foreground">Totale giornata:</div>
                  <div className="font-semibold text-right">
                    {formatImporto(report?.totale ?? 0)}
                  </div>
                  <div className="text-muted-foreground">Di cui contanti:</div>
                  <div className="font-semibold text-right">
                    {formatImporto(report?.totale_contanti ?? 0)}
                  </div>
                  <div className="text-muted-foreground">Transazioni:</div>
                  <div className="font-semibold text-right">
                    {report?.numero_transazioni ?? 0}
                  </div>
                </div>
              </CardContent>
            </Card>

            <Separator />

            <div>
              <Label htmlFor="fondoFinale">Fondo Cassa Finale (€)</Label>
              <Input
                id="fondoFinale"
                type="number"
                step="0.01"
                min="0"
                value={fondoFinale}
                onChange={(e) => setFondoFinale(e.target.value)}
                placeholder="Conta i contanti in cassa"
                className="text-xl"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Conta i contanti presenti in cassa e inserisci il totale
              </p>
            </div>

            <div>
              <Label htmlFor="noteChiusura">Note (opzionale)</Label>
              <Textarea
                id="noteChiusura"
                value={noteChiusura}
                onChange={(e) => setNoteChiusura(e.target.value)}
                placeholder="Note sulla chiusura..."
                rows={2}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowChiusura(false)}>
              Annulla
            </Button>
            <Button
              onClick={handleChiudiCassa}
              disabled={!fondoFinale}
              variant="default"
            >
              Conferma Chiusura
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
