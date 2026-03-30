# FLUXION — Handoff Sessione 122 → 123 (2026-03-30)

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

## COMPLETATO SESSIONE 122 — 10 COMMIT, 15+ BUG FIX SARA FSM

### Fix critici applicati
1. **Orchestrator intent routing** — "Sono Anna Bianchi" ora instradato al booking FSM (IGNORECASE + _has_name + _has_booking_words)
2. **Surname extraction in IDLE** — "Sono Alessia Gentile" estrae nome+cognome in un turno
3. **DB lookup surname-first** — cerca per cognome poi filtra per nome (bridge HTTP non supporta query combinate)
4. **Phone "Sì" handling** — "Perfetto, mi dica il numero" invece di "Mi ripete"
5. **Italian word phone** — "tre tre uno quattro..." → 3314983901
6. **Confirmation words** — "registrami", "procediamo" non trattati come cognomi
7. **Package goodbye** — "Sì grazie arrivederci" chiude la chiamata
8. **Session reset** — pending flags resettati tra sessioni
9. **Service "/" split** — "Meches/Balayage" → sinonimi "meches" + "balayage"
10. **IDLE→WAITING_NAME chain** — primo messaggio con nome processato in un turno

### Feature test matrix (S122)
```
✅ Booking nuovo cliente (nome→cognome→telefono IT→servizio→data→ora→conferma→chiusura)
✅ Booking cliente esistente ("Sono Anna Bianchi" → trovata → Bentornato!)
✅ Pacchetti post-booking (Festa Papà, Natale Glamour proposti automaticamente)
✅ Disdetta (trova appuntamento, chiede conferma cancellazione)
✅ FAQ orari ("Lun-Sab 9:00-19:00")
✅ FAQ servizi (lista completa)
✅ Riconoscimento soprannome (Gigio → Gigio Peruzzi)
⚠️ Servizio ambiguo: "taglio donna" → Taglio Donna + Taglio Uomo (specificity filter parziale)
⚠️ Multi-servizio: "taglio donna e piega" → 3 servizi (dovrebbe essere 2)
⚠️ FAQ prezzi: non risponde, chiede il nome
⚠️ Spostamento: chiede nome ma non trova appuntamento
⚠️ Lista attesa: non testabile (slot sempre disponibili nel DB test)
⚠️ Verticali non-salone: non testabili (DB iMac è solo salone)
```

---

## STATO GIT
```
Branch: master | HEAD: 8cdaebb
type-check: 0 errori
voice pipeline: ATTIVO con VoIP
Commits S122: 10 fix Sara FSM + orchestrator
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:   Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10:  Video V7             ✅ COMPLETATO (S117)
Phase 10b: Sara Features        ✅ COMPLETATO (S118)
Phase 10c: Sara VoIP EHIWEB    ✅ BRIDGE + FSM FIX (S121-S122)
Phase 11:  Landing + Deploy     ⏳ (video YT non caricato)
Phase 12:  Sales Agent WA       ⏳
Phase 13:  Post-Lancio          ⏳
```

---

## PROSSIMA SESSIONE 123 — PRIORITÀ

### A. Fix servizio ambiguo (CRITICO)
Il problema `extract_services` non si risolve col specificity filter attuale. Serve approccio diverso:
- "taglio donna" matcha sia Taglio Donna che Taglio Uomo (entrambi hanno "taglio" come sinonimo)
- "barba" matcha sia Barba che Colore barba
- **Proposta**: quando un servizio è substring di un altro E il testo utente non contiene TUTTI i token del servizio lungo, tenere solo il corto

### B. Test COMPLETI per ogni verticale
1. **Seed script per 4 verticali** (palestra, medical, auto + salone già OK)
   - Inserire servizi, operatori, clienti, appuntamenti, pacchetti per ogni verticale
   - Testare OGNI scenario per OGNI verticale
2. **Scenari da testare per verticale**:
   - Nuovo cliente → registrazione → booking completo → chiusura
   - Cliente esistente → booking rapido
   - Lista attesa (riempire slot per forzare waitlist)
   - Proposta pacchetti post-booking
   - Disdetta + spostamento
   - FAQ settoriali (orari, prezzi, servizi specifici)
   - Terminologia settoriale (cheratina, personal training, tagliando, ecografia...)
   - Compleanni (testare auguri automatici)
   - Multi-servizio per verticale

### C. Bug rimasti
- [ ] FAQ prezzi non funziona ("Quanto costa un taglio?" → chiede il nome)
- [ ] Spostamento non trova appuntamenti
- [ ] Two-digit phone words (trentatre, ventuno)
- [ ] Multi-turn phone buffer (VAD split)
- [ ] Servizio dal primo messaggio non estratto ("Sono Alessia, vorrei un colore")

---

## FILE CHIAVE SESSIONE
- `voice-agent/src/booking_state_machine.py` — 15+ fix
- `voice-agent/src/orchestrator.py` — routing, DB lookup, session reset
- `voice-agent/src/entity_extractor.py` — phone normalization, service specificity
- `voice-agent/src/italian_regex.py` — VERTICAL_SERVICES (61 servizi, 379 sinonimi, 4 verticali)

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 123.
PRIORITÀ ASSOLUTA: Sara deve essere STUPEFACENTE per OGNI verticale.
1. Crea seed DB per palestra, medical, auto (servizi + clienti + appuntamenti + pacchetti)
2. Testa OGNI feature per OGNI verticale (booking, waitlist, disdetta, pacchetti, FAQ, compleanni)
3. Fix servizio ambiguo (taglio donna → 2 servizi)
4. Fix FAQ prezzi
```
