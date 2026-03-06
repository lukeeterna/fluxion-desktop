// ═══════════════════════════════════════════════════════════════════
// FLUXION - MediaUploadZone
// Zona drag-drop upload foto/video con compressione canvas automatica
// ═══════════════════════════════════════════════════════════════════

import { useCallback, useRef, useState } from 'react';
import { Upload, ImagePlus, Video, X } from 'lucide-react';
import type { MediaCategoria } from '../../types/media';
import { useSaveMediaImage, useSaveMediaVideo } from '../../hooks/use-media';
import { toast } from 'sonner';

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

const MAX_IMAGE_BYTES = 5 * 1024 * 1024; // 5 MB
const MAX_VIDEO_BYTES = 50 * 1024 * 1024; // 50 MB
const MAX_VIDEO_DURATION = 30; // secondi
const COMPRESS_MAX_PX = 1200;
const COMPRESS_QUALITY = 0.85;

// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────

function fileToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // strip "data:...;base64,"
      resolve(result.split(',')[1] ?? '');
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

async function compressImage(file: File): Promise<{ base64: string; w: number; h: number }> {
  const sourceFile: File | Blob = file;
  // HEIC: notify user to convert first (Sprint B: add heic2any npm package)
  if (file.name.toLowerCase().endsWith('.heic') || file.type === 'image/heic') {
    toast.error('HEIC non supportato — converti prima in JPEG');
    throw new Error('HEIC non supportato in questa versione');
  }

  const img = await new Promise<HTMLImageElement>((resolve, reject) => {
    const i = new Image();
    i.onload = () => resolve(i);
    i.onerror = reject;
    i.src = URL.createObjectURL(sourceFile as Blob);
  });

  const ratio = Math.min(COMPRESS_MAX_PX / img.naturalWidth, COMPRESS_MAX_PX / img.naturalHeight, 1);
  const w = Math.round(img.naturalWidth * ratio);
  const h = Math.round(img.naturalHeight * ratio);

  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(img, 0, 0, w, h);

  const blob = await new Promise<Blob>((resolve) =>
    canvas.toBlob((b) => resolve(b!), 'image/jpeg', COMPRESS_QUALITY),
  );

  URL.revokeObjectURL(img.src);
  return { base64: await fileToBase64(blob), w, h };
}

async function extractVideoThumbnail(file: File): Promise<string> {
  const video = document.createElement('video');
  video.src = URL.createObjectURL(file);
  video.muted = true;
  video.playsInline = true;
  await new Promise<void>((resolve) => {
    video.addEventListener('loadeddata', () => resolve(), { once: true });
    video.load();
  });
  video.currentTime = Math.min(1, video.duration / 2);
  await new Promise<void>((resolve) =>
    video.addEventListener('seeked', () => resolve(), { once: true }),
  );

  const canvas = document.createElement('canvas');
  canvas.width = 640;
  canvas.height = Math.round(video.videoHeight * (640 / video.videoWidth));
  canvas.getContext('2d')!.drawImage(video, 0, 0, canvas.width, canvas.height);

  const blob = await new Promise<Blob>((resolve) =>
    canvas.toBlob((b) => resolve(b!), 'image/jpeg', 0.8),
  );
  URL.revokeObjectURL(video.src);
  return fileToBase64(blob);
}

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

interface Props {
  clienteId: number;
  categoria?: MediaCategoria;
  consensoGdpr?: boolean;
  onUploaded?: () => void;
  acceptVideo?: boolean;
  label?: string;
  className?: string;
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────

export function MediaUploadZone({
  clienteId,
  categoria = 'generale',
  consensoGdpr = false,
  onUploaded,
  acceptVideo = false,
  label,
  className = '',
}: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const saveImage = useSaveMediaImage(clienteId);
  const saveVideo = useSaveMediaVideo(clienteId);

  const processFile = useCallback(
    async (file: File) => {
      setError(null);
      setUploading(true);

      try {
        const isVideo = file.type.startsWith('video/');

        if (isVideo) {
          if (file.size > MAX_VIDEO_BYTES) {
            setError(`File troppo grande (${(file.size / 1024 / 1024).toFixed(1)}MB > 50MB)`);
            return;
          }

          setProgress('Generazione anteprima...');
          const video = document.createElement('video');
          video.src = URL.createObjectURL(file);
          await new Promise<void>((r) => video.addEventListener('loadedmetadata', () => r(), { once: true }));
          if (video.duration > MAX_VIDEO_DURATION) {
            URL.revokeObjectURL(video.src);
            setError(`Video troppo lungo (${Math.round(video.duration)}s > 30s)`);
            return;
          }
          const durataSec = Math.round(video.duration);
          URL.revokeObjectURL(video.src);

          const thumbBase64 = await extractVideoThumbnail(file);
          setProgress('Salvataggio video...');
          const videoBase64 = await fileToBase64(file);

          await saveVideo.mutateAsync({
            cliente_id: clienteId,
            video_base64: videoBase64,
            thumb_base64: thumbBase64,
            original_name: file.name,
            durata_sec: durataSec,
            categoria,
          });
          toast.success('Video salvato');
        } else {
          if (file.size > MAX_IMAGE_BYTES) {
            setError(`File troppo grande (${(file.size / 1024 / 1024).toFixed(1)}MB > 5MB)`);
            return;
          }

          setProgress('Ottimizzazione immagine...');
          const { base64, w, h } = await compressImage(file);
          setProgress('Salvataggio...');

          await saveImage.mutateAsync({
            cliente_id: clienteId,
            bytes_base64: base64,
            original_name: file.name,
            larghezza_px: w,
            altezza_px: h,
            categoria,
            consenso_gdpr: consensoGdpr,
          });
          toast.success('Foto salvata');
        }

        onUploaded?.();
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(`Errore upload: ${msg}`);
        toast.error('Upload fallito');
      } finally {
        setUploading(false);
        setProgress(null);
      }
    },
    [clienteId, categoria, consensoGdpr, saveImage, saveVideo, onUploaded],
  );

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files || files.length === 0) return;
      Array.from(files).forEach((f) => processFile(f));
    },
    [processFile],
  );

  const accept = acceptVideo
    ? '.jpg,.jpeg,.png,.heic,.webp,.mp4,.mov'
    : '.jpg,.jpeg,.png,.heic,.webp';

  return (
    <div className={className}>
      <div
        role="button"
        tabIndex={0}
        aria-label="Zona upload file"
        className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-all duration-200 select-none outline-none
          ${dragging
            ? 'border-primary bg-primary/10 scale-[1.01]'
            : 'border-border hover:border-primary/60 bg-card/30 hover:bg-primary/5'
          }
          ${uploading ? 'pointer-events-none opacity-60' : ''}
        `}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />

        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            {uploading
              ? <Upload className="w-5 h-5 text-primary animate-bounce" />
              : acceptVideo
              ? <Video className="w-5 h-5 text-primary" />
              : <ImagePlus className="w-5 h-5 text-primary" />
            }
          </div>

          {uploading && progress ? (
            <p className="text-sm text-primary font-medium">{progress}</p>
          ) : (
            <>
              <p className="text-sm text-foreground font-medium">
                {label ?? 'Trascina foto qui'}
              </p>
              <p className="text-xs text-muted-foreground">
                {acceptVideo
                  ? 'JPG · PNG · HEIC max 5MB · MP4/MOV max 50MB'
                  : 'JPG · PNG · HEIC · WebP — max 5MB'}
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-2 flex items-center gap-2 text-sm text-destructive bg-destructive/10 rounded-lg px-3 py-2">
          <X className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
