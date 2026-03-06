// ═══════════════════════════════════════════════════════════════════
// FLUXION - ProgressTimeline (F06 Sprint B)
// Timeline cronologica foto progress per SchedaFitness
// newest-on-top, metriche affiancate, click → lightbox
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';
import { Camera, TrendingUp, ImageOff } from 'lucide-react';
import type { MediaRecord } from '../../types/media';
import { useClienteMedia, readMediaAsDataUrl } from '../../hooks/use-media';
import { MediaLightbox } from './MediaLightbox';
import { MediaUploadZone } from './MediaUploadZone';

// ─────────────────────────────────────────────────────────────────────
// SUB: SingleEntry thumbnail
// ─────────────────────────────────────────────────────────────────────

function ProgressEntry({
  record,
  index,
  allRecords,
}: {
  record: MediaRecord;
  index: number;
  allRecords: MediaRecord[];
}) {
  const [src, setSrc] = useState<string | null>(null);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  useEffect(() => {
    const path = record.thumb_path ?? record.media_path;
    readMediaAsDataUrl(path, 'image/jpeg')
      .then(setSrc)
      .catch(() => setSrc(null));
  }, [record]);

  const date = new Date(record.created_at).toLocaleDateString('it-IT', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });

  // Estrai metriche dal campo note (formato JSON opzionale: {"peso":75,"bf":18})
  let metriche: { peso?: number; bf?: number; note?: string } = {};
  if (record.note) {
    try {
      metriche = JSON.parse(record.note);
    } catch {
      metriche = { note: record.note };
    }
  }

  return (
    <>
      <div className="flex gap-4 group">
        {/* Timeline line + dot */}
        <div className="flex flex-col items-center">
          <div className="w-3 h-3 rounded-full bg-cyan-500 border-2 border-slate-800 mt-1 z-10 flex-shrink-0" />
          <div className="w-0.5 bg-slate-700 flex-1 mt-1" />
        </div>

        {/* Content */}
        <div className="flex-1 pb-6">
          <span className="text-xs text-slate-500 mb-2 block">{date}</span>
          <div className="flex gap-3">
            {/* Thumbnail */}
            <div
              className="w-24 h-24 rounded-lg overflow-hidden bg-slate-900 flex-shrink-0 cursor-pointer group-hover:ring-2 group-hover:ring-cyan-500/50 transition-all"
              onClick={() => setLightboxOpen(true)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === 'Enter') setLightboxOpen(true); }}
              aria-label="Apri foto progress"
            >
              {src ? (
                <img
                  src={src}
                  alt={`Progress ${date}`}
                  className="w-full h-full object-cover hover:scale-105 transition-transform"
                  draggable={false}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <ImageOff className="w-5 h-5 text-slate-600" />
                </div>
              )}
            </div>

            {/* Metriche */}
            <div className="flex flex-col gap-1.5 justify-center">
              {metriche.peso != null && (
                <div className="flex items-baseline gap-1">
                  <span className="text-xs text-slate-500">Peso</span>
                  <span className="text-sm font-semibold text-white">{metriche.peso} kg</span>
                </div>
              )}
              {metriche.bf != null && (
                <div className="flex items-baseline gap-1">
                  <span className="text-xs text-slate-500">Grasso</span>
                  <span className="text-sm font-semibold text-cyan-400">{metriche.bf}%</span>
                </div>
              )}
              {metriche.note && (
                <p className="text-xs text-slate-400 max-w-xs">{metriche.note}</p>
              )}
              {!metriche.peso && !metriche.bf && !metriche.note && (
                <p className="text-xs text-slate-600 italic">Nessuna metrica registrata</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {lightboxOpen && (
        <MediaLightbox
          records={allRecords}
          initialIndex={index}
          onClose={() => setLightboxOpen(false)}
        />
      )}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT: ProgressTimeline
// ─────────────────────────────────────────────────────────────────────

interface Props {
  clienteId: number;
  className?: string;
}

export function ProgressTimeline({ clienteId, className = '' }: Props) {
  const { data: records = [], isLoading } = useClienteMedia(clienteId, 'foto', 'progress');

  // newest-on-top
  const sorted = [...records].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
  );

  if (isLoading) {
    return (
      <div className={`space-y-4 ${className}`}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-4">
            <div className="w-3 h-3 rounded-full bg-slate-700 mt-1" />
            <div className="flex-1 h-24 rounded-lg bg-slate-800 animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Upload zone */}
      <div className="mb-6">
        <MediaUploadZone
          clienteId={clienteId}
          categoria="progress"
          consensoGdpr
          label="Aggiungi foto progress"
        />
      </div>

      {/* Timeline */}
      {sorted.length === 0 ? (
        <div className="text-center py-10 text-slate-500">
          <TrendingUp className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm">Nessuna foto progress ancora</p>
          <p className="text-xs text-slate-600 mt-1">
            Carica la prima foto per iniziare la timeline
          </p>
        </div>
      ) : (
        <div className="mt-4">
          <div className="flex items-center gap-2 mb-4">
            <Camera className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-medium text-white">{sorted.length} foto</span>
          </div>
          {sorted.map((record, idx) => (
            <ProgressEntry
              key={record.id}
              record={record}
              index={idx}
              allRecords={sorted}
            />
          ))}
        </div>
      )}
    </div>
  );
}
