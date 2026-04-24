# PROMPT RIPARTENZA — SESSIONE 168 FLUXION

> **Uso**: copia il blocco sotto nella nuova sessione Claude Code aperta in `/Volumes/MontereyT7/FLUXION`.
> **Regola non negoziabile**: Claude ESEGUE i comandi direttamente, NON li passa al fondatore. Se manca qualcosa, lo crea.

---

## BLOCCO DA COPIARE (tutto quello che sta dentro i triple-backtick)

```
Sei il CTO tecnico di FLUXION. Lavori in autonomia. Il fondatore (Gianluca Di Stasi) NON è developer: non gli passare comandi da eseguire, esegui tu. Se manca uno strumento, lo crei. Se un test fallisce, diagnosi + fix, non escalation.

## Contesto sessione S167 (completata parzialmente nella sessione precedente)

Stato del repo: commit pending con le seguenti modifiche NON ancora committate:
- `video-factory/assemble_landing_v4.py` — fix bug `pad_video_to_audio()`: sostituito `tpad=stop_mode=clone` con `-stream_loop -1 + -shortest` per eliminare freeze frame sistemico (17 eventi, 73% video congelato).
- `.claude/NORTH_STAR.md` — contratto strategico immutabile FLUXION (cliente PMI italiane, pricing €497/€897 lifetime, Sara voice AI, vincoli immutabili).
- `.claude/PLAYBOOK.md` — procedure correnti (pricing, sales WA, deploy CF Pages/Worker/voice pipeline, runbook incident, convenzioni codice).
- `HANDOFF.md` — aggiunta sezione S167.
- `~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md` — stato S167.
- `~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/project_enterprise_delta.md` — analisi prompt enterprise universale + delta applicato.

## Task sessione S168 (eseguili IN AUTONOMIA, uno dopo l'altro)

### Task 1 — Commit lavoro S167 pending
1. `git status` e `git diff --stat` per verificare che ci siano solo le modifiche attese sopra (più eventuali altri file già modificati ereditati da sessioni precedenti — NON toccarli).
2. Se ci sono file inattesi nel diff, fermati e riporta.
3. Altrimenti: `git add .claude/NORTH_STAR.md .claude/PLAYBOOK.md .claude/NEXT_SESSION_PROMPT.md video-factory/assemble_landing_v4.py HANDOFF.md` e crea il commit:
   ```
   fix(S167): video freeze root cause + enterprise delta

   - pad_video_to_audio: tpad=stop_mode=clone → -stream_loop -1 + -shortest
     Elimina 17 freeze events (73% video congelato) in landing_v4_16x9.mp4
   - .claude/NORTH_STAR.md: contratto strategico immutabile
   - .claude/PLAYBOOK.md: procedure correnti consolidate (pricing, deploy, runbook)
   - HANDOFF.md: sezione S167

   Research: 2 subagenti paralleli (Explore + general-purpose) hanno
   identificato root cause sistemica nella funzione pad_video_to_audio,
   non un singolo punto a 00:24 come inizialmente segnalato.
   ```
4. `git push origin master`.

### Task 2 — Sync iMac e rigenerazione video
1. Verifica connettività: `ping -c 2 192.168.1.2` (se fallisce, diagnosi: `arp -a | grep 192.168.1.2`).
2. Su iMac: `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"`.
3. Verifica che il fix sia arrivato: `ssh imac "grep 'stream_loop' '/Volumes/MacSSD - Dati/fluxion/video-factory/assemble_landing_v4.py' | head -3"`.
4. Rigenera il video (usa il Python system iMac, no venv):
   ```
   ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/video-factory' && \
     /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python \
     assemble_landing_v4.py 2>&1 | tail -50"
   ```
   Se lo script richiede flag particolari, leggi prima `assemble_landing_v4.py` in cima per capire il CLI atteso. Non inventare flag.
5. Se lo script fallisce per dipendenze mancanti, diagnosi + fix (pip install sul Python giusto). Non skippare.

### Task 3 — Verifica frame-level (goal: ZERO freeze events)
1. Identifica il path del video rigenerato su iMac (probabilmente `video-factory/output/landing_v4/landing_v4_16x9.mp4` o simile — verifica).
2. Esegui via SSH:
   ```
   ssh imac 'V="/Volumes/MacSSD - Dati/fluxion/video-factory/output/landing_v4/landing_v4_16x9.mp4"; \
     ffmpeg -hide_banner -nostats -i "$V" -vf "freezedetect=n=0.003:d=0.5" \
     -map 0:v:0 -f null - 2>&1 | grep lavfi.freezedetect'
   ```
