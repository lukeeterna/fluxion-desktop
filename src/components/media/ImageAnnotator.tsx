// ═══════════════════════════════════════════════════════════════════
// FLUXION - ImageAnnotator (F06 Sprint C)
// SVG overlay su immagine: freccia, cerchio, testo
// World-class: nessun competitor PMI offre annotation nativa su foto
// ═══════════════════════════════════════════════════════════════════

import { useState, useRef, useCallback } from 'react';
import { ArrowUpRight, Circle, Type, RotateCcw } from 'lucide-react';
import { Button } from '../ui/button';

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

export type AnnotaTool = 'freccia' | 'cerchio' | 'testo';

export interface Annotation {
  id: string;
  tipo: AnnotaTool;
  x1: number;  // 0-100 (percentuale)
  y1: number;
  x2?: number; // endpoint freccia
  y2?: number;
  testo?: string;
  colore: string;
}

interface Props {
  imageSrc: string;           // data URL
  annotations: Annotation[];
  onChange?: (anns: Annotation[]) => void;
  readOnly?: boolean;
}

// ─────────────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────────────

const COLORI = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ffffff'];
const CERCHIO_R = 8; // raggio cerchio in % rispetto al lato corto

// ─────────────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────────────

function genId() {
  return typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);
}

function svgPoint(e: React.PointerEvent<SVGSVGElement>): { x: number; y: number } {
  const svg = (e.target as SVGElement).closest('svg');
  if (!svg) {
    return { x: 0, y: 0 };
  }
  const rect = svg.getBoundingClientRect();
  return {
    x: ((e.clientX - rect.left) / rect.width) * 100,
    y: ((e.clientY - rect.top) / rect.height) * 100,
  };
}

// ─────────────────────────────────────────────────────────────────────
// COMPONENT
// ─────────────────────────────────────────────────────────────────────

