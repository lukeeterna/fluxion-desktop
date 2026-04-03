# FLUXION — Handoff Sessione 131 → 132 (2026-04-03)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 131

### 1. Ristrutturazione Enterprise Agent-First
- **CLAUDE.md**: 522 → 85 righe (max 200 target)
- **Nuovi rules**: `workflow-cove2026.md`, `architecture-distribution.md`, `e2e-testing.md`
- **settings.json**: 22 allow permissions + deny rules aggiornate
- **Model hierarchy**: Opus/Sonnet/Haiku delegation documentata

### 2. Video Factory Pipeline — Veo 3 + CapCut
- **9 prompt JSON V3** con dati reali, fonti citate, competitor per settore
- **Veo 3 auth** funzionante (OAuth2 Google → token cachato)
- **Veo 3 pipeline**: submit → fetchPredictOperation → base64 decode → MP4
- **7 clip Veo 3 generate** per parrucchiere (hook_warm v1+v2, salon_beauty v1+v2, 3 clip originali)
- **FFmpeg pipeline V5**: 108s con musica, screenshot Ken Burns, CTA con logo
- **CapCut project generator** (pyCapCut): progetto aperto con successo in CapCut Desktop
- **Copioni V2 definitivi**: 9 storyboard con dati reali e fonti (fondatore)
- **Deep research**: MoviePy vs CapCutAPI vs Shotstack vs Manim → CapCutAPI vince

### 3. Research CoVe 2026 Video Tools
- `.claude/cache/agents/moviepy-video-research-2026.md` — MoviePy NON raccomandato (10x slower v2)
- `.claude/cache/agents/capcut-api-research-2026.md` — CapCutAPI/pyCapCut raccomandato
- `.claude/cache/agents/video-tools-comparison-2026.md` — Shotstack backup, Manim skip

### 4. Remotion 9:16 (bloccato da macOS)
- Componenti creati: VerticalVideo, ScreenshotScene, Veo3Scene, CTAScene
- TypeScript: 0 errori
- **BLOCCATO**: macOS 11 (MacBook) e 12 (iMac) troppo vecchi per Remotion 4.x Chromium
- Tutto pronto per quando si aggiorna macOS

---

## FIX DA APPLICARE SESSIONE 132

### Video CapCut Parrucchiere — 3 fix richiesti dal fondatore:
1. **Prezzo**: "Base €297" NON ESISTE → deve essere **€497** (Base) o **€897** (Pro)
2. **URL landing**: deve essere **fluxion-landing.pages.dev** (NON fluxion.app)
3. **"Voice AI"** → rinominare **"Segretaria AI"** o **"Assistente AI Sara"**

### Poi: generare gli altri 8 verticali CapCut
- Barbiere, Officina, Carrozzeria, Dentista, Estetica, Nail, Palestra, Fisioterapista
- Stessa struttura: Veo3 hook + 6 screenshot + CTA
- Voiceover Edge-TTS per ognuno
- Costo Veo 3: ~€72 rimanenti (8 × 3 clip × ~€3)

---

## STATO GIT
```
Branch: master | HEAD: 78d5095
Modifiche non committate: CLAUDE.md restructure + video-factory + rules + settings
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       DONE (S123-S126)
Phase 10e: Sara Bug Fixes       DONE (S127)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    IN PROGRESS — CapCut pipeline funzionante, 1/9 video
Sprint 4:  Landing Definitiva   PENDING
Sprint 5:  Sales Agent WA       PENDING
```

---

## ASSET DISPONIBILI

### Video Parrucchiere
- `video-factory/output/parrucchiere/clips/parrucchiere_salon_beauty_v1.mp4` (3.3MB)
- `video-factory/output/parrucchiere/clips/parrucchiere_salon_beauty_v2.mp4` (5.2MB)
- `video-factory/output/parrucchiere/clips/parrucchiere_hook_warm_v1.mp4` (3.7MB)
- `video-factory/output/parrucchiere/clips/parrucchiere_hook_warm_v2.mp4` (3.4MB)
- `video-factory/output/parrucchiere/parrucchiere_80s_v3.mp4` (25MB, FFmpeg V5 con musica)
- `~/Desktop/fluxion_media/` — tutti i media copiati su SSD locale per CapCut

### CapCut
- **pyCapCut** installato: `pip3 install pyCapCut`
- **VectCutAPI** clonato: `tools/VectCutAPI/`
- **Script generatore**: `video-factory/build_capcut_v2.py`
- **Draft folder CapCut**: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`

### Voiceover
- Edge-TTS IsabellaNeural funzionante
- Voiceover generati per parrucchiere (8 blocchi)

---

## PROSSIMA SESSIONE 132

### A. Fix video parrucchiere (15 min)
1. Fix €497 (non €297)
2. Fix URL fluxion-landing.pages.dev
3. "Segretaria AI Sara" (non "Voice AI")
4. Rigenera progetto CapCut → export

### B. Genera 8 verticali rimanenti (2-3h)
1. Per ogni verticale: genera 3 clip Veo 3 (~€72 totali)
2. Genera voiceover Edge-TTS
3. Crea progetto CapCut con pyCapCut
4. Export da CapCut Desktop

### C. Framework Agent-First (applicare in OGNI task)
```
FASE 0: Skill ID → identifica skill/agent per il task
FASE 1: Research → 2+ subagenti paralleli
FASE 2: Plan → AC misurabili
FASE 3: Implement → commit atomici
FASE 4: Review → /fluxion-code-review
FASE 5: Verify → TEST E2E
FASE 6: Deploy → git push + sync + update
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 132.
PRIORITA:
1. Fix 3 bug video parrucchiere (€497, URL, "Segretaria AI")
2. Genera CapCut + export per parrucchiere definitivo
3. Genera 8 verticali: Veo 3 clips + CapCut projects
4. Upload Vimeo + landing embed
```
