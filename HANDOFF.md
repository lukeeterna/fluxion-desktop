# FLUXION — Handoff Sessione 90 → 91 (2026-03-19)

## CTO MANDATE — NON NEGOZIABILE
> **"COPY E IMMAGINI PERFETTE. Code signing GRATIS. ZERO COSTI licensing. VoIP NON in v1 Base. ARGOS = ALTRO progetto. SEMPRE 1 NICCHIA per tier. USA SEMPRE SKILL CODE REVIEWER."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | **iMac DISPONIBILE**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22

---

## STATO GIT
```
Branch: master | HEAD: 32d34e7 (pushed)
Uncommitted: setup.ts + license-ed25519.ts + LicenseManager.tsx (tier fix)
type-check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 90

### Decisioni Strategiche (TUTTE MEMORIZZATE)
1. **WhatsApp v1**: Opzione A — 1-tap safe (`https://wa.me/{phone}?text={msg}`), zero rischio, zero costo
2. **Tier Strategy DEFINITIVA**:
   - **Base €497**: 1 nicchia, gestionale completo, Sara 30gg trial poi si blocca
   - **Pro €897**: 1 nicchia, gestionale + Sara AI sempre + VoIP Telnyx + WhatsApp + Loyalty
   - **SEMPRE 1 nicchia** — una PMI = un'attività (MAI multi-nicchia)
   - **Clinic**: nascosto dalla UI, riattivare dopo validazione mercato
3. **Leva upgrade Base→Pro**: Sara trial lock 30gg + reminder countdown
4. **Protezione anti-crack**: Phone-home via Cloudflare Worker (GRATIS) + Ed25519 + HW fingerprint
5. **Zero costi**: MAI servizi a pagamento per licensing (no Keygen.sh, no Keyforge)

### Fix Implementati
- **setup.ts**: prezzi 199/399/799 → 497/897, Clinic/Enterprise rimosso, copy "nicchia"
- **license-ed25519.ts**: allineato con nuovi tier (Base+Pro only), copy "nicchia"
- **LicenseManager.tsx**: upgrade path senza enterprise
- **Zod schema**: rimosso 'enterprise' da enum license_tier
- **Type-check**: 0 errori ✅

### Research CoVe 2026 Completata (4 subagenti)
- **Cloudflare Workers Proxy**: architettura, Ed25519 auth, rate limiting, fallback chain, $0/mese fino 100 clienti
- **WhatsApp 1-tap**: `wa.me` schema cross-platform, 6 template IT, UX flow
- **YouTube SRT**: copy aggiornata, SEO keywords, timing ottimizzato
- **PyInstaller sidecar**: one-file, ~160-220MB (non 520), spec file, tauri-plugin-shell needed

### Audit UI Completato
| Severità | Problema | Status |
|----------|---------|--------|
| CRITICAL | setup.ts prezzi sbagliati | ✅ FIXATO |
| CRITICAL | guida-pmi.html descrive VoIP v1 | ⏳ TODO |
| HIGH | VoipSettings visibile in Impostazioni | ⏳ TODO |
| HIGH | console.log() in produzione | ⏳ TODO |

---

## ⭐ DA FARE S91 (in ordine di priorità)

### 1. Cloudflare Workers Proxy API (PRIORITÀ ASSOLUTA)
- Auth Ed25519 + HW fingerprint → Groq + Cerebras fallback
- Phone-home license validation (anti-crack per TUTTO il gestionale)
- Sara trial lock 30gg su tier Base
- Rate limit: 200 call NLU/giorno per licenza
- Grace period 7gg offline
- **Research pronta**: `.claude/cache/agents/cloudflare-workers-proxy-research.md` (nel contesto S90)
- **Account CF**: `22ddff3a4ef544511523a841b3dcadf8`
- **Effort**: 4-6h

### 2. Audit UI fix residui
- Rimuovere console.log (App.tsx + use-voice-pipeline.ts)
- Nascondere VoipSettings in Impostazioni
- Aggiornare guida-pmi.html (rimuovere sezioni VoIP)
- **Effort**: 1-2h

### 3. SRT Video aggiornato
- Subtitle #8: "Risponde al telefono" → "Gestisce le prenotazioni dei clienti"
- YouTube SEO: title, description, tags ottimali
- **Effort**: 30min

### 4. WhatsApp 1-tap implementazione
- `src/lib/whatsapp-1tap.ts`: normalizePhone, buildUrl, sendWhatsApp1Tap, fillTemplate
- 6 template messaggi IT (conferma, reminder, cancellazione, birthday, follow-up, waitlist)
- Bottone "Invia su WhatsApp" nell'app
- **Research pronta**: nel contesto S90
- **Effort**: 2-3h

### 5. PyInstaller sidecar build (iMac)
- Update voice-agent.spec (collect_all, UPX off, hidden imports)
- get_resource_path() per _MEIPASS
- tauri-plugin-shell + capabilities + sidecar.rs
- Build su iMac Intel
- **Research pronta**: nel contesto S90
- **Effort**: 4-8h

---

## DIRETTIVE CTO (NON NEGOZIABILI)

1. **COPY E IMMAGINI PERFETTE** — usa SEMPRE skill copy per testo commerciale
2. **SEMPRE skill code reviewer** dopo ogni implementazione significativa
3. **Code signing GRATIS** — ad-hoc macOS + MSI unsigned Windows
4. **ZERO COSTI** per licensing, protezione, infra (tutto gratis: CF Worker, Ed25519, HW fingerprint)
5. **VoIP solo Pro** — Base = gestionale + Sara 30gg trial, Pro = Sara sempre + Telnyx VoIP
6. **SEMPRE 1 nicchia** — una PMI = un'attività. MAI multi-nicchia.
7. **ARGOS = reference** — progetto separato
8. **Deep research CoVe 2026** — SEMPRE subagenti PRIMA di implementare

---

## FILE UNCOMMITTED (da committare a inizio S91)
```
M src/types/setup.ts          — tier fix (497/897, no Clinic, nicchia-based)
M src/types/license-ed25519.ts — allineato con nuovi tier
M src/components/license/LicenseManager.tsx — upgrade path senza enterprise
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 91. PRIMA DI TUTTO:
1. Committa i file uncommitted (tier fix S90)
2. Cloudflare Workers Proxy API (license validation + anti-crack + Sara proxy)
3. Audit UI fix residui (console.log, VoipSettings, guida-pmi)
4. SRT video aggiornato
5. WhatsApp 1-tap implementazione
DIRETTIVE: SEMPRE code reviewer, SEMPRE 1 nicchia, ZERO costi, copy PERFETTA, VoIP solo Pro.
```
