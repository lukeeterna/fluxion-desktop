// ═══════════════════════════════════════════════════════════════════
// FLUXION - Impostazioni (P1.0 Redesign)
// Sidebar verticale sinistra 240px + badge stato + plain language
// CoVe 2026: Linear/Notion gold standard — sidebar + 4 macro-gruppi
// ═══════════════════════════════════════════════════════════════════

import { type FC, useState, useEffect, useCallback } from 'react';
import {
  useOrariLavoro,
  useGiorniFestivi,
  useDeleteOrarioLavoro,
  useDeleteGiornoFestivo,
} from '@/hooks/use-orari';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { GIORNI_SETTIMANA } from '@/types/orari';
import { OrarioDialog } from '@/components/impostazioni/OrarioDialog';
import { FestivoDialog } from '@/components/impostazioni/FestivoDialog';
import { DiagnosticsPanel } from '@/components/impostazioni/DiagnosticsPanel';
import { SmtpSettings } from '@/components/impostazioni/SmtpSettings';
import { SdiProviderSettings } from '@/components/impostazioni/SdiProviderSettings';
import { VoiceAgentSettings } from '@/components/impostazioni/VoiceAgentSettings';
import { LicenseManager } from '@/components/license/LicenseManager';
import { PacchettiAdmin } from '@/components/loyalty/PacchettiAdmin';
import { WhatsAppQRKit } from '@/components/marketing/WhatsAppQRKit';
import { WhatsAppAutoResponder } from '@/components/whatsapp/WhatsAppAutoResponder';
import { RagChat } from '@/components/rag/RagChat';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import {
  useImpostazioniStatus,
  type SectionStatus,
  STATUS_LABELS,
} from '@/hooks/use-impostazioni-status';

// ─────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────

const SECTION_IDS = [
  'orari', 'festivita',
  'whatsapp', 'risposte-wa', 'email',
  'sara', 'ia',
  'fatturazione', 'fedelta', 'licenza', 'diagnostica',
] as const;

type SectionId = typeof SECTION_IDS[number];

const STATUS_DOT_COLOR: Record<SectionStatus, string> = {
  ok:       'bg-emerald-400',
  warning:  'bg-amber-400',
  error:    'bg-red-400',
  optional: 'bg-slate-600',
};

const STATUS_TEXT_COLOR: Record<SectionStatus, string> = {
  ok:       'text-emerald-400',
  warning:  'text-amber-400',
  error:    'text-red-400',
  optional: 'text-slate-500',
};

// ─────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────

const StatusDot: FC<{ status: SectionStatus }> = ({ status }) => (
  <span
    className={`w-2 h-2 rounded-full shrink-0 ${STATUS_DOT_COLOR[status]}`}
    title={STATUS_LABELS[status]}
    aria-label={STATUS_LABELS[status]}
  />
);

