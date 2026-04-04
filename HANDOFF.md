# FLUXION — Handoff Sessione 132 → 133 (2026-04-04)

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

## COMPLETATO SESSIONE 132

### 1. Fix URL video pipeline
- **`fluxion.app` → `fluxion-landing.pages.dev`** in 8 file sorgente + 12 file output
- €497 e "Sara" erano già corretti ovunque (non servivano fix)

### 2. Veo 2.0 — 48 clip generate per 9 verticali
- **Migrato da Veo 3.0-preview a Veo 2.0 GA** (3.0 richiedeva accesso speciale scaduto)
- **veo3_client.py** aggiornato: fetchPredictOperation polling + base64 video extraction
- **Budget tracker** con hard stop, log persistente, stima conservativa +20% margine
- 8 verticali × 3 clip × 2 varianti = **48 file MP4** (~€150 crediti Google)
- Barbiere, Officina, Carrozzeria, Dentista, Centro Estetico, Nail Artist, Palestra, Fisioterapista

### 3. Edge-TTS voiceover — 8 verticali
- `generate_all_voiceovers.py` — 8/8 voiceover IsabellaNeural generati

### 4. CapCut — 9 progetti draft
- `build_capcut_all.py` — genera draft CapCut per ogni verticale
- Screenshot specifici per verticale (scheda veicoli, odontoiatrica, fitness, estetica, etc.)
- CTA con competitor line specifico per settore
- 9 draft pronti in CapCut Desktop per export manuale

### 5. Google Cloud sicurezza
- Vertex AI API **disabilitata** (impossibile generare costi)
- Budget alert **€1** creato su billing account
- `veo3_cost_log.json` traccia ogni richiesta

---

## STATO GIT
```
Branch: master | HEAD: aa04582
Ultimo commit: feat(S132): 9 verticali Veo 2.0 + CapCut pipeline completo + budget tracker
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       DONE (S123-S126)
Phase 10e: Sara Bug Fixes       DONE (S127)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    DONE (S132) — 9 verticali, 48 clip, 9 CapCut draft
Sprint 4:  Landing Definitiva   PENDING — embed video + hero screenshots
Sprint 5:  Sales Agent WA       PENDING
```

---

## ASSET VIDEO (su disco locale, gitignored)

### Clip Veo 2.0 (48 file)
```
video-factory/output/{verticale}/clips/{verticale}_clip{1-3}_v{1-2}.mp4
```
Verticali: parrucchiere, barbiere, officina, carrozzeria, dentista, centro_estetico, nail_artist, palestra, fisioterapista

### Voiceover Edge-TTS (9 file)
```
video-factory/output/{verticale}/{verticale}_voiceover.mp3
```

### CapCut Drafts (9 progetti)
```
~/Movies/CapCut/User Data/Projects/com.lveditor.draft/
  FLUXION_Parrucchiere
  FLUXION_Barbiere
  FLUXION_Officina
  FLUXION_Carrozzeria
  FLUXION_Dentista
  FLUXION_CentroEstetico
  FLUXION_NailArtist
  FLUXION_Palestra
  FLUXION_Fisioterapista
```

---

## EXPORT CAPCUT — ISTRUZIONI

1. Apri **CapCut Desktop**
2. Nella home, sezione **Drafts** → trovi 9 progetti `FLUXION_*`
3. Per ogni progetto:
   - Click per aprire
   - Verifica timeline (hook Veo 8s → 6 screenshot → CTA)
   - **Esporta**: 1080×1920, 30fps, qualità Alta
   - Salva in `video-factory/output/{verticale}/{verticale}_finale.mp4`
4. Ripeti per tutti e 9

---

## PROSSIMA SESSIONE 133

### A. Video export + upload (se CapCut export completato)
1. Upload 9 video su Vimeo
2. Embed nella landing page (sezioni verticali)

### B. Sprint 4: Landing Definitiva
1. Sezioni verticali con video embed
2. Hero screenshots aggiornati
3. Testimonial/social proof

### C. Sprint 5: Sales Agent WhatsApp
1. Scraping contatti PMI per verticale
2. WhatsApp outreach automatico con video

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 133.
PRIORITA:
1. Export 9 video da CapCut Desktop
2. Upload Vimeo + embed landing
3. Sprint 4: Landing Definitiva con video per settore
```
