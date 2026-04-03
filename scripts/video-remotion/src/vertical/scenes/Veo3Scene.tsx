import React from "react";
import { AbsoluteFill, OffthreadVideo, interpolate, useCurrentFrame, useVideoConfig, staticFile } from "remotion";

interface Props {
  src: string;
}

export const Veo3Scene: React.FC<Props> = ({ src }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const fadeIn = interpolate(frame, [0, 9], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: "#000", opacity: fadeIn }}>
      <OffthreadVideo
        src={staticFile(src)}
        muted
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
    </AbsoluteFill>
  );
};
