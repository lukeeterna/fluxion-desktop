import { type FC, useState } from 'react';
import { useOrariLavoro, useGiorniFestivi, useDeleteOrarioLavoro, useDeleteGiornoFestivo } from '@/hooks/use-orari';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { GIORNI_SETTIMANA } from '@/types/orari';
import { OrarioDialog } from '@/components/impostazioni/OrarioDialog';
import { FestivoDialog } from '@/components/impostazioni/FestivoDialog';
import { DiagnosticsPanel } from '@/components/impostazioni/DiagnosticsPanel';
import { PacchettiAdmin } from '@/components/loyalty/PacchettiAdmin';
import { WhatsAppQRKit } from '@/components/marketing/WhatsAppQRKit';
import { RagChat } from '@/components/rag/RagChat';

export const Impostazioni: FC = () => {
  const { data: orariLavoro, isLoading: loadingOrari } = useOrariLavoro();
  const { data: festivi, isLoading: loadingFestivi } = useGiorniFestivi();
  const deleteOrario = useDeleteOrarioLavoro();
  const deleteFestivo = useDeleteGiornoFestivo();

  const [orarioDialogOpen, setOrarioDialogOpen] = useState(false);
  const [festivoDialogOpen, setFestivoDialogOpen] = useState(false);

  // Raggruppa orari per giorno settimana
  const orariPerGiorno = GIORNI_SETTIMANA.map((giorno) => {
    const orariGiorno = (orariLavoro || []).filter((o) => o.giorno_settimana === giorno.value);
    const lavoro = orariGiorno.filter((o) => o.tipo === 'lavoro');
    const pausa = orariGiorno.filter((o) => o.tipo === 'pausa');
    return { giorno, lavoro, pausa };
  });

  const handleDeleteOrario = async (id: string) => {
    if (confirm('Vuoi eliminare questo orario?')) {
      await deleteOrario.mutateAsync(id);
    }
  };

  const handleDeleteFestivo = async (id: string) => {
    if (confirm('Vuoi eliminare questa festività?')) {
      await deleteFestivo.mutateAsync(id);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white">Impostazioni</h1>
        <p className="text-slate-400">Configura orari di lavoro e festività</p>
      </div>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: Orari di Lavoro */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <Card className="p-6 bg-slate-900 border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">Orari di Lavoro</h2>
            <p className="text-sm text-slate-400">Configura apertura, chiusura e pause pranzo</p>
          </div>
          <Button
            onClick={() => setOrarioDialogOpen(true)}
            className="bg-cyan-500 hover:bg-cyan-600 text-white"
          >
            + Aggiungi Orario
          </Button>
        </div>

        {loadingOrari ? (
          <p className="text-slate-400">Caricamento orari...</p>
        ) : (
          <div className="space-y-4">
            {orariPerGiorno.map(({ giorno, lavoro, pausa }) => {
              const hasOrari = lavoro.length > 0 || pausa.length > 0;
              return (
                <div
                  key={giorno.value}
                  className={`p-4 rounded-lg border ${
                    hasOrari
                      ? 'bg-slate-950 border-slate-700'
                      : 'bg-slate-950/50 border-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-white w-32">{giorno.label}</h3>
                    <div className="flex-1 flex gap-4">
                      {/* Orari Lavoro */}
                      {lavoro.length > 0 ? (
                        <div className="flex-1">
                          <p className="text-xs text-slate-500 uppercase mb-1">Apertura</p>
                          {lavoro.map((o) => (
                            <div
                              key={o.id}
                              className="flex items-center gap-2 text-sm text-green-400"
                            >
                              <span>
                                {o.ora_inizio} - {o.ora_fine}
                              </span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteOrario(o.id)}
                                className="h-6 px-2 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                              >
                                ✕
                              </Button>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="flex-1">
                          <p className="text-sm text-slate-600 italic">Chiuso</p>
                        </div>
                      )}

                      {/* Pause */}
                      {pausa.length > 0 && (
                        <div className="flex-1">
                          <p className="text-xs text-slate-500 uppercase mb-1">Pause</p>
                          {pausa.map((p) => (
                            <div
                              key={p.id}
                              className="flex items-center gap-2 text-sm text-orange-400"
                            >
                              <span>
                                {p.ora_inizio} - {p.ora_fine}
                              </span>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeleteOrario(p.id)}
                                className="h-6 px-2 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                              >
                                ✕
                              </Button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: Festività */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <Card className="p-6 bg-slate-900 border-slate-800">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">Festività</h2>
            <p className="text-sm text-slate-400">
              Calendario festività italiane e personalizzate
            </p>
          </div>
          <Button
            onClick={() => setFestivoDialogOpen(true)}
            className="bg-purple-500 hover:bg-purple-600 text-white"
          >
            + Aggiungi Festività
          </Button>
        </div>

        {loadingFestivi ? (
          <p className="text-slate-400">Caricamento festività...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {(festivi || []).map((f) => (
              <div
                key={f.id}
                className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-between"
              >
                <div>
                  <p className="text-white font-semibold">{f.descrizione}</p>
                  <p className="text-sm text-slate-400">{f.data}</p>
                  {f.ricorrente === 1 && (
                    <span className="text-xs text-purple-400">🔁 Ricorrente</span>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteFestivo(f.id)}
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                >
                  ✕
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: Pacchetti (Fase 5) */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <PacchettiAdmin />

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: WhatsApp QR Kit (Fase 5) */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <Card className="p-6 bg-slate-900 border-slate-800">
        <WhatsAppQRKit />
      </Card>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: RAG Chat Test (Fase 7) */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <div className="pt-8 border-t border-slate-800">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          <span className="text-3xl">🤖</span> FLUXION IA
        </h2>
        <p className="text-slate-400 mb-4">
          Assistente intelligente FLUXION. Fai domande basate sulle FAQ della categoria selezionata.
        </p>
        <RagChat />
      </div>

      {/* ─────────────────────────────────────────────────────────────── */}
      {/* SEZIONE: Diagnostica & Supporto (Fluxion Care) */}
      {/* ─────────────────────────────────────────────────────────────── */}
      <div className="pt-8 border-t border-slate-800">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          <span className="text-3xl">🛠️</span> Fluxion Care
        </h2>
        <DiagnosticsPanel />
      </div>

      {/* Dialogs */}
      <OrarioDialog
        open={orarioDialogOpen}
        onOpenChange={setOrarioDialogOpen}
        onSuccess={() => setOrarioDialogOpen(false)}
      />
      <FestivoDialog
        open={festivoDialogOpen}
        onOpenChange={setFestivoDialogOpen}
        onSuccess={() => setFestivoDialogOpen(false)}
      />
    </div>
  );
};
