import React from "react";
import { interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import logoUrl from "../assets/logo.png";

// ── Brand colors ────────────────────────────────────────────────────────────
export const C = {
  bg:       "#020617",   // slate-950
  sidebar:  "#0f172a",   // slate-900
  card:     "#1e293b",   // slate-800
  card2:    "#334155",   // slate-700
  t1:       "#f1f5f9",   // slate-100
  t2:       "#94a3b8",   // slate-400
  t3:       "#475569",   // slate-600
  cyan:     "#22d3ee",   // cyan-400  brand
  cyanDk:   "#0891b2",   // cyan-600
  teal:     "#14b8a6",   // teal-500
  green:    "#10b981",   // emerald-500
  yellow:   "#f59e0b",   // amber-500
  red:      "#ef4444",   // red-500
  violet:   "#8b5cf6",   // violet-500
  blue:     "#3b82f6",   // blue-500
  rose:     "#f43f5e",   // rose-500
} as const;

const NAV = [
  { label: "Dashboard",    path: "/" },
  { label: "Calendario",   path: "/calendario" },
  { label: "Clienti",      path: "/clienti" },
  { label: "Servizi",      path: "/servizi" },
  { label: "Operatori",    path: "/operatori" },
  { label: "Fatture",      path: "/fatture" },
  { label: "Cassa",        path: "/cassa" },
  { label: "Fornitori",    path: "/fornitori" },
  { label: "Voice Agent",  path: "/voice" },
  { label: "Impostazioni", path: "/impostazioni" },
];

interface LayoutProps {
  active?: string;
  children: React.ReactNode;
  fadeIn?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({ active = "/", children, fadeIn = true }) => {
  const frame = useCurrentFrame();
  const opacity = fadeIn ? interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" }) : 1;

  return (
    <div style={{ width: 1280, height: 720, background: C.bg, fontFamily: "'Inter', 'Helvetica', sans-serif", opacity, display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <div style={{ height: 56, background: "#0a1228", borderBottom: `1px solid ${C.card2}`, display: "flex", alignItems: "center", flexShrink: 0 }}>
        {/* Logo area */}
        <div style={{ width: 224, display: "flex", alignItems: "center", gap: 10, paddingLeft: 14 }}>
          <img src={logoUrl} style={{ width: 28, height: 28 }} />
          <span style={{ color: C.cyan, fontWeight: 800, fontSize: 16, letterSpacing: -0.5 }}>FLUXION</span>
        </div>
        {/* Page title */}
        <div style={{ flex: 1, paddingLeft: 16 }}>
          <span style={{ color: C.t1, fontWeight: 700, fontSize: 15 }}>
            {NAV.find(n => n.path === active)?.label ?? ""}
          </span>
        </div>
        {/* Right controls */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, paddingRight: 16 }}>
          <div style={{ background: C.card, borderRadius: 6, padding: "4px 10px", fontSize: 11, color: C.t3 }}>⌘K</div>
          <div style={{ width: 30, height: 30, borderRadius: 15, background: C.cyanDk, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, color: C.t1 }}>MR</div>
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Sidebar */}
        <div style={{ width: 224, background: C.sidebar, borderRight: `1px solid ${C.card2}`, padding: "8px 0", flexShrink: 0 }}>
          {NAV.map(n => {
            const isActive = n.path === active;
            return (
              <div key={n.path} style={{
                margin: "1px 8px", padding: "8px 12px", borderRadius: 6,
                background: isActive ? C.cyanDk : "transparent",
                color: isActive ? C.t1 : C.t2,
                fontSize: 13, fontWeight: isActive ? 700 : 400, cursor: "default",
              }}>
                {n.label}
              </div>
            );
          })}
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflow: "hidden", padding: 16 }}>
          {children}
        </div>
      </div>
    </div>
  );
};

// ── Reusable UI atoms ────────────────────────────────────────────────────────

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ background: C.card, border: `1px solid ${C.card2}`, borderRadius: 8, padding: 14, ...style }}>
    {children}
  </div>
);

export const Badge: React.FC<{ label: string; color: string; textColor?: string }> = ({ label, color, textColor }) => (
  <span style={{ background: color, color: textColor ?? C.t1, borderRadius: 4, padding: "2px 8px", fontSize: 11, fontWeight: 700 }}>
    {label}
  </span>
);

export const ProgressBar: React.FC<{ value: number; max: number; color: string; height?: number }> = ({ value, max, color, height = 8 }) => (
  <div style={{ background: C.card2, borderRadius: height, overflow: "hidden", height }}>
    <div style={{ width: `${(value/max)*100}%`, background: color, height, borderRadius: height }} />
  </div>
);

export const SectionTitle: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ color: C.t1, fontWeight: 700, fontSize: 18, marginBottom: 12 }}>{children}</div>
);

// Animated callout number
export const Callout: React.FC<{ n: number; delay?: number; style?: React.CSSProperties }> = ({ n, delay = 0, style }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [delay, delay + 6], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  return (
    <div style={{
      position: "absolute", width: 24, height: 24, borderRadius: 12,
      background: C.cyan, display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 12, fontWeight: 800, color: C.bg,
      transform: `scale(${scale})`,
      boxShadow: `0 0 0 3px ${C.bg}`,
      ...style,
    }}>
      {n}
    </div>
  );
};

// Fade-in wrapper
export const FadeIn: React.FC<{ from?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ from = 0, children, style }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [from, from + 10], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const y = interpolate(frame, [from, from + 10], [12, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  return <div style={{ opacity, transform: `translateY(${y}px)`, ...style }}>{children}</div>;
};
