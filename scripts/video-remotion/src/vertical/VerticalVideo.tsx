import React from "react";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { ScreenshotScene, CropRegion } from "./scenes/ScreenshotScene";
import { Veo3Scene } from "./scenes/Veo3Scene";
import { CTAScene } from "./scenes/CTAScene";

interface BlockDef {
  id: string;
  type: "veo3" | "screenshot" | "cta";
  source?: string;
  crop?: CropRegion;
  subtitle?: string;
  durationFrames: number;
}

export type VerticalVideoProps = {
  verticale: string;
  competitor?: string;
  blocks: BlockDef[];
} & Record<string, unknown>;

const TRANSITION_FRAMES = 9; // 0.3s at 30fps

export const VerticalVideo: React.FC<VerticalVideoProps> = ({ blocks, competitor }) => {
  return (
    <TransitionSeries>
      {blocks.map((block, i) => (
        <React.Fragment key={block.id}>
          <TransitionSeries.Sequence durationInFrames={block.durationFrames}>
            {block.type === "veo3" && block.source && (
              <Veo3Scene src={block.source} />
            )}
            {block.type === "screenshot" && block.source && (
              <ScreenshotScene
                src={block.source}
                crop={block.crop}
                subtitle={block.subtitle}
                durationFrames={block.durationFrames}
              />
            )}
            {block.type === "cta" && (
              <CTAScene competitor={competitor || "€4.320 in 3 anni"} />
            )}
          </TransitionSeries.Sequence>
          {i < blocks.length - 1 && (
            <TransitionSeries.Transition
              presentation={fade()}
              timing={linearTiming({ durationInFrames: TRANSITION_FRAMES })}
            />
          )}
        </React.Fragment>
      ))}
    </TransitionSeries>
  );
};
