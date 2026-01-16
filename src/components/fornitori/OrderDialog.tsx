// ═══════════════════════════════════════════════════════════════════
// FLUXION - Order Dialog Component
// Create/View supplier order with dynamic line items + file import
// ═══════════════════════════════════════════════════════════════════

import { type FC, useEffect, useState, useRef } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, Plus, Trash2, Mail, MessageCircle, FileSpreadsheet } from 'lucide-react';
import type { Supplier, SupplierOrder, CreateOrderInput } from '@/types/supplier';
import { ORDER_STATUS_LABELS, formatCurrency } from '@/types/supplier';
import { useFileParser } from '@/hooks/use-file-parser';

interface OrderItem {
  sku: string;
  descrizione: string;
  qty: number;
  price: number;
}

interface OrderDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  order?: SupplierOrder;
  suppliers: Supplier[];
  selectedSupplierId?: string;
  onSubmit: (data: CreateOrderInput) => Promise<void>;
  onSendEmail?: (order: SupplierOrder) => void;
  onSendWhatsApp?: (order: SupplierOrder) => void;
  isSubmitting: boolean;
}

export const OrderDialog: FC<OrderDialogProps> = ({
  open,
  onOpenChange,
  order,
  suppliers,
  selectedSupplierId,
  onSubmit,
  onSendEmail,
  onSendWhatsApp,
  isSubmitting,
}) => {
  const isView = !!order;
  const isEditable = !order || order.status === 'draft';

  const [supplierId, setSupplierId] = useState(selectedSupplierId || '');
  const [ordineNumero, setOrdineNumero] = useState('');
  const [dataConsegna, setDataConsegna] = useState('');
  const [notes, setNotes] = useState('');
  const [items, setItems] = useState<OrderItem[]>([
    { sku: '', descrizione: '', qty: 1, price: 0 },
  ]);

  // File import state
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showColumnMapping, setShowColumnMapping] = useState(false);
  const [columnMapping, setColumnMapping] = useState({
    descrizione: '',
    price: '',
    qty: '',
    sku: '',
  });

  const fileParser = useFileParser();

  // Generate order number
  const generateOrderNumber = () => {
    const year = new Date().getFullYear();
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `ORD-${year}-${random}`;
  };

  // Reset form when dialog opens
  useEffect(() => {
    if (open) {
      if (order) {
        setSupplierId(order.supplier_id);
        setOrdineNumero(order.ordine_numero);
        setDataConsegna(order.data_consegna_prevista || '');
        setNotes(order.notes || '');
        try {
          const parsedItems = JSON.parse(order.items);
          setItems(parsedItems.length > 0 ? parsedItems : [{ sku: '', descrizione: '', qty: 1, price: 0 }]);
        } catch {
          setItems([{ sku: '', descrizione: '', qty: 1, price: 0 }]);
        }
      } else {
        setSupplierId(selectedSupplierId || '');
        setOrdineNumero(generateOrderNumber());
        setDataConsegna('');
        setNotes('');
        setItems([{ sku: '', descrizione: '', qty: 1, price: 0 }]);
      }
      // Reset file parser
      fileParser.reset();
      setShowColumnMapping(false);
    }
  }, [open, order, selectedSupplierId]);

  // Calculate total
  const total = items.reduce((sum, item) => sum + item.qty * item.price, 0);

  // Add item row
  const addItem = () => {
    setItems([...items, { sku: '', descrizione: '', qty: 1, price: 0 }]);
  };

  // Remove item row
  const removeItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  // Update item
  const updateItem = (index: number, field: keyof OrderItem, value: string | number) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  // Handle file import
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const result = await fileParser.parseFile(file);

    if (result.error) {
      return;
    }

    // Try auto-detect mapping (pass columns directly to bypass async state)
    const autoMapping = fileParser.autoDetectMapping(result.columns);

    if (autoMapping) {
      // Auto-mapping found, apply directly (pass rawData directly)
      const products = fileParser.mapToProducts(autoMapping, result.rawData);
      if (products.length > 0) {
        setItems(products.map((p) => ({
          sku: p.sku || '',
          descrizione: p.descrizione,
          qty: p.qty,
          price: p.price,
        })));
      }
    } else if (result.columns.length > 0) {
      // Show column mapping dialog
      setColumnMapping({
        descrizione: result.columns[0] || '',
        price: result.columns[1] || '',
        qty: '',
        sku: '',
      });
      setShowColumnMapping(true);
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Apply manual column mapping
  const applyColumnMapping = () => {
    if (!columnMapping.descrizione || !columnMapping.price) return;

    const products = fileParser.mapToProducts({
      descrizione: columnMapping.descrizione,
      price: columnMapping.price,
      qty: columnMapping.qty || undefined,
      sku: columnMapping.sku || undefined,
    });

    if (products.length > 0) {
      setItems(products.map((p) => ({
        sku: p.sku || '',
        descrizione: p.descrizione,
        qty: p.qty,
        price: p.price,
      })));
    }

    setShowColumnMapping(false);
  };

  // Handle submit
  const handleSubmit = async () => {
    if (!supplierId || !ordineNumero || items.length === 0) return;

    const validItems = items.filter((item) => item.descrizione && item.qty > 0);
    if (validItems.length === 0) return;

    await onSubmit({
      supplier_id: supplierId,
      ordine_numero: ordineNumero,
      data_consegna_prevista: dataConsegna || undefined,
      importo_totale: total,
      items: JSON.stringify(validItems),
      notes: notes || undefined,
    });
  };

  const selectedSupplier = suppliers.find((s) => s.id === supplierId);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-slate-950 border-slate-800 max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-white">
              {isView ? `Ordine ${order.ordine_numero}` : 'Nuovo Ordine'}
            </DialogTitle>
            {order && (
              <Badge
                className={`${
                  order.status === 'delivered'
                    ? 'bg-green-500'
                    : order.status === 'cancelled'
                    ? 'bg-red-500'
                    : 'bg-cyan-500'
                } text-white`}
              >
                {ORDER_STATUS_LABELS[order.status]}
              </Badge>
            )}
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Header Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-slate-300">Fornitore *</Label>
              {isEditable ? (
                <Select value={supplierId} onValueChange={setSupplierId}>
                  <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                    <SelectValue placeholder="Seleziona fornitore" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-700">
                    {suppliers
                      .filter((s) => s.status === 'active')
                      .map((supplier) => (
                        <SelectItem key={supplier.id} value={supplier.id} className="text-white">
                          {supplier.nome}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              ) : (
                <p className="text-white mt-1">{selectedSupplier?.nome || '-'}</p>
              )}
            </div>

            <div>
              <Label className="text-slate-300">N. Ordine</Label>
              <Input
                value={ordineNumero}
                onChange={(e) => setOrdineNumero(e.target.value)}
                disabled={!isEditable}
                className="bg-slate-900 border-slate-700 text-white font-mono"
              />
            </div>

            <div>
              <Label className="text-slate-300">Data Consegna Prevista</Label>
              <Input
                type="date"
                value={dataConsegna}
                onChange={(e) => setDataConsegna(e.target.value)}
                disabled={!isEditable}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>

            {selectedSupplier && (
              <div>
                <Label className="text-slate-300">Contatto</Label>
                <p className="text-white text-sm mt-1">
                  {selectedSupplier.email && <span className="block">{selectedSupplier.email}</span>}
                  {selectedSupplier.telefono && (
                    <span className="block text-slate-400">{selectedSupplier.telefono}</span>
                  )}
                </p>
              </div>
            )}
          </div>

          {/* Items */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <Label className="text-slate-300">Articoli</Label>
              {isEditable && (
                <div className="flex gap-2">
                  {/* Import from file button */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls,.csv,.docx"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={fileParser.loading}
                    className="border-purple-700 text-purple-400 hover:bg-purple-900/20"
                  >
                    {fileParser.loading ? (
                      <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                    ) : (
                      <FileSpreadsheet className="h-4 w-4 mr-1" />
                    )}
                    Importa
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={addItem}
                    className="border-slate-700 text-slate-300 hover:bg-slate-800"
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Aggiungi
                  </Button>
                </div>
              )}
            </div>

            {/* File parse error */}
            {fileParser.error && (
              <div className="mb-2 p-2 bg-red-900/20 border border-red-800 rounded text-red-400 text-sm">
                {fileParser.error}
              </div>
            )}

            {/* File import success message */}
            {fileParser.fileName && !fileParser.error && !showColumnMapping && (
              <div className="mb-2 p-2 bg-green-900/20 border border-green-800 rounded text-green-400 text-sm">
                Importato da: {fileParser.fileName} ({fileParser.rawData.length} righe)
              </div>
            )}

            {/* Column Mapping Modal */}
            {showColumnMapping && (
              <div className="mb-4 p-4 bg-slate-900 border border-slate-700 rounded-lg">
                <h4 className="text-white font-medium mb-3">Mappa Colonne</h4>
                <p className="text-slate-400 text-sm mb-3">
                  Seleziona le colonne corrispondenti dal file "{fileParser.fileName}"
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label className="text-slate-400 text-xs">Descrizione *</Label>
                    <Select value={columnMapping.descrizione} onValueChange={(v) => setColumnMapping((m) => ({ ...m, descrizione: v }))}>
                      <SelectTrigger className="bg-slate-800 border-slate-600 text-white text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-600">
                        {fileParser.columns.map((col) => (
                          <SelectItem key={col} value={col} className="text-white text-sm">
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-slate-400 text-xs">Prezzo *</Label>
                    <Select value={columnMapping.price} onValueChange={(v) => setColumnMapping((m) => ({ ...m, price: v }))}>
                      <SelectTrigger className="bg-slate-800 border-slate-600 text-white text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-600">
                        {fileParser.columns.map((col) => (
                          <SelectItem key={col} value={col} className="text-white text-sm">
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-slate-400 text-xs">Quantità</Label>
                    <Select value={columnMapping.qty || '__none__'} onValueChange={(v) => setColumnMapping((m) => ({ ...m, qty: v === '__none__' ? '' : v }))}>
                      <SelectTrigger className="bg-slate-800 border-slate-600 text-white text-sm">
                        <SelectValue placeholder="(opzionale)" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-600">
                        <SelectItem value="__none__" className="text-slate-400 text-sm">Nessuna</SelectItem>
                        {fileParser.columns.map((col) => (
                          <SelectItem key={col} value={col} className="text-white text-sm">
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-slate-400 text-xs">SKU/Codice</Label>
                    <Select value={columnMapping.sku || '__none__'} onValueChange={(v) => setColumnMapping((m) => ({ ...m, sku: v === '__none__' ? '' : v }))}>
                      <SelectTrigger className="bg-slate-800 border-slate-600 text-white text-sm">
                        <SelectValue placeholder="(opzionale)" />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-600">
                        <SelectItem value="__none__" className="text-slate-400 text-sm">Nessuna</SelectItem>
                        {fileParser.columns.map((col) => (
                          <SelectItem key={col} value={col} className="text-white text-sm">
                            {col}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="flex gap-2 mt-3">
                  <Button
                    type="button"
                    size="sm"
                    onClick={applyColumnMapping}
                    disabled={!columnMapping.descrizione || !columnMapping.price}
                    className="bg-cyan-500 hover:bg-cyan-600 text-white"
                  >
                    Applica
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setShowColumnMapping(false)}
                    className="border-slate-600 text-slate-300"
                  >
                    Annulla
                  </Button>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {/* Header */}
              <div className="grid grid-cols-12 gap-2 text-xs text-slate-400 px-1">
                <div className="col-span-2">SKU</div>
                <div className="col-span-5">Descrizione</div>
                <div className="col-span-2 text-right">Qta</div>
                <div className="col-span-2 text-right">Prezzo</div>
                <div className="col-span-1"></div>
              </div>

              {/* Rows */}
              {items.map((item, index) => (
                <div key={index} className="grid grid-cols-12 gap-2 items-center">
                  <Input
                    value={item.sku}
                    onChange={(e) => updateItem(index, 'sku', e.target.value)}
                    placeholder="SKU"
                    disabled={!isEditable}
                    className="col-span-2 bg-slate-900 border-slate-700 text-white text-sm"
                  />
                  <Input
                    value={item.descrizione}
                    onChange={(e) => updateItem(index, 'descrizione', e.target.value)}
                    placeholder="Descrizione articolo"
                    disabled={!isEditable}
                    className="col-span-5 bg-slate-900 border-slate-700 text-white text-sm"
                  />
                  <Input
                    type="number"
                    min="1"
                    value={item.qty}
                    onChange={(e) => updateItem(index, 'qty', parseInt(e.target.value) || 0)}
                    disabled={!isEditable}
                    className="col-span-2 bg-slate-900 border-slate-700 text-white text-sm text-right"
                  />
                  <Input
                    type="number"
                    min="0"
                    step="0.01"
                    value={item.price}
                    onChange={(e) => updateItem(index, 'price', parseFloat(e.target.value) || 0)}
                    disabled={!isEditable}
                    className="col-span-2 bg-slate-900 border-slate-700 text-white text-sm text-right"
                  />
                  <div className="col-span-1 flex justify-center">
                    {isEditable && items.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeItem(index)}
                        className="h-8 w-8 text-red-400 hover:text-red-300"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}

              {/* Total */}
              <div className="grid grid-cols-12 gap-2 pt-2 border-t border-slate-700">
                <div className="col-span-9 text-right text-slate-300 font-medium">Totale:</div>
                <div className="col-span-2 text-right text-white font-bold">
                  {formatCurrency(total)}
                </div>
                <div className="col-span-1"></div>
              </div>
            </div>
          </div>

          {/* Notes */}
          <div>
            <Label className="text-slate-300">Note</Label>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={!isEditable}
              placeholder="Note per il fornitore..."
              className="bg-slate-900 border-slate-700 text-white resize-none"
              rows={2}
            />
          </div>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          {/* Send buttons for draft orders */}
          {order && order.status === 'draft' && (
            <div className="flex gap-2 mr-auto">
              <Button
                type="button"
                variant="outline"
                onClick={() => onSendEmail?.(order)}
                className="border-cyan-700 text-cyan-400 hover:bg-cyan-900/20"
              >
                <Mail className="h-4 w-4 mr-2" />
                Invia Email
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => onSendWhatsApp?.(order)}
                className="border-green-700 text-green-400 hover:bg-green-900/20"
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Invia WhatsApp
              </Button>
            </div>
          )}

          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="border-slate-700 text-slate-300 hover:bg-slate-800"
          >
            {isView ? 'Chiudi' : 'Annulla'}
          </Button>

          {isEditable && !isView && (
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting || !supplierId || total === 0}
              className="bg-cyan-500 hover:bg-cyan-600 text-white"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Crea Ordine
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
