# AI Music Generation — Free Tier Research for Commercial Video Background Music

**Researched:** 2026-04-03
**Context:** 9 marketing videos (30-60s each) for FLUXION, Italian B2B SaaS
**Goal:** FREE or zero-cost background music with commercial rights
**Overall Confidence:** HIGH (multiple sources cross-verified)

---

## Executive Summary

**There is no truly free AI music generator with commercial rights that matches professional quality.** However, there are two viable zero-cost paths:

1. **Meta MusicGen (self-hosted)** — Open source, MIT-licensed, commercial use explicitly permitted. Quality is "good enough" for background music under voiceover. **RECOMMENDED.**
2. **Suno Free Tier + upgrade strategy** — Generate on free tier to test, then pay $10 for one month of Pro to regenerate the 9 tracks you like with commercial rights. Total cost: $10 one-time.

For a project with a ZERO COSTS constraint, MusicGen is the only fully free option with clear commercial rights.

---

## Tool-by-Tool Analysis

### 1. Suno AI

| Attribute | Details |
|-----------|---------|
| Free tier | 50 credits/day (~10 songs/day), replenishes daily |
| Duration | Up to 4 minutes per song |
| Commercial rights (free) | **NO** — personal use only, Suno retains ownership |
| Commercial rights (paid) | YES — Pro $10/mo or Premier $30/mo |
| Quality | **BEST in class** for AI music, near-professional |
| Vocals | Can generate vocals (use "instrumental" tag to avoid) |
| Best for | Highest quality output, but requires paid plan for commercial use |

**Verdict:** Best quality but violates ZERO COSTS for commercial use. Could do a one-month $10 Pro subscription to generate all 9 tracks commercially.

**Prompt pattern for corporate background:**
```
Style: corporate background, instrumental, inspiring, uplifting, clean production,
       motivational, professional, no vocals, 100 BPM
Lyrics: [Instrumental]
Negative: no singing, no humming, no choir, no voice
```

**Sources:**
- https://suno.com/pricing
- https://help.suno.com/en/articles/2416769
- https://margabagus.com/suno-pricing/

---

### 2. Udio AI

| Attribute | Details |
|-----------|---------|
| Free tier | 10 daily credits + 100 monthly credits |
| Duration | Up to ~2 minutes |
| Commercial rights (free) | **UNCLEAR** — requires attribution "Created with Udio" |
| Commercial rights (paid) | YES — Standard $10/mo, Pro $30/mo |
| Quality | Very high, comparable to Suno |
| Critical blocker | **Downloads temporarily disabled** during licensing transition (2025-2026) |

**Verdict: DO NOT USE.** Downloads are currently disabled across all plans during their licensing transition. This is a hard blocker regardless of pricing.

**Sources:**
- https://www.udio.com/pricing
- https://www.soundverse.ai/blog/article/is-udio-ai-free-0531

---

### 3. Google MusicFX (AI Test Kitchen)

| Attribute | Details |
|-----------|---------|
| Free tier | Free to use, no credit limits mentioned |
| Duration | 30, 50, or 70 seconds (configurable) |
| Commercial rights | **UNCLEAR** — no explicit commercial license; assume NO |
| Quality | Good for experimental use |
| Critical blocker | **NOT AVAILABLE IN EUROPE** (Italy excluded) |
| No vocals | Correct — cannot generate vocals |

**Verdict: BLOCKED.** Not available in Italy/Europe. Even if accessed via VPN, commercial rights are unclear. Do not use for an Italian business product.

**Sources:**
- https://www.androidauthority.com/what-is-google-musiclm-3333829/
- https://support.google.com/gemini/thread/374564367

---

### 4. Meta MusicGen (Open Source) -- RECOMMENDED

| Attribute | Details |
|-----------|---------|
| Free tier | **Completely free** — open source, self-hosted |
| Duration | Up to 30 seconds natively (can extend with techniques) |
| Commercial rights | **YES** — MIT license, explicitly permits commercial use |
| Quality | Good for instrumental/background, not vocal-capable |
| Self-hosted | Yes — runs locally with Hugging Face Transformers |
| Models | small (300M), medium (1.5B), large (3.3B) |
| Training data | 400K recordings, 20K hours, Meta-owned/licensed music |
| Hardware needs | GPU recommended (large model needs ~10GB VRAM) |

