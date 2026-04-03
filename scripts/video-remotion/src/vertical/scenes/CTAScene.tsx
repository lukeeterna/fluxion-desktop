import React from "react";
import { AbsoluteFill, Img, interpolate, spring, useCurrentFrame, useVideoConfig, staticFile } from "remotion";

interface Props {
  competitor: string;
}

const LOGO = staticFile("logo_fluxion.jpg");

export const CTAScene: React.FC<Props> = ({ competitor }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fadeEl = (delay: number) => ({
    opacity: interpolate(frame, [delay, delay + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
    transform: `translateY(${interpolate(frame, [delay, delay + 12], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
  });

  const logoScale = spring({ frame, fps, config: { damping: 14, stiffness: 100 }, delay: 5 });

  return (
    <AbsoluteFill style={{
      background: "#000",
      fontFamily: "'Inter', 'Helvetica Neue', sans-serif",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
    }}>
      {/* Logo */}
      <div style={{ transform: `scale(${logoScale})`, marginBottom: 30 }}>
        <Img src={LOGO} style={{ width: 180, height: 180, borderRadius: 40, objectFit: "cover" }} />
      </div>

      {/* FLUXION */}
      <div style={{ ...fadeEl(15), fontSize: 80, fontWeight: 900, letterSpacing: 4, color: "white" }}>
        FLUXION
      </div>

      {/* Tagline */}
      <div style={{ ...fadeEl(30), fontSize: 24, color: "#AAAAAA", marginTop: 16 }}>
        Il gestionale che non ti costa ogni mese
      </div>

      {/* Separator */}
      <div style={{ ...fadeEl(45), width: "70%", height: 1, background: "#333", marginTop: 40, marginBottom: 40 }} />

      {/* Price */}
      <div style={{ ...fadeEl(55), fontSize: 96, fontWeight: 900, color: "white" }}>€497</div>
      <div style={{ ...fadeEl(65), fontSize: 34, color: "white", marginTop: 8 }}>una volta. per sempre.</div>

      {/* Separator */}
      <div style={{ ...fadeEl(80), width: "70%", height: 1, background: "#333", marginTop: 40, marginBottom: 40 }} />

      {/* Competitor */}
      <div style={{ ...fadeEl(90), fontSize: 22, color: "#FF5555" }}>{competitor}</div>

      {/* URL */}
      <div style={{ ...fadeEl(110), fontSize: 44, color: "#7799FF", fontWeight: 700, marginTop: 50 }}>
        fluxion.app
      </div>
    </AbsoluteFill>
  );
};
