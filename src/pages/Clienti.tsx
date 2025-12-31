// ═══════════════════════════════════════════════════════════════════
// FLUXION - Clienti Page
// Manage clienti with CRUD operations
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { Plus, Loader2 } from 'lucide-react';
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
import { ClientiTable } from '@/components/clienti/ClientiTable';
import { ClienteDialog } from '@/components/clienti/ClienteDialog';
import {
  useClienti,
  useCreateCliente,
  useUpdateCliente,
  useDeleteCliente,
} from '@/hooks/use-clienti';
import type { Cliente, CreateClienteInput, UpdateClienteInput } from '@/types/cliente';
import { getClienteFullName } from '@/types/cliente';

export const Clienti: FC = () => {
  // State
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedCliente, setSelectedCliente] = useState<Cliente | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [clienteToDelete, setClienteToDelete] = useState<Cliente | undefined>();

  // Queries and mutations
  const { data: clienti = [], isLoading, error } = useClienti();
  const createMutation = useCreateCliente();
  const updateMutation = useUpdateCliente();
  const deleteMutation = useDeleteCliente();

  // Handlers
  const handleNewCliente = () => {
    setSelectedCliente(undefined);
    setDialogOpen(true);
  };

  const handleEditCliente = (cliente: Cliente) => {
    setSelectedCliente(cliente);
    setDialogOpen(true);
  };

  const handleDeleteCliente = (cliente: Cliente) => {
    setClienteToDelete(cliente);
    setDeleteDialogOpen(true);
  };

  const handleSubmit = async (data: CreateClienteInput | UpdateClienteInput) => {
    try {
      if ('id' in data) {
        // Update
        await updateMutation.mutateAsync(data as UpdateClienteInput);
      } else {
        // Create
        await createMutation.mutateAsync(data as CreateClienteInput);
      }
      setDialogOpen(false);
    } catch (error) {
      console.error('Failed to save cliente:', error);
      // Error is already handled by React Query
    }
  };

  const handleConfirmDelete = async () => {
    if (!clienteToDelete) return;

    try {
      await deleteMutation.mutateAsync(clienteToDelete.id);
      setDeleteDialogOpen(false);
      setClienteToDelete(undefined);
    } catch (error) {
      console.error('Failed to delete cliente:', error);
    }
  };

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
        <h1 className="text-3xl font-bold text-white">Clienti</h1>
        <div className="bg-red-900/20 border border-red-800 rounded-lg p-6">
          <p className="text-red-400">
            Errore nel caricamento dei clienti: {error instanceof Error ? error.message : 'Unknown error'}
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
          <h1 className="text-3xl font-bold text-white">Clienti</h1>
          <p className="text-slate-400 mt-1">
            {clienti.length} {clienti.length === 1 ? 'cliente' : 'clienti'} totali
          </p>
        </div>
        <Button
          onClick={handleNewCliente}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          <Plus className="w-5 h-5 mr-2" />
          Nuovo Cliente
        </Button>
      </div>

      {/* Table */}
      <ClientiTable
        clienti={clienti}
        onEdit={handleEditCliente}
        onDelete={handleDeleteCliente}
      />

      {/* Create/Edit Dialog */}
      <ClienteDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        cliente={selectedCliente}
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-slate-950 border-slate-800">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-white">Elimina Cliente</AlertDialogTitle>
            <AlertDialogDescription className="text-slate-400">
              Sei sicuro di voler eliminare{' '}
              <span className="font-semibold text-white">
                {clienteToDelete && getClienteFullName(clienteToDelete)}
              </span>
              ? Questa azione non può essere annullata.
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
