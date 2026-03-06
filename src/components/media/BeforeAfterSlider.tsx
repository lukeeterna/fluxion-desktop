// ═══════════════════════════════════════════════════════════════════
// FLUXION - BeforeAfterSlider (F06 Sprint B)
// Slider interattivo Prima/Dopo — drag + tastiera + touch
// ═══════════════════════════════════════════════════════════════════

import { useRef, useState, useCallback } from 'react';
import { GripVertical } from 'lucide-react';

// ─────────────────────────────────────────────────────────────────────
// PROPS
// ─────────────────────────────────────────────────────────────────────

interface Props {
  /** Data URL immagine "Prima" */
  srcPrima: string;
  /** Data URL immagine "Dopo" */
  srcDopo: string;
  /** Posizione iniziale handle (0–100, default 50) */
  initialPosition?: number;
  className?: string;
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────

export function BeforeAfterSlider({
  srcPrima,
  srcDopo,
  initialPosition = 50,
  className = '',
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState(initialPosition); // 0–100
  const isDragging = useRef(false);

  // ─── calcola posizione da evento pointer ───────────────────────────
  const calcPosition = useCallback((clientX: number): number => {
    const el = containerRef.current;
    if (!el) return position;
    const rect = el.getBoundingClientRect();
    const x = clientX - rect.left;
    return Math.min(100, Math.max(0, (x / rect.width) * 100));
  }, [position]);

  // ─── pointer events ────────────────────────────────────────────────
  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    e.currentTarget.setPointerCapture(e.pointerId);
    isDragging.current = true;
    setPosition(calcPosition(e.clientX));
  }, [calcPosition]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!isDragging.current) return;
    setPosition(calcPosition(e.clientX));
  }, [calcPosition]);

  const handlePointerUp = useCallback(() => {
    isDragging.current = false;
  }, []);

  // ─── tastiera: frecce ±5% ─────────────────────────────────────────
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      setPosition((p) => Math.max(0, p - 5));
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      setPosition((p) => Math.min(100, p + 5));
    }
  }, []);

  return (
    <div
      ref={containerRef}
      className={`relative select-none overflow-hidden rounded-xl ${className}`}
      style={{ cursor: 'ew-resize' }}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerUp}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="slider"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(position)}
      aria-label="Slider Prima/Dopo"
    >
      {/* Immagine DOPO (sfondo completo) */}
      <img
        src={srcDopo}
        alt="Dopo"
        className="block w-full h-full object-cover pointer-events-none"
        draggable={false}
      />

      {/* Immagine PRIMA (clip da sinistra) */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{ width: `${position}%` }}
      >
        <img
          src={srcPrima}
          alt="Prima"
          className="block w-full h-full object-cover pointer-events-none"
          style={{ width: `${100 * (100 / position)}%`, maxWidth: 'none' }}
          draggable={false}
        />
      </div>

      {/* Linea divisoria */}
      <div
        className="absolute top-0 bottom-0 w-0.5 bg-white drop-shadow-lg z-10 pointer-events-none"
        style={{ left: `${position}%` }}
      />

      {/* Handle circolare */}
      <div
        className="absolute top-1/2 z-20 -translate-y-1/2 -translate-x-1/2 w-9 h-9 rounded-full bg-white shadow-lg flex items-center justify-center text-slate-700 pointer-events-none"
        style={{ left: `${position}%` }}
      >
        <GripVertical className="w-4 h-4" />
      </div>

      {/* Label PRIMA */}
      <span className="absolute top-3 left-3 z-10 text-xs font-bold text-white bg-black/50 px-2 py-0.5 rounded pointer-events-none">
        PRIMA
      </span>

      {/* Label DOPO */}
      <span className="absolute top-3 right-3 z-10 text-xs font-bold text-white bg-black/50 px-2 py-0.5 rounded pointer-events-none">
        DOPO
      </span>
    </div>
  );
}
