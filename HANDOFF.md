# FLUXION — Handoff Sessione 172 (2026-04-27)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## SESSIONE 172 — FASE A.2 CHIUSA, DEPLOY MAIN LIVE (2026-04-27)

### ✅ Fatto S172
**Deploy main**: https://fluxion-landing.pages.dev/#feature-deep (HTTP 200, 150555B, 304ms)
**Preview finale**: https://6260e867.fluxion-landing.pages.dev/#feature-deep
**9 nuove headline verificate via curl+grep**: "Mentre sei col cliente / Slot pieno / Non viene da 2 mesi / al posto tuo / sul dente giusto / riparti in 5 minuti / come in banca / Aruba o Fattura24 / prima della fattura"
**ZERO residui tecnici** (grep production HTML): Groq | Microsoft | Edge-TTS | Node.js | nascoste nel codice | AES-256 | GCM | FDI | Oswestry → 0 match nel copy primario.

### Feedback fondatore S171 → tutti risolti
| Feedback | Risolto |
|----------|---------|
| Copy da rivedere completamente | ✅ 15 edit applicati su `landing/index.html` (45 ins / 33 del) |
| Riferimenti Grok/Microsoft TTS rimuovere | ✅ sostituiti con "provider esterni internazionali certificati" |
| Node.js bundled nei pacchetti | ✅ disclosure WhatsApp riscritta ("scansione QR code una volta all'attivazione") |
| "9 funzioni nascoste nel codice" non piace | ✅ rimossa, headline nuovo "Mentre sei col cliente, FLUXION ci pensa lui" |
| "Puoi sicuramente fare di meglio" | ✅ trend-researcher + landing-optimizer (2 subagenti paralleli) → iterazione mirata |

### Subagenti S172
1. `trend-researcher` (Opus) → `.claude/cache/agents/s172-best-practice-landing-it.md`
   - Competitor analysis WeGest / FattureInCloud / Fresha / Booksy
   - Pattern copy IT 2026: "tu" form, euro-anchored, paragrafi 35-40 parole
   - 5 alternative headline + razionale colloquiale PMI
2. `landing-optimizer` (Sonnet) → `.claude/cache/agents/s172-feature-deep-audit.md`
   - 12-dim audit S171 preview: 4 BLOCK / 5 FLAG / 3 PASS
   - Full copy rewrite per 9 card + disclosure cleanup checklist + bridge CTA mancante
3. **Sintesi**: per ogni card scelto best-of (trend più colloquiale per headline section, audit per body)

### Edit applicati (15 totali)
- **Header section** (1697-1704): "9 funzioni già incluse" + headline nuovo + sottotitolo PMI-friendly
- **3 hero card** body ridotti 78-85 → 35-40 parole (Instapage 2025 / Fresha pattern)
  - Sara Waitlist: pain €40-€80/slot* concretizzato
  - Recall: "non viene da 2 mesi" colloquiale
  - GDPR: "€20 milioni*" + "consenso digitale firmato — valido per ispezione"
- **6 secondary card** h3 riscritti zero jargon: dente giusto / dolore in 30s / PC rotto / banca / Aruba o Fattura24 / prima della fattura
- **Bridge CTA nuovo** (post-grid): "Tutte e 9 le funzioni sono già incluse. Nessun extra da pagare." → btn `#prezzi`
- **Disclosure footnotes** aggiunti per claim quantitativi (€40-€80, 60 giorni, €20M) — D.Lgs 206/2005 art.21 + GDPR art.83 co.5
- **Pulizia globale**: rif. AES-256/Groq/Edge-TTS/Node.js anche in 3-pilastri (line 361), FAQ (2238), pricing table BASE (2037)

### 🛑 Tech debt aperto (non bloccante per landing)
- **`clienti.rs:309` E0282/E0599 sqlx** — bloccante per `tauri dev` (=> screenshot reali Fase A.3) e build PKG/MSI release. Da fixare PRIMA di S173.

---

## PIANO S173 — FIX CARGO + SCREENSHOT REALI + VIDEO REPLACE VO

### Fase A.3 — Screenshot reali (priority #1)
1. **Subagent `gsd-debugger` o `engineering/debugger`**: fix `clienti.rs:309` E0282/E0599 sqlx type inference
2. Avvio `tauri dev` su iMac via SSH
3. Cattura 8 screenshot mancanti (Sara Waitlist agenda, Recall WhatsApp thread, GDPR audit, Odontogramma, scale dolore, Backup ripristino, Cifratura icona, SDI provider switch, Listini fornitori storico)
4. Sostituzione mock CSS `.app-win` con `<img>` reali in `#feature-deep`

### Fase B — Video REPLACE VO (post-screenshot)
- 4 REPLACE VO Edge-TTS Isabella: parrucchiere/nail/dentista/centro_estetico (target 50-60s)
- 3 REWORK: officina (€13k hook 0-3s), barbiere (-1 screenshot), palestra (retention pain)
- Re-upload YouTube via `youtube_batch_upload.py --only X --replace`

### Fase C — Garanzia 30gg + Template GDPR
- CF Worker `fluxion-proxy/src/routes/refund.ts`: form public `/rimborso` + Stripe Refund API + KV audit
- 4 template GDPR: `informativa-privacy.docx`, `registro-trattamenti.docx`, `consenso-art9-sanitario.pdf`, `guida-gdpr.html`

---

## Prompt ripartenza S173
```
Sessione 173. Leggi HANDOFF.md → S172.
S172: Deploy main LIVE https://fluxion-landing.pages.dev/#feature-deep (15 edit, zero residui tecnici).
TASK S173 PARTE 1: fix tech debt cargo `clienti.rs:309` E0282/E0599
  → Subagent engineering/debugger (Sonnet)
PARTE 2: tauri dev su iMac → cattura 8 screenshot reali → sostituzione mock CSS
PARTE 3: Fase B video REPLACE VO 4 verticali (parrucchiere/nail/dentista/estetico)
Memorie attive: feedback_valorize_real_features, project_1_settore_per_licenza,
                feedback_understand_before_code, feedback_only_enterprise_skills
```

---

## SESSIONE 171 — FASE A IMPLEMENTATA, DEPLOY MAIN POSTICIPATO (2026-04-27)

### ✅ Fatto S171
**Commit `47c2885`** — `feat(S171): Fase A — sezione 9 feature underpromise valorizzate` (pushato master).
**Preview LIVE**: https://8520ad6b.fluxion-landing.pages.dev (HTTP 200, tutte 9 card verificate via curl+grep).