export function ImageAnnotator({ imageSrc, annotations, onChange, readOnly = false }: Props) {
  const [tool, setTool] = useState<AnnotaTool>('freccia');
  const [colore, setColore] = useState('#ef4444');
  const [drawing, setDrawing] = useState<{ x1: number; y1: number; x2: number; y2: number } | null>(null);
  const [pendingText, setPendingText] = useState<{ x: number; y: number } | null>(null);
  const [testoInput, setTestoInput] = useState('');
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const addAnnotation = useCallback(
    (ann: Annotation) => {
      onChange?.([...annotations, ann]);
    },
    [annotations, onChange]
  );

  const removeAnnotation = useCallback(
    (id: string) => {
      onChange?.(annotations.filter((a) => a.id !== id));
    },
    [annotations, onChange]
  );

  // ── Pointer events ──────────────────────────────────────────────

  const handlePointerDown = (e: React.PointerEvent<SVGSVGElement>) => {
    if (readOnly) return;
    if (e.button !== 0) return;
    const pt = svgPoint(e);

    if (tool === 'cerchio') {
      addAnnotation({ id: genId(), tipo: 'cerchio', x1: pt.x, y1: pt.y, colore });
      return;
    }
    if (tool === 'testo') {
      setPendingText({ x: pt.x, y: pt.y });
      setTestoInput('');
      setTimeout(() => inputRef.current?.focus(), 50);
      return;
    }
    // freccia: start drag
    (e.currentTarget as SVGSVGElement).setPointerCapture(e.pointerId);
    setDrawing({ x1: pt.x, y1: pt.y, x2: pt.x, y2: pt.y });
  };

  const handlePointerMove = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!drawing) return;
    const pt = svgPoint(e);
    setDrawing((d) => (d ? { ...d, x2: pt.x, y2: pt.y } : null));
  };

  const handlePointerUp = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!drawing) return;
    const pt = svgPoint(e);
    const dx = pt.x - drawing.x1;
    const dy = pt.y - drawing.y1;
    if (Math.abs(dx) > 1 || Math.abs(dy) > 1) {
      addAnnotation({
        id: genId(),
        tipo: 'freccia',
        x1: drawing.x1,
        y1: drawing.y1,
        x2: pt.x,
        y2: pt.y,
        colore,
      });
    }
    setDrawing(null);
  };

  const confirmTesto = () => {
    if (!pendingText || !testoInput.trim()) {
      setPendingText(null);
      return;
    }
    addAnnotation({
      id: genId(),
      tipo: 'testo',
      x1: pendingText.x,
      y1: pendingText.y,
      testo: testoInput.trim(),
      colore,
    });
    setPendingText(null);
    setTestoInput('');
  };

  const cursor = readOnly
    ? 'default'
    : tool === 'testo'
    ? 'text'
    : tool === 'cerchio'
    ? 'crosshair'
    : 'crosshair';

  return (
    <div className="space-y-2">
      {/* Toolbar */}
      {!readOnly && (
        <div className="flex items-center gap-2 flex-wrap">
          {/* Tool buttons */}
          {(
            [
              { id: 'freccia' as AnnotaTool, icon: <ArrowUpRight className="w-3.5 h-3.5" />, label: 'Freccia' },
              { id: 'cerchio' as AnnotaTool, icon: <Circle className="w-3.5 h-3.5" />, label: 'Cerchio' },
              { id: 'testo' as AnnotaTool, icon: <Type className="w-3.5 h-3.5" />, label: 'Testo' },
            ] as const
          ).map(({ id, icon, label }) => (
            <Button
              key={id}
              size="sm"
              variant={tool === id ? 'default' : 'outline'}
              className={`h-7 px-2 gap-1 text-xs ${
                tool === id
                  ? 'bg-blue-600 border-blue-600 text-white'
                  : 'border-slate-600 text-slate-400 hover:text-white'
              }`}
              onClick={() => setTool(id)}
            >
              {icon}
              {label}
            </Button>
          ))}

          {/* Color swatches */}
          <div className="flex gap-1 ml-2">
            {COLORI.map((c) => (
              <button
                key={c}
                onClick={() => setColore(c)}
                className={`w-5 h-5 rounded-full border-2 transition-transform ${
                  colore === c ? 'border-white scale-110' : 'border-transparent hover:border-slate-400'
                }`}
                style={{ backgroundColor: c }}
                title={c}
              />
            ))}
          </div>

          {/* Reset */}
          {annotations.length > 0 && (
            <Button
              size="sm"
              variant="ghost"
              className="h-7 px-2 text-xs text-slate-500 hover:text-red-400 ml-auto"
              onClick={() => onChange?.([])}
            >
              <RotateCcw className="w-3 h-3 mr-1" />
              Cancella tutto
            </Button>
          )}
        </div>
      )}

      {/* Image + SVG overlay */}
      <div className="relative rounded-lg overflow-hidden bg-slate-950 select-none">
        <img
          src={imageSrc}
          alt="Immagine annotabile"
          className="w-full h-auto block"
          draggable={false}
        />

        {/* SVG overlay */}
        <svg
          ref={svgRef}
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          style={{ cursor, touchAction: 'none' }}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
        >
          <defs>
            {COLORI.map((c) => (
              <marker
                key={c}
                id={`arrow-${c.replace('#', '')}`}
                markerWidth="6"
                markerHeight="6"
                refX="5"
                refY="3"
                orient="auto"
              >
                <path d="M0,0 L6,3 L0,6 Z" fill={c} />
              </marker>
            ))}
          </defs>

          {/* Rendered annotations */}
          {annotations.map((ann) => (
            <g
              key={ann.id}
              onPointerEnter={() => !readOnly && setHoveredId(ann.id)}
              onPointerLeave={() => setHoveredId(null)}
            >
              {ann.tipo === 'freccia' && ann.x2 !== undefined && ann.y2 !== undefined && (
                <line
                  x1={ann.x1}
                  y1={ann.y1}
                  x2={ann.x2}
                  y2={ann.y2}
                  stroke={ann.colore}
                  strokeWidth="1.2"
                  markerEnd={`url(#arrow-${ann.colore.replace('#', '')})`}
                />
              )}

              {ann.tipo === 'cerchio' && (
                <circle
                  cx={ann.x1}
                  cy={ann.y1}
                  r={CERCHIO_R}
                  fill="none"
                  stroke={ann.colore}
                  strokeWidth="1.5"
                />
              )}

              {ann.tipo === 'testo' && (
                <>
                  <text
                    x={ann.x1}
                    y={ann.y1}
                    fill={ann.colore}
                    fontSize="4"
                    fontFamily="sans-serif"
                    fontWeight="bold"
                    style={{ filter: 'drop-shadow(0 0 2px #000)' }}
                  >
                    {ann.testo}
                  </text>
                </>
              )}

              {/* Delete button on hover */}
              {hoveredId === ann.id && !readOnly && (
                <g
                  onClick={(e) => {
                    e.stopPropagation();
                    removeAnnotation(ann.id);
                    setHoveredId(null);
                  }}
                  style={{ cursor: 'pointer' }}
                >
                  <circle
                    cx={ann.x1 + (ann.x2 !== undefined ? (ann.x2 - ann.x1) / 2 : 0) + 5}
                    cy={ann.y1 + (ann.y2 !== undefined ? (ann.y2 - ann.y1) / 2 : 0) - 5}
                    r="3.5"
                    fill="#ef4444"
                  />
                  <text
                    x={ann.x1 + (ann.x2 !== undefined ? (ann.x2 - ann.x1) / 2 : 0) + 5}
                    y={ann.y1 + (ann.y2 !== undefined ? (ann.y2 - ann.y1) / 2 : 0) - 3.8}
                    fill="white"
                    fontSize="3.5"
                    textAnchor="middle"
                    fontFamily="sans-serif"
                  >
                    ×
                  </text>
                </g>
              )}
            </g>
          ))}

          {/* Preview freccia in drawing */}
          {drawing && tool === 'freccia' && (
            <line
              x1={drawing.x1}
              y1={drawing.y1}
              x2={drawing.x2}
              y2={drawing.y2}
              stroke={colore}
              strokeWidth="1.2"
              strokeDasharray="2 1"
              markerEnd={`url(#arrow-${colore.replace('#', '')})`}
              pointerEvents="none"
            />
          )}
        </svg>

        {/* Text input overlay */}
        {pendingText && (
          <div
            className="absolute"
            style={{
              left: `${pendingText.x}%`,
              top: `${pendingText.y}%`,
              transform: 'translate(-50%, -100%)',
            }}
          >
            <input
              ref={inputRef}
              value={testoInput}
              onChange={(e) => setTestoInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') confirmTesto();
                if (e.key === 'Escape') setPendingText(null);
              }}
              onBlur={confirmTesto}
              placeholder="Testo..."
              className="bg-slate-900/90 border border-slate-500 text-white text-xs px-2 py-1 rounded w-32 outline-none focus:border-blue-400"
              style={{ color: colore }}
            />
          </div>
        )}
      </div>

      {/* Legenda annotazioni */}
      {annotations.length > 0 && (
        <div className="flex items-center gap-1 flex-wrap">
          <span className="text-slate-500 text-xs">{annotations.length} annotazion{annotations.length === 1 ? 'e' : 'i'}</span>
          {!readOnly && (
            <span className="text-slate-600 text-xs">· Click su × per eliminare</span>
          )}
        </div>
      )}

      {/* Istruzioni tool attivo */}
      {!readOnly && (
        <p className="text-slate-600 text-xs">
          {tool === 'freccia' && 'Trascina per disegnare una freccia'}
          {tool === 'cerchio' && 'Clicca per posizionare un cerchio'}
          {tool === 'testo' && 'Clicca per aggiungere testo'}
        </p>
      )}
    </div>
  );
}

export type { Annotation as ImageAnnotation };
