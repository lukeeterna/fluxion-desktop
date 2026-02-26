import { Composition } from "remotion";
import { FluxionTutorial, calculateTutorialMetadata } from "./Video";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="FluxionTutorial"
      component={FluxionTutorial}
      durationInFrames={900} // fallback, overridden by calculateMetadata
      fps={30}
      width={1280}
      height={720}
      calculateMetadata={calculateTutorialMetadata}
    />
  );
};

// Required for React
import React from "react";
