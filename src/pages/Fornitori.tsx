// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fornitori Page
// Manage suppliers and orders with CRUD operations
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useMemo } from 'react';
import { openUrl } from '@tauri-apps/plugin-opener';
import { Plus, Loader2, Package, ShoppingCart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
import { SupplierOrdersTable } from '@/components/fornitori/SupplierOrdersTable';
import { OrderDialog } from '@/components/fornitori/OrderDialog';
import { SendConfirmDialog } from '@/components/fornitori/SendConfirmDialog';
import {
  useFornitori,
  useCreateFornitore,
  useUpdateFornitore,
  useDeleteFornitore,
  useAllOrders,
  useCreateOrder,
  useUpdateOrderStatus,
  useLogInteraction,
} from '@/hooks/use-fornitori';
import type { Supplier, CreateSupplierInput, UpdateSupplierInput, SupplierOrder, CreateOrderInput } from '@/types/supplier';
import { getSupplierDisplayName } from '@/types/supplier';

export const Fornitori: FC = () => {
  // Tab state
  const [activeTab, setActiveTab] = useState('fornitori');

  // Supplier dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedFornitore, setSelectedFornitore] = useState<Supplier | undefined>();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [fornitoreToDelete, setFornitoreToDelete] = useState<Supplier | undefined>();

  // Order dialog state
  const [orderDialogOpen, setOrderDialogOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<SupplierOrder | undefined>();

  // Send confirmation dialog state
  const [sendConfirmOpen, setSendConfirmOpen] = useState(false);
  const [sendType, setSendType] = useState<'email' | 'whatsapp'>('email');
  const [orderToSend, setOrderToSend] = useState<SupplierOrder | null>(null);
  const [isSending, setIsSending] = useState(false);

  // Queries and mutations
  const { data: fornitori = [], isLoading, error } = useFornitori();
  const { data: orders = [], isLoading: ordersLoading } = useAllOrders();
  const createMutation = useCreateFornitore();
  const updateMutation = useUpdateFornitore();
  const deleteMutation = useDeleteFornitore();
  const createOrderMutation = useCreateOrder();
  const updateOrderStatusMutation = useUpdateOrderStatus();
  const logInteractionMutation = useLogInteraction();

  // Supplier name lookup for orders table
  const supplierNames = useMemo(() => {
    const names: Record<string, string> = {};
    fornitori.forEach((s) => {
      names[s.id] = s.nome;
    });
    return names;
  }, [fornitori]);

  // Supplier Handlers
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

  // Order Handlers
  const handleNewOrder = () => {
    setSelectedOrder(undefined);
    setOrderDialogOpen(true);
  };

  const handleViewOrder = (order: SupplierOrder) => {
    setSelectedOrder(order);
    setOrderDialogOpen(true);
  };

  const handleCreateOrder = async (data: CreateOrderInput) => {
    try {
      await createOrderMutation.mutateAsync(data);
      setOrderDialogOpen(false);
    } catch (error) {
      console.error('Failed to create order:', error);
    }
  };

  const handleUpdateOrderStatus = async (order: SupplierOrder, status: SupplierOrder['status']) => {
    try {
      await updateOrderStatusMutation.mutateAsync({ id: order.id, status });
    } catch (error) {
      console.error('Failed to update order status:', error);
    }
  };

  // Format order message for sending
  const formatOrderMessage = (order: SupplierOrder, supplier: Supplier): string => {
    let items: { descrizione: string; qty: number; price: number }[] = [];
    try {
      items = JSON.parse(order.items);
    } catch {
      items = [];
    }

    const itemsList = items
      .map((item, i) => `${i + 1}. ${item.descrizione} - Qtà: ${item.qty} - €${item.price.toFixed(2)}`)
      .join('\n');

    return `*ORDINE ${order.ordine_numero}*

Gentile ${supplier.nome},

Vi inviamo il seguente ordine:

${itemsList}

*TOTALE: €${order.importo_totale.toFixed(2)}*

${order.data_consegna_prevista ? `Data consegna richiesta: ${new Date(order.data_consegna_prevista).toLocaleDateString('it-IT')}` : ''}
${order.notes ? `\nNote: ${order.notes}` : ''}

Cordiali saluti,
FLUXION`;
  };

  // Communication Handlers - Show confirmation dialog first
  const handleSendEmail = (order: SupplierOrder) => {
    const supplier = fornitori.find((s) => s.id === order.supplier_id);
    if (!supplier?.email) {
      window.alert('Il fornitore non ha un indirizzo email configurato');
      return;
    }
    setOrderToSend(order);
    setSendType('email');
    setSendConfirmOpen(true);
  };

  const handleSendWhatsApp = (order: SupplierOrder) => {
    const supplier = fornitori.find((s) => s.id === order.supplier_id);
    if (!supplier?.telefono) {
      window.alert('Il fornitore non ha un numero di telefono configurato');
      return;
    }
    setOrderToSend(order);
    setSendType('whatsapp');
    setSendConfirmOpen(true);
  };

  // Actual send after confirmation
  const handleConfirmSend = async () => {
    if (!orderToSend) return;

    const supplier = fornitori.find((s) => s.id === orderToSend.supplier_id);
    if (!supplier) return;

    setIsSending(true);

    try {
      const message = formatOrderMessage(orderToSend, supplier);

      if (sendType === 'email') {
        // Parse items from order
        let items: { descrizione: string; qty: number; price: number; sku?: string }[] = [];
        try {
          items = JSON.parse(orderToSend.items);
        } catch {
          items = [];
        }

        // Send via SMTP through Voice Agent HTTP endpoint
        // CoVe 2026: Voice Agent runs on iMac (192.168.1.7)
        const response = await window.fetch('http://192.168.1.7:3002/api/supplier-orders/send-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: supplier.email,
            ordine_numero: orderToSend.ordine_numero,
            items: items.map(item => ({
              sku: item.sku || '',
              descrizione: item.descrizione,
              qty: item.qty,
              price: item.price,
            })),
            importo_totale: orderToSend.importo_totale,
            data_consegna_prevista: orderToSend.data_consegna_prevista,
            notes: orderToSend.notes || '',
          }),
        });

        const result = await response.json();
        if (!result.success) {
          throw new Error(result.error || 'Invio email fallito');
        }

        // Log interaction
        await logInteractionMutation.mutateAsync({
          supplierId: orderToSend.supplier_id,
          orderId: orderToSend.id,
          tipo: 'email',
          messaggio: `Ordine ${orderToSend.ordine_numero} inviato via email a ${supplier.email}`,
          status: 'sent',
        });
      } else {
        // WhatsApp - open wa.me URL
        const cleanPhone = (supplier.telefono || '').replace(/\D/g, '');
        const phone = cleanPhone.startsWith('39') ? cleanPhone : `39${cleanPhone}`;
        const waUrl = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
        await openUrl(waUrl);

        // Log the interaction
        await logInteractionMutation.mutateAsync({
          supplierId: orderToSend.supplier_id,
          orderId: orderToSend.id,
          tipo: 'whatsapp',
          messaggio: `Ordine ${orderToSend.ordine_numero} inviato via WhatsApp a ${supplier.telefono}`,
          status: 'sent',
        });
      }

      // Update order status to sent
      await updateOrderStatusMutation.mutateAsync({ id: orderToSend.id, status: 'sent' });

      // Close dialog and reset state
      setSendConfirmOpen(false);
      setOrderToSend(null);
    } catch (error) {
      console.error('Failed to send order:', error);
    } finally {
      setIsSending(false);
    }
  };

  // Stats
  const activeCount = fornitori.filter((f) => f.status === 'active').length;
  const totalCount = fornitori.length;
  const pendingOrdersCount = orders.filter((o) => o.status === 'sent' || o.status === 'confirmed').length;
  const draftOrdersCount = orders.filter((o) => o.status === 'draft').length;

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
          <p className="text-slate-400 text-sm">Ordini in Corso</p>
          <p className="text-2xl font-bold text-cyan-400">{pendingOrdersCount}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <p className="text-slate-400 text-sm">Bozze Ordini</p>
          <p className="text-2xl font-bold text-yellow-400">{draftOrdersCount}</p>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="flex items-center justify-between mb-4">
          <TabsList className="bg-slate-900 border border-slate-800">
            <TabsTrigger
              value="fornitori"
              className="data-[state=active]:bg-cyan-500 data-[state=active]:text-white"
            >
              <Package className="w-4 h-4 mr-2" />
              Fornitori
            </TabsTrigger>
            <TabsTrigger
              value="ordini"
              className="data-[state=active]:bg-cyan-500 data-[state=active]:text-white"
            >
              <ShoppingCart className="w-4 h-4 mr-2" />
              Ordini
              {draftOrdersCount > 0 && (
                <span className="ml-2 px-1.5 py-0.5 text-xs bg-yellow-500 text-white rounded-full">
                  {draftOrdersCount}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          {/* Context-aware action button */}
          {activeTab === 'fornitori' ? (
            <Button
              data-testid="new-fornitore"
              onClick={handleNewFornitore}
              className="bg-cyan-500 hover:bg-cyan-600 text-white"
            >
              <Plus className="w-5 h-5 mr-2" />
              Nuovo Fornitore
            </Button>
          ) : (
            <Button
              data-testid="new-order"
              onClick={handleNewOrder}
              className="bg-cyan-500 hover:bg-cyan-600 text-white"
            >
              <Plus className="w-5 h-5 mr-2" />
              Nuovo Ordine
            </Button>
          )}
        </div>

        {/* Fornitori Tab */}
        <TabsContent value="fornitori" className="mt-0">
          <FornitoriTable
            fornitori={fornitori}
            onEdit={handleEditFornitore}
            onDelete={handleDeleteFornitore}
          />
        </TabsContent>

        {/* Ordini Tab */}
        <TabsContent value="ordini" className="mt-0">
          {ordersLoading ? (
            <div className="flex items-center justify-center h-48">
              <Loader2 className="w-6 h-6 text-cyan-500 animate-spin" />
            </div>
          ) : (
            <SupplierOrdersTable
              orders={orders}
              onViewOrder={handleViewOrder}
              onSendEmail={handleSendEmail}
              onSendWhatsApp={handleSendWhatsApp}
              onUpdateStatus={handleUpdateOrderStatus}
              showSupplierName
              supplierNames={supplierNames}
            />
          )}
        </TabsContent>
      </Tabs>

      {/* Create/Edit Supplier Dialog */}
      <FornitoreDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        fornitore={selectedFornitore}
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />

      {/* Create/View Order Dialog */}
      <OrderDialog
        open={orderDialogOpen}
        onOpenChange={setOrderDialogOpen}
        order={selectedOrder}
        suppliers={fornitori}
        onSubmit={handleCreateOrder}
        onSendEmail={handleSendEmail}
        onSendWhatsApp={handleSendWhatsApp}
        isSubmitting={createOrderMutation.isPending}
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

      {/* Send Confirmation Dialog */}
      {orderToSend && (
        <SendConfirmDialog
          open={sendConfirmOpen}
          onOpenChange={(open) => {
            setSendConfirmOpen(open);
            if (!open) setOrderToSend(null);
          }}
          type={sendType}
          recipient={
            sendType === 'email'
              ? fornitori.find((s) => s.id === orderToSend.supplier_id)?.email || ''
              : fornitori.find((s) => s.id === orderToSend.supplier_id)?.telefono || ''
          }
          recipientName={supplierNames[orderToSend.supplier_id] || 'Fornitore'}
          orderNumber={orderToSend.ordine_numero}
          message={formatOrderMessage(
            orderToSend,
            fornitori.find((s) => s.id === orderToSend.supplier_id)!
          )}
          onConfirm={handleConfirmSend}
          isSending={isSending}
        />
      )}
    </div>
  );
};
