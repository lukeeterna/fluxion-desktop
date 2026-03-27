# FLUXION — Handoff Sessione 117 → 118 (2026-03-27)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**
> **"Capire cosa ho → capire cosa è possibile → definire insieme cosa fare. MAI codice come secondo step."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 117

### Video V7.7 FINALE — APPROVATO
- `landing/assets/fluxion-promo-v7.mp4` — 46 scene, 6:19, 51.5 MB
- 5 clip Veo3 nuove: V14 medico+paziente, V15 portfolio, V16 Sara (croppata anti-film), V17 Sara dialogo, V18 cliente telefono
- Sara ha un VOLTO (V16/V17) + Cliente ha un volto (V18)
- Numeri animati Pillow: €120/mese, €4.320, MAI TUO, SPARISCE TUTTO, €497, €897, 30GG RIMBORSATI, FLUXION
- 16 feature mostrate: Dashboard, Calendario, Sara+dialogo, 5 schede verticali (parrucchiere, veicoli, medica, odontoiatrica, fisioterapia), PT, Portfolio prima/dopo, QR+Fedelta, Operatori, Servizi, Fatture+SDI, Fornitori, Cassa, Analytics
- 3 schede sanitarie: medica generica + odontoiatrica + fisioterapia
- Endcard 13s (5s animazione + 8s logo fermo)
- Audio fix: `-ar 48000 -ac 2` su ogni clip, musica 0.12
- Audit verita' completato: zero false claims nel video finale

### Regola salvata in memory
- `feedback_understand_before_code.md` — Capire prima, codice dopo. Tutto è possibile, basta cercare bene.

### Lezioni S117
- Veo 3 genera SEMPRE film strip borders → CROP ffmpeg è l'unico fix affidabile
- MAI scrivere copione video senza verificare PRIMA cosa il software fa realmente
- L'endcard animata va costruita come: animazione + hold ultimo frame statico
- Audio concat: FORZARE `-ar 48000 -ac 2` su OGNI singola clip prima di concat

---

## DA FARE S118 — PRIORITA' ASSOLUTA

### Sara: 3 feature mancanti da implementare (PROMESSE NEL VIDEO)
```
1. RESCHEDULE — Sara sposta appuntamenti (nuovo stato FSM)
   - Cliente dice "posso spostare a giovedì?"
   - Sara verifica disponibilità, propone alternative, conferma spostamento
   - WhatsApp con nuova conferma

2. PROPOSTA PACCHETTI — Sara propone pacchetti fedelta' al momento giusto
   - Dopo booking completato, Sara controlla se esistono pacchetti attivi
   - "Marco, abbiamo un pacchetto 5 sedute colore a €200 invece di €250. Le interessa?"
   - Logica: dopo N visite senza pacchetto → proponi

3. DISDICI + RIPRENOTA — Sara cancella e propone alternativa
   - Cliente dice "devo disdire domani"
   - Sara: "Capisco. Vuole che le trovi un altro orario questa settimana?"
   - Non solo cancella, ma propone reschedule
```

### S33 — Automazione promemoria/compleanno da implementare
- Template WhatsApp esistono (`whatsapp-1tap.ts`)
- Manca: cron/scheduler che li invia automaticamente
- Promemoria 24h prima + auguri compleanno

### POI: Phase 11 Landing + Deploy (dopo Sara fix)

---

## STATO GIT
```
Branch: master | HEAD: c90e829 (video non committato — commit dopo approvazione)
type-check: 0 errori
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:  Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10: Video V7             ✅ COMPLETATO (S117) — V7.7 approvato
Phase 11: Landing + Deploy     ⏳
Phase 12: Sales Agent WA       ⏳
Phase 13: Post-Lancio          ⏳
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 118.
PRIORITA': Implementare 3 feature Sara promesse nel video:
1. RESCHEDULE (sposta appuntamenti)
2. PROPOSTA PACCHETTI (fedelta' post-booking)
3. DISDICI + RIPRENOTA (cancella con alternativa)
Poi: automazione promemoria WA + auguri compleanno.
Voice agent su iMac (192.168.1.2:3002).
```
