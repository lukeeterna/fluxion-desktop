import { Composition } from "remotion";
import { FluxionTutorial, calculateTutorialMetadata, FluxionMarketing, calculateMarketingMetadata } from "./Video";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="FluxionMarketing"
        component={FluxionMarketing}
        durationInFrames={2052} // fallback: (150+450+600+450+450) - 4*12
        fps={30}
        width={1280}
        height={720}
        calculateMetadata={calculateMarketingMetadata}
      />
      <Composition
        id="FluxionTutorial"
        component={FluxionTutorial}
        durationInFrames={900}
        fps={30}
        width={1280}
        height={720}
        calculateMetadata={calculateTutorialMetadata}
      />
    </>
  );
};

// Required for React
import React from "react";