3. Success criteria: **zero righe output `lavfi.freezedetect.freeze_start`**.
4. Se ci sono ancora freeze: diagnosi (probabilmente clip sorgente troppo corte, pad con loop produce saltino percepibile come freeze). Report con lista eventi + proposta fix.
5. Esegui anche `mpdecimate` e `silencedetect` e riporta sintesi.

### Task 4 — Crea skill `/verify-videos` (riusabile per tutti i video futuri)
1. Crea directory: `.claude/skills/verify-videos/`.
2. Dentro, crea `SKILL.md` con frontmatter YAML (description trigger-rich) + body che spieghi quando si attiva (ogni volta che l'utente menziona "verifica video", "controlla video", o ha appena generato un video in `video-factory/output/`).
3. Crea script `verify-videos.sh` con snippet bash completo (metadata ffprobe + freezedetect + mpdecimate + blackdetect + silencedetect + idet), output colorato, exit code != 0 se trova problemi. Base lo snippet sulla ricerca già fatta in S167 (presente in `memory/project_enterprise_delta.md` se salvato, altrimenti riproducilo dalla knowledge ffmpeg 2025 standard).
4. Rendi eseguibile: `chmod +x .claude/skills/verify-videos/verify-videos.sh`.
5. Test: esegui lo script sul video appena rigenerato via SSH e verifica output coerente.

### Task 5 — Commit finale e update stato
1. `git add .claude/skills/verify-videos/` e commit:
   ```
   feat(S167): skill /verify-videos per QA video frame-level

   freezedetect + mpdecimate + blackdetect + silencedetect + idet.
   Auto-attivata quando utente genera video o menziona verifica video.
   ```
2. `git push origin master`.
3. Aggiorna `HANDOFF.md`: marca S167 come CHIUSA, elenca verifiche superate (zero freeze post-fix), aggiorna `ROADMAP_REMAINING.md` se esiste la voce S167.
4. Aggiorna `~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`: sposta "Stato Corrente S167" → "Stato Precedente", crea "Stato Corrente S168 CHIUSA" con sintesi 3 righe.
5. Genera il nuovo prompt di ripartenza S169 in `.claude/NEXT_SESSION_PROMPT.md` (sostituisci questo file) con il prossimo step realistico dal backlog: opzioni in priorità —
   (a) **Upload video YouTube** dei 9 verticali + landing_v4 fixato
   (b) **S168 Windows MSI build** (bloccante per 75% PMI italiane)
   (c) **Enterprise gap #2**: Sentry error tracking integration
   (d) **S162 WA verifica risposte** primo batch + secondo batch 5 msg

## Regole operative sessione

- **Esegui, non chiedere.** Per operazioni di sola lettura (Read, Grep, Bash non destructive) non chiedere mai conferma.
- **Scritture e push**: considera già autorizzate per lo scope S167/S168. NON aspettare OK del fondatore per commit/push/restart pipeline.
- **Se un test fallisce**: diagnosi prima, fix poi. Non passare il problema al fondatore. Puoi chiedere SOLO se la diagnosi è genuinamente ambigua (esempio: 2 strade tecniche valide, devi sapere quale preferenza business).
- **Path critici**:
  - MacBook dev: `/Volumes/MontereyT7/FLUXION`
  - iMac build: `/Volumes/MacSSD - Dati/fluxion` (via SSH alias `imac` → 192.168.1.2)
  - Memory: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/`
- **Zero costi**: nessun servizio a pagamento nuovo. Solo CF free tier, Groq free, Stripe 1.5%, Edge-TTS free.
- **Enterprise grade**: zero `any`, zero `--no-verify`, zero workaround.

Parti dal Task 1.
```

---

## Note per il fondatore

1. Apri una **nuova sessione** di Claude Code nella directory `/Volumes/MontereyT7/FLUXION`.
2. Copia TUTTO il blocco sopra (tra i triple-backtick) e incollalo come primo messaggio.
3. Claude eseguirà i 5 task in autonomia. Lo vedrai committare, pushare, fare SSH, rigenerare il video, verificare e creare la skill.
4. Intervieni solo se ti chiede una scelta tecnica ambigua (esempio: "se il nuovo video ha ancora micro-freeze da loop visibili, accorciamo voiceover o cerchiamo clip più lunghe?").
