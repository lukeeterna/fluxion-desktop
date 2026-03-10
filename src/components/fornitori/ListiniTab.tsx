// ═══════════════════════════════════════════════════════════════════
// FLUXION - Listini Tab (Gap #5)
// Container per il tab listini nella pagina Fornitori
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState } from 'react';
import { Upload, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { Supplier } from '@/types/supplier';
import { useListiniFornitore } from '@/hooks/use-listini';
import { ListiniTable } from './ListiniTable';
import { ImportListinoWizard } from './ImportListinoWizard';

interface Props {
  fornitori: Supplier[];
}

export const ListiniTab: FC<Props> = ({ fornitori }) => {
  const [selectedFornitoreId, setSelectedFornitoreId] = useState<string>(
    fornitori[0]?.id ?? ''
  );
  const [wizardOpen, setWizardOpen] = useState(false);

  const selectedFornitore = fornitori.find((f) => f.id === selectedFornitoreId);
  const { data: listini = [], isLoading } = useListiniFornitore(selectedFornitoreId);

  const activeFornitori = fornitori.filter((f) => f.status === 'active');

  if (fornitori.length === 0) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-12 text-center">
        <p className="text-slate-400">Nessun fornitore presente. Aggiungi prima un fornitore.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <Select value={selectedFornitoreId} onValueChange={setSelectedFornitoreId}>
            <SelectTrigger className="bg-slate-900 border-slate-700 text-white w-72">
              <SelectValue placeholder="Seleziona fornitore..." />
            </SelectTrigger>
            <SelectContent className="bg-slate-900 border-slate-700">
              {activeFornitori.map((f) => (
                <SelectItem key={f.id} value={f.id} className="text-white">
                  {f.nome}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button
          onClick={() => setWizardOpen(true)}
          disabled={!selectedFornitoreId}
          className="bg-cyan-500 hover:bg-cyan-600 text-white"
        >
          <Upload className="w-4 h-4 mr-2" />
          Importa Listino
        </Button>
      </div>

      {/* Listini */}
      {isLoading ? (
        <div className="flex items-center justify-center h-32">
          <Loader2 className="w-6 h-6 text-cyan-500 animate-spin" />
        </div>
      ) : (
        <ListiniTable fornitoreId={selectedFornitoreId} listini={listini} />
      )}

      {/* Wizard */}
      {selectedFornitore && (
        <ImportListinoWizard
          open={wizardOpen}
          onOpenChange={setWizardOpen}
          fornitoreId={selectedFornitore.id}
          fornitoreNome={selectedFornitore.nome}
        />
      )}
    </div>
  );
};
