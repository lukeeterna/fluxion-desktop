# FLUXION — Handoff Sessione 133 → 134 (2026-04-04)

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

## COMPLETATO SESSIONE 133

### 1. veo3_client.py aggiornato per Veo 3.1 GA
- Supporta tutti i tier: `3.1` / `3.1-fast` / `3.1-lite` / `3.0` / `2.0`
- Alias: `fast` → `3.1-fast`, `standard` → `3.1`
- Nuovi parametri: `resolution`, `personGeneration`, `storageUri`
- `load_storyboard()` carica JSON v1 direttamente in VeoRequest
- CLI: `python veo3_client.py storyboard --file storyboards/X.json`

### 2. 9 JSON storyboard PAS v1 — `output/storyboards/`
- Schema v1: 5 beat (HOOK/PROBLEM/AGITATION/SOLUTION/CTA), 30s
- 36 prompt video cinematografici pronti per Kling/Veo
- Copioni da `copioni_v2_definitivi.txt` con dati reali + fonti
- CTA frame con layout grafico
- Music config + WA message per ogni verticale

### 3. kling_iterate.py — Workflow iterazione prompt
- `export --vertical X`: prompt per copia-incolla su klingai.com
- `log --vertical X --beat N --rating good`: registra risultato
- `status`: dashboard 36 prompt con stato proven
- `export-veo --vertical X`: esporta proven per batch (futuro)

### 4. Musica royalty-free scaricata
- 4 tracce Incompetech (Kevin MacLeod, CC) in `assets/music/`
- tense_background.mp3, uplifting_commercial.mp3, cta_punch.mp3, notification_ding.mp3

### 5. Vertex AI — CREDITI ESAURITI
- **€204.73 totali spesi** (crediti coperto €183.90, €20.83 reali dalla carta)
- Vertex AI API **DISABILITATA** — MAI riabilitare senza ok fondatore
- Da ora: SOLO strumenti gratuiti (Kling 3.0 free 66 credits/day)

---

## ASSET DISPONIBILI

### Clip Veo 2.0 esistenti (48 file)
```
~/Desktop/fluxion_media/{verticale}/clips/{verticale}_clip{1-3}_v{1-2}.mp4
```

### Voiceover Edge-TTS (9 file)
```
~/Desktop/fluxion_media/{verticale}/{verticale}_voiceover.mp3
```

### Storyboard JSON v1 (9 file)
```
video-factory/output/storyboards/{verticale}.json
```

### Musica royalty-free (4 tracce)
```
video-factory/assets/music/*.mp3
```

### Copioni V2
```
video-factory/output/copioni_v2_definitivi.txt
```

---

## STATO GIT
```
Branch: master | HEAD: post-S133 commit
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       DONE (S123-S126)
Phase 10e: Sara Bug Fixes       DONE (S127)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    IN PROGRESS — storyboard+prompt pronti, clip da generare su Kling free
Sprint 4:  Landing Definitiva   PENDING
Sprint 5:  Sales Agent WA       PENDING
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 134.
PRIORITA:
1. Apri klingai.com → genera clip con i 36 prompt (kling_iterate.py export --vertical parrucchiere)
2. Per ogni clip buona: python kling_iterate.py log --vertical X --beat N --rating good
3. Assembla video con FFmpeg: clip + voiceover + musica + CTA frame
4. Quando 9 video pronti → embed su landing
REGOLA: ZERO COSTI. Solo Kling free tier. Vertex AI DISABILITATA.
```
