# FLUXION — Handoff Sessione 33 (2026-03-06)

## ⚡ PRINCIPIO CoVe 2026 — SEMPRE IN OGNI TASK (CTO Approvato Sessione 31)

> **"Non implementare feature. Colma gap reali delle PMI italiane."**
>
> Ogni commento, ogni componente deve portare la risposta: *"perché questo è world-class?"*
>
> Deep Research CoVe 2026 = **identifica il gap reale** → implementa il salto competitivo.

---

## ⚠️ LEGGERE PRIMA DI TUTTO — GUARDRAIL SESSIONE

**Working directory corretta**: `/Volumes/MontereyT7/FLUXION`
**Memory corretta**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

Se Claude Code è aperto da `/Volumes/MontereyT7` (root T7) → memory SBAGLIATA → chiudi e riapri da `/Volumes/MontereyT7/FLUXION`.

Il T7 contiene anche `backup-combaretrovamiauto-20260306_144150/` — backup temporaneo pre-upgrade macOS iMac di un progetto DIVERSO. Ignorare completamente. Non leggere, non citare, non includere.

---

## STATO GIT
```
Branch: master | HEAD: d321e66
CI: ✅ verde (tutti i run success)
type-check: 0 errori
cargo check iMac: 0 errori
```

---

## PROSSIMO TASK: F07 — LemonSqueezy Payment Integration

### Decisione CTO CoVe 2026 — ordine esecuzione
```
1. F07 LemonSqueezy   [3h] — REVENUE blocker. Senza pagamento non esiste business.
2. P0.5 Onboarding    [4h] — VENDITE blocker. Senza setup frictionless F07 è inutile.
3. F06 schede gap     [2h] — QUALITÀ. Non blocca prima vendita.
```

### Stato F07
- Account LemonSqueezy Kashish: **APPROVATO** ✅
- Store LemonSqueezy: **NON ANCORA CREATO** ← primo step
- Server webhook: `scripts/license-delivery/server.py` ✅ già completo
- `scripts/license-delivery/config.env`: **NON ESISTE** — va creato con credenziali reali (non in git)
- **BUG da fixare**: `server.py` riga 74 mappa `"fluxion enterprise"` → deve essere `"fluxion clinic"`

### Prodotti da creare su LemonSqueezy (nomi esatti — il server fa `.lower()`)
| Nome prodotto | Prezzo | Tier interno |
|---------------|--------|-------------|
| `FLUXION Base` | €497 | `base` |
| `FLUXION Pro` | €897 | `pro` |
| `FLUXION Clinic` | €1.497 | `clinic` |

### Acceptance Criteria F07
- [ ] Fix `"fluxion enterprise"` → `"fluxion clinic"` in server.py
- [ ] 3 prodotti creati su LemonSqueezy con nomi esatti
- [ ] Webhook configurato → Signing Secret nel config.env
- [ ] config.env compilato (LS_WEBHOOK_SECRET + SMTP_USER + SMTP_PASS + KEYGEN_PATH + KEYPAIR_PATH)
- [ ] Server avviato su iMac porta 3010
- [ ] Cloudflare Tunnel espone `/webhook/lemonsqueezy` pubblicamente
- [ ] Test acquisto → licenza attivata in <5s
- [ ] In-app upgrade path (Base → Pro → Clinic) in UI Tauri

---

## STATO F06 — Media Upload Schede Cliente

**Sprint A** ✅ `7601ca3` — MediaUploadZone/Gallery/Lightbox/ConsentModal, Migration 030
**Sprint B** ✅ `3fdd19a` — BeforeAfterSlider, ProgressTimeline, VideoThumbnail
**Sprint C** ✅ `847fcbe` — ImageAnnotator, SchedaCarrozzeria Foto tab, PDF export

**Schede con media integrato** (verificato sul codice):
| Scheda | Media |
|--------|-------|
| SchedaCarrozzeria | ✅ + ImageAnnotator |
| SchedaEstetica | ✅ |
| SchedaMedica | ✅ |
| SchedaParrucchiere | ✅ |
| SchedaFitness | ❌ gap |
| SchedaFisioterapia | ❌ gap |
| SchedaOdontoiatrica | ❌ gap |
| SchedaVeicoli | ❌ gap |

**Nota**: ROADMAP diceva Sprint B aveva fatto SchedaFitness — il codice dice il contrario. Gap reale confermato. Non blocca prima vendita (verticali principali coperti).

---

## STATO KAGGLE NOTEBOOK
- File: `_bmad-output/kaggle-fluxion-generator.ipynb`
- Scopo: genera mockup UI con FLUX.1-schnell su P100 per landing/marketing
- **Stato**: FUNZIONANTE ✅ (sessione 33, 2026-03-06) — v19 = Kaggle kernel v11
- Pattern: pre-encode T5+CLIP → del → pipeline float16 + sequential_cpu_offload (zero bitsandbytes)

---

## Completato Sessione 33
| Lavoro | Esito |
|--------|-------|
| Kaggle notebook fix P100 | ✅ FUNZIONANTE v19 |
| CI verde verificata (GitHub API) | ✅ d321e66 success |
| Memory path corretto identificato e guardrail aggiunti | ✅ |
| Analisi gap F06 schede | ✅ 4 schede senza media |
| Decisione CTO ordine F07→P0.5→F06 | ✅ |
| Bug server.py "enterprise"→"clinic" identificato | ✅ da fixare |

---

## PROMPT RIPARTENZA SESSIONE 34

```
Sessione 34 — F07 LemonSqueezy

⚠️ PRIMA DI TUTTO:
- Sei in /Volumes/MontereyT7/FLUXION (working dir corretta)?
- Hai letto MEMORY.md da /Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md?
- Ignora backup-combaretrovamiauto-* nel T7 — progetto diverso, non pertinente.

STATO:
- CI ✅ verde | HEAD: d321e66
- LemonSqueezy account approvato, store NON ancora creato
- server.py esiste ma ha bug: "fluxion enterprise" → "fluxion clinic" (riga 74)
- config.env mancante — credenziali da raccogliere

STEP 1: fix server.py "enterprise" → "clinic"
STEP 2: Luke crea 3 prodotti su LemonSqueezy (FLUXION Base/Pro/Clinic)
STEP 3: Luke crea webhook → fornisce Signing Secret + SMTP credentials
STEP 4: creare config.env + avviare server su iMac porta 3010
STEP 5: Cloudflare Tunnel → test acquisto end-to-end
STEP 6: in-app upgrade path UI Tauri

Procedi con RESEARCH → PLAN → IMPLEMENT → VERIFY → DEPLOY
```
