# FLUXION — Handoff Sessione 115 → 116 (2026-03-26)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**
> **"SEMPRE valutare la skill migliore per il task specifico — è una REGOLA."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002 | **sshd ha Screen Recording + Accessibility**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS, Pillow, gcloud SDK, google-genai

---

## STATO GIT
```
Branch: master | HEAD: 58491a9
type-check: 0 errori
iMac: Tauri dev RIAVVIATO (nuovi PID, WinID=719, bounds 1472x914)
```

---

## COMPLETATO SESSIONE 115

### Phase 9: Screenshot Perfetti — COMPLETO ✅
- **23 screenshot** in `landing/screenshots/` (01-23)
- **22-pacchetti.png** (1472x914): 3 pacchetti stagionali con prezzi, sconti -28/-29%, servizi badges
- **23-fedelta.png** (1472x914): Anna Ferrari VIP 8/10 timbri, progress bar, VIP toggle
- **seed-pacchetti-fedelta.sql**: 3 pacchetti + loyalty data per Anna/Chiara/Elena
- Audit qualità tutti i 23 screenshot: PASS (dati IT, zero overlay, zero glitch)

### Bug trovato e fixato
- `servizi_inclusi` nella tabella `pacchetti` aveva dati JSON (inseriti da UI) che crashavano la query Rust `get_pacchetti` (aspetta i32, riceveva TEXT)
- Fix: eliminati vecchi pacchetti con tipo sbagliato, mantenuti solo i 3 stagionali con integer corretto
- **ATTENZIONE**: se qualcuno crea pacchetti dalla UI, il campo `servizi_inclusi` potrebbe essere salvato come JSON di nuovo → verificare il codice Rust/React

### Lezioni screenshot iMac (S115)
- **WinID cambia** dopo restart Tauri dev → SEMPRE ri-verificare con CGWindowListCopyWindowInfo
- **Window bounds**: dopo restart, finestra è 1472x914 (non 1200x800) → coordinate image = coordinate schermo-relative
- **Display sleep**: CGEvent NON sveglia il display → serve intervento fisico del fondatore
- **AXRaise**: necessario per portare la finestra in foreground prima di cliccare (`osascript AXRaise`)
- **Sidebar Y calibration**: Calendario=y226, spacing ~47px, Impostazioni=y651 (da window top)
- **NON sprecare token** su click automatici — chiedere al fondatore di aprire la pagina se i click non funzionano

---

## DA FARE S116

### IMMEDIATO: Phase 10 — Video V6
```
/gsd:plan-phase 10
```
- PAS formula: Problem(0:00-0:15) → Agitate(0:15-0:45) → Solution(0:45-5:00)
- Mostrare TUTTE le feature (Dashboard, Calendario, Clienti, Schede, Pacchetti, Fedeltà, Sara, Cassa, Analytics)
- 5 nuove clip AI Veo3 (scene "dopo FLUXION")
- Prezzo competitor: "centoventi euro al mese, millequattrocento all'anno"
- Thumbnail YouTube professionale
- Upload YouTube con capitoli, SRT, metadata SEO

### Research già pronta (272KB, 9 file)
```
.claude/cache/agents/
├── 2026-video-selling-trends-research.md     ← 19KB
├── veo3-clips-v6-research.md                 ← 3KB (prompt V6)
├── video-copywriter-v6-research.md           ← 29KB (bozza script PAS)
├── storyboard-v6-research.md                 ← 25KB (sequenza scene)
├── growth-first-100-clients-research.md      ← 28KB
├── landing-v2-optimization-research.md       ← 31KB
├── competitor-video-analysis-2026.md         ← 35KB
├── video-sales-outreach-research-2026.md     ← 32KB
└── us-smb-sales-outreach-research-2026.md    ← 36KB
```

---

## ACCOUNT & CREDENZIALI

### Google Cloud (Video AI)
```
Email: fluxion.gestionale@gmail.com
Project: project-07c591f2-ed4e-4865-8af
Crediti: €254 (scadenza 22 giugno 2026)
Auth: gcloud SDK (/usr/local/share/google-cloud-sdk/bin/gcloud)
```

### Stripe
```
Base: https://buy.stripe.com/bJe7sM19ZdWegU727E24000
Pro: https://buy.stripe.com/00w28sdWL8BU0V9fYu24001
```

---

## GSD MILESTONE v1.0 Lancio

```
Phase 9:  Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10: Video V6             ⏳ PROSSIMO
Phase 11: Landing + Deploy     ⏳
Phase 12: Sales Agent WA       ⏳
Phase 13: Post-Lancio          ⏳
```
Ordine: 9 → 10 → 11 → 12 → 13 (dipendenze sequenziali)

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 116.
Phase 9 Screenshot COMPLETATA. 23 screenshot pronti.
COMANDO: /gsd:plan-phase 10
- Video V6 PAS formula, tutte le feature
- Research 272KB già pronta in .claude/cache/agents/
- Screenshot 01-23 pronti per compositing
- Google Cloud €254 crediti, Veo 3 operativo
- Servizi iMac ATTIVI (3001 + 3002)
```
