# FLUXION — Handoff Sessione 93 → 94 (2026-03-19)

## CTO MANDATE — NON NEGOZIABILE
> **"COPY E IMMAGINI PERFETTE. Code signing GRATIS. ZERO COSTI licensing. VoIP EHIWEB ~€2/mese. SEMPRE 1 NICCHIA per tier. USA SEMPRE SKILL CODE REVIEWER."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | **iMac DISPONIBILE**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22

---

## STATO GIT
```
Branch: master | HEAD: 0b60584 (pushato)
Uncommitted: nessuno
type-check: 0 errori
```

---

## COMPLETATO SESSIONE 93

### Commit S93 (3 commit)
| # | Commit | Descrizione |
|---|--------|-------------|
| 1 | `acac4c1` | PyInstaller _MEIPASS resource path helper — 12 file aggiornati |
| 2 | `00944f3` | build-sidecar.sh fallback `python3 -m PyInstaller` |
| 3 | `0b60584` | SIP config allineata EHIWEB VivaVox `sip.vivavox.it` + env vars |

### Dettaglio Implementazioni

#### PyInstaller Sidecar Build COMPLETO
- **Binary**: `src-tauri/binaries/voice-agent-x86_64-apple-darwin` — **59 MB**
- **Health check**: OK (`/health` → 200, pipeline 4-layer RAG attiva)
- **Booking flow**: OK ("Buongiorno, vorrei prenotare" → "Mi dice il suo nome?" + audio TTS)
- **resource_path.py**: helper `get_bundle_root()` / `get_writable_root()` per `_MEIPASS`
- **12 file sorgente aggiornati** per usare il helper (orchestrator, vertical_loader, tts, vad, etc.)
- **voice-agent.spec**: hidden imports completi, excludes torch/spaCy, datas bundle
- **build-sidecar.sh**: platform detection, `python3 -m PyInstaller` fallback, smoke test
- **voice_pipeline.rs**: già gestisce sidecar + Python fallback + self-healing 30s

#### VoIP Deep Research COMPLETATA
- **2 subagenti in parallelo** con web search reale → 2 report dettagliati con fonti
- **Decisione**: EHIWEB VivaVox (~€2/mese canone fisso, inbound GRATIS)
- **Server SIP corretto**: `sip.vivavox.it:5060` (NON sip.ehiweb.it)
- **Env vars rinominate**: `EHIWEB_SIP_USER`, `EHIWEB_SIP_PASS`, `EHIWEB_SIP_SERVER`
- **voip.py** (1236 righe) già implementato: SIP REGISTER/INVITE/BYE + RTP G.711 + auto-answer
- **In attesa**: numero definitivo EHIWEB dal CTO → poi test SIP reale
- **Research files**:
  - `.claude/cache/agents/voip-italy-market-research-2026.md`
  - `.claude/cache/agents/voip-pmi-italia-pricing-deep-research-2026.md`

#### Pricing VoIP — Dati Reali Verificati
| Provider | Costo/mese | API | Fonte |
|----------|-----------|-----|-------|
| EHIWEB VivaVox | ~€2 (canone) + inbound gratis | SIP only | ehiweb.it |
| Telnyx | €8-14 (a consumo) | REST+WebSocket | telnyx.com |
| Twilio | €13-19 (a consumo) | REST+TwiML | twilio.com |
| TIM deviazione | €100+ (volume alto) | NO | sostariffe.it |

---

## DA FARE S94 (in ordine di priorità)

### 1. Test VoIP SIP con numero EHIWEB definitivo
- CTO fornirà numero attivo → creare `.env` su iMac → `python voip.py` → test chiamata reale
- Verificare: registration, ricezione INVITE, auto-answer, audio bidirezionale
- **Effort**: 2-4h (dipende da NAT/firewall)
- **BLOCCATO DA**: attesa riattivazione numero EHIWEB

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
5. **VoIP EHIWEB** — ~€2/mese canone fisso, costo linea telefonica NON costo FLUXION
6. **SEMPRE 1 nicchia** — una PMI = un'attività. MAI multi-nicchia.
7. **ARGOS = reference** — progetto separato
8. **Deep research CoVe 2026** — SEMPRE subagenti PRIMA di implementare

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 94. Priorità:
1. Test VoIP SIP EHIWEB (SE numero disponibile — CTO avvisa)
2. Landing page redeploy su Cloudflare Pages
3. Test VAD live con microfono su iMac
DIRETTIVE: SEMPRE code reviewer, SEMPRE 1 nicchia, ZERO costi, copy PERFETTA, VoIP EHIWEB €2/mese.
```