**Verdict: BEST FREE OPTION.** Open source, commercially licensed, no attribution required, runs locally. Quality is good enough for background music under voiceover. The 30-second limit is manageable for our 30-60s videos (generate two segments and crossfade, or use the melody-conditioned continuation).

**How to run locally:**
```bash
pip install transformers torch scipy
```
```python
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy

processor = AutoProcessor.from_pretrained("facebook/musicgen-large")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-large")

inputs = processor(
    text=["uplifting corporate background, piano and light strings, warm, professional, 100bpm, instrumental"],
    padding=True,
    return_tensors="pt",
)
audio_values = model.generate(**inputs, max_new_tokens=1503)  # ~30 seconds at 32kHz
scipy.io.wavfile.write("output.wav", rate=32000, data=audio_values[0, 0].numpy())
```

**Also available on Replicate API** (pay-per-use, very cheap) or **Hugging Face Spaces** (free but rate-limited).

**Prompt patterns that work well:**
```
"uplifting corporate background music, piano and soft strings, warm tone,
 professional, clean production, 100bpm, instrumental, no vocals"

"modern tech startup background, light electronic beats, ambient synth pads,
 crisp percussion, optimistic, 110bpm, instrumental"

"emotional piano ballad, building strings, cinematic, hope and confidence,
 clean mix, 90bpm, instrumental, no drums"
```

**Sources:**
- https://ai.meta.com/resources/models-and-libraries/audiocraft/
- https://huggingface.co/facebook/musicgen-large
- https://replicate.com/meta/musicgen

---

### 5. Stable Audio

| Attribute | Details |
|-----------|---------|
| Free tier | 10 credits on registration, then exhausted |
| Duration | Limited on free tier |
| Commercial rights (free) | **NO** — paid subscription required |
| Commercial rights (paid) | YES — Creator plan for individuals |
| Quality | High quality |
| Open source model | `stable-audio-open-1.0` exists on HuggingFace (limited) |

**Verdict:** Free tier is negligible (10 credits total, not per month). Not viable for our needs. The open-source model exists but has more restrictive licensing than MusicGen.

**Sources:**
- https://stableaudio.com/pricing
- https://huggingface.co/stabilityai/stable-audio-open-1.0

---

### 6. AIVA

| Attribute | Details |
|-----------|---------|
| Free tier | 3 downloads/month, up to 3 minutes each |
| Commercial rights (free) | **NO** — non-commercial license only |
| Commercial rights (paid) | Standard: limited (YouTube/Twitch/TikTok only). Pro: full commercial |
| Quality | Classical/orchestral excellent, modern genres decent |

**Verdict:** Free tier exists but NO commercial rights. 3 downloads/month is too few anyway (would take 3 months to get 9 tracks). Not suitable.

**Sources:**
- https://www.aiva.ai/legal/1
- https://singify.fineshare.com/blog/ai-music-apps/aiva

---

### 7. Soundraw

| Attribute | Details |
|-----------|---------|
| Free tier | **NO free tier** — can preview but not download |
| Pricing | Starts at $11-13/month |
| Commercial rights | Included with all paid plans |
| Quality | Good, customizable stems |

**Verdict:** No free tier at all. Not viable under ZERO COSTS constraint.

**Sources:**
- https://soundraw.io
- https://cybernews.com/ai-tools/soundraw-ai-music-generator-review/

---

### 8. Epidemic Sound

| Attribute | Details |
|-----------|---------|
| Free tier | **NO free tier** — subscription only (~$13/month) |
| AI features | "Adapt" tool for customizing tracks |
| Quality | Professional grade (human-composed + AI-enhanced) |

**Verdict:** No free option whatsoever. Premium product, premium price. Not viable.

**Sources:**
- https://www.epidemicsound.com/
- https://creatortrail.com/epidemic-sound-review-2026/

---

## Comparison Matrix

| Tool | Free Tracks | Commercial (Free) | Quality | Duration | Verdict |
|------|-------------|-------------------|---------|----------|---------|
| **MusicGen** | Unlimited | **YES** | 7/10 | 30s native | **USE THIS** |
| Suno | ~300/mo | NO | 9/10 | 4 min | Best quality, $10 for commercial |
| Udio | ~130/mo | Unclear | 8/10 | 2 min | Downloads BLOCKED |
| MusicFX | Unlimited | Unclear | 7/10 | 70s | NOT in Europe |
| Stable Audio | 10 total | NO | 8/10 | Limited | Negligible free tier |
| AIVA | 3/mo | NO | 7/10 | 3 min | Too few, no commercial |
| Soundraw | 0 | N/A | 7/10 | N/A | No free tier |
| Epidemic | 0 | N/A | 9/10 | N/A | No free tier |

