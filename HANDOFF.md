# FLUXION — Handoff Sessione 130 → 131 (2026-04-01)

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

## COMPLETATO SESSIONE 130

### 1. Video V8 Generico (fluxion-promo-v8.mp4)
- 55.1 MB, 6:38, 47 scene, H.264 High CRF 18, 1280x720
- Aggiunta scena Fedelta' (23-fedelta.png) con voiceover VIP/timbri/premi
- Aggiunta "Con Sara lavori in maniera ordinata" (sostituisce s31 broken)
- Fix riferimento inesistente 21-trasformazioni-prima-dopo.png
- YouTube metadata (titolo, 31 tags, capitoli, SRT) + thumbnail 1280x720

### 2. Deep Research Verticale — 6 Report Completati
Research esigenze REALI per settore con dati mercato, pain points, competitor, pricing:
- `.claude/cache/agents/vertical-needs-parrucchiere.md` (120k attivita', no-show 30%, formula colore)
- `.claude/cache/agents/vertical-needs-officina.md` (89k attivita', revisione scaduta, mani nel grasso)
- `.claude/cache/agents/vertical-needs-dentista.md` (47k studi, no-show €200/poltrona, XDENT €200+/mese)
- `.claude/cache/agents/vertical-needs-estetica.md` (133k attivita', Treatwell 25% commissioni, pacchetti)
- `.claude/cache/agents/vertical-needs-palestra.md` (45k target, churn 40-60%, certificato medico)
- `.claude/cache/agents/vertical-needs-fisioterapista.md` (65k fisioterapisti, cicli 10 sedute, VAS)

### 3. Script Video per Settore — 6 Script Completati
Ogni script: formula PAS, dialogo Sara specifico, screenshot scheda verticale, confronto competitor reale:
- `scripts/video-scripts/01-parrucchiere.md` — 10 scene, ~2:30
- `scripts/video-scripts/02-officina.md` — 11 scene, ~2:30
- `scripts/video-scripts/03-dentista.md` — 11 scene, ~2:28
- `scripts/video-scripts/04-estetica.md` — PAS con controindicazioni, pacchetti, ~2:25
- `scripts/video-scripts/05-palestra.md` — 10 scene, churn + certificato, ~2:30
- `scripts/video-scripts/06-fisioterapista.md` — 10 scene, VAS 7→3, ~2:22

---

## STATO GIT
```
Branch: master | HEAD: 5ed9efb (pre-commit S130)
S130 work: scripts, research, video assets (to be committed)
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       DONE (S123-S126)
Phase 10e: Sara Bug Fixes       DONE FAQ vars + intent routing (S127)
Sprint 1:  Product Ready        DONE Prezzi + Phone-home + Demo seed (S127)
Sprint 2:  Screenshot Perfetti  DONE — 13 main + 9 schede + 3 recaptured (S128-S129)
Sprint 3:  Video per Settore    IN PROGRESS — 6 script pronti, voiceover+assembly NEXT
Sprint 4:  Landing Definitiva   PENDING
Sprint 5:  Sales Agent WA       PENDING
```

---

## VIDEO FACTORY INTEGRATA (fine S130)

Pipeline completa in `/video-factory/`:
- `run_all.py` — orchestratore CLI
- `video_factory/` — 9 moduli Python (veo3_client, script_generator, assembly, qa_check, music_layer, upload_distributor, wa_distributor, runway_fallback)
- 9 verticali: parrucchiere, barbiere, officina, carrozzeria, dentista, fisioterapista, palestra, nail_artist, centro_estetico
- Prompt Veo 3 esportati in `output/prompts/` per review
- GCP Project ID: `project-07c591f2-ed4e-4865-8af` (€234 crediti residui)
- Costo stimato: 27 clip × €3 = ~€81

---

## PROSSIMA SESSIONE 131

### A. Sprint 3 COMPLETAMENTO: Video Factory Pipeline (PRIORITY)
1. **REVIEW PROMPT** (gratis): `cat output/prompts/parrucchiere_prompts.json`
   - Verificare ogni prompt Veo 3 per qualita' e aderenza al settore
   - Integrare i pain point dalla deep research (vertical-needs-*.md)
2. **Musica**: fondatore fornisce tracce per mood settoriale
3. **TEST 1 verticale** (~€9): `python3 run_all.py --vertical parrucchiere`
   - **TEST E2E**: ffprobe durata 28-34s, 1080p 9:16, audio, brand "FLUXION" + "€497" nel CTA
4. **QA SKILL REVIEW**: qa_check.py su 9 dimensioni prima di procedere
5. **Se ok → tutti** (~€81): `python3 run_all.py --vertical all`
6. **Upload**: Vimeo (unlisted per WA) + R2 (CDN)

### B. Sprint 4: Landing con Video Embeddati
- Embed 9 video settoriali nella landing (sezioni dedicate)
- Hero screenshots aggiornati
- **TEST E2E**: curl landing + verifica video visibili + flusso acquisto

### C. Sprint 5: Sales Agent WA (Luca Ferretti)
- wa_distributor.py genera sequenza Day 0/2/5/10
- Anti-ban: max 5 contatti/giorno
- Scraping + outreach automatizzato

---

## ASSET VIDEO DISPONIBILI

### AI Clips (landing/assets/ai-clips-v2/)
V01_salone, V02_officina, V03_dentista, V04_palestra, V05_estetista,
V06_nails, V07_fisioterapista, V08_gommista, V09_elettrauto, V10_frustrazione,
V11_qrcode, V12_soddisfatta, V13_finale, V14_medico_paziente, V15_foto_portfolio,
V16_sara_intro, V17_sara_dialogo, V18_cliente_telefono,
V6-03_proprietario_soddisfatto, V6-04_cliente_whatsapp, V6-05_imprenditrice_pc,
V6-11_salone_sereno, V6-13_hook_missed_calls

### Screenshot (landing/screenshots/)
01-dashboard, 02-calendario, 03-clienti, 04-servizi, 05-operatori,
06-fatture, 07-cassa, 08-voice, 09-fornitori, 10-analytics, 11-impostazioni,
12-scheda-parrucchiere, 13-scheda-fitness, 14-scheda-estetica, 15-scheda-medica,
16-scheda-fisioterapia, 17-scheda-odontoiatrica, 18-scheda-veicoli,
19-scheda-carrozzeria, 20-scheda-selector, 22-pacchetti, 23-fedelta

### Musica
background-music.mp3, music-inspiring-cinematic.mp3

---

## NOTE TECNICHE

### Script generazione video per settore
Per ogni verticale serve:
1. `scripts/generate-sector-voiceover.py` — legge script .md, genera MP3 Edge-TTS
2. `scripts/compose-sector-video.py` — assembla clip + screenshot + voiceover + musica
3. Pattern: stessa architettura di compose-v8-video.py ma piu' semplice (meno scene)

### Pipeline riavvio iMac
```bash
ssh imac "kill \$(lsof -ti:3002); kill \$(lsof -ti:5080); sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && DYLD_LIBRARY_PATH=lib/pjsua2 PYTHONUNBUFFERED=1 nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 131.
PRIORITA:
1. Sprint 3 COMPLETAMENTO: generare voiceover + assemblare 6 video per settore
   - Per OGNI video: voiceover Edge-TTS → assembly ffmpeg → TEST E2E (ffprobe durata/risoluzione)
2. Sprint 4: Landing con video embeddati + hero screenshots
```
