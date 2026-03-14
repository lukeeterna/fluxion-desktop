# FLUXION — Handoff Sessione 71 → 72 (2026-03-14)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: 1bb14e2
fix(voice): RC-1+RC-2+RC-3 WKWebView audio context e microfono
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1488 PASS / 0 FAIL ✅
```

---

## COMPLETATO SESSIONE 71

### VAD Open-Mic Debug + Fix (commit ac0e285, b389282, 1bb14e2)

**Root causes identificati e fixati (CoVe 2026 research):**

| RC | Causa | Fix |
|----|-------|-----|
| RC-1 | AudioContext creato dopo `await` → WKWebView suspended | AudioContext PRIMA di qualsiasi await |
| RC-2 | `entitlements.plist` ignorato in tauri.conf.json | `"entitlements": "../entitlements.plist"` |
| RC-3 | ScriptProcessorNode garbage-collected da WKWebView | GainNode silencer (gain=0) mantiene chain viva |
| RC-4 | `startListening` swallowava errori → `waitForTurn` hang infinito | re-throw + timeout 60s |

**Stato finale:**
- ✅ Sara saluta automaticamente all'apertura Voice Agent
- ✅ Modalità manuale (mic → invio) funziona perfettamente
- ⚠️ Open-mic phone button: ScriptProcessorNode non invia chunk in WKWebView produzione
- ✅ Per EHIWEH SIP: VAD gira su Python, NO browser coinvolto → funzionerà automaticamente

### Architettura chiarita
- **EHIWEB SIP** (caso reale): cliente chiama → RTP audio → Python VAD → STT → LLM → TTS → risposta automatica. Zero bottoni, zero browser.
- **UI Phone button** (demo simulata): usa ScriptProcessorNode che non funziona in WKWebView prod. Fix richiede AudioWorklet (rebuild).

### Roadmap aggiornata
- **F17** aggiunto: Distribuzione Cross-Platform (Mac + Windows)
- **F18** aggiunto: Agenti Autonomi (Sales + Marketing + Support) con Groq free tier

### localhost → 127.0.0.1 fix
WKWebView risolve `localhost` → `::1` (IPv6) ma Python ascolta su `127.0.0.1` (IPv4).
Fix applicato: `VOICE_PIPELINE_URL = 'http://127.0.0.1:3002'`

---

## PENDING / PROSSIMA SESSIONE S72

### P1 — EHIWEB SIP (bloccante su credenziali)
- Credenziali ancora in arrivo → quando arrivano: `/gsd:plan-phase F15`
- `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER` → inserire in config.env iMac

### P2 — AudioWorklet fix (UI demo phone button)
- Sostituire `ScriptProcessorNode` con `AudioWorklet` in `use-voice-pipeline.ts`
- AudioWorklet: thread dedicato, non throttlato da WKWebView, gold standard 2026
- Research già in `.claude/cache/agents/vad-openmicloop-cove2026.md`

### P3 — F17 Distribuzione Windows
- Build Windows via GitHub Actions (Tauri cross-compile)

### P4 — F18 Agenti Autonomi (post-lancio)
- Support + Marketing + Sales agent con Groq free tier
- `/gsd:plan-phase F18` quando FLUXION è su entrambe le piattaforme

---

## PROMEMORIA TECNICI
- **Pipeline iMac**: avviare con `-u` (unbuffered) per log completi
- **t1_live_test.py**: BASE `http://127.0.0.1:3002`
- **Nuovo Fluxion.app**: `/Volumes/MacSSD - Dati/FLUXION/src-tauri/target/release/bundle/macos/Fluxion.app`
- **App vecchia in /Applications**: aprire sempre quella della build directory
