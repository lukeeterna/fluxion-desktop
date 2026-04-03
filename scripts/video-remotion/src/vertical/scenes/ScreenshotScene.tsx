import React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig, staticFile } from "remotion";

export interface CropRegion {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

interface Props {
  src: string;
  crop?: CropRegion;
  subtitle?: string;
  durationFrames: number;
}

const BG = "#0a0a0f";

export const ScreenshotScene: React.FC<Props> = ({ src, crop, subtitle, durationFrames }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 9], [0, 1], { extrapolateRight: "clamp" });
  const zoom = interpolate(frame, [0, durationFrames], [1.0, 1.2], { extrapolateRight: "clamp" });

  // Crop percentages to pixel offsets
  const cl = crop?.left ?? 0;
  const ct = crop?.top ?? 0;
  const cr = crop?.right ?? 1;
  const cb = crop?.bottom ?? 1;
  const cropW = cr - cl;
  const cropH = cb - ct;

  // Scale screenshot to fill ~85% of width
  const targetW = width * 0.85;
  const aspectRatio = cropW / cropH;
  const displayW = targetW;
  const displayH = targetW / aspectRatio;

  // Cap height
  const maxH = height * 0.75;
  const scale = displayH > maxH ? maxH / displayH : 1;
  const finalW = displayW * scale;
  const finalH = displayH * scale;

  // Center position (slightly above center)
  const x = (width - finalW) / 2;
  const y = (height - finalH) / 2 - 60;

  // Subtitle bar
  const subOpacity = subtitle
    ? interpolate(frame, [6, 15, durationFrames - 12, durationFrames - 3], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 0;

  return (
    <AbsoluteFill style={{ background: BG, opacity: fadeIn }}>
      <div style={{
        position: "absolute",
        left: x, top: y,
        width: finalW, height: finalH,
        overflow: "hidden",
        borderRadius: 12,
        transform: `scale(${zoom})`,
        transformOrigin: "center center",
        boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
      }}>
        <Img
          src={staticFile(src)}
          style={{
            position: "absolute",
            left: `-${(cl / cropW) * 100}%`,
            top: `-${(ct / cropH) * 100}%`,
            width: `${(1 / cropW) * 100}%`,
            height: `${(1 / cropH) * 100}%`,
          }}
        />
      </div>

      {/* Subtitle bar */}
      {subtitle && (
        <div style={{
          position: "absolute",
          bottom: 80,
          left: 0, right: 0,
          opacity: subOpacity,
          display: "flex",
          justifyContent: "center",
        }}>
          <div style={{
            background: "rgba(0,0,0,0.75)",
            backdropFilter: "blur(10px)",
            padding: "14px 32px",
            borderRadius: 10,
            color: "white",
            fontSize: 28,
            fontFamily: "'Inter', 'Helvetica Neue', sans-serif",
            fontWeight: 600,
            letterSpacing: -0.3,
          }}>
            {subtitle}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
