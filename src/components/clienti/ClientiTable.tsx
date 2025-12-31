// ═══════════════════════════════════════════════════════════════════
// FLUXION - Clienti Table
// Display clienti in a table with actions
// ═══════════════════════════════════════════════════════════════════

import { type FC } from 'react';
import { Edit, Trash2, Phone, Mail } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Cliente } from '@/types/cliente';
import { getClienteFullName, getClienteFormattedPhone } from '@/types/cliente';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface ClientiTableProps {
  clienti: Cliente[];
  onEdit: (cliente: Cliente) => void;
  onDelete: (cliente: Cliente) => void;
  className?: string;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export const ClientiTable: FC<ClientiTableProps> = ({
  clienti,
  onEdit,
  onDelete,
  className,
}) => {
  if (clienti.length === 0) {
    return (
      <div className={cn('text-center py-12', className)}>
        <p className="text-slate-400 text-lg">Nessun cliente trovato</p>
        <p className="text-slate-500 text-sm mt-2">
          Inizia aggiungendo il tuo primo cliente
        </p>
      </div>
    );
  }

  return (
    <div className={cn('rounded-md border border-slate-800', className)}>
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-slate-900/50">
            <TableHead className="text-slate-300">Nome</TableHead>
            <TableHead className="text-slate-300">Telefono</TableHead>
            <TableHead className="text-slate-300">Email</TableHead>
            <TableHead className="text-slate-300">Città</TableHead>
            <TableHead className="text-slate-300 text-right">Azioni</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {clienti.map((cliente) => (
            <TableRow
              key={cliente.id}
              className="hover:bg-slate-900/30 border-slate-800"
            >
              {/* Nome */}
              <TableCell className="font-medium text-white">
                {getClienteFullName(cliente)}
              </TableCell>

              {/* Telefono */}
              <TableCell>
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4 text-slate-500" />
                  <span className="text-slate-300">
                    {getClienteFormattedPhone(cliente)}
                  </span>
                </div>
              </TableCell>

              {/* Email */}
              <TableCell>
                {cliente.email ? (
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-slate-500" />
                    <span className="text-slate-300">{cliente.email}</span>
                  </div>
                ) : (
                  <span className="text-slate-600">-</span>
                )}
              </TableCell>

              {/* Città */}
              <TableCell>
                <span className="text-slate-300">
                  {cliente.citta || '-'}
                </span>
              </TableCell>

              {/* Azioni */}
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onEdit(cliente)}
                    className="text-slate-300 hover:text-cyan-400 hover:bg-slate-800"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onDelete(cliente)}
                    className="text-slate-300 hover:text-red-400 hover:bg-slate-800"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};
