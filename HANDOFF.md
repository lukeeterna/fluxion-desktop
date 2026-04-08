# FLUXION — Handoff Sessione 134 → 135 (2026-04-08)

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

## COMPLETATO SESSIONE 134

### 1. Bug critico FSM VoIP — RISOLTO
- `process_audio()` chiamava `process()` senza `session_id` → FSM resettata ogni turno
- Fix: passa `current_sid` e skip reset se sessione attiva
- **Test E2E**: booking flow salone completo funzionante

### 2. Endpoint `/api/voice/set-vertical` — CREATO
- POST `{"vertical":"auto"}` → switch verticale + business name + reset FSM
- Business names test: Salone/Officina/Studio Medico/Palestra/Centro Estetico Demo
- Tutti i 5 verticali switchano correttamente

### 3. Disambiguation fix — RISOLTO
- "Sì confermo" → accetta candidato, esce a `waiting_service`
- "Domani alle 10" → escape booking, accetta candidato + continua
- Prima: loop infinito DOB → Ora: flusso corretto

### 4. Combo service `taglio_+_barba` — AGGIUNTO
- Aggiunto a `DEFAULT_SERVICES`, `SERVICE_DISPLAY`, `VERTICAL_SERVICES`
- `extract_multi_services` usa longest-match-first
- Nota: entity extractor ancora cattura solo "barba" in alcuni casi (da investigare)

### 5. Kling client API — CREATO (non usato)
- `video-factory/kling_client.py` — client JWT completo
- API richiede saldo prepagato (min ~$4,200) → non usabile per ora
- Free tier = solo web UI manuale (30 crediti/clip, 166 crediti disponibili)

---

## STATO TEST E2E (10/10 test core + 26 test verticali)

### Test Core (salone): 10/10 ✅
- Booking flow, disambiguation, multi-service, FAQ, closing, new client, set-vertical

### Test Multi-Verticale: 14 OK / 7 WARN / 5 FAIL
- **Salone**: 4/5 OK — solo "taglio" ambiguo (3 varianti)
- **Auto**: 2/5 — guardrail blocca "tagliando", FAQ variabili non risolte
- **Medical**: 3/5 — FAQ variabili non risolte
- **Palestra**: 3/5 — FAQ generiche
- **Beauty**: 3/5 — FAQ variabili non risolte, servizi contaminati

### Bug rimanenti (NON bloccanti per salone)
1. DB servizi non cambia per verticale (SQLite ha solo salone)
2. FAQ variabili `[PREZZO_X]` non risolte per auto/medical/beauty
3. Guardrail non vertical-aware (blocca auto su auto)
4. Entity extractor multi-service inconsistente

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

### Kling API Client
```
video-factory/kling_client.py (richiede saldo API)
```

---

## STATO GIT
```
Branch: master | HEAD: S134 — 4 commit fix voice agent
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       DONE (S123-S126)
Phase 10e: Sara Bug Fixes       DONE (S127, S134)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    IN PROGRESS — prompt pronti, clip da generare Kling free
Sprint 4:  Landing Definitiva   PENDING
Sprint 5:  Sales Agent WA       PENDING
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 135.
PRIORITA:
1. Sara multi-verticale: popolare DB servizi per auto/medical/palestra/beauty
2. Fix guardrail vertical-aware + FAQ variabili per tutti i verticali
3. Test live VoIP su 0972536918 (salone funziona, testare flusso completo)
4. Kling web UI: genera clip parrucchiere (4 beat) + barbiere (2 beat)
REGOLA: ZERO COSTI. Solo Kling free tier. Vertex AI DISABILITATA.
```
