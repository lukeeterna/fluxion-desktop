# B3-PROMOTE-r2 — Run Log 2026-07-30

**Task**: T-B3-PROMOTE-r2 (#34v)
**Sessione**: 0d30c66d-1dd6-4283-b6c9-31c5b2843a62
**Baseline commit**: 13f36040

---

## GATE-0

- `22446998` auto-close: tocca solo `vos-out/decisions.jsonl` (whitelist) ✅
- `.claude/NEXT_SESSION_PROMPT.md` rimosso (non tracciato in git) ✅
- push `22446998` → origin/master allineato ✅
- `./bin/vos_check.sh`: PASS=7 FAIL=0 ✅

---

## F1 — RUNBOOK AVVIO

Fonti consultate (ordine prescritto):
1. `rig/launch_rig.sh` → NOT FOUND in root; trovato in `.claude/cache/T-SARA-TURNTAKING/rig/launch_rig.sh` ✅
2. `main.py` linea 1326 — selettore VOICE_ENGINE verificato ✅
3. Definizioni servizio/launchd/plist — nessuna per il voice agent (solo `com.fluxion.license-server.plist` e `com.fluxion.salesagent.plist`) ✅
4. `restore.sh` → `.claude/cache/T-SARA-TURNTAKING/B3_RUNBOOK/scripts/restore.sh` ✅ (python executable, working dir, argv)

**Output**: `docs/judge/RUNBOOK-AVVIO.md` scritto con distinzione VERIFICATO/DEDOTTO.

**Avvio verificabile**: SÌ — python executable, working dir, argv, env vars tutti ricavati da fonti.

---

## F2 — AVVIO GO ENGINE SU :3002

**Baseline**: :3002 DOWN (lsof count=0 verificato prima dell'avvio)

**Comando usato**:
```bash
ssh imac 'bash -s' << 'SCRIPT'
cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
set -a; . ".env"; set +a
VOICE_ENGINE=go
export VOICE_ENGINE
PYBIN="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python"
nohup "$PYBIN" main.py --port 3002 > /tmp/sara_3002_r2.log 2>&1 &
echo "sara pid=$!"
SCRIPT
```

### Verifiche (≤8 righe di evidenza)

| Check | Evidenza | Esito |
|-------|----------|-------|
| Processo :3002 UP, pid dichiarato | `lsof -ti:3002 → 13067` | ✅ |
| Motore = go engine | log: `GoEngine start: registered=True reg_status=200`; status API: `engine: go` | ✅ |
| Registrazione SIP trunk (registered / 200) | log: `registered=True reg_status=200` | ✅ |
| Greeting contiene disclosure AI Act | TTS log: `'Salone Demo FLUXION, buonasera! Sono Sara, l'assistente virtuale.'` | ✅ |
| FIX-A (congedo senza «collega») | `escalation_manager.py:97` — "E6-FIX: congedo onesto — il salone richiamerà, Sara non promette un collega" | ✅ |
| FIX-C (conferma nome) | `booking_state_machine.py:756` — `return "Mi conferma il nome corretto?"` | ✅ |

---

## Stato finale

**:3002**: UP — pid=13067 — engine=go — SIP registered=True

---

## VERDETTO: VERDE