---

## RECOMMENDATION

### Primary: Meta MusicGen (self-hosted)

**Why:** The ONLY option that is completely free AND explicitly permits commercial use. MIT license means no attribution required, no restrictions. Quality is good enough for background music under voiceover (the voiceover is the star, not the music).

**Implementation plan:**
1. Run MusicGen-large locally on iMac (has the GPU power)
2. Generate 3-5 variations per vertical with tailored prompts
3. Select best, crossfade/loop for 30-60s duration
4. Apply EQ ducking for voiceover mix

### Fallback: Suno $10 one-month

If MusicGen quality is insufficient, subscribe to Suno Pro for one month ($10), generate all 9 tracks with commercial rights, cancel subscription. Total cost: $10, within reason for a commercial product charging $497-897.

### Alternative: Free royalty-free libraries (non-AI)

These sites offer free, commercially-usable music (human-composed):
- **Mixkit** (mixkit.co) — Free, no attribution, commercial use OK
- **Chosic** (chosic.com) — Free royalty-free for YouTube/social
- **Fesliyan Studios** (fesliyanstudios.com) — Free commercial music
- **Pixabay Music** — Free commercial use

**Downside:** Less customizable, may not match exact emotional arc needed per vertical. But legitimate, free, and commercially safe.

---

## Music Under Voiceover: Technical Best Practices

### Volume Levels

| Element | Level | Standard |
|---------|-------|----------|
| Voiceover | -12 dB to -6 dB peak | Broadcast standard |
| Background music (during VO) | -25 dB to -20 dB | 15-20 dB below voice |
| Background music (no VO) | -12 dB to -8 dB | Can be louder in gaps |
| W3C accessibility | Voice 20 dB above background | WCAG 2.0 G56 |

### Frequency EQ for Voice Clarity

Human voice fundamentals sit at **250 Hz - 5 kHz**. For background music under voiceover:

1. **Cut music 250-500 Hz by 2-4 dB** — Makes space for male voiceover fundamentals
2. **Cut music 2-5 kHz by 2-3 dB** — Makes space for consonant clarity
3. **Boost music below 150 Hz slightly** — Keeps warmth without competing
4. **Boost music above 8 kHz slightly** — Adds shimmer/air without competing

### Ducking Technique

**Sidechain compression / volume automation:**
- Threshold: Set so music ducks when VO starts
- Attack: 50-100ms (fast but not jarring)
- Release: 200-500ms (smooth return)
- Ratio: 3:1 to 6:1
- Duck amount: -6 dB to -12 dB

**Key insight:** "The ducks you can hear are the ones that start too early." Place the volume drop microscopically AFTER the leading edge of voiceover, not before.

### Music Selection for Under-Voiceover

Best characteristics for background music under speech:
- **Minimal mid-range instrumentation** (avoid piano melody in 250-1kHz range)
- **Ambient pads and textures** over melodic lines
- **Consistent energy** (no sudden dynamic changes that distract)
- **No vocals/choir** (competes with speech)
- **Moderate tempo** (80-110 BPM, not distracting)

---

## Emotional Arc for PAS (Problem-Agitation-Solution) Videos

### Structure Mapping

| Video Section | Emotion | Music Character | Tempo | Key |
|---------------|---------|-----------------|-------|-----|
| **Problem** (0-10s) | Tension, frustration | Minor key, sparse, low strings | 70-85 BPM | Minor |
| **Agitation** (10-25s) | Urgency, pain | Building percussion, dissonance | 85-100 BPM | Minor → transition |
| **Solution** (25-40s) | Hope, relief | Major key, bright, piano/strings | 100-110 BPM | Major |
| **CTA** (40-60s) | Confidence, action | Full arrangement, uplifting | 110-120 BPM | Major |

### MusicGen Prompts per Video Section

**Problem section:**
```
"tense minimal background, low cello drone, sparse piano notes, uneasy atmosphere,
 minor key, 80bpm, cinematic, no vocals, dark ambient"
```

