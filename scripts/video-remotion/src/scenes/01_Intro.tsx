import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { C } from "../components/Layout";
import logoUrl from "../assets/logo.png";

export const SceneIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoScale = spring({ frame, fps, config: { damping: 14, stiffness: 120 }, delay: 0 });
  const titleOpacity = interpolate(frame, [12, 22], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const titleY = interpolate(frame, [12, 22], [20, 0], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const subtitleOpacity = interpolate(frame, [22, 34], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });
  const chipsOpacity = interpolate(frame, [34, 46], [0, 1], { extrapolateRight: "clamp", extrapolateLeft: "clamp" });

  const chips = ["✂ Saloni", "🏋 Palestre", "🏥 Cliniche", "🔧 Officine", "🦷 Odontoiatria", "💆 Estetica"];

  return (
    <div style={{
      width: 1280, height: 720,
      background: `radial-gradient(ellipse at 50% 40%, #0c1a3a 0%, #020617 70%)`,
      fontFamily: "'Inter','Helvetica',sans-serif",
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      position: "relative", overflow: "hidden",
    }}>
      {/* Subtle grid */}
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: `linear-gradient(${C.card2}22 1px, transparent 1px), linear-gradient(90deg, ${C.card2}22 1px, transparent 1px)`,
        backgroundSize: "60px 60px",
      }} />

      {/* Glow */}
      <div style={{
        position: "absolute", width: 400, height: 400, borderRadius: 200,
        background: `radial-gradient(circle, ${C.cyan}18 0%, transparent 70%)`,
        top: "10%", left: "50%", transform: "translateX(-50%)",
      }} />

      {/* Logo */}
      <div style={{ transform: `scale(${logoScale})`, marginBottom: 16, zIndex: 1 }}>
        <img src={logoUrl} style={{ width: 96, height: 96, filter: "drop-shadow(0 0 20px #22d3ee88)" }} />
      </div>

      {/* Title */}
      <div style={{ opacity: titleOpacity, transform: `translateY(${titleY}px)`, zIndex: 1, textAlign: "center" }}>
        <div style={{ fontSize: 72, fontWeight: 900, letterSpacing: -3,
          background: `linear-gradient(90deg, ${C.cyan}, ${C.teal})`,
          WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", lineHeight: 1 }}>
          FLUXION
        </div>
      </div>

      {/* Subtitle */}
      <div style={{ opacity: subtitleOpacity, marginTop: 14, zIndex: 1, textAlign: "center" }}>
        <p style={{ color: C.t2, fontSize: 22, margin: 0, fontWeight: 400 }}>
          Il gestionale desktop che lavora per te
        </p>
      </div>

      {/* Verticals chips */}
      <div style={{ opacity: chipsOpacity, display: "flex", gap: 10, marginTop: 40, flexWrap: "wrap", justifyContent: "center", zIndex: 1, maxWidth: 700 }}>
        {chips.map(c => (
          <div key={c} style={{
            background: C.card, border: `1px solid ${C.card2}`,
            borderRadius: 20, padding: "7px 16px",
            fontSize: 13, fontWeight: 600, color: C.t1,
          }}>{c}</div>
        ))}
      </div>

      {/* Bottom label */}
      <div style={{ position: "absolute", bottom: 32, color: C.t3, fontSize: 13, textAlign: "center" }}>
        Tutorial completo — tutte le funzionalità
      </div>
    </div>
  );
};
