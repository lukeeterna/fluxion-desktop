# Veo 3 / 3.1 Prompt Optimization — FLUXION Video Demo
> Research: 2026-03-23 | CoVe 2026 Deep Research
> Sources: Google DeepMind official, Google Cloud Vertex AI docs, snubroot/Veo-3-Prompting-Guide, community guides

---

## 1. THE FILM STRIP BORDER PROBLEM — ROOT CAUSE & FIX

### Why It Happens
When you use words like **"Kodak"**, **"35mm film"**, **"film grain"**, **"shot on film"**, or **"analog"** in your prompt, Veo interprets this as a request for a **vintage film aesthetic** — complete with:
- 35mm film strip borders / sprocket holes
- Film grain overlay
- Vignetting / letterboxing
- Color cast (warm amber, desaturated)

Veo weights **early words heavily**. If "Kodak" or "film" appears near the start, the entire generation skews vintage.

### THE FIX — Use These Instead

| AVOID (triggers vintage) | USE INSTEAD (clean modern) |
|--------------------------|---------------------------|
| "Kodak Portra" | "natural warm color palette" |
| "shot on 35mm film" | "shot on digital cinema camera" |
| "film grain" | "clean sensor, no noise" |
| "analog look" | "modern digital cinematography" |
| "cinematic film" | "cinematic, clean digital" |
| "vintage" | "contemporary" |
| "film stock" | "digital color grade" |
| "Super 8" / "16mm" | "4K digital" |
| "Kodak Vision3" | "professional color science" |
| "anamorphic" (risky) | "widescreen 16:9 composition" |

### Negative Prompt (ALWAYS include)
```
negativePrompt: "film grain, film strip, sprocket holes, film borders, letterbox bars, vintage effect, analog noise, VHS, old film, film reel, film frame edges, scratches, dust particles, vignette, sepia tone, retro filter"
```

---

## 2. PROMPT STRUCTURE — GOLD STANDARD

### Optimal Length
**3-6 sentences, 100-150 words.** This gives room for subject, context, action, style, camera, and audio.