**Solution section:**
```
"uplifting corporate reveal, bright piano melody, warm strings swell, optimistic,
 major key, 110bpm, cinematic hope, clean production, no vocals"
```

**CTA section:**
```
"confident corporate closing, full orchestral swell, triumphant, major key,
 115bpm, inspirational, professional, no vocals, building energy"
```

### Per-Vertical Differentiation

| Vertical | Musical Flavor | Instruments | Feel |
|----------|---------------|-------------|------|
| Parrucchiere | Modern, trendy | Electronic beats + piano | Fashion-forward |
| Barbiere | Classic, confident | Acoustic guitar + light drums | Traditional cool |
| Estetica | Elegant, spa-like | Ambient pads + soft piano | Relaxing luxury |
| Palestra | High-energy | Electronic, driving beats | Motivational |
| Fisioterapia | Calm, clinical | Soft strings + piano | Professional trust |
| Meccanico | Industrial-modern | Synth bass + percussion | Strong, reliable |
| Ristorante | Warm, inviting | Acoustic guitar + light jazz | Convivial |
| Veterinario | Gentle, caring | Soft piano + ambient | Warm trust |
| Dentista | Clean, professional | Modern minimal + piano | Clinical confidence |

---

## Italian Market Music Preferences

**Confidence: LOW** (limited specific data found)

Key findings from available research:
- Italian audiences prefer **domestic/local-sounding** music over generic international
- **Nostalgia** (80s-90s) works well but not for B2B software marketing
- For B2B commercial: **modern European** style preferred over American corporate
- Avoid: overly "Silicon Valley startup" music (too American for Italian PMI)
- Prefer: warm, human-feeling production over cold electronic

**Recommendation for FLUXION videos:**
- Use **piano-forward** arrangements (universally appealing in Italy)
- Include **acoustic elements** (guitar, strings) for warmth
- Avoid pure electronic/synth tracks (feels cold for PMI audience)
- Keep it **professional but warm**, not corporate-cold

---

## Implementation Roadmap

### Step 1: Set up MusicGen on iMac
```bash
pip3 install transformers torch scipy
# Download facebook/musicgen-large model (~3.3GB)
```

### Step 2: Generate per-vertical tracks
- 3-5 variations per vertical
- Use section-specific prompts (Problem/Solution/CTA)
- Generate 30-second segments, crossfade for longer tracks

### Step 3: Post-process with FFmpeg
```bash
# Normalize volume
ffmpeg -i raw.wav -af "loudnorm=I=-23:LRA=7:TP=-2" normalized.wav

# Crossfade two 30s segments into 60s
ffmpeg -i part1.wav -i part2.wav -filter_complex \
  "[0][1]acrossfade=d=3:c1=tri:c2=tri" output.wav

# Apply EQ cut for voiceover space (duck 250-5000Hz)
ffmpeg -i music.wav -af "equalizer=f=500:t=o:w=2000:g=-4" ducked.wav
```

### Step 4: Mix with voiceover in CapCut/FFmpeg
- Music at -20dB under voiceover
- Music at -8dB in intro/outro without voiceover
- Apply sidechain ducking if CapCut supports it, otherwise manual automation

---

## Confidence Assessment

| Finding | Confidence | Reason |
|---------|------------|--------|
| Suno free = no commercial | HIGH | Official ToS verified |
| MusicGen = commercial OK | HIGH | MIT license, Meta official docs |
| Udio downloads blocked | MEDIUM | Multiple 2025-2026 sources agree |
| MusicFX not in Europe | HIGH | Multiple sources, Google docs |
| Volume levels for mixing | HIGH | Broadcast standards, W3C |
| Italian music preferences | LOW | Limited specific data |
| MusicGen quality for BG music | MEDIUM | Based on community reports, not tested |

---

## Open Questions

1. **MusicGen on iMac hardware** — Does the iMac have enough GPU/RAM for musicgen-large? CPU inference is possible but slow (~5-10 min per 30s clip). Need to test.
2. **30-second limit** — MusicGen natively generates ~30s. For 60s videos, crossfading works but needs testing for musical coherence.
3. **Hugging Face Spaces** — Free hosted inference exists but may be rate-limited. Worth testing as alternative to local install.
4. **Replicate API** — Pay-per-use (~$0.01-0.05 per generation). Could generate all 9 tracks for under $1 total if local install fails.