Sezione `id="feature-deep"` integrata in `landing/index.html` riga 1687 (post 3 Pilastri, pre Prezzi):
- **3 hero card** (full-width, layout 2 col testo+mock CSS app-win): Sara Waitlist (€40-€80/slot, centro estetico), Recall dormienti (30% clienti persi/anno, parrucchiere), Audit GDPR (€20M Garante, dentista/medico)
- **6 secondary card** (grid 3x2): Odontogramma FDI 32 denti, VAS/Oswestry/NDI, Backup notturni, AES-256-GCM, SDI multi-provider, Storico prezzi fornitori
- Headline scelta: **Variante A** "Quello che FLUXION fa, e i tuoi concorrenti non sanno ancora che esiste"
- Mock CSS `.app-win/.feature-pill/.g-card/.tag-ok` riusati (zero nuove dipendenze, zero JS)
- Disclaimer "Simulazione — dati dimostrativi" sotto ogni mock (D.Lgs 206/2005)
- Mobile-first (grid stacks <768px), lazy loading

### 🛑 Deploy main RINVIATO a S172 — decisione CTO
Founder ha richiesto best practice mondiali assimilate al mercato italian PMI. Con context S171 al 77% rischio overflow su research seria. **Non si improvvisa**. Preview rimane vivo come artefatto da auditare.

### ⚠️ Bug scoperti S171 (da risolvere S172+)
1. **Token CF `cfut_` scope mancante** — autentica ma manca `Account → Cloudflare Pages → Edit`. **RISOLTO da fondatore in sessione** (deploy preview funzionato), ma da verificare se persiste su nuovo sessione. Memory `reference_cloudflare_token.md` aggiornata.
2. **Cargo errors `clienti.rs:309` PREESISTENTI** — E0282/E0599 sqlx type inference bloccano `tauri dev` (=> screenshot reali impossibili) e build PKG/MSI release. Documentato in S170 handoff, **ancora aperto**. PRIMA di S173 Windows MSI va fixato.
3. **Subagent screenshot-capturer auto-blocked** — sandbox perm Bash/Write. Bypass con mock CSS riuscito. Per recapture screenshot reali servirà fix #2 sopra.

### Output subagent salvato
- `.claude/cache/agents/s171-landing-section.md` (410 righe) — 3 varianti headline, razionale ordine card, HTML completo, raccomandazioni copy. Riusabile in S172 per iterazione.

---

## PIANO S172 — RESEARCH + AUDIT + DEPLOY MAIN

### Fase A.2 — Best practice research (priority #1)
1. **Subagent `trend-researcher`** (Opus, ~5min): ricerca landing page B2B SaaS italiane 2026
   - Pattern Animalz/Marketing Profs/Wynter sul mercato IT
   - Top 10 SaaS italiani PMI: Fatture in Cloud, Wallabee, Welcome, Treedom, Faire — analisi sezioni feature
   - Specificità copy italiano vs english (formality, hierarchy, numeri concreti)
   - Output: `.claude/cache/agents/s172-best-practice-landing-it.md` (max 200 righe)
2. **Subagent `landing-optimizer`** (Sonnet, ~5min): audit del preview S171 vs best practice
   - https://8520ad6b.fluxion-landing.pages.dev sezione `#feature-deep`
   - 12 dimensioni: hierarchy, copy density, mobile UX, scroll friction, social proof, CTA flow, accessibility, semantic HTML, JSON-LD, alt-text, color contrast, typography
   - Output: `.claude/cache/agents/s172-feature-deep-audit.md` con verdict PASS/FLAG/BLOCK per dimensione
3. **Iterazione mirata** (max 30min): solo i FLAG/BLOCK del audit. Headline può cambiare se dati lo suggeriscono.
4. **Re-deploy preview** → re-verify → **deploy main** con `wrangler pages deploy . --branch=main`

### Fase A.3 — Screenshot reali (post fix cargo)
- DOPO fix `clienti.rs:309` (Sonnet, gsd-debugger), avvio `tauri dev` su iMac
- Cattura 8 screenshot mancanti (lista in HANDOFF S170 sezione 9 feature underpromise)
- Sostituzione mock CSS con `<img>` reali

### Fase B — Video REPLACE VO (post-audit landing)
- 4 REPLACE VO Edge-TTS Isabella: parrucchiere/nail/dentista/centro_estetico (target 50-60s finali)
- 3 REWORK: officina (sposta €13k in hook 0-3s), barbiere (-1 screenshot), palestra (chiarisci pain retention)
- Re-upload YouTube via `youtube_batch_upload.py --only X --replace`

### Fase C — Garanzia 30gg + Template GDPR (post-Fase A.3)
- CF Worker `fluxion-proxy/src/routes/refund.ts`: form public `/rimborso` + Stripe Refund API + KV audit
- 4 template GDPR: `informativa-privacy.docx`, `registro-trattamenti.docx`, `consenso-art9-sanitario.pdf`, `guida-gdpr.html`

---

## Prompt ripartenza S172
```
Sessione 172. Leggi HANDOFF.md → S171.
S171: Fase A implementata + preview LIVE https://8520ad6b.fluxion-landing.pages.dev
      Deploy main RINVIATO per research best practice IT.
TASK S172 PARTE 1: spawn 2 subagenti paralleli:
  - trend-researcher → best practice landing B2B SaaS italiani 2026
  - landing-optimizer → audit 12-dim del preview attuale
PARTE 2: iterazione mirata sui FLAG/BLOCK
PARTE 3: deploy main + commit final + update HANDOFF/MEMORY/ROADMAP
Memorie attive: feedback_valorize_real_features, project_1_settore_per_licenza,
                feedback_understand_before_code (best practice → research → implement)
```

---

## SESSIONE 170 — FASE 0 CHIUSA (2026-04-27)

### ✅ FASE 0 UNBLOCK LEGALE — COMPLETATA (10 step in 1 commit)
**Commit**: `19154b5` fix(S170): Pro max_verticals 3→1 (vincolo 1 settore per licenza)
**Deploy**: https://fluxion-landing.pages.dev/ (HTTP 200, verificato curl)

| # | Step | Esito |
|---|------|-------|
| 1 | STOP LaunchAgent WA monitor iMac | ✅ unloaded + plist .DISABLED |
| 2 | Rimuovi card Clinic dalla landing | ✅ spostata in `landing/_clinic_disabled.html` |
| 3 | `Pro: max_verticals: 1` | ✅ `license_ed25519.rs:202` (era 3) |
| 4 | Rebuild iMac via SSH | ⚠️ cargo check: errori PREESISTENTI in `clienti.rs:309` (E0282/E0599) — non causati dal mio fix, ma da segnalare in S171 |
| 5 | Riallinea tabella prezzi landing | ✅ grid 3→2 col, Pro card riscritta con 8 feature reali (Sara, WA AI, Recall, Tessera, RAG chat, Listini, Audit GDPR) |
| 6 | Riscrivi sezione fedeltà landing | ✅ rimossi 4-tier Bronze/Silver/Gold/Platinum + sistema punti, sostituiti con 3 strumenti reali (tessera timbri, clienti VIP, pacchetti prepagati) + box riconoscimento Sara |
| 7 | Riscrivi claim GDPR | ✅ "in regola senza fare nulla" → "strumenti GDPR + 4 template, 30 min" + dichiarazione onesta su Sara/Groq US |
| 8 | Asterischi disclosure landing | ✅ blocco "Note &amp; precisazioni" con 6 voci: VoIP separato, 200 NLU/giorno + provider USA, Node.js per WA, SDI provider esterno, GDPR responsabilità titolare, garanzia 30gg meccanismo email + Stripe Refund 5-10gg |
| 9 | Latenza claim 1-2s | ✅ "<1 secondo" → "1-2 secondi", mockup "680ms" → "1.2s" |
| 10 | Deploy CF Pages production | ✅ wrangler pages deploy main, 90 file uploaded |

