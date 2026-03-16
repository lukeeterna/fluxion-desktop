# FLUXION — Handoff Sessione 77 → 78 (2026-03-16)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*
> **SUPPORTO POST-VENDITA = ZERO MANUALE. Sara fa tutto.**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 | License server: porta 3010

---

## STATO GIT
```
Branch: master | HEAD: 34edd1e
docs(f-sara-voice): COMPLETE — Serena voice approved, 1910 PASS, step 9 UI verified
type-check: 0 errori ✅ | iMac pytest: 1910 PASS ✅
⚠️ Sessione 77: file creati ma NON committati — commit da fare a inizio S78
```

---

## COMPLETATO SESSIONE 77

### DECISIONI ARCHITETTURALI — Stack Agenti €0/mese ✅
4 subagenti di ricerca completati. Decisioni ferme:

**LLM Multi-Provider (€0/mese)**:
- Primario: Gemini 2.5 Flash (IT 9/10, 250 RPD)
- Secondario: Cerebras llama-70b (1M tok/giorno)
- Terziario: Groq 8B (14.4K RPD, task semplici)
- Batch: Mistral Large (1B tok/mese, content)

**Lead Gen Italia (€0 → €750 one-time)**:
- Google Maps API (10K/mese free) → lead database
- OpenAPI.com (€0.015/req) → PEC + P.IVA (arma segreta Italia)
- ISTAT Open Data → market sizing gratuito
- SKIP: PagineGialle (scraping illegale), LinkedIn (irrilevante PMI), Instagram

**Outreach**: WhatsApp diretto (wa.me links), PEC personalizzata, contact form siti
**CRM**: HubSpot Free (1M contatti) — NON SQLite custom
**Support**: In-app diagnostics + FAQ + health check + email auto-reply LLM (soglia 0.85)
**NO RustDesk**: overkill, GDPR concerns, PMI diffidano

### FILE CREATI (da committare S78) ✅
```
voice-agent/data/sales_knowledge_base.json      (21KB) — 8 pitch, 15 obiezioni, closing, follow-up
voice-agent/data/support_knowledge_base.json     (19KB) — 9 step onboarding WA, 23 FAQ, 8 troubleshooting
voice-agent/data/wa_first_contact_templates.json (8KB)  — 16 template primo contatto, 8 verticali
scripts/lead_generator.py                        (27KB) — Google Maps paste → wa.me HTML links
```

### LEAD GENERATOR TESTATO ✅
- 10/10 lead parsati con telefono (fissi + cellulari)
- Vertical detection automatico (8 verticali)
- Template WA personalizzati per verticale dal JSON
- Output: leads.json + wa_links.html (bottoni verdi) + leads_report.txt

### Research salvata in `.claude/cache/agents/`:
- `best-free-llm-2026-research.md` — 12 provider LLM comparati
- `italian-lead-gen-research.md` — 15 fonti Italia, legalità GDPR, strategia PEC
- `zero-touch-support-research.md` — pattern Figma/Linear, auto-diagnostics
- `zero-cost-agent-stack-research.md` — Gmail, n8n, HubSpot, Cal.com, Resend

---

## 🔥 NOVITÀ — CREDENZIALI EHIWEB ARRIVATE!
- Il numero VoIP EHIWEB può essere usato come numero "Sara Sales" su WhatsApp Business
- Sblocca F15 VoIP + numero dedicato outreach (non il personale di Gianluca)
- `/gsd:plan-phase F15` ora possibile

---

## ⚠️ GAP IDENTIFICATO — Materiale Demo per Clienti
- Nessun video demo / screenshot / PDF da mostrare ai prospect
- Il WA template funziona per primo contatto ma serve materiale per chi risponde "come funziona?"
- Opzioni: video Loom di 2 min / PDF one-pager / landing page aggiornata con screenshots

---

## AZIONE IMMEDIATA S78

### Priorità 1: Commit + Wire Sara Sales
```bash
# 1. Commit file creati S77
git add voice-agent/data/sales_knowledge_base.json voice-agent/data/support_knowledge_base.json voice-agent/data/wa_first_contact_templates.json scripts/lead_generator.py
git commit -m "feat(f18): add Sara Sales dataset + lead generator tool"

# 2. Wire dataset nella pipeline Sara (FSM sales mode WhatsApp)
# Nuovo stato FSM: SALES_QUALIFYING → SALES_PITCHING → SALES_OBJECTION → SALES_CLOSING
```

### Priorità 2: EHIWEB VoIP
```
/gsd:plan-phase F15
# Credenziali arrivate — configurare SIP + numero dedicato Sara
```

### Priorità 3: Materiale Demo
```
# Video Loom 2 min / PDF one-pager / Screenshots landing
# Sara deve poter inviare link a materiale quando prospect chiede "fammi vedere"
```

---

## PIPELINE SARA — VISIONE COMPLETA

```
Sara Receptionist (DONE):  Prende appuntamenti per i clienti della PMI
Sara Sales (IN PROGRESS):  Vende FLUXION ai prospect via WhatsApp
Sara Support (TODO):       Onboarding + troubleshooting post-vendita via WhatsApp
Sara VoIP (UNBLOCKED):     Risponde al telefono con numero EHIWEB dedicato
```

---

## PROSSIME FASI
1. **F18-SARA-SALES**: Wire dataset → FSM sales mode → test WhatsApp
2. **F15 VoIP EHIWEB**: Credenziali arrivate → SIP config → numero dedicato
3. **DEMO MATERIAL**: Video/PDF per prospect che rispondono ai WA
4. **P1.0**: Impostazioni Redesign (quando c'è tempo)

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 78: commit file S77, wire Sara Sales dataset nel FSM, poi F15 EHIWEB VoIP. Credenziali EHIWEB pronte.
```
