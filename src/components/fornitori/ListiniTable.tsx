// ═══════════════════════════════════════════════════════════════════
// FLUXION - Listini Table (Gap #5)
// Elenco listini importati con dettaglio righe espandibile
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { FileSpreadsheet, Trash2, ChevronDown, ChevronRight, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import type { ListinoFornitore } from '@/types/listino';
import { useListinoRighe, useDeleteListino } from '@/hooks/use-listini';

interface Props {
  fornitoreId: string;
  listini: ListinoFornitore[];
}

const FORMATO_BADGE: Record<string, string> = {
  xlsx: 'bg-green-900/40 text-green-400 border-green-800',
  xls: 'bg-green-900/40 text-green-400 border-green-800',
  csv: 'bg-blue-900/40 text-blue-400 border-blue-800',
};

export const ListiniTable: FC<Props> = ({ fornitoreId, listini }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const deleteMutation = useDeleteListino();

  const handleDelete = async () => {
    if (!deleteId) return;
    await deleteMutation.mutateAsync({ listinoId: deleteId, fornitoreId });
    setDeleteId(null);
  };

  if (listini.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-12 text-center">
        <FileSpreadsheet className="w-12 h-12 text-slate-600 mx-auto mb-3" />
        <p className="text-slate-400 font-medium">Nessun listino importato</p>
        <p className="text-slate-500 text-sm mt-1">
          Clicca "Importa Listino" per caricare il primo listino prezzi
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {listini.map((l) => (
        <ListinoRow
          key={l.id}
          listino={l}
          expanded={expandedId === l.id}
          onToggle={() => setExpandedId(expandedId === l.id ? null : l.id)}
          onDelete={() => setDeleteId(l.id)}
        />
      ))}

      <AlertDialog open={!!deleteId} onOpenChange={(o) => !o && setDeleteId(null)}>
        <AlertDialogContent className="bg-slate-950 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Elimina listino</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Tutte le righe e le variazioni di prezzo associate verranno eliminate.
              Questa azione non può essere annullata.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Annulla
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => void handleDelete()}
              disabled={deleteMutation.isPending}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              Elimina
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

// ─── Single row ───────────────────────────────────────────────────

const ListinoRow: FC<{
  listino: ListinoFornitore;
  expanded: boolean;
  onToggle: () => void;
  onDelete: () => void;
}> = ({ listino, expanded, onToggle, onDelete }) => {
  const { data: righe, isLoading } = useListinoRighe(expanded ? listino.id : '');

  const dataImport = new Date(listino.data_import).toLocaleDateString('it-IT');
  const dataValidita = listino.data_validita
    ? new Date(listino.data_validita).toLocaleDateString('it-IT')
    : null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
      {/* Header row */}
      <div className="flex items-center gap-3 p-4 hover:bg-slate-800/50 transition-colors">
        <button onClick={onToggle} className="text-slate-400 hover:text-white">
          {expanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>

        <FileSpreadsheet className="w-5 h-5 text-cyan-500 shrink-0" />

        <div className="flex-1 min-w-0">
          <p className="text-white font-medium truncate">{listino.nome_listino}</p>
          <p className="text-slate-400 text-xs">
            Importato il {dataImport}
            {dataValidita && ` · Valido fino al ${dataValidita}`}
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Badge
            variant="outline"
            className={`text-xs ${FORMATO_BADGE[listino.formato_fonte] ?? 'border-slate-700 text-slate-400'}`}
          >
            .{listino.formato_fonte}
          </Badge>
          <div className="text-right">
            <p className="text-white text-sm font-medium">{listino.righe_totali}</p>
            <p className="text-slate-500 text-xs">righe</p>
          </div>
          {listino.righe_aggiornate > 0 && (
            <div className="text-right">
              <p className="text-cyan-400 text-sm font-medium flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                {listino.righe_aggiornate}
              </p>
              <p className="text-slate-500 text-xs">aggiornati</p>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="text-slate-500 hover:text-red-400 hover:bg-red-900/20 h-8 w-8"
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Expanded: righe */}
      {expanded && (
        <div className="border-t border-slate-800">
          {isLoading ? (
            <div className="p-6 text-center text-slate-400 text-sm">Caricamento righe...</div>
          ) : (
            <ScrollArea className="max-h-72">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-800 bg-slate-950">
                    <th className="px-3 py-2 text-left text-slate-400">Codice</th>
                    <th className="px-3 py-2 text-left text-slate-400">Descrizione</th>
                    <th className="px-3 py-2 text-left text-slate-400">Categoria</th>
                    <th className="px-3 py-2 text-right text-slate-400">P. Acquisto</th>
                    <th className="px-3 py-2 text-right text-slate-400">Sconto</th>
                    <th className="px-3 py-2 text-right text-slate-400">P. Netto</th>
                    <th className="px-3 py-2 text-center text-slate-400">IVA</th>
                    <th className="px-3 py-2 text-center text-slate-400">UM</th>
                  </tr>
                </thead>
                <tbody>
                  {(righe ?? []).map((r) => (
                    <tr key={r.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                      <td className="px-3 py-2 text-slate-400 font-mono">{r.codice_articolo ?? '—'}</td>
                      <td className="px-3 py-2 text-white max-w-[200px] truncate">{r.descrizione}</td>
                      <td className="px-3 py-2 text-slate-400">{r.categoria ?? '—'}</td>
                      <td className="px-3 py-2 text-right text-white">€{r.prezzo_acquisto.toFixed(2)}</td>
                      <td className="px-3 py-2 text-right text-slate-400">
                        {r.sconto_pct > 0 ? `${r.sconto_pct}%` : '—'}
                      </td>
                      <td className="px-3 py-2 text-right text-cyan-400">
                        {r.prezzo_netto != null ? `€${r.prezzo_netto.toFixed(2)}` : '—'}
                      </td>
                      <td className="px-3 py-2 text-center text-slate-400">{r.iva_pct}%</td>
                      <td className="px-3 py-2 text-center text-slate-400">{r.unita_misura}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </ScrollArea>
          )}
        </div>
      )}
    </div>
  );
};
