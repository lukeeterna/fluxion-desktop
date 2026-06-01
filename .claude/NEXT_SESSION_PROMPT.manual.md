# Prompt ripartenza S321 — Sara LIVE stress test su tutti i verticali (gate "pronto a vendere")

> **META-VINCOLO (REGOLA #18 VALIDATE-THEN-IMPLEMENT)**: prima di dichiarare CHIUSO qualsiasi anello/feature production-critical, eseguire S187 FASE 1 (research + tabella validazione fonte + verdetto + evidenza reale) e FERMARSI per GO Luke. NO production claim senza output reale di test letto da Luke.
> **REGOLA #21 (founder-input S320)**: Sara = pilastro, NON deferrabile. "Pronto a vendere" = Sara testata LIVE su TUTTI i verticali con chiamata reale (iMac + smartphone) + stress test, criterio = "soddisfa pienamente il cliente". Payment rail OK = necessario, non sufficiente.

## ✅ STATO REALE POST-S320 (audit code-truth completato)

| Anello | Stato | Evidenza |
|--------|-------|----------|
| Payment rail €497/€897 | ✅ VERIFIED-E2E-LIVE | smoke €1 Base S317 + Pro S319, webhook 200 + Ed25519 + D1 + Resend delivered + refund |
| C-FLUXI-002 primo CLOSED_WON | ✅ RESOLVED (Luke GO S318) | — |
| Verticali canonici | ✅ RISOLTO da codice S320 | `src/types/setup.ts:66` |
| **Sara live multi-verticale** | 🔴 **BLOCKER #1 — mai eseguito E2E runtime** | server 3002 DOWN |
| Wizard activate GUI cliente | 🟡 CLAIMED (codice ok, mai live) | richiede founder GUI iMac |
| macOS signing ad-hoc + download URL | 🟡 da implementare | #2b deciso €0 S319 |

### Verticali canonici (RISOLTO S320 — non chiedere a Luke)
- Fonte verità: `src/types/setup.ts:66` `MACRO_CATEGORIE` = **8 macro** (medico, beauty, hair, auto, wellness, professionale, pet, formazione) + `MICRO_CATEGORIE:129` ~50 micro con flag `hasScheda`.
- `CATEGORIE_ATTIVITA:238` (5 valori) = `CONSTANTS LEGACY:230` MORTO, ignorare.
- Schede React + DB reali per **6/8 macro** (medico, beauty, hair, auto, wellness, pet). `professionale` + `formazione` = gusci vuoti (no scheda, no demo Sara).
- **Matrice test Sara** = 9 verticali voice-agent con DB demo pronti (`voice-agent/scripts/create_vertical_dbs.py`): salone, barbiere, beauty, odontoiatra, fisioterapia, gommista, toelettatura, palestra, medical.

## 🎯 OBIETTIVO S321
Far chiamare Sara da smartphone reale (Luke), per ogni verticale, sotto stress, misurare le lacune, produrre piano di integrazione/modifiche con test E2E obbligatori.

## 🚦 SCOPE S321 — fasi ordinate

### PRE-FLIGHT (CTO autonomous)
- Voice Pipeline 3002 su iMac: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python main.py > /tmp/sara.log 2>&1 &"` poi `curl http://192.168.1.2:3002/health`.
- HTTP Bridge 3001 già UP (hook). Verificare anche.

### FASE 0 — RESEARCH come lo smartphone "parla" a Sara (BLOCCANTE, research-first REGOLA #16)
- **Finding audit S320**: `voice-agent/src/voip_pjsua2.py` = SCAFFOLD, gate `if voip_sip_user` default OFF, nessuna credenziale SIP attiva. Quindi "chiamata reale da smartphone" NON è ancora cablata.
- Vincolo ZERO-COSTI: niente DID/numero a pagamento. Ipotesi da verificare (NON assumere): softphone SIP sullo smartphone (es. Linphone) → PJSIP/Asterisk locale su iMac in LAN → Sara. Zero costo, solo wifi.
- Leggere research esistente: `.claude/cache/agents/universal-voip-solution-research.md`, `voip-italy-deep-research-2026.md`, `f15-voip-telnyx-research.md`.
- Output: UNA raccomandazione motivata sul path zero-cost per chiamata vocale reale smartphone→Sara su iMac. Se VoIP reale non è zero-cost in tempi brevi → fallback: interfaccia web-audio sulla LAN servita dalla pipeline (smartphone apre URL iMac, parla via microfono browser). Decidere il path con dati prima di procedere.

### FASE 1 — SETUP harness stress test (CTO autonomous)
- `voice-agent/scripts/switch_vertical.sh` per swap DB demo per verticale + restart pipeline.
- `voice-agent/scripts/create_vertical_dbs.py` (rigenera DB demo se mancanti).
- `voice-agent/scripts/test_all_verticals_e2e.py` (harness booking + faq + triage per i 9 verticali) — usare come baseline automatizzata PRIMA della chiamata vocale umana.

### FASE 2 — RUN test (Luke + CTO)
1. Baseline automatizzata: `test_all_verticals_e2e.py` su tutti i 9 verticali → log strutturati.
2. Chiamata vocale reale: Luke parla da smartphone, scenari per ogni verticale (booking nuovo cliente, FAQ, disambiguazione nome, slot pieno→waitlist, chiusura graceful). Vedi `voice-agent-details.md` "Test Live Scenari".
3. Catturare log per verticale: trascrizione STT, intent NLU, risposta, latenza per turno, TTS.

### FASE 3 — MISURARE LACUNE (criterio "soddisfa pienamente il cliente")
- Scoring per verticale: booking completato sì/no, FAQ corretta sì/no, disambiguazione ok, latenza p95 < 800ms (soglia PLAN), naturalezza/errori. Formato output `e2e-testing.md`: `OK/WARN/FAIL [VERTICAL] [SCENARIO]: input → output`.
- Evidence file: `~/venture-os/state/s321-sara-live-stresstest-evidence.json` (per verticale: pass/fail + lacune + latenze).

### FASE 4 — PIANO INTEGRAZIONE (con E2E obbligatori)
- Da lacune misurate, proporre modifiche prioritizzate (NLU, FSM, RAG, TTS, latenza).
- Ogni modifica DEVE avere test E2E obbligatorio (`e2e-testing.md`): curl `POST /api/voice/process` su iMac + ri-test vocale.
- NO "production ready Sara" senza S187 FASE 1 evidence + GO Luke (META-VINCOLO).

## 🧹 CLEANUP carry-over (context fresco)
- PLAN.md `OBIETTIVO:19` "9 verticali" → "8 macro / 6 implementati" (cosmetico, deferred da S320 per BLOCK_CRITICAL 66%).
- Nascondere `professionale` + `formazione` dal Setup Wizard finché senza scheda+demo (filtro 1-riga, toglie falsa promessa vendita).
- C-LIC-001 `[DEFERRED]`→`[ADDRESSED]` (credenziali LIVE attive da S316).
- #2b macOS ad-hoc signing (€0, deciso S319) + DMG download URL pubblico verificato + wizard activate GUI live.

## REGOLE ATTIVE S321
- **#21** Sara pilastro, gate vendita include Sara live (NUOVA)
- **#14** CTO autonomous (pre-flight, FASE 0/1/4 autonome; FASE 2 chiamata = Luke)
- **#16** research-first (FASE 0 path VoIP zero-cost PRIMA di procedere)
- **#18** VALIDATE-THEN-IMPLEMENT (no "Sara ready" senza evidence + GO Luke)
- **#4** critica + autocritica 4 punti su ogni piano FASE 4
- **#5** chiusura: commit + prompt ripartenza
- **E2E obbligatorio** (`e2e-testing.md`) su ogni modifica FASE 4

## ARTEFATTI PRODUCTION (invariati)
- Stripe LIVE Base `plink_1TcpAk...8boabwRX` €497 / Pro `...fn8dioIo` €897; Webhook `we_1TcpBL...`; Worker prod; Landing `fluxion-landing.pages.dev`; Email `fluxion-app.com` verified. VOS gate VERDE.

## PRIMO COMANDO S321
```
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python main.py > /tmp/sara.log 2>&1 &" && sleep 5 && curl -s http://192.168.1.2:3002/health
```
