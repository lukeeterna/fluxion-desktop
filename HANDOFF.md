# FLUXION — Handoff Sessione 66 → 67 (2026-03-13)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 (bind 127.0.0.1) | Test via SSH

---

## STATO GIT
```
Branch: master | HEAD: af4227a
feat(voice): GAP-P1-1/P1-2/P1-8 Sprint 5 — intl phone, email priority, multi-operator
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
MacBook pytest: 1461 PASS / 0 new failures ✅
iMac pytest: 1477 PASS / 0 FAIL ✅ (+10 vs S65)
```

---

## COMPLETATO SESSIONE 66

### 1. EHIWEB Risposto (2026-03-13)
Email da Tatiana Semincov: numero SIP in attivazione, email credenziali entro 24/48h.
Allegato tutorial ZoIPer Android. → **F15 test SIP pronto appena arrivano credenziali**

### 2. GAP-P1-1 — Intl Phone Formats (commit `af4227a`)
`extract_phone()` ora gestisce tutti i formati internazionali italiani:
- `0039 333 1234567` → `3331234567` (strips `0039`)
- `39 345 6789012` → `3456789012` (strips `39` bare prefix)
- `+39 333 1234567` → `+393331234567` (backward compat: keeps `+`)
- Fix `_is_valid_mobile()`: `len >= 12` (era `> 11`), length gate 9-10
- AGCOM range `3[1-8]` instead of `3\d{2}` (evita falsi positivi `39x`)
- 10 nuovi test cases → tutti PASS

### 3. GAP-P1-2 — Email Keyword Priority + STT Artifacts (commit `af4227a`)
`extract_email()` ora supporta:
- **Keyword anchoring** (Dialogflow/Rasa pattern): cerca dopo "la mia email è", "mail è", "indirizzo email", "mia mail"
  - Es: "support@azienda.it, la mia email è mario@gmail.com" → `mario@gmail.com` ✅
- **STT artifacts**: `chiocciola`→`@`, `at`→`@`, `punto`→`.`, collapse spaces@
  - Es: "mario chiocciola gmail punto com" → `mario@gmail.com` ✅
- Fallback comportamento invariato (primo match se nessun anchor)
- 8 nuovi test cases → tutti PASS

### 4. GAP-P1-8 — Multi-Operator Selection (commit `af4227a`)
- `ExtractedOperatorList` dataclass: `names: List[str]`, `is_any: bool`
- `extract_operators_multi()`: trigger + re.findall pattern
  - "voglio Mario o Giulia" → `[Mario, Giulia]`
  - "sia Marco che Laura" → `[Marco, Laura]`
  - "con Marco oppure con Luca" → `[Marco, Luca]`
  - "Marco o chiunque" → `[Marco]`, `is_any=True`
- `ExtractionResult.operators: List[ExtractedOperator]` (backward compat: `result.operator = operators[0]`)
- `BookingContext.operator_names: List[str]` ordered preference list
- `_update_context_from_extraction()` popola `operator_names`
- `get_summary()` mostra "con Mario o Giulia" per multi-op
- 10 nuovi test cases → tutti PASS

---

## F15 VoIP — PRONTO PER TEST

✅ **EHIWEB risposto** — credenziali SIP in arrivo entro 24/48h (da: 2026-03-13)
Architettura F15 già implementata (voip.py, migration 032, VoipSettings.tsx).

Appena arrivano le credenziali:
1. Configura `config.env` su iMac con `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER`
2. Testa endpoint `/api/voice/voip/status`
3. Test chiamata end-to-end ZoIPer → Sara

---

## F07 — Config.env iMac (BLOCKERS mancanti)

```bash
LS_WEBHOOK_SECRET=<preso da LemonSqueezy webhook settings>
SMTP_USER=<email@gmail.com>
SMTP_PASS=<16-char app password da myaccount.google.com/apppasswords>
ACTIVATE_URL_BASE=https://<dominio-cloudflare> (tunnel già attivo)
FLUXION_KEYGEN_PATH=/Users/gianlucadistasi/fluxion-keygen
KEYPAIR_PATH=/Users/gianlucadistasi/fluxion-keypair.json
```

---

## PROSSIMA SESSIONE S67

> **Skill**: `fluxion-voice-agent` (se GAP residui) o `fluxion-tauri-architecture` (F15/F07)

### Priorità S67 (in ordine):
1. **SE credenziali EHIWEB arrivate** → F15 test SIP end-to-end (VoIP)
2. **F07 go-live** → se credenziali config.env disponibili
3. **GAP residui** → verifica se restano P1 gaps dopo Sprint 5

### Sprint 5 Summary:
| GAP | Stato | Sessione |
|-----|-------|---------|
| P1-1 | ✅ DONE | S66 |
| P1-2 | ✅ DONE | S66 |
| P1-7 | ✅ DONE | S65 |
| P1-8 | ✅ DONE | S66 |

**Sprint 5 COMPLETATO** — tutti i GAP P1 implementati!

### Al via sessione S67:
```bash
# Verifica pytest iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python \
  -m pytest tests/ --tb=short 2>&1 | tail -5"
```
