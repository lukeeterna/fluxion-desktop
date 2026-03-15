# FLUXION — Handoff Sessione 72/73 → 73 (2026-03-14)

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
Branch: master | HEAD: 770c710
docs(audioworklet): create phase plan
Working tree: 4 file modificati non committati (piani + session_state)
type-check: 0 errori ✅ | lint: 0 errori ✅
iMac pytest voice: 1488 PASS / 0 FAIL ✅
```

---

## COMPLETATO SESSIONE 72

### Piano AudioWorklet VAD — creato e verificato

**Fase**: `audioworklet-vad-fix`
**Piani**: 2 in `.planning/phases/audioworklet-vad-fix/`
**Status**: PLAN COMPLETE — pronto per execute

| Piano | Wave | Cosa fa |
|-------|------|---------|
| audioworklet-01-PLAN.md | 1 (autonomous) | Crea `public/audio-processor.worklet.js` + migra `useVADRecorder` da ScriptProcessorNode a AudioWorkletNode |
| audioworklet-02-PLAN.md | 2 (human-verify) | Build .app su iMac via SSH + human verify phone button in produzione |

**Decisioni chiave nei piani:**
- `postMessage` usa `.slice()` (copia) — NON transferable → evita buffer neutered silenzioso
- setInterval per HTTP chunk dispatch rimane (worklet sostituisce solo l'acquisizione audio)
- `processorRef` tipato `AudioWorkletNode | null` (no `any`)
- `port.close()` in tutti e 3 i cleanup path (stop/cancel/unmount)
- `audio-processor.worklet.js` in `public/` → servito a `/audio-processor.worklet.js` da Vite

**Verifica piani (2 iterazioni checker):**
- Blocker 1 fixato: rimosso `startTimeRef` inutilizzato (avrebbe rotto `noUnusedLocals`)
- Blocker 2 fixato: postMessage ora esplicito con `.slice()` nel piano
- Warning 1 fixato: `must_haves.truths` ora corretto su setInterval
- Warning 2 fixato: artifact `.app` bundle aggiunto in piano 02

---

## PENDING / PROSSIMA SESSIONE S73

### P1 — AudioWorklet Execute (PRIORITÀ ASSOLUTA)

```bash
/gsd:execute-phase audioworklet-vad-fix
```

**Wave 1** (autonomous): crea worklet JS + migra hook TypeScript → type-check 0 errori
**Wave 2** (human-verify su iMac):
1. Build .app: `ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && npm run tauri build 2>&1 | tail -30"`
2. Apri `.app` su iMac fisicamente
3. Naviga Voice Agent → click Phone button
4. Parla → Sara deve rispondere (prova che AudioWorklet funziona in WKWebView prod)

### P2 — EHIWEB SIP (bloccante su credenziali)
- Credenziali ancora in arrivo → quando arrivano: `/gsd:plan-phase F15`
- Inserire `VOIP_SIP_USER`, `VOIP_SIP_PASS`, `VOIP_SIP_SERVER` in config.env iMac

### P3 — F17 Distribuzione Windows
- Dopo AudioWorklet funzionante: `/gsd:plan-phase F17`
- Build Windows via GitHub Actions (Tauri cross-compile)

---

## PROMEMORIA TECNICI
- **Pipeline iMac**: avviare con `-u` (unbuffered) per log completi
- **t1_live_test.py**: BASE `http://127.0.0.1:3002`
- **Nuovo Fluxion.app**: `/Volumes/MacSSD - Dati/FLUXION/src-tauri/target/release/bundle/macos/Fluxion.app`
- **App vecchia in /Applications**: aprire sempre quella della build directory
- **AudioWorklet addModule path**: `/audio-processor.worklet.js` (assoluto, Vite serve da `public/` → `dist/`)
