// ═══════════════════════════════════════════════════════════════════
// FLUXION - VideoThumbnail (F06 Sprint B)
// Thumbnail video con badge durata + click → MediaLightbox
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';
import { Play, Video } from 'lucide-react';
import type { MediaRecord } from '../../types/media';
import { readMediaAsDataUrl } from '../../hooks/use-media';
import { MediaLightbox } from './MediaLightbox';

// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────

function formatDuration(sec: number): string {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

// ─────────────────────────────────────────────────────────────────────
// PROPS
// ─────────────────────────────────────────────────────────────────────

interface Props {
  record: MediaRecord;
  /** Tutti i record del contesto (per navigazione lightbox) */
  allRecords?: MediaRecord[];
  className?: string;
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────

export function VideoThumbnail({ record, allRecords, className = '' }: Props) {
  const [thumbSrc, setThumbSrc] = useState<string | null>(null);
  const [lightboxOpen, setLightboxOpen] = useState(false);

  useEffect(() => {
    const path = record.thumb_path ?? record.media_path;
    readMediaAsDataUrl(path, 'image/jpeg')
      .then(setThumbSrc)
      .catch(() => setThumbSrc(null));
  }, [record]);

  const records = allRecords ?? [record];
  const index = records.findIndex((r) => r.id === record.id);

  return (
    <>
      <div
        className={`relative aspect-video rounded-xl overflow-hidden bg-slate-900 cursor-pointer group ${className}`}
        onClick={() => setLightboxOpen(true)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setLightboxOpen(true); }}
        aria-label={`Video — ${record.durata_sec ? formatDuration(record.durata_sec) : ''}`}
      >
        {/* Thumbnail */}
        {thumbSrc ? (
          <img
            src={thumbSrc}
            alt="Anteprima video"
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            draggable={false}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-slate-800">
            <Video className="w-10 h-10 text-slate-600" />
          </div>
        )}

        {/* Overlay scuro on hover */}
        <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors" />

        {/* Bottone play centrale */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-14 h-14 rounded-full bg-black/60 flex items-center justify-center group-hover:bg-black/80 transition-colors">
            <Play className="w-6 h-6 text-white fill-white ml-0.5" />
          </div>
        </div>

        {/* Badge durata */}
        {record.durata_sec != null && record.durata_sec > 0 && (
          <span className="absolute bottom-2 right-2 text-xs font-mono font-semibold text-white bg-black/70 px-1.5 py-0.5 rounded">
            {formatDuration(record.durata_sec)}
          </span>
        )}

        {/* Badge tipo video */}
        <span className="absolute top-2 left-2 text-[10px] font-semibold text-white/80 bg-black/50 px-1.5 py-0.5 rounded uppercase tracking-wide">
          VIDEO
        </span>
      </div>

      {lightboxOpen && (
        <MediaLightbox
          records={records}
          initialIndex={index >= 0 ? index : 0}
          onClose={() => setLightboxOpen(false)}
        />
      )}
    </>
  );
}
