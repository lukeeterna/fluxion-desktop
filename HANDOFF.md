# FLUXION — Handoff Sessione 56 → 57 (2026-03-12)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 (bind 127.0.0.1) | Test via SSH

---

## STATO GIT
```
Branch: master | HEAD: 2fe6f46
fix(tests): aggiorna test_reminder_24h_template — CONFERMO vs OK
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac: sincronizzato ✅ | pytest: 1323 PASS / 0 FAIL ✅
```

---

## ✅ COMPLETATO SESSIONE 56 — Sara Enterprise Sprint 1

### 9 Fix P0 implementati (7 commit + 2 già presenti)

| Fix | Commit | Descrizione | AC |
|-----|--------|-------------|-----|
| FIX-1 | `ad812b2` | TimeConstraint AFTER verifica slot libero | "dopo le 17" → 17:30+ ✅ |
| FIX-2 | `c6fb4b1` | Loop CONFIRMING — soglia 3 correzioni → exit | Loop infinito risolto ✅ |
| FIX-3 | già presente | Groq rate limit → graceful msg | — |
| FIX-4 | già presente | "no/ma/però" rimossi da escalation | — |
| FIX-5 | `e5177cd` | Date TTS "13/03" → "tredici marzo" | ✅ |
| FIX-6 | `c8b5263` | GDPR: PII mascherati nei log DEBUG | 0 PII in chiaro ✅ |
| FIX-7 | `2fc43fb` | "il sette" → giorno 7 estratto | ✅ |
| FIX-8 | `8eebc8e` | "il primo" → giorno 1 estratto | ✅ |
| FIX-9 | `c230847` | "tra le 3 e le 4" → 15:00-16:00 PM | ✅ |
| TEST  | `2fe6f46` | Fix test_whatsapp disallineato (CONFERMO) | 1323 PASS ✅ |

---

## 🔴 PROSSIMA SESSIONE S57 — Sara Enterprise Sprint 2 (13 Fix P1)

> **Skill**: `fluxion-voice-agent` | Python su iMac via SSH
> **Research**: `.claude/cache/agents/sara-enterprise-agente-[a|b|c].md` (ancora valide)

### 13 Fix P1 (da implementare in ordine priorità):
1. **Multi-servizio**: "taglio e colore" → 2 servizi in booking_data
2. **Flexible scheduling**: "qualsiasi giorno tranne lunedì" → exclude_days constraint
3. **Streaming LLM**: Groq streaming response per latency < 600ms
4. **Fallback progressivo**: L4 Groq → L3 FAQ → L2 guided → L1 fallback
5. **Slot waterfall**: se slot pieno → propone prossimo slot disponibile automatico
6. **Selezione ordinale slot**: "il secondo" → seleziona 2° slot della lista
7. **FAQ mid-booking resume**: risponde FAQ e torna al flusso booking senza perdere stato
8. **Sessioni concorrenti**: 2+ chiamate parallele senza stato condiviso
9. **Escalation context**: passa contesto FSM all'operatore umano
10. **Anchors CONFERMA/RIFIUTO**: "esatto", "giusto", "negativo" → intent mapping
11. **"Anzi"**: "anzi, meglio le 15" → override intent immediato
12. **TIME_PRESSURE**: "ho fretta" → risposta accelerata senza domande superflue
13. **Constraint negativi**: "non il lunedì" → giorno escluso dal waterfall

---

## Riavvio pipeline iMac (dopo ogni modifica .py):
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```