### Word Order Matters
Veo weights **early words heavily**. Structure:
1. **Core shot type + subject** (FIRST — most important)
2. **Action** (what's happening)
3. **Environment/location** (where)
4. **Lighting + mood** (atmosphere)
5. **Camera details** (movement, lens)
6. **Style reference** (LAST — to avoid it dominating)
7. **Audio** (separate sentence at end)

### Template — Clean Modern Professional

```
[SHOT TYPE] of [SUBJECT DESCRIPTION], [ACTION].
[ENVIRONMENT with specific details].
[LIGHTING DESCRIPTION], [COLOR PALETTE].
Camera: [MOVEMENT], [LENS/FRAMING].
Style: clean digital cinematography, professional production, modern color grade.
Audio: [AMBIENT SOUNDS]. No background music.
```

### Example — FLUXION Salon Scene

```
Medium shot of a 35-year-old Italian woman with brown hair, wearing a
professional black apron, checking appointments on a tablet at a modern
hair salon reception desk. Warm natural daylight streams through large
windows. Clean white and wood interior with plants. Soft natural lighting
with warm tones. Camera: static tripod, eye-level, slight shallow depth
of field. Style: clean digital cinematography, shot on professional
digital camera, modern color grade, crisp and sharp.
Audio: soft ambient salon sounds, gentle background chatter.
```

---

## 3. CLEAN MODERN DIGITAL LOOK — KEYWORD ARSENAL

### Camera References That Work (NO vintage trigger)
- "shot on professional digital camera" (safe, generic)
- "shot on Sony FX6" / "shot on Canon C70" (modern digital cinema cameras)
- "shot on RED Komodo" (digital, NOT film)
- "ARRI Alexa digital" (modern reference)
- "mirrorless camera footage" (inherently digital)

### Style Keywords for Clean Modern
```
clean digital cinematography
professional production quality
modern color grade
crisp sharp detail
natural skin tones
contemporary visual style
broadcast quality
corporate video aesthetic
professional lighting setup
studio-quality footage
4K digital
high dynamic range
clean sensor
no noise
```

### Lighting Keywords (Modern, Not Vintage)
```
soft natural daylight
professional LED lighting
warm ambient light
clean key light with soft fill
diffused window light
modern office lighting
soft overhead lighting
natural color temperature
```

### Color Keywords (Modern, Not Film)
```
natural color palette
warm neutral tones
clean whites
accurate skin tones
balanced exposure
modern color science
subtle warm grade
```

---

## 4. REALISTIC ITALIAN PEOPLE — WITHOUT STEREOTYPES

### The Problem
AI models tend to generate stereotypical "Italian" features (exaggerated gestures, overly dark features, pizza/pasta context).

### The Solution — Specific Character Descriptions

**DO describe:**
- Specific age, hair color, style, clothing
- Professional context (what they DO, not where they're "from")
- Natural expressions and micro-actions
- Material textures (cotton shirt, leather apron, silk blouse)

**DON'T mention:**
- "Italian-looking" (triggers stereotypes)
- Nationality directly (unless essential)
- Cultural clichés

### Character Templates for FLUXION Scenes

**Salon Owner (Female):**
```
A 38-year-old woman with shoulder-length brown hair, olive skin, wearing
a fitted black cotton apron over a white blouse. Professional and warm
expression. Natural makeup.
```

**Gym Trainer (Male):**
```
A 32-year-old athletic man with short dark hair and light stubble, wearing
a dark fitted polo shirt with a small logo. Confident, friendly smile.
```

**Clinic Receptionist:**
```
A 28-year-old woman with dark hair pulled back, wearing a clean white
medical uniform. Welcoming expression, professional posture.
```

**Auto Mechanic:**
```
A 45-year-old man with gray-streaked dark hair, wearing navy blue work
coveralls. Hands slightly oil-stained, genuine smile.
```

### Consistency Trick
Keep the **exact same character description** across all prompts for the same person. Veo generates similar-looking characters from identical descriptions.

---

## 5. MULTIPLE PEOPLE IN SCENE

### What Works
- Specify **exact number**: "two women", "three people"
- Describe **each person** briefly but distinctly
- Define **spatial relationship**: "standing side by side", "one seated, one standing"
- Describe **interaction**: "looking at the same screen", "one gesturing while the other listens"

### What Fails
- Vague groups: "some people" (unpredictable count)
- Too many individuals (>4 gets unreliable)
- No spatial anchoring

### Example — Two People Scene
```
Medium shot of two people in a modern barbershop. A 40-year-old male barber
with short gray hair, wearing a black apron, carefully trimming the hair of
a seated 30-year-old male client in a leather barber chair. Both are smiling
naturally. Warm interior lighting, exposed brick wall background.
```

---

## 6. API SETTINGS — OPTIMAL CONFIGURATION

### Resolution & Aspect Ratio
| Setting | Recommendation | Notes |
|---------|---------------|-------|
| **Resolution** | `1080p` | Best quality/latency balance. 720p faster, 4K much slower |
| **Aspect Ratio** | `16:9` (landscape) | Default, best for demo video |
| **Duration** | `8s` per clip | Maximum length, gives most footage |
| **FPS** | 24 FPS | Default, cinematic standard |

### generateAudio Parameter
```json
"generateAudio": false
```
**YES, disable audio generation** if you:
- Will add voiceover separately (our case — Edge-TTS narration)
- Want faster generation
- Want to save API credits/quota

**Enable audio** ONLY if you need synchronized dialogue or specific sound effects in the clip.

### personGeneration Parameter
```json
"personGeneration": "allow_adult"
```
This is the **default**. Required for any scene with people.

### negativePrompt (CRITICAL — always include)
```json
"negativePrompt": "film grain, film strip borders, sprocket holes, vintage effect, letterbox, black bars, VHS, analog, old film, sepia, scratches, dust, vignette, blurry, distorted faces, text overlay, watermark, logo, subtitle, caption"
```

### Complete API Call Template
```json
{
  "instances": [{
    "prompt": "YOUR PROMPT HERE"
  }],
  "parameters": {
    "aspectRatio": "16:9",
    "resolution": "1080p",
    "durationSeconds": 8,
    "generateAudio": false,
    "personGeneration": "allow_adult",
    "negativePrompt": "film grain, film strip borders, sprocket holes, vintage effect, letterbox, black bars, VHS, analog, old film, sepia, scratches, dust, vignette, blurry, distorted faces, text overlay, watermark, logo, subtitle, caption",
    "sampleCount": 2,
    "seed": 42
  }
}
```

**sampleCount: 2** generates two variations per prompt. Pick the best one.
**seed**: Set a fixed seed for reproducibility, or omit for random.

---

## 7. AVOIDING UNCANNY VALLEY IN CLOSE-UPS

### Veo 3/3.1 Status
Veo 3.1 is widely considered the **first AI video model to largely eliminate uncanny valley**. However, close-ups still need care.

### Best Practices for Face Close-Ups
1. **Shallow depth of field** — slightly blurs background, focuses on face naturally
2. **Avoid extreme close-up (ECU)** — medium close-up (MCU) is safer
3. **Add micro-actions** — blinking, slight head turn, subtle smile change
4. **Specify natural skin texture** — "natural skin with subtle pores and texture"
5. **Avoid static faces** — always give the subject something to DO
6. **Material cues on clothing** — helps Veo stabilize the entire figure
7. **Natural eye focus** — "eyes focused on [specific thing]"

### Safe Close-Up Template
```
Medium close-up of [CHARACTER], [MICRO-ACTION like adjusting glasses or
tucking hair behind ear]. Natural skin texture, subtle expression change.
Shallow depth of field, soft natural lighting from camera-left.
Shot on digital cinema camera, clean and sharp.
```

---

## 8. WORKPLACE / PROFESSIONAL SCENES — BEST PRACTICES

### Key Elements
1. **Specific workspace details** — name exact furniture, equipment, decor
2. **Activity, not posing** — people DOING something, not standing idle
3. **Props** — tablet, phone, appointment book, tools of the trade
4. **Realistic lighting** — match the actual venue type (salon = warm, clinic = bright)
5. **Background depth** — mention what's visible behind the subject

### Vertical-Specific Scene Recipes

**Hair Salon:**
```
Modern hair salon interior, white walls, large mirrors with LED frame
lighting, styling chairs, products on glass shelves. Warm ambient lighting.
```

**Gym/Fitness:**
```
Clean modern fitness studio with wooden floor, mirrors along one wall,
minimal equipment. Bright natural light from large windows.
```

**Medical Clinic:**
```
Modern medical reception area, white and light gray interior, clean desk
with computer monitor, potted plant. Bright, even overhead lighting.
```

**Auto Workshop:**
```
Professional automotive workshop, clean organized tool wall, car on
hydraulic lift in background. Industrial LED overhead lighting,
slightly warm color temperature.
```

**Barbershop:**
```
Modern barbershop with vintage-inspired leather chairs, exposed brick
accent wall, warm Edison-style LED bulbs. Warm, inviting atmosphere.
```

---

## 9. JSON PROMPT FORMAT (ADVANCED)

Veo 3.1 responds well to JSON-structured prompts for complex scenes:

```json
{
  "scene": "Professional hair salon, late morning",
  "subject": "A 38-year-old female salon owner with shoulder-length brown hair, wearing a black cotton apron over white blouse",
  "action": "She smiles warmly while checking the day's appointments on a modern tablet, then looks up to greet an arriving client",
  "environment": "Modern salon with large windows, white walls, styling stations with round mirrors, green plants on shelves",
  "camera": {
    "shot": "medium shot",
    "movement": "slow subtle dolly forward",
    "angle": "eye level",
    "lens": "50mm equivalent, shallow depth of field"
  },
  "lighting": "Warm natural daylight from windows, supplemented by soft overhead LED panels",
  "color": "Natural warm tones, clean whites, accurate skin tones",
  "style": "Clean digital cinematography, professional production, modern color grade, crisp and sharp",
  "audio": "Soft ambient salon sounds, hairdryer in distance",
  "negative": "No film grain, no vintage effect, no borders, no text, no watermark"
}
```

However, **plain-text prompts are equally effective** and simpler. Use JSON only if you want more structured control.

---

## 10. PROMPT REWRITER WARNING

### Veo Has a Built-In Prompt Rewriter
By default, Veo 3.1 **rewrites your prompt** before generating. This can:
- Add unwanted stylistic elements
- Change your intent
- Introduce film-like qualities you didn't ask for

### How to Disable (Vertex AI API)
```json
"parameters": {
  "enhancePrompt": false  // Veo 2 only — check if available for Veo 3
}
```

For Veo 3.1, the prompt rewriter may be on by default. If you're getting unwanted effects despite clean prompts, this could be the cause. Google Cloud docs have a specific page on turning off the prompt rewriter:
https://cloud.google.com/vertex-ai/generative-ai/docs/video/turn-the-prompt-rewriter-off

---

## 11. FLUXION-SPECIFIC PROMPT TEMPLATES

### Scene 1: Salon Owner Checking Calendar
```
Medium shot of a 38-year-old woman with shoulder-length brown hair, olive
complexion, wearing a fitted black cotton apron over a white blouse. She
stands at a modern reception desk in a bright hair salon, tapping on a
sleek tablet showing a colorful calendar interface. She smiles with
satisfaction. Behind her: large windows with natural daylight, styling
stations with round mirrors, green plants on glass shelves. Clean digital
cinematography, shot on professional camera, modern color grade, crisp
and sharp image. Camera static, eye level, slight shallow depth of field.
No film grain, no vintage effect.
```

### Scene 2: Voice Assistant Interaction (Phone at Reception)
```
Close-up of a modern smartphone on a minimalist desk, screen showing an
incoming call interface with the name "Sara" and a voice waveform animation.
A woman's hand with natural nails reaches to answer. Soft warm lighting,
clean white desk surface, blurred salon background with bokeh lights.
Clean digital look, professional production quality. Camera: static,
slight overhead angle. No text overlay, no borders.
```

### Scene 3: Mechanic Workshop with Tablet
```
Medium wide shot of a 45-year-old man with gray-streaked dark hair, wearing
navy blue work coveralls, standing in a clean automotive workshop. He holds
a tablet showing a scheduling app, nodding with approval. Behind him:
organized tool wall, a silver car on a hydraulic lift. Industrial LED
overhead lighting with slightly warm tone. Clean digital cinematography,
professional camera, modern color grade. Camera: slow subtle dolly
forward. No vintage effect, no film grain.
```

### Scene 4: Multiple Clients in Waiting Area
```
Wide shot of a modern, bright medical clinic waiting area. Three people
sit in comfortable gray chairs: a 50-year-old man reading his phone, a
30-year-old woman with a child on her lap. A 28-year-old receptionist
with dark hair in a white uniform smiles from behind a clean desk with
a computer monitor. Large windows, green plants, calming atmosphere.
Soft natural daylight, clean modern interior. Shot on digital cinema
camera, professional quality. Camera: static wide establishing shot.
No film grain, no borders, no vintage.
```

---

## 12. CHECKLIST — BEFORE EVERY VEO 3 GENERATION

- [ ] **No "Kodak", "film", "35mm", "analog", "vintage"** anywhere in prompt
- [ ] **negativePrompt** includes film grain, borders, vintage, text, watermark
- [ ] **"Clean digital cinematography"** or similar modern reference present
- [ ] **Subject described first** (Veo weights early words)
- [ ] **Specific character details** — age, hair, clothing material, expression
- [ ] **Action specified** — never just standing/posing
- [ ] **Lighting described** — matches venue type
- [ ] **Camera specified** — shot type, movement, angle
- [ ] **generateAudio: false** if adding voiceover separately
- [ ] **personGeneration: "allow_adult"** for people scenes
- [ ] **aspectRatio: "16:9"** for landscape demo video
- [ ] **resolution: "1080p"** for quality/speed balance
- [ ] **sampleCount: 2** for two variations to choose from
- [ ] Prompt is **100-150 words** (sweet spot)

---

## Sources

### Official Google Documentation
- [Google DeepMind — Veo Prompt Guide](https://deepmind.google/models/veo/prompt-guide/)
- [Google Cloud — Ultimate Prompting Guide for Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [Google Cloud — Veo Video Generation API Reference](https://docs.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation)
- [Google Cloud — Veo Prompt Guide (Vertex AI)](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide)
- [Google Cloud — Turn Off Prompt Rewriter](https://cloud.google.com/vertex-ai/generative-ai/docs/video/turn-the-prompt-rewriter-off)
- [Google AI — Generate Videos with Veo 3.1 (Gemini API)](https://ai.google.dev/gemini-api/docs/video)

### Community Guides & Research
- [snubroot/Veo-3-Prompting-Guide (GitHub)](https://github.com/snubroot/Veo-3-Prompting-Guide)
- [Replicate — How to Prompt Veo 3](https://replicate.com/blog/using-and-prompting-veo-3)
- [Leonardo.ai — Veo 3 Prompt Guide](https://leonardo.ai/news/mastering-prompts-for-veo-3/)
- [Medium — Cinematic AI Videos with Veo 3 (Antony Matthews)](https://medium.com/@Antony-Matthews/how-to-make-cinematic-ai-videos-with-google-veo-3-full-breakdown-f770fecf43ee)
- [Medium — Mastering Veo 3: Camera Control (Miguel Ivanov)](https://medium.com/@miguelivanov/mastering-veo-3-an-expert-guide-to-optimal-prompt-structure-and-cinematic-camera-control-693d01ae9f8b)
- [Sider.ai — Best Prompt Techniques for Veo 3.1](https://sider.ai/blog/ai-tools/best-prompt-techniques-for-veo-3_1-video-output-a-field-guide-to-cinematic-control)
- [Anakin.ai — Veo 3 Negative Prompts](http://anakin.ai/blog/veo-3-negative-prompts-how-to-reduce-artifacts-and-unwanted-objects/)
- [DEV.to — JSON Prompting for Veo 3.1](https://dev.to/yigit-konur/best-practices-of-json-prompting-for-video-generation-models-examples-for-veo-31-1mc0)
- [ImagineArt — Veo 3.1 Prompt Guide](https://www.imagine.art/blogs/veo-3-1-prompt-guide)
- [Invideo — Veo 3.1 Prompting Guide](https://invideo.io/blog/google-veo-prompt-guide/)
- [DesignHero — Veo 3 Cinematic Realism](https://blog.designhero.tv/veo-3-flow-cinematic-realism-midjourney/)
