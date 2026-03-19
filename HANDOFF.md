# FLUXION — Handoff Sessione 92 → 93 (2026-03-19)

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
Branch: master | HEAD: 830024b (pushato ✅)
Uncommitted: nessuno
type-check: 0 errori ✅
cargo check iMac: OK ✅
```

---

## COMPLETATO SESSIONE 92

### Commit S92 (2 commit)
| # | Commit | Descrizione |
|---|--------|-------------|
| 1 | `6ef29da` | CF Worker deployed + phone-home wired + Rust tier info aligned |
| 2 | `830024b` | Rust LicenseTier::price() aligned — 497/897/1497 |

### Dettaglio Implementazioni

#### CF Worker LIVE ✅
- **URL**: `https://fluxion-proxy.gianlucanewtech.workers.dev`
- **Health**: `/health` → 200 OK ✅
- **KV**: `LICENSE_CACHE` ID `12dbb4f8d88441429d07799764e8c3d9`
- **Secrets**: ED25519_PUBLIC_KEY, GROQ_API_KEY, CEREBRAS_API_KEY, OPENROUTER_API_KEY — tutti settati
- **Costo**: $0/mese (CF free tier)
- **wrangler.toml**: KV ID aggiornato da placeholder a reale

#### Phone-Home Wired ✅
- `src/lib/phone-home.ts`: URL fixato a `fluxion-proxy.gianlucanewtech.workers.dev`
- `src/hooks/use-phone-home.ts`: hook startup + 24h interval, graceful fallback se no token
- `src/components/license/SaraTrialBanner.tsx`: countdown ≤14gg, CTA upgrade, offline warning
- `src/components/layout/MainLayout.tsx`: banner wired tra Header e contenuto
- `src-tauri/src/commands/license_ed25519.rs`: nuovo comando `get_license_token_ed25519` (esporta signed license base64)
- `src-tauri/src/lib.rs`: comando registrato

#### Prezzi Rust Allineati ✅
- `LicenseTier::price()`: 199/399/799 → 497/897/1497
- `get_tier_info_ed25519()`: Base €497, Pro €897, enterprise rimosso dalla lista UI
- `cargo check` su iMac: OK ✅

#### CF Token Aggiornato
- Token `fluxion-tunnel` rigenerato con permessi Workers KV + Workers Scripts
- Memory `reference_cloudflare_token.md` aggiornata

---

## ⭐ DA FARE S93 (in ordine di priorità)

### 1. PyInstaller sidecar build (PRIORITÀ ASSOLUTA)
- Update voice-agent.spec (collect_all, UPX off, hidden imports)
- `get_resource_path()` per `_MEIPASS`
- `tauri-plugin-shell` + capabilities + `sidecar.rs`
- Build su iMac Intel
- **Research pronta**: `.claude/cache/agents/` (S90)
- **Effort**: 4-8h

### 2. Landing page redeploy
- Aggiornare con nuove pagine (installazione)
- Deploy su Cloudflare Pages
- **Effort**: 1h

### 3. Test VAD live con microfono su iMac
- Testare open-mic end-to-end su iMac reale
- Verificare che silero VAD + webrtcvad funzionino con audio reale
- **Effort**: 1h

### 4. Cleanup Enterprise tier dal Rust
- `LicenseTier` enum ha ancora `Enterprise` variant (unused)
- Rimuovere completamente se confermato CTO
- **Effort**: 30min

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
Leggi HANDOFF.md. Sessione 93. Priorità:
1. PyInstaller sidecar build (voice agent → binario nativo, iMac)
2. Landing page redeploy su Cloudflare Pages
3. Test VAD live con microfono su iMac
DIRETTIVE: SEMPRE code reviewer, SEMPRE 1 nicchia, ZERO costi, copy PERFETTA, VoIP solo Pro.
```
