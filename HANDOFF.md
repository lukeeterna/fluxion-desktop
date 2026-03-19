# FLUXION — Handoff Sessione 91 → 92 (2026-03-19)

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
Branch: master | HEAD: 184550e (non pushato)
Uncommitted: nessuno
type-check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 91

### Commit S91 (5 commit)
| # | Commit | Descrizione |
|---|--------|-------------|
| 1 | `158b00a` | Tier strategy definitiva — Base €497 / Pro €897, Clinic rimosso |
| 2 | `9aac8c7` | Audit UI — 18 console.log rimossi, VoipSettings nascosto, guida-pmi VoIP rimosso (-1206 righe) |
| 3 | `4201b5f` | SRT subtitle #8 — "telefono" → "gestisce le prenotazioni" |
| 4 | `fa7ab86` | **CF Workers Proxy API** — Ed25519 auth + NLU proxy + Sara trial lock |
| 5 | `184550e` | **WhatsApp 1-tap** — wa.me deep links + 6 template IT + bottone conferma |

### Dettaglio Implementazioni

#### CF Workers Proxy API (`fluxion-proxy/`)
- **Ed25519 verification** via WebCrypto (NODE-ED25519) in CF Workers runtime
- **Hono router** con CORS per origini Tauri
- **Auth middleware**: verifica firma, cache KV 24h, revocation list
- **Phone-home** (`POST /api/v1/phone-home`): validazione license + Sara trial status
- **NLU proxy** (`POST /api/v1/nlu/chat`): Groq → Cerebras → OpenRouter fallback
- **Rate limiting**: 200 NLU calls/giorno per licenza (counter KV)
- **Trial lock**: 30 giorni Sara per Base/Trial, server-side timestamp (tamper-proof)
- **Client**: `src/lib/phone-home.ts` — offline grace period 7 giorni, localStorage cache
- **Costo**: $0/mese fino a ~500 clienti (CF free tier)
- **DA FARE**: deploy su CF (`wrangler deploy`), set secrets, create KV namespace

#### WhatsApp 1-tap (`src/lib/whatsapp-1tap.ts`)
- `normalizePhone()`: +39/0039/3xx → formato wa.me (393331234567)
- `buildWhatsAppUrl()`: costruisce `https://wa.me/{phone}?text={msg}`
- `sendWhatsApp1Tap()`: apre URL via `@tauri-apps/plugin-opener`
- **6 template IT**: conferma, reminder24h, cancellazione, compleanno, follow-up, waitlist
- **Bottone "WhatsApp"** in AppuntamentoDialog (verde, icona MessageCircle)
- Zero costo, zero rischio ban Meta

#### Audit UI Fix
- **18 console.log** rimossi da `use-voice-pipeline.ts` + 1 da `App.tsx`
- **VoipSettings** rimosso da Impostazioni (nascosto per v1)
- **guida-pmi.html**: sezione deviazione chiamata rimossa, copy aggiornata (Sara in-app)
- **SetupWizard**: rimosso riferimento VoIP EhiWeb
- **Backup file** eliminato (`use-voice-pipeline.ts.backup`)

---

## ⭐ DA FARE S92 (in ordine di priorità)

### 1. Deploy CF Worker su Cloudflare (PRIORITÀ ASSOLUTA)
- `cd fluxion-proxy && wrangler deploy`
- Creare KV namespace: `wrangler kv:namespace create LICENSE_CACHE`
- Aggiornare `wrangler.toml` con ID namespace reale
- Set secrets: `wrangler secret put ED25519_PUBLIC_KEY` (+ GROQ/CEREBRAS/OPENROUTER API keys)
- Test `/health` endpoint
- **Effort**: 30min

### 2. Wire phone-home nell'app
- Integrare `src/lib/phone-home.ts` nel ciclo di vita app (startup + interval 24h)
- Hook `usePhoneHome()` in `App.tsx` o `Dashboard.tsx`
- UI: banner "Sara si disattiva tra X giorni" per Base tier
- UI: banner "Modalità offline — funzionalità limitate" se grace period vicino
- **Effort**: 2-3h

### 3. Prezzi Rust alignment (iMac)
- `license_ed25519.rs`: aggiornare prezzi 199/399/799 → 497/897
- Rimuovere tier 'enterprise' dal Rust code
- Build su iMac
- **Effort**: 30min

### 4. PyInstaller sidecar build (iMac)
- Update voice-agent.spec (collect_all, UPX off, hidden imports)
- get_resource_path() per _MEIPASS
- tauri-plugin-shell + capabilities + sidecar.rs
- Build su iMac Intel
- **Research pronta**: `.claude/cache/agents/` (S90)
- **Effort**: 4-8h

### 5. Landing page redeploy
- Aggiornare con nuove pagine (installazione)
- Deploy su Cloudflare Pages
- **Effort**: 1h

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

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 92. Priorità:
1. Deploy CF Worker su Cloudflare (wrangler deploy + secrets + KV)
2. Wire phone-home nell'app (hook React + UI banner trial)
3. Prezzi Rust alignment su iMac
4. PyInstaller sidecar build
DIRETTIVE: SEMPRE code reviewer, SEMPRE 1 nicchia, ZERO costi, copy PERFETTA, VoIP solo Pro.
```
