// ═══════════════════════════════════════════════════════════════════
// FLUXION - MediaGallery
// Griglia thumbnail con lightbox + delete
// ═══════════════════════════════════════════════════════════════════

import { useState, useEffect } from 'react';
import { Trash2, Play, ImageOff } from 'lucide-react';
import type { MediaRecord, MediaCategoria } from '../../types/media';
import { useClienteMedia, useDeleteMedia, readMediaAsDataUrl } from '../../hooks/use-media';
import { MediaLightbox } from './MediaLightbox';
import { toast } from 'sonner';

// ─────────────────────────────────────────────────────────────────────
// Thumbnail card
// ─────────────────────────────────────────────────────────────────────

function ThumbnailCard({
  record,
  onClick,
  onDelete,
}: {
  record: MediaRecord;
  onClick: () => void;
  onDelete: () => void;
}) {
  const [src, setSrc] = useState<string | null>(null);

  useEffect(() => {
    const path = record.tipo === 'video' && record.thumb_path
      ? record.thumb_path
      : record.media_path;
    readMediaAsDataUrl(path, 'image/jpeg').then(setSrc).catch(() => setSrc(null));
  }, [record]);

  return (
    <div className="relative aspect-[4/3] rounded-lg overflow-hidden bg-card group cursor-pointer hover:scale-[1.03] transition-transform">
      <div onClick={onClick} className="absolute inset-0">
        {src ? (
          <img
            src={src}
            alt={record.categoria}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-muted">
            <ImageOff className="w-6 h-6 text-muted-foreground" />
          </div>
        )}
      </div>

      {/* Video play icon */}
      {record.tipo === 'video' && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-10 h-10 rounded-full bg-black/60 flex items-center justify-center">
            <Play className="w-5 h-5 text-white fill-white" />
          </div>
        </div>
      )}

      {/* Hover overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-2 justify-between">
        <span className="text-white text-[10px] truncate max-w-[80%]">
          {new Date(record.created_at).toLocaleDateString('it-IT', { day: '2-digit', month: 'short' })}
        </span>
        <button
          type="button"
          onClick={(e) => { e.stopPropagation(); onDelete(); }}
          className="text-white/70 hover:text-red-400 transition-colors"
          aria-label="Elimina"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────

interface Props {
  clienteId: number;
  tipo?: string;
  categoria?: MediaCategoria;
  emptyMessage?: string;
  className?: string;
  /** Se fornito, sovrascrive il comportamento lightbox: viene chiamato con il record cliccato */
  onRecordClick?: (record: MediaRecord, index: number) => void;
}

export function MediaGallery({ clienteId, tipo, categoria, emptyMessage, className = '', onRecordClick }: Props) {
  const { data: records = [], isLoading } = useClienteMedia(clienteId, tipo, categoria);
  const deleteMedia = useDeleteMedia(clienteId);
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  const handleDelete = async (mediaId: number) => {
    try {
      await deleteMedia.mutateAsync(mediaId);
      toast.success('File eliminato');
    } catch {
      toast.error('Errore durante l\'eliminazione');
    }
  };

  if (isLoading) {
    return (
      <div className={`grid grid-cols-3 gap-2 ${className}`}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="aspect-[4/3] rounded-lg bg-muted animate-pulse" />
        ))}
      </div>
    );
  }

  if (records.length === 0) {
    return (
      <div className={`text-center py-8 text-muted-foreground text-sm ${className}`}>
        {emptyMessage ?? 'Nessun file caricato'}
      </div>
    );
  }

  return (
    <>
      <div className={`grid grid-cols-3 gap-2 ${className}`}>
        {records.map((r, i) => (
          <ThumbnailCard
            key={r.id}
            record={r}
            onClick={() => onRecordClick ? onRecordClick(r, i) : setLightboxIndex(i)}
            onDelete={() => handleDelete(r.id)}
          />
        ))}
      </div>

      {lightboxIndex !== null && (
        <MediaLightbox
          records={records}
          initialIndex={lightboxIndex}
          onClose={() => setLightboxIndex(null)}
        />
      )}
    </>
  );
}