### ⚠️ Note Fase 0
- **Cargo check errors PREESISTENTI**: `src-tauri/src/commands/clienti.rs:309` ha errori E0282/E0599 (sqlx type inference) NON causati dal fix Pro=1. Verificato con `git stash` su iMac: errori presenti anche senza modifica. Da fixare in S171 prima di build release.
- **macOS minimum**: aggiornato 11→12 (Big Sur→Monterey) sia in FAQ che in box requisiti minimi.
- **VIP CSS classes leftover**: `.vip-bronze/.vip-silver/.vip-gold/.vip-platinum` (righe 140-143 landing/index.html) ancora presenti ma non più usate. Pulizia cosmetica per S171.
- **WA monitor**: per riattivare, `mv ~/Library/LaunchAgents/com.fluxion.wa-monitor.plist.DISABLED ...plist && launchctl load`.

---

## SESSIONE 170 — RICERCHE PRE-FASE 0 (riferimento storico)

### Fatto: Embed YouTube nella landing CF Pages — LIVE
1. **`landing/index.html` — sostituito `<video>` locale con iframe YouTube**
   - URL: `https://www.youtube-nocookie.com/embed/22IQmealPrw?rel=0&modestbranding=1&playsinline=1`
   - `loading="lazy"` → no payload 17.5MB finché non scrolla (LCP boost)
   - `referrerpolicy="strict-origin-when-cross-origin"` (privacy hardening)
   - Domain `youtube-nocookie.com` → no tracking pre-interazione
2. **JSON-LD VideoObject aggiornato (SEO)**:
   - `thumbnailUrl` → `https://i.ytimg.com/vi/22IQmealPrw/maxresdefault.jpg`
   - `contentUrl` + `embedUrl` → YouTube
   - `duration` → `PT2M29S` (corretto, era `PT1M20S` errato)
   - `uploadDate` → `2026-04-27`
3. **Deploy CF Pages production**: https://fluxion-landing.pages.dev/ (HTTP 200, embed verificato live)
4. **Push GitHub**: `094ac4f..62ad259 master -> master` (CI bypass landing-only OK)
5. **File orfano**: `landing/assets/fluxion-demo.mp4` (12MB) NON era git-tracked — solo asset locale, può restare come backup. Prossimo deploy CF Pages non lo serve più.

### Commit S170
```
62ad259  feat(S170): YouTube iframe embed landing — 22IQmealPrw
```

### Research professionale conversion (3 agenti paralleli + audit) — COMPLETATA
File in `.claude/cache/agents/s170-conversion-research/`:
- `01-competitor-benchmark.md` — Fresha/Booksy/Mindbody/Housecall/Jane vs Panema/WeGest (gap IT). Wistia 2025: <1min=52% engagement. Wyzowl 2026: 71% utenti preferisce 30s-2min. Lift video landing +34-86%. CR B2B SaaS media 1.1%, HVAC 3.1%.
- `02-funnel-ux-audit.md` — funnel WA→landing→video→Stripe stimato 0.2-0.3% baseline → target 0.6-1.2% (3-4x). 5 quick wins <2h: og:image, copy sopra iframe, banner garanzia, link verticale WA, link riga propria.
- `03-storyboard-per-vertical.md` — 9 verticali analizzati frame-by-frame. **Verdict**: 4 REPLACE VO (parrucchiere VO 40s, nail 42s, dentista 45s, centro_estetico 47s — bloated → target 25-27s), 3 REWORK (officina/barbiere/palestra), 3 KEEP (landing/carrozzeria/fisioterapista). Costo €0 (Edge-TTS Isabella + FFmpeg remix).
- `04-landing-vs-reality.md` — **AUDIT CRITICO**: voto C+. 30 claim → 11 OK / 9 sfumature / **6 CRITICI** / 4 non verificabili.
- `SYNTHESIS.md` — decision matrix + roadmap 4 fasi.

### Audit Critico Landing — 3 mismatch CRITICI scoperti
1. **🔴 Tier "Clinic €1.497" FANTASMA** — Stripe webhook (`stripe-webhook.ts:35-37`) mappa solo `49700→base, 89700→pro`. CTA Clinic punta a stesso payment link Pro (`buy.stripe.com/00w28sdWL8BU0V9fYu24001`). Cliente paga €897 credendo €1.497 → chargeback + AGCM.
2. **🔴 Pro promette "6 settori" ma codice ne dà 3** — `license_ed25519.rs:201` `Pro: max_verticals: 3`. Reso garantito.
3. **🔴 Loyalty 4-tier "Bronze/Silver/Gold/Platinum a punti" INVENTATO** — DB reale (`005_loyalty_pacchetti_vip.sql:14-17`) ha solo `loyalty_visits` counter (tessera timbri). Nessun tier, nessun bonus euro/compleanno/referral.
4. ⚠️ "Risponde in <1 secondo" + mockup "680ms" — realtà ~1330ms (`voice-agent-details.md:28`)
5. ⚠️ "Garanzia 30gg" — nessun meccanismo nel codice (solo email manuale)
6. ⚠️ "GDPR senza fare nulla" — pericoloso per studi sanitari (Art. 9, registro trattamenti)

