// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fornitori Page
// Manage suppliers with CRUD operations
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { Plus, Loader2, Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
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
import { FornitoriTable } from '@/components/fornitori/FornitoriTable';
import { FornitoreDialog } from '@/components/fornitori/FornitoreDialog';
import {
  useFornitori,
  useCreateFornitore,
  useUpdateFornitore,
  useDeleteFornitore,
} from '@/hooks/use-fornitori';
import type { Supplier, CreateSupplierInput, UpdateSupplierInput } from '@/types/supplier';
import { getSupplierDisplayName } from '@/types/supplier';

export const Fornitori: FC = () => {
  // State
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedFornitore, setSelectedFornitore] = useState<Supplier | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fornitoreToDelete, setFornitoreToDelete] = useState<Supplier | undefined>();

  // Queries and mutations
  const { data: fornitori = [], isLoading, error } = useFornitori();
  const createMutation = useCreateFornitore();
  const updateMutation = useUpdateFornitore();
  const deleteMutation = useDeleteFornitore();

  // Handlers
  const handleNewFornitore = () => {
    setSelectedFornitore(undefined);
    setDialogOpen(true);
  };

  const handleEditFornitore = (fornitore: Supplier) => {
    setSelectedFornitore(fornitore);
    setDialogOpen(true);
  };

  const handleDeleteFornitore = (fornitore: Supplier) => {
    setFornitoreToDelete(fornitore);
    setDeleteDialogOpen(true);
  };

  const handleSubmit = async (data: CreateSupplierInput | UpdateSupplierInput) => {
    try {
      if ('id' in data) {
        await updateMutation.mutateAsync(data as UpdateSupplierInput);
      } else {
        await createMutation.mutateAsync(data as CreateSupplierInput);
      }
      setDialogOpen(false);
    } catch (error) {
      console.error('Failed to save fornitore:', error);
    }
  };

  const handleConfirmDelete = async () => {
    if (!fornitoreToDelete) return;

    try {
      await deleteMutation.mutateAsync(fornitoreToDelete.id);
      setDeleteDialogOpen(false);
      setFornitoreToDelete(undefined);
    } catch (error) {
      console.error('Failed to delete fornitore:', error);
    }
  };

  // Stats
  const activeCount = fornitori.filter((f) => f.status === 'active').length;
  const totalCount = fornitori.length;

  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-white">Fornitori</h1>
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
          <p className="text-red-400">
            Errore nel caricamento dei fornitori:{' '}
            {error instanceof Error ? error.message : 'Errore sconosciuto'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Package className="w-8 h-8 text-cyan-500" />
            Fornitori
          </h1>
          <p className="text-slate-400 mt-1">
            {activeCount} attivi su {totalCount} totali
          </p>
        </div>
        <Button
          data-testid="new-fornitore"
          onClick={handleNewFornitore}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          <Plus className="w-5 h-5 mr-2" />
          Nuovo Fornitore
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <p className="text-slate-400 text-sm">Totale Fornitori</p>
          <p className="text-2xl font-bold text-white">{totalCount}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <p className="text-slate-400 text-sm">Attivi</p>
          <p className="text-2xl font-bold text-green-400">{activeCount}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <p className="text-slate-400 text-sm">Inattivi</p>
          <p className="text-2xl font-bold text-yellow-400">
            {fornitori.filter((f) => f.status === 'inactive').length}
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <p className="text-slate-400 text-sm">Bloccati</p>
          <p className="text-2xl font-bold text-red-400">
            {fornitori.filter((f) => f.status === 'blocked').length}
          </p>
        </div>
      </div>

      {/* Table */}
      <FornitoriTable
        fornitori={fornitori}
        onEdit={handleEditFornitore}
        onDelete={handleDeleteFornitore}
      />

      {/* Create/Edit Dialog */}
      <FornitoreDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        fornitore={selectedFornitore}
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-slate-950 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Elimina Fornitore</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Sei sicuro di voler eliminare{' '}
              <span className="font-semibold text-white">
                {fornitoreToDelete && getSupplierDisplayName(fornitoreToDelete)}
              </span>
              ? Questa azione non puo essere annullata.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Annulla
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              disabled={deleteMutation.isPending}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {deleteMutation.isPending ? 'Eliminazione...' : 'Elimina'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};
