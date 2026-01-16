// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fornitori Table Component
// Displays suppliers in a sortable, searchable table
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
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Search, MoreHorizontal, Edit, Trash2, Phone, Mail, FileText } from 'lucide-react';
import type { Supplier } from '@/types/supplier';
import { SUPPLIER_STATUS_LABELS } from '@/types/supplier';

interface FornitoriTableProps {
  fornitori: Supplier[];
  onEdit: (fornitore: Supplier) => void;
  onDelete: (fornitore: Supplier) => void;
  onViewOrders?: (fornitore: Supplier) => void;
}

export const FornitoriTable: FC<FornitoriTableProps> = ({
  fornitori,
  onEdit,
  onDelete,
  onViewOrders,
}) => {
  const [search, setSearch] = useState('');

  const filteredFornitori = useMemo(() => {
    if (!search) return fornitori;

    const searchLower = search.toLowerCase();
    return fornitori.filter(
      (f) =>
        f.nome.toLowerCase().includes(searchLower) ||
        f.email?.toLowerCase().includes(searchLower) ||
        f.telefono?.includes(search) ||
        f.partita_iva?.includes(search) ||
        f.categoria?.toLowerCase().includes(searchLower)
    );
  }, [fornitori, search]);

  const getStatusBadgeVariant = (status: Supplier['status']) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'inactive':
        return 'secondary';
      case 'blocked':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <Input
          data-testid="search-fornitori"
          placeholder="Cerca fornitore..."
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
              <TableHead className="text-slate-300">Nome</TableHead>
              <TableHead className="text-slate-300">Contatti</TableHead>
              <TableHead className="text-slate-300">P.IVA</TableHead>
              <TableHead className="text-slate-300">Categoria</TableHead>
              <TableHead className="text-slate-300">Status</TableHead>
              <TableHead className="text-slate-300 w-[60px]"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredFornitori.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-slate-400 py-8">
                  {search ? 'Nessun fornitore trovato' : 'Nessun fornitore registrato'}
                </TableCell>
              </TableRow>
            ) : (
              filteredFornitori.map((fornitore) => (
                <TableRow
                  key={fornitore.id}
                  className="border-slate-800 hover:bg-slate-900/50"
                >
                  <TableCell className="font-medium text-white">
                    {fornitore.nome}
                    {fornitore.citta && (
                      <span className="block text-sm text-slate-400">{fornitore.citta}</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col gap-1">
                      {fornitore.telefono && (
                        <span className="flex items-center gap-1 text-slate-300">
                          <Phone className="h-3 w-3" />
                          {fornitore.telefono}
                        </span>
                      )}
                      {fornitore.email && (
                        <span className="flex items-center gap-1 text-slate-400 text-sm">
                          <Mail className="h-3 w-3" />
                          {fornitore.email}
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-slate-300 font-mono text-sm">
                    {fornitore.partita_iva || '-'}
                  </TableCell>
                  <TableCell className="text-slate-300">
                    {fornitore.categoria || '-'}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusBadgeVariant(fornitore.status)}>
                      {SUPPLIER_STATUS_LABELS[fornitore.status]}
                    </Badge>
                  </TableCell>
                  <TableCell>
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
                          onClick={() => onEdit(fornitore)}
                          className="text-slate-300 hover:text-white focus:text-white"
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Modifica
                        </DropdownMenuItem>
                        {onViewOrders && (
                          <DropdownMenuItem
                            onClick={() => onViewOrders(fornitore)}
                            className="text-slate-300 hover:text-white focus:text-white"
                          >
                            <FileText className="h-4 w-4 mr-2" />
                            Ordini
                          </DropdownMenuItem>
                        )}
                        <DropdownMenuItem
                          onClick={() => onDelete(fornitore)}
                          className="text-red-400 hover:text-red-300 focus:text-red-300"
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Elimina
                        </DropdownMenuItem>
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
      <div className="text-sm text-slate-400">
        {filteredFornitori.length} di {fornitori.length} fornitori
      </div>
    </div>
  );
};