### Decisioni Fondatore (RECEPITE — vincoli per tutta sessione futura)
| # | Decisione | Implicazione |
|---|-----------|--------------|
| 1 | **STOP invio WA** | Disable LaunchAgent monitor su iMac fino a Fase 0 chiusa |
| 2 | **Tier Clinic → RIMOSSO** | Commenta HTML in `_clinic_disabled.html`, riprogrammiamo quando business parte |
| 3 | **VINCOLO ASSOLUTO: 1 SETTORE PER LICENZA** | `Pro: max_verticals: 1` (NON 3, NON 6). Multi-attività = multi-licenza. Pro≠più verticali. |
| 4 | "Dati sul tuo PC" → lascia (sotto sua responsabilità) | Manteniamo claim, niente DPA changes |
| 5 | NO testimonial inventati | Bloccato D.Lgs 206/2005 art. 23. Andiamo di numeri reali + demo Sara live + garanzia |
| 6 | GDPR → 4 template scaricabili | Da costruire: informativa, registro trattamenti, consenso Art.9, guida 30min |
| 7 | Garanzia 30gg → meccanismo automatico | CF Worker route `/rimborso` + Stripe Refund API (~80 LOC + 2h) |
| 8 | **VALORIZZARE FEATURE REALI** (priorità #1 dopo unblock) | Fondatore frustrato: "100 sessioni cerco di evidenziarti queste feature" |

### Differenza Base/Pro RIALLINEATA (1-settore-per-licenza)
| Feature | Base €497 | Pro €897 |
|---------|-----------|----------|
| Settore | 1 | 1 |
| Calendario+clienti+cassa+schede verticali+SDI+WA conferme+backup+AES | ✅ | ✅ |
| **Sara Voice Agent 24/7** | ❌ | ✅ |
| **WhatsApp AI auto-risposta** | ❌ | ✅ |
| **Loyalty/Pacchetti/Recall dormienti** | ❌ | ✅ |
| **RAG Chat (Sara testuale)** | ❌ | ✅ |
| **Listini fornitori + tracking prezzi** | ❌ | ✅ |
| **Audit trail GDPR completo** | ❌ | ✅ |

### 9 Feature UNDERPROMISE (assenti/svalutate sulla landing — Fase A le porta in evidenza)
1. Waitlist intelligente Sara (PROPOSING_WAITLIST → WAITLIST_SAVED)
2. Recall dormienti automatico (`reminder_scheduler.py:627`, dopo 60gg)
3. Odontogramma FDI 32 denti (scheda dentista)
4. Scale dolore VAS/Oswestry/NDI (scheda fisio)
5. Audit trail GDPR completo (`018_gdpr_audit_logs.sql` + `037_gdpr_art9_consent.sql`)
6. Backup automatici locali giornalieri (`lib.rs:466 run_auto_backup_if_needed`)
7. Encryption AES-256-GCM at rest (`encryption.rs gdpr_encrypt`)
8. Multi-provider SDI Aruba/Fattura24/OpenAPI (`029_sdi_multi_provider.sql`)
9. Listini fornitori con tracking variazioni prezzo (`031_listini_fornitori.sql`)

### Piano S170 → S171 (4 Fasi)
**Fase 0 — UNBLOCK LEGALE** (~3h, bloccante, reversibile)
1. STOP LaunchAgent WA monitor su iMac
2. Rimuovi card Clinic dalla landing → `landing/_clinic_disabled.html` (commentata)
3. `license_ed25519.rs:201` → `Pro: max_verticals: 1`
4. Rebuild iMac via SSH dopo modifica Rust
5. Riallinea tabella prezzi landing alla nuova differenza Base/Pro
6. Riscrivi sezione fedeltà landing → tessera timbri + VIP + pacchetti (no 4-tier)
7. Riscrivi claim GDPR → "Strumenti GDPR + 4 template pronti, 30 min e sei in regola"
8. Asterischi: VoIP separato, 200 NLU/giorno, macOS 12+, Node.js per WA
9. Cambia "<1 secondo" → "1-2 secondi" + mockup 680ms→1.2s
10. Deploy CF Pages production

**Fase A — VALORIZZAZIONE FEATURE REALI** (~4-6h) — priorità fondatore #1
- Nuova sezione hero post-video, pre-prezzi: "Le 9 cose che FLUXION fa e nessun altro ti dice"
- Per ogni feature: pain → soluzione FLUXION (1 frase) → screenshot reale dell'app
- Screenshot mancanti da catturare via skill `fluxion-screenshot-capture` su iMac

**Fase B — VIDEO REPLACE VO + REWORK**
- 4 REPLACE VO Edge-TTS Isabella: parrucchiere/nail/dentista/centro_estetico (target 50-60s finali)
- 3 REWORK: officina (sposta €13k in hook 0-3s), barbiere (-1 screenshot), palestra (chiarisci pain retention)
- Re-upload YouTube via `youtube_batch_upload.py --only X --replace`
- Incorporare nei copioni le feature reali Fase A (odontogramma in dentista, VAS in fisio, waitlist in estetico, recall in parrucchiere)

**Fase C — Garanzia 30gg + Template GDPR**
- CF Worker `fluxion-proxy/src/routes/refund.ts`: form public `/rimborso` + Stripe Refund API + KV audit
- 4 template GDPR: `informativa-privacy.docx`, `registro-trattamenti.docx`, `consenso-art9-sanitario.pdf`, `guida-gdpr.html`

### Prompt ripartenza S171 (post-compact)
```
Sessione 171 - Fase 0 UNBLOCK LEGALE in corso.
Leggi HANDOFF.md → S170 sezione COMPLETA. Decisioni fondatore RECEPITE.
Step Fase 0: 1) STOP WA LaunchAgent iMac 2) commenta Clinic landing
3) Pro:max_verticals:1 in license_ed25519.rs:201 4) rebuild iMac
5) tabella prezzi landing nuova 6) sezione fedeltà honest
7) GDPR claim onesto 8) asterischi (VoIP/NLU/macOS12/Node)
9) latency 1-2s 10) deploy CF Pages.
Commit atomici per ogni step. Memorie attive: feedback_valorize_real_features,
project_1_settore_per_licenza.
```

---

## SESSIONE 169 — CHIUSA (2026-04-27)

### Fatto: Upload YouTube 10 video — TUTTI ONLINE
1. **OAuth setup completato** — Google Cloud project `553726534325`, YouTube Data API v3 abilitata, OAuth Desktop client `client_secrets.json` + token salvato (entrambi gitignored)
2. **Script batch `scripts/youtube_batch_upload.py` creato** — resumable, multi-video, progress bar, retry automatico, log JSON, supporto `--only`/`--privacy`/`--retry-failed`
3. **10 video uploadati** (privacy: `unlisted` per safety review)
4. **Sync iMac→MacBook** di `landing_v4_16x9.mp4` rebuilt post-fix S168 (17.5 MB, 24 Apr 19:11)

### URL video uploadati (tutti UNLISTED — promuovere a public dopo review)

| Video | URL | Embed |
|-------|-----|-------|
| **landing_v4** (main) | https://www.youtube.com/watch?v=22IQmealPrw | `/embed/22IQmealPrw` |
| parrucchiere | https://www.youtube.com/watch?v=FlNHHvxxfOE | `/embed/FlNHHvxxfOE` |
| barbiere | https://www.youtube.com/watch?v=Dd9DgAzfUtk | `/embed/Dd9DgAzfUtk` |
| officina | https://www.youtube.com/watch?v=pG9VKWSbYd4 | `/embed/pG9VKWSbYd4` |
| carrozzeria | https://www.youtube.com/watch?v=1HXQBBUmgp0 | `/embed/1HXQBBUmgp0` |
| centro_estetico | https://www.youtube.com/watch?v=hWs8wI6t3xU | `/embed/hWs8wI6t3xU` |
| nail_artist | https://www.youtube.com/watch?v=rau4yuR9NS4 | `/embed/rau4yuR9NS4` |
| dentista | https://www.youtube.com/watch?v=1sa4MN8bmGU | `/embed/1sa4MN8bmGU` |
| fisioterapista | https://www.youtube.com/watch?v=y8YMK7GWKLU | `/embed/y8YMK7GWKLU` |
| palestra | https://www.youtube.com/watch?v=GzSbYJBCXAk | `/embed/GzSbYJBCXAk` |

Log completo: `scripts/youtube_uploads_log.json` (gitignored).

### Backlog S170
1. **Review video su YouTube Studio** — qualità, titoli, descrizioni, thumbnail
2. **Promuovere a `public`** quelli approvati:
   ```bash
   python3 scripts/youtube_batch_upload.py --execute --privacy public --retry-failed
   ```
   (oppure manualmente da YouTube Studio per maggior controllo)
3. **Thumbnail dedicate verticali** — ora hanno solo auto-generated YT (script supporta thumbnail custom in `landing/assets/`)
4. **Aggiornare landing** — embeddare `https://www.youtube.com/embed/22IQmealPrw` nella landing principale (sostituire video file locale per loading veloce + analytics YT)
5. **Backlog S168 ancora aperto**: dinamicizzare waveform Sara, slide-static whitelist verify-videos, Windows MSI, Sentry, WA verifica risposte primo batch

### Prompt ripartenza S170
```
Sessione 170. Leggi HANDOFF.md → S169.
S169: 10 video YouTube ONLINE (unlisted). Landing principale: 22IQmealPrw.
TASK: (1) review qualità video YouTube Studio. (2) promuovere a public quelli approvati.
(3) embeddare landing_v4 YouTube nella landing CF Pages (sostituire video locale).
```

---

## SESSIONE 168 — CHIUSA (2026-04-24)

### Fatto
1. **Commit + push S167** → `5484cf1 fix(S167): video freeze root cause + enterprise delta`
2. **Fix path portable SCREENSHOTS** → `1a68cd6 fix(S167): portable SCREENSHOTS path in assemble_landing_v4`
   - Hardcoded `/Volumes/MontereyT7/FLUXION/landing/screenshots` bloccava build iMac
   - Sostituito con `BASE.parent / "landing" / "screenshots"` (repo-relative)
3. **Rigenerazione `landing_v4_16x9.mp4` su iMac** — 149.4s, 16.7 MB (prima era 143s / 73% congelato)
4. **Skill `/verify-videos` creata + testata**
   - `.claude/skills/verify-videos/SKILL.md` (frontmatter trigger-rich)
   - `.claude/skills/verify-videos/verify-videos.sh` (freezedetect + mpdecimate + blackdetect + silencedetect + idet)
   - Smoke test su video esistenti → detection corretta (40% duplicates, 7 freeze, ecc.)
5. **Verifica frame-level post-fix**:
   - **Clip Veo3 dinamiche (0-31s): ZERO freeze events** → fix S167 verificato al 100%
   - Freeze residui (16 eventi totali, 95s) **sono tutti su contenuto statico atteso**: screenshot dashboard, CTA, URL, scheda parrucchiere, calendario. Semanticamente corretto (non è più il bug patologico di clip dinamiche congelate).
   - Waveform Sara (43-75s): 10 freeze durante pause naturali del dialogo — limite intrinseco di `showwaves mode=cline`.

### Verdetto S167
✅ **BUG SISTEMICO PAD_VIDEO_TO_AUDIO RISOLTO.**
Le 17 freeze events originali (73% congelato) erano tutte dovute a `tpad=stop_mode=clone` che congelava l'ultimo frame quando VO > clip. Ora con `-stream_loop -1 + -shortest` il video ricicla. Nelle clip dinamiche (Veo3) i freeze sono spariti completamente. I freeze residui esistono solo dove è semanticamente atteso (slide statiche + waveform con pause audio).

### Backlog S169
1. **Dinamicizzare waveform Sara** (elim. 10 freeze residui nella sezione 43-75s)
   - Opzioni: background gradient animato, pulse ring sul dot "CHIAMATA IN CORSO", showspectrum+showwaves combinato, drawtext lampeggiante
2. **Skill verify-videos: slide-static whitelist** — aggiungere concept "expected-static-regions" per filtrare falsi positivi su screenshot slide.
3. **Upload YouTube** dei 9 verticali + landing_v4 corretto
4. **S168 Windows MSI build** (bloccante per 75% PMI italiane)
5. **Enterprise gap #2**: Sentry error tracking integration
6. **S162 WA verifica risposte** primo batch + secondo batch 5 msg

---

## SESSIONE 167 — CHIUSA (2026-04-24)

### Fatto
1. **Analisi prompt enterprise universale** (`~/Downloads/PROMPT_CC_ENTERPRISE_UNIVERSALE.md`)
   - Verdetto: metodologia 7.5/10, ma FLUXION ha già foundation (47 skill + 67 agent + 4 hook). Duplicherebbe.
   - Applicato solo il **delta reale** (NORTH_STAR + PLAYBOOK).
   - Dettagli in `memory/project_enterprise_delta.md`.

2. **Bug video `landing_v4_16x9.mp4` — ROOT CAUSE IDENTIFICATA + FIX**
   - Inizialmente segnalato come "freeze a 00:24"
   - Research (2 subagenti paralleli CoVe 2026) rivela: **17 freeze events, 105s su 143s congelati (73%)**
   - Root cause: `video-factory/assemble_landing_v4.py:747` funzione `pad_video_to_audio()` usava `tpad=stop_mode=clone:stop_duration=X` che congelava ultimo frame quando voiceover > clip
   - FIX applicato: sostituito con `-stream_loop -1 + -shortest` → video ricicla clip fino a fine audio, zero freeze frame possibili
   - `assemble_all.py` (9 verticali) NON ha il bug: usa `image_to_video()` con durata controllata

3. **Enterprise delta creato**
   - `.claude/NORTH_STAR.md` — contratto strategico immutabile (cliente, dolore, valore, revenue, esclusioni, vincoli)
   - `.claude/PLAYBOOK.md` — procedure correnti (pricing, messaggistica, sales WA, deploy CF/iMac/Tauri, runbook incident, sessioni CC, convenzioni codice)

### Da fare (S168 o continuazione S167)
1. **Rigenerare `landing_v4_16x9.mp4` su iMac** con il fix:
   ```bash
   ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master && \
     cd video-factory && python3 assemble_landing_v4.py"
   ```
2. **Verifica frame-level** con i comandi ricercati (da salvare come skill `/verify-videos`):
   ```bash
   ffmpeg -i landing_v4_16x9.mp4 -vf "freezedetect=n=0.003:d=0.5" -map 0:v:0 -f null - 2>&1 | grep lavfi
   # Expected: ZERO freeze events post-fix
   ```
3. **Creare skill `/verify-videos`** con il bash snippet completo (metadata + freezedetect + mpdecimate + blackdetect + silencedetect + idet)
4. **Commit**: `fix(S167): video freeze root cause + enterprise delta (NORTH_STAR + PLAYBOOK)`

### Backlog enterprise (post-lancio)
- ADR directory `docs/adr/` per decisioni architetturali
- Sentry error tracking (free tier) per crash clienti reali
- Rollback automatico landing post-deploy
- Coverage threshold pre-commit
- Skill `alignment-check` (gate NORTH_STAR pre-feature)

### Prompt ripartenza S168
```
Sessione 168. Leggi HANDOFF.md → sezione S167.
Task: (1) ssh imac + git pull + rigenera landing_v4_16x9.mp4 con fix assemble_landing_v4.py.
(2) Verifica frame-level con freezedetect — expected 0 eventi.
(3) Se OK, crea skill /verify-videos con bash snippet.
(4) Commit S167.
```

---

## SESSIONE 162 PRECEDENTE (2026-04-15)

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline porta 3002 | SIP: 0972536918

---

## SESSIONE 160 — COMPLETATA (2026-04-15)

### Risultati
1. **5 messaggi WA inviati a lead reali** (warm-up settimana 1)
   - ANNAHO Hair Stylist (+393515388599) — 09:08
   - Bésame Hair Studio (+393755247777) — 09:10
   - Franco e Mimma Coiffeurs (+393756197782) — 09:15
   - La Zona Barberia (+393888809125) — 09:18
   - Lubestyle (+393336152116) — 09:20
   - 3 numeri skip (non su WA)
   - Delay gaussiano: 94-119s tra msg — anti-ban OK

2. **Reply Monitor** — `tools/SalesAgentWA/monitor.py`
   - Scansiona WA Web (headless=False, sessione persistente)
   - Comando manuale: `python3 agent.py monitor`

3. **LaunchAgent `com.fluxion.wa-monitor`** — INSTALLATO su iMac
   - Orario: 09:00–12:00 e 14:00–17:00, ogni 15min, lun-ven
   - Sincronizzato con timezone iMac (CEST)
   - Log: `/tmp/wa_monitor_cron.log`
   - Plist: `~/Library/LaunchAgents/com.fluxion.wa-monitor.plist`
   - ⚠️ NOTA: alla prima run alle 09:45 potrebbe chiedere QR scan se sessione scaduta

4. **Scraping multi-citta** — 198+ lead in DB
   - Categorie: parrucchiere, officina, estetico, palestra (+ dentista in corso)
   - Città: milano, roma, napoli, torino, bologna, firenze

5. **Dashboard live**: http://127.0.0.1:5050 su iMac

6. **Fix odontoiatra** — 12/12 booking completi
   - `VERTICAL_SERVICES["odontoiatra"]` aggiunto a `italian_regex.py`
   - `orchestrator.py`: `_load_business_context()` usa `SUB_VERTICAL_TO_MACRO`
   - Test E2E: "pulizia dei denti" → igiene_professionale → STATE:completed ✅

### Test Results S160
```
Sara FAQ:        12/12 OK
Sara Booking:    12/12 COMPLETE (odontoiatra fixato)
WA Send:         5/5 inviati a lead reali (3 skip non-WA)
Scraping:        198+ lead (6 città, 5 categorie)
Reply Monitor:   LaunchAgent attivo ogni 15min in orario operativo
Dashboard:       LIVE http://127.0.0.1:5050
TypeScript:      0 errors
```

### Commit S160
```
4403550  feat(S160): reply monitor + multi-city scraping CLI
bc41608  fix(S160): odontoiatra — pulizia dei denti → igiene_professionale
2d60b6c  docs(S160): HANDOFF updated
d867822  fix(S160): monitor headless=True (poi revertito)
58523c3  fix(S160): monitor headless=False — LaunchAgent GUI
```

---

## SESSIONE 162 — COMPLETATA (2026-04-15)

### Risultati
1. **Monitor fix** — navigazione diretta per-chat (commit `4f6bc61`)
   - Vecchio approccio: scansione lista chat WA Web → fragile, 0 items trovati
   - Nuovo approccio: naviga su `wa.me/send?phone=XXXXX` per ogni lead
   - E2E: 2/5 risposte auto-responder rilevate ✅
   - `monitor.py` deployato su iMac + push + sync

2. **Risposte ricevute** (auto-responder WA Business)
   - ANNAHO Hair Stylist: "Grazie per aver contattato Annahodesignhairstylis & Fashion!"
   - Bésame Hair Studio: "Grazie per aver contattato Bésame Hair Studio, ti risponderemo appena possibile."
   - 3 lead (Franco e Mimma, La Zona Barberia, Lubestyle): nessuna risposta ancora

3. **Stats attuali**
   - 5 inviati | 2 risposte (40% reply rate) | 3 falliti (no WA)
   - Risposte = messaggi automatici WA Business, NON risposta umana reale

4. **Production readiness verificata**
   - Voice Sara: ✅ ATTIVA porta 3002
   - TypeScript: ✅ 0 errors
   - LaunchAgent monitor: ✅ ogni 15min funzionante

### Test Results S162
```
Monitor Fix:     ✅ 2/5 risposte rilevate (auto-responder)
Voice Pipeline:  ✅ ATTIVA v2.1.0
TypeScript:      ✅ 0 errors
Git sync iMac:   ✅ aggiornato
```

### Commit S162
```
4f6bc61  fix(monitor): navigazione diretta per-chat invece di lista chat WA Web
```

---

## SESSIONE 163 — COMPLETATA (2026-04-15)

### Risultati
1. **Pianificazione Master E2E** — roadmap rivista e approvata
   - Ordine: A(Sara) → B(Video YT) → C(E2E acquisto) → E(Windows MSI) → D(WA scale)
   - Windows PRIMA di scalare WA (75% PMI italiane su Windows)
   
2. **Fase A — Sara Bug Fixes COMPLETATA** (commit `94e583f`)
   - Fix waitlist: `w.servizio_id` → `w.servizio` + LEFT JOIN by name (errore ogni 5min eliminato)
   - Fix voice_sessions: ALTER TABLE ADD COLUMN `summary TEXT DEFAULT ''`
   - Fix VoIP vertical: `_vertical_explicitly_set=False` in `greet()` → ricarica da DB ogni chiamata
   - Fix HTTP Bridge log: INFO invece di errore silenzioso
   - Fix eslint: `tmp-video-build/` + `fluxion-proxy/` ignorati, AudioWorklet globals aggiunti
   - DB aggiornato: `categoria_attivita=salone`, `nome_attivita=Salone Bella Demo`
   
3. **Test E2E Sara Fase A**
   - "Buongiorno, vorrei fare un taglio di capelli" → "Perfetto. Mi dice il nome, per cortesia?" ✅
   - Waitlist job: 0 errori nei log ✅
   - Pipeline riavviata e stabile ✅

### Test Results S163
```
Sara VoIP vertical:  ✅ salone (non più odontoiatra)
Sara waitlist:       ✅ 0 errori schema (era ogni 5min)
voice_sessions.db:   ✅ colonna summary aggiunta
HTTP Bridge log:     ✅ INFO standalone mode
ESLint:              ✅ tmp-video-build + fluxion-proxy ignorati
Git sync:            ✅ MacBook + iMac + remote allineati (94e583f)
```

### Commit S163
```
94e583f  fix(sara): waitlist servizio_id + vertical reload VoIP + voice_sessions summary + eslint
```

---

## PROSSIME SESSIONI

### SESSIONE 164 — VIDEO SU YOUTUBE (Fase B) — IN CORSO

**Video definitivo identificato**: `video-factory/output/landing/landing_final_16x9.mp4` (9 Apr, più recente)
**Problema risolto**: sezione FEATURES aveva voiceover errato (seg_1 "problema" suonava durante features list)

**Fix applicati in S164**:
- `assemble_all.py`: feature duration 2s → 6s (6s/feat × 8 + 4s finale = 52s section)
- `features_seg.mp3`: 9 clip sincronizzati (voce ~3.5s + respiro ~2s = metabolizzazione)
  - Ogni feature: Isabella la pronuncia → 1.6-2.7s di silenzio → utente metabolizza
  - Rate: +0% (voce normale, non affrettata)
- `landing_voiceover_v2.mp3`: features_seg + seg_1 + seg_2 + 6s_gap + seg_3
- Video ricostruito: ~122s ≈ 2:02 (era 97.5s)

**STEP MANCANTE**: Upload YouTube Studio manuale:
1. Video: `video-factory/output/landing/landing_final_16x9.mp4`
2. Thumbnail: `landing/assets/youtube-thumbnail-v8.png` (o fare nuova specifica per landing)
3. Metadata: `landing/assets/youtube-metadata-v8.json` (adattare titolo per video landing generico)
4. Dopo upload → ottenere URL e aggiornare landing + HANDOFF

### SESSIONE 165 — E2E ACQUISTO (Fase C)
```
STEP 1: Coupon Stripe 100% su Base €497
STEP 2: Test flusso: landing → Stripe → webhook → KV → email Resend → /installa
STEP 3: Download PKG macOS → install → attiva con email
STEP 4: /installa page: GIF Gatekeeper Sequoia 15.1+
STEP 5: Mobile test su device reale
```

### SESSIONE 166 — WINDOWS MSI (Fase E)
```
STEP 1: GitHub Actions build-windows.yml con WiX MSI
STEP 2: Test su VM Windows 10 (Parallels iMac)
STEP 3: /installa-windows + GIF SmartScreen
STEP 4: "Windows coming soon" placeholder sulla landing (bridge immediato)
```

### Sessione 164 mini — Fix statusline (2026-04-15)
- `gsd-statusline.js` → `gsd-statusline.cjs` (fix: package.json "type":"module" causava ReferenceError require)
- settings.json aggiornato a puntare `.cjs`
- Barra contesto `███░░░░░░░ 38%` ora funzionante

### PROBLEMA NOTO: Video YouTube — SI BLOCCA
- Il video `landing_final_16x9.mp4` durante l'upload su YouTube Studio si bloccava
- Da investigare nella prossima sessione (Fase B)
- Possibili cause: file troppo grande, connessione, browser issue

### Prompt di ripartenza S165
```
Leggi HANDOFF.md. Sessione 165.
S163: Fase A Sara bug fixes COMPLETATA. Commit 94e583f.
S164: Video assemblato ma upload YouTube si bloccava — da risolvere.
PIANO APPROVATO: A✅ → B(Video YT) → C(E2E acquisto) → E(Windows MSI) → D(WA scale)
TASK: Fase B — risolvere blocco upload video YouTube. Investigare causa (dimensione file? browser? connessione?).
      Video: video-factory/output/landing/landing_final_16x9.mp4
      Thumbnail: landing/assets/youtube-thumbnail-v8.png
```

---

## STATO GIT
```
STEP 1: Secondo batch invio (5 msg — 10 totali settimana 1):
        ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA' && nohup python3 agent.py send --limit 5 > /tmp/wa_send.log 2>&1 &"
        ⚠️ Inviare domani mattina (non stesso giorno — anti-ban)

STEP 2: Espandere scraping a dentista + palestra (tutte le città):
        ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA' && nohup python3 agent.py scrape --category dentista,palestra --city roma,napoli,torino,bologna,firenze > /tmp/scrape_3.log 2>&1 &"

STEP 3: Se arriva risposta umana reale (non auto-responder) → prepara follow-up manuale:
        Testo: "Ciao [NOME], vedo che gestisci [BUSINESS]. Ho creato un breve video
        su come altri saloni eliminano le chiamate perse. Posso mandarti 3 minuti di demo?"

STEP 4: Monitorare reply rate → se >10% risposte umane entro 48h → aumentare a 10 msg/giorno
```

### Prompt di ripartenza S163
```
Leggi HANDOFF.md. Sessione 163.
S162: Monitor WA fixato (navigazione diretta per-chat). 2/5 risposte auto-responder.
5 msg inviati il 15/04. Reply rate 40% (auto-responder).
TASK: Secondo batch 5 msg (domani). Scraping dentista/palestra. Gestire risposta umana se arriva.
```

---

## STATO GIT
```
Branch: master | Commit: 94e583f
```

---

## SESSIONE 165 — COMPLETATA (2026-04-16)

### Risultati
1. **Fix audio video landing** — bug critico risolto
   - Root cause: `landing_voiceover.mp3` (45.2s, senza features) usato invece di v2 (101.7s)
   - Root cause #2: `silence_6s.mp3` era 44100Hz vs tutti gli altri 24000Hz → backward in time
   - Fix: decodifica in WAV PCM 44100Hz stereo → concat pulito → remix
   - Output: `landing_v3_16x9.mp4` (12.4MB) — video 122.5s audio 122.5s ✅ zero silenzio

2. **Fix hooks settings.json** — path relativi → path assoluti
   - `pre_write_gate.py`, `stop_evidence_gate.py`, `pre_compact.py` crashavano se CWD ≠ project root
   - Fix: tutti i path ora assoluti `/Volumes/MontereyT7/FLUXION/.claude/hooks/...`

3. **Script upload YouTube** — `scripts/upload_youtube.py` creato
   - YouTube Data API v3, resumable upload, progress bar
   - Richiede `client_secrets.json` in `scripts/` (OAuth2 Desktop app)

4. **Storyboard features approvazione** — bozza v1 scritta ma NON approvata
   - Fondatore: "non rispecchia la realtà di FLUXION, si può fare molto meglio"
   - **S166: sessione dedicata al video perfetto**

### File chiave S165
```
video-factory/output/landing/landing_v3_16x9.mp4   ← video corretto (da usare)
video-factory/output/landing/landing_v3_9x16.mp4   ← 9:16 sorgente
video-factory/output/landing/landing_final_16x9.mp4 ← VECCHIO (audio tronco)
scripts/upload_youtube.py                           ← uploader API YouTube
```

### PROBLEMA APERTO: 16:9 senza sfondo sfocato
- `landing_v3_16x9.mp4` usa letterbox nero invece di blur background
- Va corretto in S166 quando si riassembla il video definitivo

### Test Results S165
```
Audio/video sync:   ✅ 122.5s / 122.5s (era 114.1s / 122.5s)
Silenzio anomalo:   ✅ ZERO (era 45s da 1:08 a fine)
Hooks path:         ✅ tutti assoluti
Upload script:      ✅ dry-run OK
```

---

## SESSIONE 166 — VIDEO PERFETTO (Fase B completa)

### Verifica automatica video (2026-04-16)
Tabella evidence completa — 12 video scansionati con ffprobe + silencedetect (-35dB/0.4s):

| Video | Dur | FPS | Res | Audio | VO% | Status |
|-------|-----|-----|-----|-------|-----|--------|
| barbiere | 58.9s | 30 | 1920x1080 | aac 24k mono | 96.8% | ✅ |
| carrozzeria | 60.0s | 30 | 1920x1080 | aac 24k mono | 98.5% | ✅ |
| centro_estetico | 81.4s | 30 | 1920x1080 | aac 24k mono | 97.7% | ✅ |
| dentista | 79.7s | 30 | 1920x1080 | aac 24k mono | 98.6% | ✅ |
| fisioterapista | 60.8s | 30 | 1920x1080 | aac 24k mono | 97.7% | ✅ |
| nail_artist | 76.2s | 30 | 1920x1080 | aac 24k mono | 97.6% | ✅ |
| officina | 60.9s | 30 | 1920x1080 | aac 24k mono | 97.8% | ✅ |
| palestra | 60.8s | 30 | 1920x1080 | aac 24k mono | 97.6% | ✅ |
| parrucchiere | 74.7s | 30 | 1920x1080 | aac 24k mono | 98.6% | ✅ |
| landing_final | 122.5s | 30 | 1920x1080 | aac 24k mono | **42.6%** | ❌ BROKEN |
| landing_v3 | 122.5s | 30 | 1920x1080 | aac 44.1k stereo | 99.0% | ⚠ letterbox |
| landing_v4 | 143.6s | 30 | 1920x1080 | aac 24k mono | 100.0% | ✅ candidato |

**Tech specs uniformi**: h264/1920x1080/30fps su tutti. CTA €497 confermata nel copione `video-factory/output/copioni_v2_definitivi.txt` per tutti i verticali.

**Azioni richieste**:
- 9 verticali: PRONTI per upload
- `landing/landing_final_16x9.mp4`: **DEPRECATO** — 70.3s silenzio (bug S165). Non uploadare.
- `landing_v4_16x9.mp4`: **BUG FREEZE scoperto dal fondatore** — a 00:24 il video si blocca ma l'audio procede. ffprobe non lo rileva (metadata OK). Serve analisi frame-by-frame in S167.

**Riferimenti `landing_final_16x9.mp4` nel repo** (verificato):
- `.claude/settings.local.json`
- `scripts/upload_youtube.py`
- `scripts/add-features-voiceover.py`
- `HANDOFF.md`
→ Prima di rinominare/eliminare il file, aggiornare questi 4 path.

### Summary verifica 2026-04-16 (preservato per S167)
- ✅ 9 video verticali — PASS (tech + narrativa + CTA €497 + VO >96%)
- ⚠️ `landing_v4_16x9.mp4` — metadata PASS ma **FREEZE video a 00:24** (audio prosegue) — da investigare
- ⚠️ `landing_v3_16x9.mp4` — audio OK, letterbox nero (non blur) — non ancora il definitivo
- ❌ `landing_final_16x9.mp4` — DEPRECATO (70s silenzio)

### Prompt di ripartenza S167
```
Leggi HANDOFF.md. Sessione 167.
S166: Verifica video completata. 9 verticali OK. Landing problemi:
  - landing_final: DEPRECATO (audio rotto S165)
  - landing_v3: letterbox invece blur
  - landing_v4: FREEZE a 00:24 (audio prosegue) — bug non rilevato da ffprobe
TASK S167:
1. Diagnosi frame-by-frame di landing_v4_16x9.mp4 (ffmpeg showinfo, mpdecimate, idet)
   → trovare causa freeze: clip sorgente? concat timestamp? fps mismatch?
2. Fix landing_v4 (riassemblare clip problematica o intero concat)
3. Ri-verifica con skill /verify-videos (da creare in .claude/skills/fluxion-video-verify/SKILL.md)
   La skill deve aggiungere check frame-level (non solo metadata): drop frames, dup frames, freeze detection.
4. Se OK → upload YouTube con scripts/upload_youtube.py
```

### Obiettivo
Creare il video definitivo FLUXION da zero, con voiceover che rispecchia la realtà del prodotto.

### Processo S166
```
STEP 1: Deep research — video competitor (Fresha, Mindbody, Calendly, software PMI IT)
         → cosa funziona, cosa no, gold standard 2026
STEP 2: Storyboard completo con Fondatore
         → ogni sezione: visivo + voiceover + timing + valore
STEP 3: Genera voiceover con Edge-TTS IsabellaNeural
         → testa ogni clip isolata prima di assemblare
STEP 4: Assembla video con blur background 16:9
         → usa assemble_all.py con voiceover_v4
STEP 5: Review con Fondatore → aggiusta → approva
STEP 6: Upload YouTube (API) + aggiorna landing
```

### Contesto per storyboard
- **Prodotto reale**: Tauri desktop app, SQLite locale, NESSUN cloud obbligatorio
- **Sara**: voce italiana al telefono, prenota, risponde FAQ, gestisce cancellazioni
- **Clienti target**: parrucchiere/barbiere, officina, dentista, estetica, palestra
- **Pain principale**: chiamate perse, doppie prenotazioni, clienti che non tornano
- **Differenziatore**: paghi UNA VOLTA (€497/€897), non abbonamento mensile
- **NON fare**: gergo tecnico, riferimenti ad AI/ML, paragoni con software enterprise

### Prompt di ripartenza S166
```
Leggi HANDOFF.md. Sessione 166.
S165: video audio fixato (landing_v3_16x9.mp4). Storyboard features NON approvato.
TASK: Sessione dedicata al VIDEO PERFETTO.
STEP 1: Deep research competitor video (Fresha, Mindbody, Jane App — cosa fa funzionare un video PMI?)
STEP 2: Proponi storyboard completo al Fondatore (OGNI feature deve rispecchiare la realtà di FLUXION)
STEP 3: Genera voiceover → assembla → review → upload YouTube
```
