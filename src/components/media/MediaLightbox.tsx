// ═══════════════════════════════════════════════════════════════════
// FLUXION - MediaLightbox
// Overlay fullscreen navigabile con tastiera (ESC/frecce)
// ═══════════════════════════════════════════════════════════════════

import { useEffect, useState, useCallback } from 'react';
import { X, ChevronLeft, ChevronRight, Download, Calendar, HardDrive } from 'lucide-react';
import type { MediaRecord } from '../../types/media';
import { readMediaAsDataUrl } from '../../hooks/use-media';

interface Props {
  records: MediaRecord[];
  initialIndex: number;
  onClose: () => void;
}

function formatBytes(bytes: number | null): string {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('it-IT', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function MediaLightbox({ records, initialIndex, onClose }: Props) {
  const [index, setIndex] = useState(initialIndex);
  const [src, setSrc] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const current = records[index];

  const loadMedia = useCallback(async (record: MediaRecord) => {
    setLoading(true);
    setSrc(null);
    try {
      const mime = record.tipo === 'video'
        ? 'video/mp4'
        : record.media_path.endsWith('.png') ? 'image/png' : 'image/jpeg';
      const url = await readMediaAsDataUrl(record.media_path, mime);
      setSrc(url);
    } catch {
      setSrc(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (current) loadMedia(current);
  }, [current, loadMedia]);

  // Keyboard navigation
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') setIndex((i) => Math.max(0, i - 1));
      if (e.key === 'ArrowRight') setIndex((i) => Math.min(records.length - 1, i + 1));
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [records.length, onClose]);

  if (!current) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center animate-in fade-in duration-200"
      onClick={onClose}
    >
      {/* Panel — stop propagation */}
      <div
        className="relative flex max-w-6xl w-full max-h-screen"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-black/60 border border-white/10 flex items-center justify-center text-white hover:bg-black/80 transition-colors"
          aria-label="Chiudi"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Prev */}
        {index > 0 && (
          <button
            type="button"
            onClick={() => setIndex((i) => i - 1)}
            className="absolute left-2 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-black/60 border border-white/10 flex items-center justify-center text-white hover:bg-black/80 transition-colors"
            aria-label="Precedente"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        )}

        {/* Next */}
        {index < records.length - 1 && (
          <button
            type="button"
            onClick={() => setIndex((i) => i + 1)}
            className="absolute right-2 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-black/60 border border-white/10 flex items-center justify-center text-white hover:bg-black/80 transition-colors"
            aria-label="Successivo"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        )}

        {/* Image / video area */}
        <div className="flex-1 flex items-center justify-center min-h-[60vh] px-16 py-8">
          {loading ? (
            <div className="w-12 h-12 border-2 border-primary border-t-transparent rounded-full animate-spin" />
          ) : src ? (
            current.tipo === 'video' ? (
              <video
                src={src}
                controls
                autoPlay
                className="max-w-full max-h-[80vh] rounded-lg"
              />
            ) : (
              <img
                src={src}
                alt={current.categoria}
                className="max-w-full max-h-[80vh] rounded-lg object-contain"
              />
            )
          ) : (
            <div className="text-white/40 text-sm">File non disponibile</div>
          )}
        </div>

        {/* Sidebar metadati */}
        <div className="w-64 shrink-0 bg-black/60 border-l border-white/10 p-4 flex flex-col gap-4 rounded-r-xl">
          <div>
            <p className="text-white/40 text-xs uppercase tracking-wider mb-2">Informazioni</p>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-white/70">
                <Calendar className="w-3.5 h-3.5 text-primary" />
                <span>{formatDate(current.created_at)}</span>
              </div>
              <div className="flex items-center gap-2 text-white/70">
                <HardDrive className="w-3.5 h-3.5 text-primary" />
                <span>{formatBytes(current.dimensione_bytes)}</span>
              </div>
              {current.larghezza_px && (
                <div className="text-white/50 text-xs">
                  {current.larghezza_px} × {current.altezza_px} px
                </div>
              )}
            </div>
          </div>

          <div>
            <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Categoria</p>
            <p className="text-white/70 text-sm capitalize">
              {current.categoria.replace(/_/g, ' ')}
            </p>
          </div>

          {current.note && (
            <div>
              <p className="text-white/40 text-xs uppercase tracking-wider mb-1">Note</p>
              <p className="text-white/70 text-sm">{current.note}</p>
            </div>
          )}

          {src && current.tipo === 'foto' && (
            <a
              href={src}
              download={`fluxion-media-${current.id}.jpg`}
              className="mt-auto flex items-center gap-2 text-sm text-primary/80 hover:text-primary transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              Download
            </a>
          )}

          <p className="text-white/30 text-xs text-center">
            {index + 1} / {records.length}
          </p>
        </div>
      </div>
    </div>
  );
}
