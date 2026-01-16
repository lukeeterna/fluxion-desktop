// ═══════════════════════════════════════════════════════════════════
// FLUXION - Supplier Orders Table Component
// Displays orders for a supplier or all orders
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Search,
  MoreHorizontal,
  Eye,
  Mail,
  MessageCircle,
  Truck,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import type { SupplierOrder } from '@/types/supplier';
import { ORDER_STATUS_LABELS, formatCurrency } from '@/types/supplier';

interface SupplierOrdersTableProps {
  orders: SupplierOrder[];
  onViewOrder?: (order: SupplierOrder) => void;
  onSendEmail?: (order: SupplierOrder) => void;
  onSendWhatsApp?: (order: SupplierOrder) => void;
  onUpdateStatus?: (order: SupplierOrder, status: SupplierOrder['status']) => void;
  showSupplierName?: boolean;
  supplierNames?: Record<string, string>;
}

const STATUS_COLORS: Record<SupplierOrder['status'], string> = {
  draft: 'bg-slate-500',
  sent: 'bg-blue-500',
  confirmed: 'bg-cyan-500',
  shipped: 'bg-purple-500',
  delivered: 'bg-green-500',
  cancelled: 'bg-red-500',
};

export const SupplierOrdersTable: FC<SupplierOrdersTableProps> = ({
  orders,
  onViewOrder,
  onSendEmail,
  onSendWhatsApp,
  onUpdateStatus,
  showSupplierName = false,
  supplierNames = {},
}) => {
  const [search, setSearch] = useState('');

  const filteredOrders = useMemo(() => {
    if (!search) return orders;
    const searchLower = search.toLowerCase();
    return orders.filter(
      (o) =>
        o.ordine_numero.toLowerCase().includes(searchLower) ||
        ORDER_STATUS_LABELS[o.status].toLowerCase().includes(searchLower)
    );
  }, [orders, search]);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getNextStatuses = (currentStatus: SupplierOrder['status']): SupplierOrder['status'][] => {
    switch (currentStatus) {
      case 'draft':
        return ['sent', 'cancelled'];
      case 'sent':
        return ['confirmed', 'cancelled'];
      case 'confirmed':
        return ['shipped', 'cancelled'];
      case 'shipped':
        return ['delivered'];
      case 'delivered':
        return [];
      case 'cancelled':
        return ['draft'];
      default:
        return [];
    }
  };

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <Input
          placeholder="Cerca ordine..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10 bg-slate-900 border-slate-700 text-white placeholder:text-slate-500"
        />
      </div>

      {/* Table */}
      <div className="rounded-lg border border-slate-800 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-slate-900/50">
              <TableHead className="text-slate-300">N. Ordine</TableHead>
              {showSupplierName && (
                <TableHead className="text-slate-300">Fornitore</TableHead>
              )}
              <TableHead className="text-slate-300">Data</TableHead>
              <TableHead className="text-slate-300">Consegna</TableHead>
              <TableHead className="text-slate-300 text-right">Importo</TableHead>
              <TableHead className="text-slate-300">Stato</TableHead>
              <TableHead className="text-slate-300 w-[60px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredOrders.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={showSupplierName ? 7 : 6}
                  className="text-center text-slate-400 py-8"
                >
                  {search ? 'Nessun ordine trovato' : 'Nessun ordine'}
                </TableCell>
              </TableRow>
            ) : (
              filteredOrders.map((order) => (
                <TableRow
                  key={order.id}
                  className="border-slate-800 hover:bg-slate-900/50 cursor-pointer"
                  onClick={() => onViewOrder?.(order)}
                >
                  <TableCell className="font-mono font-medium text-white">
                    {order.ordine_numero}
                  </TableCell>
                  {showSupplierName && (
                    <TableCell className="text-slate-300">
                      {supplierNames[order.supplier_id] || '-'}
                    </TableCell>
                  )}
                  <TableCell className="text-slate-300">
                    {formatDate(order.data_ordine)}
                  </TableCell>
                  <TableCell className="text-slate-300">
                    {formatDate(order.data_consegna_prevista)}
                  </TableCell>
                  <TableCell className="text-right font-medium text-white">
                    {formatCurrency(order.importo_totale)}
                  </TableCell>
                  <TableCell>
                    <Badge className={`${STATUS_COLORS[order.status]} text-white`}>
                      {ORDER_STATUS_LABELS[order.status]}
                    </Badge>
                  </TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-slate-400 hover:text-white"
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent
                        align="end"
                        className="bg-slate-900 border-slate-700"
                      >
                        <DropdownMenuItem
                          onClick={() => onViewOrder?.(order)}
                          className="text-slate-300 hover:text-white focus:text-white"
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          Dettagli
                        </DropdownMenuItem>

                        {order.status === 'draft' && (
                          <>
                            <DropdownMenuSeparator className="bg-slate-700" />
                            <DropdownMenuItem
                              onClick={() => onSendEmail?.(order)}
                              className="text-slate-300 hover:text-white focus:text-white"
                            >
                              <Mail className="h-4 w-4 mr-2" />
                              Invia Email
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              onClick={() => onSendWhatsApp?.(order)}
                              className="text-slate-300 hover:text-white focus:text-white"
                            >
                              <MessageCircle className="h-4 w-4 mr-2" />
                              Invia WhatsApp
                            </DropdownMenuItem>
                          </>
                        )}

                        {getNextStatuses(order.status).length > 0 && (
                          <>
                            <DropdownMenuSeparator className="bg-slate-700" />
                            {getNextStatuses(order.status).map((status) => (
                              <DropdownMenuItem
                                key={status}
                                onClick={() => onUpdateStatus?.(order, status)}
                                className="text-slate-300 hover:text-white focus:text-white"
                              >
                                {status === 'shipped' && <Truck className="h-4 w-4 mr-2" />}
                                {status === 'delivered' && <CheckCircle className="h-4 w-4 mr-2" />}
                                {status === 'cancelled' && <XCircle className="h-4 w-4 mr-2" />}
                                {status === 'sent' && <Mail className="h-4 w-4 mr-2" />}
                                {status === 'confirmed' && <CheckCircle className="h-4 w-4 mr-2" />}
                                {status === 'draft' && <Eye className="h-4 w-4 mr-2" />}
                                {ORDER_STATUS_LABELS[status]}
                              </DropdownMenuItem>
                            ))}
                          </>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Summary */}
      <div className="flex justify-between text-sm text-slate-400">
        <span>{filteredOrders.length} ordini</span>
        <span>
          Totale: {formatCurrency(filteredOrders.reduce((sum, o) => sum + o.importo_totale, 0))}
        </span>
      </div>
    </div>
  );
};
