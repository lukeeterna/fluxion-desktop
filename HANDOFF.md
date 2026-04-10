# FLUXION — Handoff Sessione 142 → 143 (2026-04-10)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 142

### Fase 1: Fix VoIP crash + 7 bug critici dal live test (3 commit)

**Commit 1** — `fix(S142): 7 critical VoIP bugs`
- P0-a: NameCorrector SOLO in stati nome (was: corrompe "farmi"→"Fabbri")
- P0-b: Goodbye ("arrivederci") → should_exit=True + SIP hangup
- P0-c: Bare name "Marco Rossi" entra nel booking da IDLE
- P1-a: Barge-in energy-delta (caller può interrompere Sara)
- P1-b: Name-only DB lookup (1→direct, 2+→cognome, 0→new client)
- P1-c: pjlib thread registration (fix crash assertion)

**Commit 2** — `fix(S142): VoIP audio audit fixes`
- B1 CRITICAL: Barge-in control flow — audio non più scartato
- L1 HIGH: Hangup thread race condition → guard _hangup_pending
- L2: Pipeline timeout 30s→15s
- E2: pjsua2 crash → no più zombie state
- A1: audioop.rms() (C, 100x faster)
- B5: Grace period 0.3s→0.15s (non clippa "sì"/"no")

**Commit 3** — `fix(S142): audit-driven fixes`
- UX: Greeting 17s→3s ("Salone X, buongiorno! Come posso aiutarla?")
- NLU: 13 compound goodbye phrases added
- NLU: Standalone CHIUSURA detector (decoupled from L1 response gate)
- NLU: _nlu_to_intent_result guaranteed response for CHIUSURA
- FSM: Bare name case-insensitive

### Fase 2: Audit sistematico completo (7 agenti)

| Audit | Agente | Risultato |
|-------|--------|-----------|
| FSM 23 stati | sara-fsm-architect | 8/23 stati morti, 15 bug, top 5 fix prioritizzati |
| NLU intents | sara-nlu-trainer | should_exit broken (FIXED), compound goodbyes (FIXED) |
| Audio pipeline | voice-engineer | 1 CRITICAL + 5 HIGH (tutti FIXED) |
| RAG quality | sara-rag-optimizer | L4 hallucina disponibilità (P0 backlog) |
| Multi-turn tests | api-tester | 26 test creati in test_multi_turn_conversations.py |
| UX caller | ux-researcher | Greeting 17s (FIXED), 8→3 turn target |
| VoIP ISP | general-purpose | Matrice compatibilità tutti ISP italiani |

### Test verificati via API
```
OK "Marco Rossi" da IDLE → booking flow (disambiguating_name)
OK "Marco" (6 in DB) → "Mi dice il cognome?"
OK "Arrivederci" → Exit=True + hangup SIP
OK "Grazie a tutti" → Exit=True
OK "Basta così" → Exit=True
OK "Ho finito" → Exit=True
OK "Ciao a presto" → Exit=True
OK "barba" in frase → NON corrotto (NameCorrector off)
OK Greeting → 3 secondi (was 17s)
```

---

## STATO GIT
```
Branch: master | HEAD: f480504
Commits S142:
  fix(S142): 7 critical VoIP bugs — barge-in, name flow, goodbye, NameCorrector
  fix(S142): VoIP audio audit fixes — barge-in control flow, race conditions, RMS
  fix(S142): audit-driven fixes — greeting, goodbyes, NLU, bare-name
```

---

## AUDIT BACKLOG (P0 — Prima del lancio)

1. **L4 Groq hallucina disponibilità** — No slot data nel system prompt
   - Fix: aggiungere guardrail "Per disponibilità, chiedi al cliente servizio+data e guida nel booking"
   - O: query DB per prossimi slot e iniettare nel prompt
2. **Conversation history** — L4 è single-turn, perde contesto
   - Fix: passare ultimi 3 turni come messages array
3. **FAQ variables non risolte** — PREZZO_COLORE_COMPLETO etc. dropped silently
4. **TURN server** — 20% PMI con CGNAT (EOLO, 4G, WISP) non possono ricevere chiamate
   - Fix: coturn su Oracle Cloud Free Tier (ZERO costi)

## AUDIT BACKLOG (P1 — Sprint 5)

5. **8 stati FSM morti** — CHECKING_AVAILABILITY, SLOT_UNAVAILABLE, PROPOSING_WAITLIST etc.
6. **Exit path registrazione** — "lascia perdere" durante registrazione → loop infinito
7. **Slot presentation** — suggerire 1 slot ("Alle 15 va bene?") non lista di 3
8. **Rimuovere ASKING_CLOSE_CONFIRMATION** — WhatsApp automatico, no domanda extra
9. **UDP keepalive 15s** — previene NAT binding timeout su CGNAT
10. **cancel_booking patterns** — "disdico" non wired nel FSM

## VoIP ISP Compatibilità (Sintesi)
```
60% PMI (FTTH/FTTC) → Sara funziona ORA
20% PMI (FWA/4G/WISP) → SERVE TURN server
10% PMI (ADSL2+) → Funziona con jitter buffer tuning
5% PMI (Starlink LEO) → Funziona con TURN + keepalive aggressivo
5% PMI (GEO satellite) → Non raccomandato, WhatsApp fallback
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 143.
PROSSIMI PASSI:
1. LIVE TEST TELEFONO — fondatore chiama 0972536918, testa tutti i fix S142
2. Fix P0 backlog audit: L4 guardrail disponibilità + conversation history
3. Sprint 5: Sales Agent WA
REGOLA: ZERO COSTI. Vertex AI DISABILITATA.
REGOLA: Riavviare pipeline iMac dopo OGNI modifica Python
```
