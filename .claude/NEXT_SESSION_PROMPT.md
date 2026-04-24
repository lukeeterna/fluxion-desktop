# PROMPT RIPARTENZA — SESSIONE 169 FLUXION

> **Uso**: copia il blocco sotto nella nuova sessione Claude Code aperta in `/Volumes/MontereyT7/FLUXION`.
> **Regola non negoziabile**: Claude ESEGUE i comandi direttamente, NON li passa al fondatore.

---

## STATO ALLA FINE DI S168 (2026-04-24)

- ✅ Fix video S167 verificato: `landing_v4_16x9.mp4` rigenerato su iMac, **clip Veo3 (0-31s) ZERO freeze events**.
- ✅ Skill `/verify-videos` creata + testata (freezedetect + mpdecimate + blackdetect + silencedetect + idet).
- Freeze residui (16 eventi, ~95s su 149s) sono **tutti su slide statiche attese** (screenshot dashboard, scheda parrucchiere, calendario, CTA prezzo, URL finale) + 10 eventi nella waveform Sara durante pause dialogo.
- Repo pulito, 2 commit pushati (5484cf1 + 1a68cd6), master allineato MacBook+iMac.

---

## BLOCCO DA COPIARE (tutto tra i triple-backtick)

```
Sei il CTO tecnico di FLUXION. Lavori in autonomia. Il fondatore (Gianluca Di Stasi) NON è developer. Se un test fallisce, diagnosi + fix, non escalation.

## Contesto S169

Il bug sistemico freeze video (S167) è risolto e verificato in S168. Restano due categorie di problemi:

A. **Waveform Sara (sezione 43-75s del video)** — 10 freeze events residui durante pause naturali del dialogo perché `showwaves mode=cline` disegna una linea piatta quando l'audio è silenzioso. Non è un bug del fix pad_video_to_audio, è un limite intrinseco del filtro showwaves + natura a battute del dialogo Sara.

B. **Skill /verify-videos — falsi positivi su slide statiche** — un video con screenshot statici (dashboard, CTA, URL) viene inevitabilmente flaggato come "freeze" perché tecnicamente lo è. Serve un concetto di "expected-static-regions" per filtrare.

## Opzioni S169 (scegli UNA o due in priorità)

### Opzione 1 — Dinamicizzare waveform Sara (chiude cap A)
Modifica `video-factory/assemble_landing_v4.py:make_waveform_section` per aggiungere elementi sempre-in-movimento:
- Pulse ring animato attorno al dot "● CHIAMATA IN CORSO" (3 cerchi concentrici che crescono+svaniscono a rate 1.5s)
- `drawtext` con contatore tempo chiamata HH:MM:SS che aumenta ogni secondo
- Background gradient animato con `geq` (lent, ~0.1Hz) per evitare freezedetect
Test: rigenera video su iMac, esegui `/verify-videos`, verifica waveform section (43-75s) → 0 freeze events.
Commit + push. Aggiorna HANDOFF/MEMORY.

### Opzione 2 — Upload YouTube di TUTTI i video (sblocca marketing)
9 video verticali + landing_v4_16x9.mp4 corretto. `scripts/upload_youtube.py` esiste già.
Steps: OAuth token check, metadata per video (titolo + description + tag italiani), chapter markers dove appropriato, thumbnail personalizzato (skill `thumbnail-designer` o generazione da frame #50 del video).
Test: primo video caricato come "unlisted" per verifica, poi batch.
Commit `feat(S169): YT batch upload 10 video`. Aggiorna HANDOFF/MEMORY.

### Opzione 3 — Windows MSI build (sblocca 75% del mercato PMI)
Piano in `.claude/PLAYBOOK.md` sezione "Deploy cross-platform". Tauri 2.x supporta Windows ma serve firmare MSI (o dare istruzioni SmartScreen). Verifica:
- wix-toolset in tauri.conf.json
- SmartScreen mitigation page su landing
- Download link + email post-purchase con istruzioni Windows
Test: scarica MSI su VM Windows (se disponibile) o chiedi al fondatore di testare.
Commit `feat(S169): Windows MSI build + SmartScreen mitigation`.

### Opzione 4 — Slide-static whitelist per skill /verify-videos
Estende `.claude/skills/verify-videos/verify-videos.sh` con parametro `--static-regions "start1:end1,start2:end2"` che esclude quelle finestre dalla freezedetect. Utile per video landing con CTA/screenshot statici dove il freeze è intenzionale.
Documenta in `SKILL.md` + testa su landing_v4 con `--static-regions "31:42,75:149"` → expected exit 0.
Commit `feat(S169): verify-videos static-regions whitelist`.

## Regole operative

- **Esegui, non chiedere.** Per operazioni di sola lettura non chiedere mai conferma.
- **Scritture e push**: considera già autorizzate per lo scope S169. NON aspettare OK del fondatore.
- **Path critici**:
  - MacBook dev: `/Volumes/MontereyT7/FLUXION`
  - iMac build: `/Volumes/MacSSD - Dati/fluxion` (SSH alias `imac` → 192.168.1.2)
  - Memory: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/`
- **PATH ffmpeg su iMac via SSH**: `export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"` (altrimenti ffmpeg not found).
- **Python iMac**: `/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python` (no venv).
- **Zero costi**: solo CF free tier, Groq free, Stripe 1.5%, Edge-TTS free.
- **Enterprise grade**: zero `any`, zero `--no-verify`, zero workaround.

Chiedi al fondatore quale opzione preferisce (1/2/3/4). Se non risponde entro 1 minuto, default: **Opzione 2** (upload YouTube — sblocca il marketing del lancio e il video è pronto).
```

---

## Note per il fondatore

1. Apri una **nuova sessione** di Claude Code in `/Volumes/MontereyT7/FLUXION`.
2. Copia TUTTO il blocco sopra (tra i triple-backtick) e incollalo come primo messaggio.
3. Claude ti chiederà quale opzione preferisci (1=fix waveform, 2=upload YT, 3=Windows MSI, 4=whitelist skill). Rispondi con "1", "2", "3" o "4". Se hai fretta e non vuoi decidere, scrivi "default" → userà opzione 2 (YouTube).
