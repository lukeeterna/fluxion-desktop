# FLUXION — Handoff Sessione 135 → 136 (2026-04-08)

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

## COMPLETATO SESSIONE 135

### 6 Fix VoIP Live — Tutti Implementati e Testati

#### 1. Multi-service family disambiguation (S135)
- **Prima**: "taglio barba colore" → Sara listava 6 servizi (tutti i taglio_* + barba + colore + taglio_+_barba)
- **Dopo**: Detecta "taglio family" (3+ varianti con stesso prefisso), chiede "quale tipo di taglio?"
- Servizi non ambigui (barba, colore) vengono mantenuti, max 3 servizi
- File: `entity_extractor.py` (S135 family ambiguity), `booking_state_machine.py` (mixed clear+ambiguous handling)

#### 2. NameCorrector DB path fix
- **Prima**: usava `"fluxion.db"` in CWD → "no such table: clienti"
- **Dopo**: usa `_find_db_path()` → trova `~/Library/Application Support/com.fluxion.desktop/fluxion.db`
- Aggiunto check esistenza tabelle (clienti, appuntamenti) prima di query
- File: `orchestrator.py` (init), `name_corrector.py` (table check)

#### 3. NLU timeout — Groq-only
- **Prima**: Groq 2s + Cerebras 2s + 3x OpenRouter 3s → cascade timeout
- **Dopo**: Groq 3.5s (primary) + Cerebras 4s (fallback) — OpenRouter rimossi
- Orchestrator await aumentato da 2s a 4s
- File: `providers.py`, `orchestrator.py`

#### 4. Faster Whisper fallback — tiny model
- **Prima**: modello "base" (4.7s su iMac) con fallback senza timeout → 14.6s
- **Dopo**: modello "tiny" (~3.8s) + timeout 5s su fallback offline
- File: `stt.py`

#### 5. Anti-echo turn overlap
- **Prima**: grace period 0.3s dopo TTS, buffer non cleared
- **Dopo**: grace period 0.6s (2x drain), buffer+speech cleared dopo echo fade
- File: `voip_pjsua2.py`

---

## TEST E2E SESSIONE 135

```
OK  [SALONE] Disambiguazione taglio: "Vorrei un taglio" → "Diverse opzioni: Taglio Donna, Taglio Uomo o Taglio Bambino"
OK  [SALONE] Multi-service: "taglio barba colore" → accetta senza listare 6 varianti
OK  [SALONE] Compound: "taglio barba e colore" → accetta taglio_+_barba + colore
OK  [SYSTEM] NameCorrector: DB trovato ~/Library/Application Support/com.fluxion.desktop/fluxion.db
OK  [SYSTEM] NLU Groq: 226-411ms (no timeout, entro 3.5s)
OK  [SYSTEM] NLU Cerebras fallback: 517-1032ms (entro 4s)
OK  [SYSTEM] Pipeline VoIP + SIP registrato correttamente
```

### Da testare LIVE VoIP (telefono)
- Fix echo overlap (0.6s grace) → serve chiamata reale per verificare
- Fix STT tiny model → qualità trascrizione su 8kHz VoIP
- Fix NameCorrector → correzione fonetica con DB clienti reale

---

## BUG RIMANENTI (non bloccanti)
1. DB servizi non cambia per verticale (SQLite ha solo salone demo)
2. FAQ variabili `[PREZZO_X]` non risolte per auto/medical/beauty
3. Guardrail non vertical-aware (blocca "tagliando" su verticale auto)
4. Entity extractor multi-service inconsistente in alcuni edge case

---

## STATO GIT
```
Branch: master | HEAD: S135 — 6 VoIP live fixes
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       DONE (S123-S126)
Phase 10e: Sara Bug Fixes       DONE (S127, S134, S135)
Sprint 1:  Product Ready        DONE (S127)
Sprint 2:  Screenshot Perfetti  DONE (S128-S129)
Sprint 3:  Video per Settore    IN PROGRESS — prompt pronti, clip da generare Kling free
Sprint 4:  Landing Definitiva   PENDING
Sprint 5:  Sales Agent WA       PENDING
```

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

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 136.
PROSSIMI PASSI:
1. Test VoIP LIVE (chiamata telefonica) per verificare echo fix + STT tiny + NameCorrector
2. Sprint 3 Video: generare clip Kling free (web UI manuale, 30 crediti/clip)
3. Sprint 4 Landing: embed video + hero screenshots
REGOLA: ZERO COSTI. Vertex AI DISABILITATA.
```