const SectionHeader: FC<{ title: string; subtitle: string; status: SectionStatus }> = ({
  title,
  subtitle,
  status,
}) => (
  <div className="flex items-start justify-between mb-4">
    <div>
      <h2 className="text-2xl font-bold text-white">{title}</h2>
      <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
    </div>
    <span
      className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 shrink-0 ml-4 ${STATUS_TEXT_COLOR[status]}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${STATUS_DOT_COLOR[status]}`} />
      {STATUS_LABELS[status]}
    </span>
  </div>
);

const SectionError: FC<{ name: string }> = ({ name }) => (
  <Card className="p-4 bg-slate-900 border-red-500/30">
    <p className="text-red-400 text-sm">
      ⚠️ Errore nel caricamento sezione "{name}". Ricarica la pagina.
    </p>
  </Card>
);

// ─────────────────────────────────────────────────────────────────
// Sidebar group definition
// ─────────────────────────────────────────────────────────────────

interface SidebarItem {
  id: SectionId;
  label: string;
  status: SectionStatus;
}
interface SidebarGroupDef {
  label: string;
  items: SidebarItem[];
}

// ─────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────

export const Impostazioni: FC = () => {
  const status = useImpostazioniStatus();
  const { data: orariLavoro, isLoading: loadingOrari } = useOrariLavoro();
  const { data: festivi, isLoading: loadingFestivi } = useGiorniFestivi();
  const deleteOrario = useDeleteOrarioLavoro();
  const deleteFestivo = useDeleteGiornoFestivo();

  const [orarioDialogOpen, setOrarioDialogOpen] = useState(false);
  const [festivoDialogOpen, setFestivoDialogOpen] = useState(false);
  const [activeSection, setActiveSection] = useState<SectionId>('orari');

  // 4 macro-gruppi sidebar (CoVe 2026: Linear pattern)
  const sidebarGroups: SidebarGroupDef[] = [
    {
      label: 'ATTIVITÀ',
      items: [
        { id: 'orari',    label: 'Orari di lavoro', status: status.orari },
        { id: 'festivita', label: 'Festività',       status: status.festivita },
      ],
    },
    {
      label: 'COMUNICAZIONE',
      items: [
        { id: 'whatsapp',    label: 'Collega WhatsApp Business',      status: status.whatsapp },
        { id: 'risposte-wa', label: 'Risposte automatiche WhatsApp',  status: status['risposte-wa'] },
        { id: 'email',       label: 'Email per le notifiche',         status: status.email },
      ],
    },
    {
      label: 'AUTOMAZIONE',
      items: [
        { id: 'sara', label: 'Sara — Receptionist AI',              status: status.sara },
        { id: 'ia',   label: 'Intelligenza artificiale FLUXION',    status: status.ia },
      ],
    },
    {
      label: 'SISTEMA',
      items: [
        { id: 'fatturazione', label: 'Fatturazione elettronica',  status: status.fatturazione },
        { id: 'fedelta',      label: 'Pacchetti fedeltà',          status: status.fedelta },
        { id: 'licenza',      label: 'Il tuo piano FLUXION',       status: status.licenza },
        { id: 'diagnostica',  label: 'Stato del sistema',          status: status.diagnostica },
      ],
    },
  ];

  // Deep link: scroll to hash on mount
  useEffect(() => {
    const hash = window.location.hash.slice(1) as SectionId;
    if (hash && (SECTION_IDS as readonly string[]).includes(hash)) {
      setTimeout(() => {
        document.getElementById(hash)?.scrollIntoView({ behavior: 'smooth' });
        setActiveSection(hash);
      }, 150);
    }
  }, []);

  // Scroll spy: IntersectionObserver — module-level SECTION_IDS (stable, no deps issue)
  useEffect(() => {
    const visibleSections = new Map<string, number>();
    const observers: IntersectionObserver[] = [];

    SECTION_IDS.forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              visibleSections.set(id, entry.intersectionRatio);
            } else {
              visibleSections.delete(id);
            }
          });

          if (visibleSections.size > 0) {
            const best = [...visibleSections.entries()].sort(
              (a, b) => b[1] - a[1],
            )[0][0] as SectionId;
            setActiveSection(best);
          }
        },
        { threshold: [0, 0.2, 0.5], rootMargin: '-5% 0px -60% 0px' },
      );

      observer.observe(el);
      observers.push(observer);
    });

    return () => observers.forEach((o) => o.disconnect());
  }, []);

  const scrollToSection = useCallback((id: SectionId) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setActiveSection(id);
    window.history.replaceState(null, '', `#${id}`);
  }, []);

  // Raggruppa orari per giorno settimana
  const orariPerGiorno = GIORNI_SETTIMANA.map((giorno) => {
    const orariGiorno = (orariLavoro ?? []).filter(
      (o) => o.giorno_settimana === giorno.value,
    );
    return {
      giorno,
      lavoro: orariGiorno.filter((o) => o.tipo === 'lavoro'),
      pausa:  orariGiorno.filter((o) => o.tipo === 'pausa'),
    };
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

  // ─────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────

  return (
    // -m-6 breaks out of MainLayout's p-6 padding; min-h-full fills container
    <div className="flex -m-6 min-h-full">

      {/* ── Sidebar ─────────────────────────────────────────────── */}
      <aside className="w-60 shrink-0 border-r border-slate-800 bg-slate-950 sticky top-0 self-start max-h-screen overflow-y-auto">
        <div className="px-4 py-4 border-b border-slate-800">
          <h1 className="text-sm font-semibold text-white tracking-tight">
            Impostazioni
          </h1>
        </div>

        <nav className="py-2" aria-label="Sezioni impostazioni">
          {sidebarGroups.map((group) => (
            <div key={group.label} className="mb-1">
              <p className="px-4 pt-4 pb-1 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                {group.label}
              </p>
              {group.items.map((item) => {
                const isActive = activeSection === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => scrollToSection(item.id)}
                    className={`w-full flex items-center gap-2.5 px-4 py-2 text-left text-sm transition-colors ${
                      isActive
                        ? 'bg-slate-800 text-white font-medium'
                        : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                    }`}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    <StatusDot status={item.status} />
                    <span className="flex-1 leading-snug">{item.label}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
      </aside>

      {/* ── Main Content ─────────────────────────────────────────── */}
      <div className="flex-1 p-8 min-w-0 space-y-12">

        {/* ── Orari di lavoro ───────────────────────────────────── */}
        <section id="orari">
          <SectionHeader
            title="Orari di lavoro"
            subtitle="Configura apertura, chiusura e pause pranzo"
            status={status.orari}
          />
          <Card className="p-6 bg-slate-900 border-slate-800">
            <div className="flex justify-end mb-6">
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
                        <h3 className="text-lg font-semibold text-white w-32">
                          {giorno.label}
                        </h3>
                        <div className="flex-1 flex gap-4">
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
        </section>

        {/* ── Festività ─────────────────────────────────────────── */}
        <section id="festivita">
          <SectionHeader
            title="Festività"
            subtitle="Calendario festività italiane e personalizzate"
            status={status.festivita}
          />
          <Card className="p-6 bg-slate-900 border-slate-800">
            <div className="flex justify-end mb-6">
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
                {(festivi ?? []).map((f) => (
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
        </section>

        {/* ── Collega WhatsApp Business ──────────────────────────── */}
        <section id="whatsapp">
          <SectionHeader
            title="Collega WhatsApp Business"
            subtitle="Scansiona il QR code per collegare il tuo numero WhatsApp"
            status={status.whatsapp}
          />
          <ErrorBoundary fallback={<SectionError name="Collega WhatsApp Business" />}>
            <Card className="p-6 bg-slate-900 border-slate-800">
              <WhatsAppQRKit />
            </Card>
          </ErrorBoundary>
        </section>

        {/* ── Risposte automatiche WhatsApp ─────────────────────── */}
        <section id="risposte-wa">
          <SectionHeader
            title="Risposte automatiche WhatsApp"
            subtitle="Configura i messaggi automatici inviati ai clienti"
            status={status['risposte-wa']}
          />
          <ErrorBoundary fallback={<SectionError name="Risposte automatiche WhatsApp" />}>
            <WhatsAppAutoResponder />
          </ErrorBoundary>
        </section>

        {/* ── Email per le notifiche ─────────────────────────────── */}
        <section id="email">
          <SectionHeader
            title="Email per le notifiche"
            subtitle="Configura l'indirizzo email per inviare notifiche ai clienti"
            status={status.email}
          />
          <ErrorBoundary fallback={<SectionError name="Email per le notifiche" />}>
            <SmtpSettings />
          </ErrorBoundary>
        </section>

        {/* ── Sara — Receptionist AI ────────────────────────────── */}
        <section id="sara">
          <SectionHeader
            title="Sara — Receptionist AI"
            subtitle="La receptionist virtuale che gestisce le prenotazioni 24/7"
            status={status.sara}
          />
          <ErrorBoundary fallback={<SectionError name="Sara — Receptionist AI" />}>
            <VoiceAgentSettings />
          </ErrorBoundary>
        </section>

        {/* ── Intelligenza artificiale FLUXION ──────────────────── */}
        <section id="ia">
          <SectionHeader
            title="Intelligenza artificiale FLUXION"
            subtitle="Assistente intelligente per domande sulle FAQ della tua categoria"
            status={status.ia}
          />
          <ErrorBoundary fallback={<SectionError name="Intelligenza artificiale FLUXION" />}>
            <RagChat />
          </ErrorBoundary>
        </section>

        {/* ── Fatturazione elettronica ──────────────────────────── */}
        <section id="fatturazione">
          <SectionHeader
            title="Fatturazione elettronica"
            subtitle="Configura il provider SDI per l'invio delle fatture elettroniche"
            status={status.fatturazione}
          />
          <ErrorBoundary fallback={<SectionError name="Fatturazione elettronica" />}>
            <SdiProviderSettings />
          </ErrorBoundary>
        </section>

        {/* ── Pacchetti fedeltà ─────────────────────────────────── */}
        <section id="fedelta">
          <SectionHeader
            title="Pacchetti fedeltà"
            subtitle="Gestisci i pacchetti e i premi per i tuoi clienti fedeli"
            status={status.fedelta}
          />
          <ErrorBoundary fallback={<SectionError name="Pacchetti fedeltà" />}>
            <PacchettiAdmin />
          </ErrorBoundary>
        </section>

        {/* ── Il tuo piano FLUXION ──────────────────────────────── */}
        <section id="licenza">
          <SectionHeader
            title="Il tuo piano FLUXION"
            subtitle="Gestisci la tua licenza e i dettagli del piano attivo"
            status={status.licenza}
          />
          <ErrorBoundary fallback={<SectionError name="Il tuo piano FLUXION" />}>
            <LicenseManager />
          </ErrorBoundary>
        </section>

        {/* ── Stato del sistema ─────────────────────────────────── */}
        <section id="diagnostica">
          <SectionHeader
            title="Stato del sistema"
            subtitle="Monitora la salute del sistema e accedi al supporto"
            status={status.diagnostica}
          />
          <ErrorBoundary fallback={<SectionError name="Stato del sistema" />}>
            <DiagnosticsPanel />
          </ErrorBoundary>
        </section>

      </div>

      {/* ── Dialogs ──────────────────────────────────────────────── */}
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
