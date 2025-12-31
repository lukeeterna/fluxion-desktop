import { type FC, useState } from 'react';
import { Users, Plus, Pencil, Trash2, Loader2 } from 'lucide-react';
import { useOperatori, useDeleteOperatore } from '@/hooks/use-operatori';
import { Button } from '@/components/ui/button';
import { OperatoreDialog } from '@/components/operatori/OperatoreDialog';
import type { Operatore } from '@/types/operatore';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';

export const Operatori: FC = () => {
  const { data: operatori, isLoading, error } = useOperatori(true);
  const deleteOperatore = useDeleteOperatore();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingOperatore, setEditingOperatore] = useState<Operatore | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [operatoreToDelete, setOperatoreToDelete] = useState<Operatore | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Users className="w-8 h-8 text-cyan-500" />
          <div>
            <h1 className="text-3xl font-bold text-white">Operatori</h1>
            <p className="text-slate-400">{operatori?.length || 0} operatori attivi</p>
          </div>
        </div>
        <Button onClick={() => { setEditingOperatore(undefined); setDialogOpen(true); }} className="bg-cyan-500 hover:bg-cyan-600 text-white">
          <Plus className="w-4 h-4 mr-2" />Nuovo Operatore
        </Button>
      </div>

      {isLoading && <div className="flex items-center justify-center py-12"><Loader2 className="w-8 h-8 text-cyan-500 animate-spin" /></div>}
      {error && <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg"><p className="text-red-500">Errore: {(error as Error).message}</p></div>}

      {!isLoading && !error && operatori && operatori.length === 0 && (
        <div className="text-center py-12 bg-slate-900/50 rounded-lg border border-slate-800">
          <Users className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">Nessun operatore trovato</h3>
          <p className="text-slate-400 mb-6">Inizia aggiungendo il tuo primo operatore</p>
          <Button onClick={() => setDialogOpen(true)} className="bg-cyan-500 hover:bg-cyan-600 text-white"><Plus className="w-4 h-4 mr-2" />Crea Operatore</Button>
        </div>
      )}

      {!isLoading && !error && operatori && operatori.length > 0 && (
        <div className="bg-slate-900/50 rounded-lg border border-slate-800 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-800/50 border-b border-slate-700">
              <tr>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Operatore</th>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Ruolo</th>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Contatti</th>
                <th className="text-left p-4 text-sm font-medium text-slate-400">Colore</th>
                <th className="text-right p-4 text-sm font-medium text-slate-400">Azioni</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {operatori.map((op) => (
                <tr key={op.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="p-4"><div className="font-medium text-white">{op.nome} {op.cognome}</div></td>
                  <td className="p-4"><span className="px-2 py-1 rounded bg-slate-800 text-sm text-slate-300">{op.ruolo}</span></td>
                  <td className="p-4"><div className="text-sm text-slate-400">{op.email || '-'}<br/>{op.telefono || '-'}</div></td>
                  <td className="p-4"><div className="flex items-center gap-2"><div className="w-6 h-6 rounded border border-slate-700" style={{ backgroundColor: op.colore }} /><span className="text-sm text-slate-400">{op.colore}</span></div></td>
                  <td className="p-4"><div className="flex items-center justify-end gap-2">
                    <Button variant="ghost" size="icon" onClick={() => { setEditingOperatore(op); setDialogOpen(true); }} className="text-slate-400 hover:text-white hover:bg-slate-800"><Pencil className="w-4 h-4" /></Button>
                    <Button variant="ghost" size="icon" onClick={() => { setOperatoreToDelete(op); setDeleteDialogOpen(true); }} className="text-slate-400 hover:text-red-400 hover:bg-red-500/10"><Trash2 className="w-4 h-4" /></Button>
                  </div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <OperatoreDialog open={dialogOpen} onOpenChange={setDialogOpen} operatore={editingOperatore} onSubmit={() => { setDialogOpen(false); setEditingOperatore(undefined); }} />
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-slate-950 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Elimina Operatore</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">Sei sicuro di voler eliminare {operatoreToDelete?.nome} {operatoreToDelete?.cognome}?</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-slate-800 text-white border-slate-700 hover:bg-slate-700">Annulla</AlertDialogCancel>
            <AlertDialogAction onClick={() => { if (operatoreToDelete) { deleteOperatore.mutate(operatoreToDelete.id); setDeleteDialogOpen(false); setOperatoreToDelete(null); } }} className="bg-red-500 text-white hover:bg-red-600">Elimina</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
