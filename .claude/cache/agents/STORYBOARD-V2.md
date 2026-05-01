# FLUXION — Storyboard Video Tutorial Installazione V2
# macOS + Windows — Flusso autocontenuto
# Target: 3:00–3:30 min | 21 scene totali | Voiceover: Edge-TTS it-IT-IsabellaNeural rate -5%
# Data: 2026-05-01 | Autore: storyboard-designer agent

---

## PARAMETRI GLOBALI

| Parametro | Valore |
|-----------|--------|
| Risoluzione | 1920x1080 @ 30fps |
| Palette brand | bg #0f172a · cyan #06b6d4 · yellow #fbbf24 · text #e2e8f0 |
| Font | Inter Bold (titoli) · Inter Regular (corpo) |
| Voiceover engine | Edge-TTS `it-IT-IsabellaNeural` rate -5% |
| Audio | voiceover + `landing/assets/background-music.mp3` (Mixkit Skyline) mix -18dB bg |
| Durata totale stimata | 3:12–3:28 min |
| Transizione default | crossfade 0.4s |

---

## STRUTTURA CAPITOLI (per YouTube description / video seek)

| Timestamp | Capitolo |
|-----------|---------|
| 0:00 | Intro — Mac o Windows? |
| 0:15 | macOS — Scarica e installa |
| 1:00 | macOS — Sblocca Gatekeeper |
| 1:30 | Windows — Scarica e installa |
| 2:00 | Windows — Sblocca SmartScreen |
| 2:30 | Setup comune — Sara + Wizard |
| 3:05 | Fine — Sei pronto |

---

## SCENE

---

### Scene 01 — HOOK: Mac o Windows?
- **Time:** 0:00–0:14 (14s)
- **Visual:** Slide Pillow fullscreen. Sfondo brand `#0f172a`. Logo FLUXION centrato in alto. Sotto: due icone affiancate — logo Apple (bianco) e logo Windows (blu #0078D4), separati da una linea verticale cyan. Testo sotto: "Installa FLUXION in 3 minuti" in Inter Bold 48px #e2e8f0. Animazione: le due icone entrano slide-in da sinistra e destra con fade-in 0.8s.
- **Voiceover:** "Ciao. Hai appena acquistato FLUXION — ottima scelta. In tre minuti esatti ti mostro come installarlo, sia su Mac che su Windows. Scegli il tuo sistema e segui."
- **Lower third:** `FLUXION · Installazione guidata · macOS & Windows`
- **Transition:** fade-in da nero
- **Asset needed:**
  - `slides/v2/01-hook-dual-os.png` (Pillow, 1920x1080)
  - Logo Apple SVG path inline Pillow
  - Logo Windows SVG path inline Pillow

---

### Scene 02 — SEZIONE MACOS: titolo capitolo
- **Time:** 0:14–0:22 (8s)
- **Visual:** Slide Pillow. Sfondo `#0f172a`. Banda sinistra verticale cyan `#06b6d4` (40px wide, full height). Testo: "macOS" in Inter ExtraBold 72px bianco. Sottotitolo: "Passaggi 1 · 2 · 3" in 28px `#94a3b8`. Icona Apple grande (120px) a destra, colore `#e2e8f0`. Background texture: puntini griglia sottili.
- **Voiceover:** "Iniziamo da Mac."
- **Lower third:** `Sezione macOS`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/02-section-macos.png` (Pillow)

---

### Scene 03 — macOS STEP 1: Download DMG
- **Time:** 0:22–0:38 (16s)
- **Visual:** Split layout Pillow. Metà sinistra: mockup browser Safari minimale (barra URL `fluxion-landing.pages.dev`) con pulsante "Scarica per macOS — DMG 70MB" evidenziato in cyan. Freccia animata (statica nel fermo immagine: freccia gialla `#fbbf24`) che punta al pulsante download. Metà destra: icona file `.dmg` con etichetta `Fluxion_1.0.1_x64.dmg` e progress bar completa verde.
- **Voiceover:** "Vai sulla pagina di download di FLUXION — il link è nel tuo email di acquisto. Clicca su 'Scarica per macOS'. Il file DMG è circa settanta megabyte, ci vuole un minuto."
- **Lower third:** `Passo 1 — Scarica il file DMG`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/03-macos-download.png` (Pillow)

---

### Scene 04 — macOS STEP 2: Drag to Applications
- **Time:** 0:38–0:54 (16s)
- **Visual:** Slide Pillow mockup finestra macOS Finder. Stile dark (sfondo `#1c1c1e`). A sinistra: icona Fluxion (cerchio cyan con F bianca). A destra: icona cartella Applicazioni. Freccia gialla curva animata (statica: disegnata da Pillow con linea spessa) da sinistra verso destra. Label "Trascina qui" sotto la cartella Applicazioni. Step counter in alto a destra: "2 / 3" in cyan.
- **Voiceover:** "Apri il file DMG con un doppio click. Si apre una finestra: vedi l'icona di FLUXION a sinistra e la cartella Applicazioni a destra. Trascina FLUXION dentro Applicazioni. Fatto — un secondo."
- **Lower third:** `Passo 2 — Trascina in Applicazioni`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/04-macos-drag.png` (Pillow)

---

### Scene 05 — macOS STEP 3a: Gatekeeper warning popup
- **Time:** 0:54–1:14 (20s)
- **Visual:** Slide Pillow. Sfondo blurred (desktop Mac scuro). In primo piano: mockup dialog macOS Gatekeeper realistico (stile macOS Ventura): bordi arrotondati, sfondo `#2c2c2e`, icona esclamazione gialla `#fbbf24`. Testo dialog: `"Fluxion" non può essere aperto perché Apple non può verificare l'assenza di malware.` Pulsanti: `OK` (grigio) e nessun "Apri". In basso a sinistra: tooltip rosso `#ef4444` pulsante: "NON cliccare OK". Callout cyan: "Questo è normale per software indipendenti".
- **Voiceover:** "Al primo avvio macOS mostra questo avviso. È normale — è la stessa cosa che vedi con Obsidian, con Figma, con centinaia di programmi professionali. Non cliccare OK. Invece, fai così."
- **Lower third:** `Passo 3 — Sblocca una volta sola`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/05-macos-gatekeeper-popup.png` (Pillow — mockup dialog macOS)

---

### Scene 06 — macOS STEP 3b: Ctrl+click o setup-mac.command
- **Time:** 1:14–1:30 (16s)
- **Visual:** Split verticale 50/50. Sinistra — titolo "Metodo rapido" su sfondo `#1e293b`: mockup Finder, icona FLUXION con menu contestuale aperto (stile macOS), voce "Apri" evidenziata in cyan. Destra — titolo "Metodo automatico (consigliato)" su sfondo `#0f2a1e`: icona file `setup-mac.command` (terminale verde) con label "Doppio click = tutto automatico". Divisore centrale: linea verticale `#334155` con testo "OPPURE" centrato in `#94a3b8`.
- **Voiceover:** "Opzione uno: tasto destro sull'icona di FLUXION, scegli 'Apri', e nel popup clicca ancora 'Apri'. Una sola volta, poi parte sempre. Oppure — e questo è il metodo consigliato — fai doppio click su 'setup-mac.command', il file che trovi nel DMG accanto all'app. Si apre il Terminale, inserisci la password del Mac, e rimuove l'avviso in automatico."
- **Lower third:** `Sblocca Gatekeeper · una sola volta`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/06-macos-unlock-split.png` (Pillow)

---

### Scene 07 — macOS: App aperta — conferma visiva
- **Time:** 1:30–1:42 (12s)
- **Visual:** Screenshot reale `landing/screenshots/01-dashboard.png` (FLUXION dashboard), con overlay verde `#22c55e` semitrasparente sulla titlebar (10% opacity) e badge "macOS — Installazione completata" in pill verde in basso a sinistra. Checkmark animazione: cerchio verde con spunta bianca (disegnata Pillow) sovrapposto al centro per 1s poi scompare.
- **Voiceover:** "Perfetto. FLUXION è aperto su Mac. Da adesso parte sempre senza chiedere niente."
- **Lower third:** `macOS — Completato`
- **Transition:** crossfade 0.5s + leggero zoom-out 102%→100%
- **Asset needed:** `landing/screenshots/01-dashboard.png` (esistente) + overlay Pillow

---

### Scene 08 — SEZIONE WINDOWS: titolo capitolo
- **Time:** 1:42–1:50 (8s)
- **Visual:** Slide Pillow. Speculare a Scene 02 ma palette Windows. Sfondo `#0f172a`. Banda sinistra verticale blu `#0078D4` (40px). Testo "Windows" in Inter ExtraBold 72px bianco. Sottotitolo "Passaggi 1 · 2 · 3" 28px `#94a3b8`. Logo Windows a 4 pannelli (blu) 120px a destra.
- **Voiceover:** "Ora Windows."
- **Lower third:** `Sezione Windows`
- **Transition:** crossfade 0.4s con wipe laterale (da destra) per segnalare cambio sezione
- **Asset needed:** `slides/v2/08-section-windows.png` (Pillow)

---

### Scene 09 — Windows STEP 1: Download MSI
- **Time:** 1:50–2:04 (14s)
- **Visual:** Slide Pillow. Mockup browser Chrome su Windows dark. Barra URL `fluxion-landing.pages.dev`. Pulsante "Scarica per Windows — MSI 75MB" evidenziato in blu `#0078D4`. Freccia gialla punta al pulsante. In basso della finestra browser: banner download stile Chrome "Fluxion_1.0.1_x64.msi" con icona MSI e bar completa.
- **Voiceover:** "Su Windows vai sulla stessa pagina di download e scegli il file MSI. Durante il download, Chrome — o Edge — ti mostra il file in basso."
- **Lower third:** `Passo 1 — Scarica il file MSI`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/09-win-download.png` (Pillow)

---

### Scene 10 — Windows STEP 2a: SmartScreen warning
- **Time:** 2:04–2:20 (16s)
- **Visual:** Slide Pillow fullscreen. Mockup popup SmartScreen realistico Windows 11 style. Sfondo `#0e0e0e`. Frame dialog 600x420px, sfondo `#1c1c1c`, bordo `#333`. Header: logo Windows + "Microsoft Defender SmartScreen". Testo: "Il PC è protetto. Windows ha impedito l'avvio di un'app non riconosciuta." Pulsanti: `Non eseguire` (primario blu scuro) e link testo piccolo "Ulteriori informazioni" evidenziato con cerchio giallo pulsante e freccia gialla `#fbbf24` che punta ad esso. Label: "Clicca qui prima".
- **Voiceover:** "Windows mostra questo avviso SmartScreen. È la stessa cosa del Gatekeeper su Mac — segnala che il programma non ha una firma digitale a pagamento. È normale per software indipendenti. Non chiudere. Clicca su 'Ulteriori informazioni'."
- **Lower third:** `Passo 2 — SmartScreen: clicca "Ulteriori informazioni"`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/10-win-smartscreen-1.png` (Pillow — mockup popup SmartScreen step 1)

---

### Scene 11 — Windows STEP 2b: "Esegui comunque"
- **Time:** 2:20–2:32 (12s)
- **Visual:** Slide Pillow. Stesso dialog SmartScreen ma stato successivo: ora mostra dettagli app "Fluxion" con publisher "Unknown Publisher" e pulsante `Esegui comunque` evidenziato in giallo `#fbbf24` con freccia e label "Clicca qui". Pulsante `Non eseguire` rimane ma grigio non evidenziato.
- **Voiceover:** "Ora compare il pulsante 'Esegui comunque'. Cliccaci. L'installer si apre, segui i passaggi normali — avanti, avanti, installa. Ci vogliono trenta secondi."
- **Lower third:** `Clicca "Esegui comunque" · poi segui l'installer`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/11-win-smartscreen-2.png` (Pillow — mockup SmartScreen step 2 "Esegui comunque")

---

### Scene 12 — Windows STEP 3: setup-win.bat — Defender exclusion
- **Time:** 2:32–2:50 (18s)
- **Visual:** Slide Pillow split verticale. Sinistra (60%): mockup finestra CMD/PowerShell stile Windows 11 dark. Terminale nero con testo verde: `[OK] Fluxion.exe trovato` · `[OK] Esclusione Defender aggiunta` · `[OK] Mark-of-the-Web rimosso` · `[OK] SETUP COMPLETATO`. Font monospace 16px. Header della finestra: `setup-win.bat — Amministratore`. Destra (40%): icona file `setup-win.bat` con etichetta "File incluso nel download" + icona scudo Windows verde con checkmark.
- **Voiceover:** "Dopo l'installazione, avvia 'setup-win.bat' che trovi nella stessa cartella del download — accetta la richiesta di amministratore. Lo script aggiunge FLUXION alle eccezioni di Defender e rimuove il mark-of-web in automatico. Vedi i messaggi OK in verde: tutto a posto."
- **Lower third:** `setup-win.bat · Lancia come amministratore`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/12-win-setup-bat.png` (Pillow — mockup terminale CMD)

---

### Scene 13 — Windows: App aperta — conferma visiva
- **Time:** 2:50–3:00 (10s)
- **Visual:** Screenshot `landing/screenshots/01-dashboard.png` con overlay blu `#0078D4` semitrasparente sulla titlebar (10% opacity) e badge "Windows — Installazione completata" in pill blu in basso a sinistra. Stesso checkmark verde di Scene 07 ma con tinta blu.
- **Voiceover:** "FLUXION è aperto. Da adesso parte dal menu Start o dal desktop, senza avvisi."
- **Lower third:** `Windows — Completato`
- **Transition:** crossfade 0.5s

---

### Scene 14 — SEZIONE COMUNE: titolo capitolo
- **Time:** 3:00–3:06 (6s)
- **Visual:** Slide Pillow. Sfondo `#0f172a`. Testo centrato "Ultimo passo" Inter ExtraBold 64px bianco. Sottotitolo "Uguale su Mac e Windows" 28px `#94a3b8`. Due icone Apple + Windows affiancate sotto, piccole (60px), colore `#94a3b8`. Linea cyan sotto il titolo.
- **Voiceover:** "Ora due passi finali, uguali su Mac e Windows."
- **Lower third:** (nessuno)
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/14-section-common.png` (Pillow)

---

### Scene 15 — Permesso microfono
- **Time:** 3:06–3:20 (14s)
- **Visual:** Slide Pillow. Mockup dialog permesso microfono stile macOS/Windows (versione generica cross-OS, stile macOS perché più leggibile). Dialog centrato: icona microfono `#06b6d4` grande. Testo: `"Fluxion" vuole accedere al microfono`. Sottotesto: `Sara ha bisogno del microfono per rispondere alle chiamate.` Pulsante `Consenti` evidenziato in cyan con freccia gialla. Pulsante `Non consentire` grigio. Badge in alto: "Sia Mac che Windows mostrano questo".
- **Voiceover:** "FLUXION chiede l'accesso al microfono. Devi cliccare Consenti — o OK su Windows — altrimenti Sara non sente niente. Questo vale sia su Mac che su Windows."
- **Lower third:** `Microfono — Clicca "Consenti"`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/15-mic-permission.png` (Pillow)

---

### Scene 16 — Setup Wizard
- **Time:** 3:20–3:36 (16s)
- **Visual:** Screenshot `landing/screenshots/11-impostazioni.png` o mockup setup wizard se lo screenshot non mostra il wizard iniziale. Overlay titolo in alto: "Setup iniziale — meno di 1 minuto". Tre bullet points sovrapposti in basso-sinistra (Pillow overlay semi-opaco `#0f172a` 80%): "Nome attività · Settore · Orari di apertura". Ogni bullet ha checkmark cyan.
- **Voiceover:** "Si apre il setup wizard. Ti chiede tre cose: nome della tua attività, settore — salone, palestra, officina, clinica — e gli orari. Ci metti meno di un minuto."
- **Lower third:** `Setup iniziale · 3 campi · 1 minuto`
- **Transition:** crossfade 0.4s
- **Asset needed:** `landing/screenshots/11-impostazioni.png` (esistente) + overlay Pillow

---

### Scene 17 — Sara attiva — la voce risponde
- **Time:** 3:36–3:52 (16s)
- **Visual:** Screenshot `landing/screenshots/08-voice.png` (Sara UI). Overlay animazione: onde audio stilizzate cyan `#06b6d4` che pulsano intorno al pannello Sara (3 cerchi concentrici semitrasparenti). Label in basso: "Sara sta ascoltando..." in Inter Bold 24px cyan. Badge in alto destra: "24/7 · Voce naturale".
- **Voiceover:** "Ora prova Sara. Dille: 'Buongiorno, sono Marco, voglio un appuntamento per domani alle tre.' Senti come risponde con voce naturale, prende l'appuntamento da sola, e manda la conferma su WhatsApp."
- **Lower third:** `Sara — Assistente vocale 24/7`
- **Transition:** crossfade 0.5s
- **Asset needed:** `landing/screenshots/08-voice.png` (esistente) + overlay onde Pillow

---

### Scene 18 — Dashboard panoramica (valore prodotto)
- **Time:** 3:52–4:02 (10s)
- **Visual:** Screenshot `landing/screenshots/01-dashboard.png` fullscreen. Overlay semi-opaco `#0f172a` 40% su tutta l'immagine. Sopra: testo centrato "Calendario · Clienti · Cassa · Sara" in Inter Bold 36px bianco, scritto su una riga con separatori `·` cyan. In basso: "Tutto in un unico programma sul tuo computer."
- **Voiceover:** "FLUXION gestisce calendario, clienti, cassa, e risponditore vocale. Tutto sul tuo computer — i dati non escono mai."
- **Lower third:** (nessuno — testo già nell'overlay)
- **Transition:** crossfade 0.4s
- **Asset needed:** `landing/screenshots/01-dashboard.png` (esistente) + overlay Pillow

---

### Scene 19 — Problema? Link supporto
- **Time:** 4:02–4:14 (12s)
- **Visual:** Slide Pillow. Sfondo `#0f172a`. Sezione superiore: icona chat support (cerchio cyan, fumetto bianco) 80px. Testo: "Qualcosa non va?" Inter Bold 40px. Sotto: due card affiancate `#1e293b` border cyan. Card 1: icona email + `fluxion.gestionale@gmail.com`. Card 2: icona link + `fluxion-landing.pages.dev/come-installare` (in cyan, testo piccolo 18px). Sotto: "Risposta entro 24 ore · In italiano."
- **Voiceover:** "Se qualcosa non funziona, trovi la guida completa sulla pagina 'Come installare' — il link è nel tuo email di acquisto. Oppure scrivi direttamente a noi: rispondiamo in italiano entro ventiquattr'ore."
- **Lower third:** `Supporto · fluxion.gestionale@gmail.com`
- **Transition:** crossfade 0.4s
- **Asset needed:** `slides/v2/19-support.png` (Pillow)

---

### Scene 20 — CTA finale + logo
- **Time:** 4:14–4:28 (14s)
- **Visual:** Slide Pillow fullscreen. Logo FLUXION centrato grande (200px, lo stesso di `landing/assets/logo_fluxion.jpg` o vettoriale). Sotto il logo: tagline "Il gestionale che lavora anche quando tu non ci sei." in Inter Regular 28px `#94a3b8`. Linea orizzontale cyan. In basso: tre benefit in fila "Calendario automatico · Sara risponde 24/7 · Zero abbonamenti" in 20px `#e2e8f0`. Cornice: leggero glow cyan ai bordi (box-shadow simulato con rettangolo Pillow semitrasparente).
- **Voiceover:** "Benvenuto in FLUXION. Buon lavoro."
- **Lower third:** (nessuno)
- **Transition:** fade-out a nero lento (1.2s)
- **Asset needed:** `slides/v2/20-cta-finale.png` (Pillow) + `landing/assets/logo_fluxion.jpg` (esistente)

---

### Scene 21 — BUMPER FINALE (opzionale, 0:04)
- **Time:** 4:28–4:32 (4s)
- **Visual:** Nero puro. Solo logo FLUXION piccolo (80px) centrato in bianco. Nessun testo.
- **Voiceover:** (silenzio)
- **Lower third:** (nessuno)
- **Transition:** fade-out
- **Asset needed:** `slides/v2/21-bumper.png` (Pillow — nero + logo)

---

## RIEPILOGO SLIDE PILLOW DA GENERARE (13 nuove)

| ID | File output | Contenuto |
|----|-------------|-----------|
| 01 | `slides/v2/01-hook-dual-os.png` | Logo + icone Apple/Windows affiancate |
| 02 | `slides/v2/02-section-macos.png` | Titolo sezione macOS + banda cyan |
| 03 | `slides/v2/03-macos-download.png` | Browser Safari mockup + DMG download |
| 04 | `slides/v2/04-macos-drag.png` | Finder drag-to-Applications mockup |
| 05 | `slides/v2/05-macos-gatekeeper-popup.png` | Dialog Gatekeeper macOS mockup |
| 06 | `slides/v2/06-macos-unlock-split.png` | Split: ctrl+click OPPURE setup-mac.command |
| 08 | `slides/v2/08-section-windows.png` | Titolo sezione Windows + banda blu |
| 09 | `slides/v2/09-win-download.png` | Browser Chrome mockup + MSI download |
| 10 | `slides/v2/10-win-smartscreen-1.png` | SmartScreen popup step 1 + freccia "Ulteriori info" |
| 11 | `slides/v2/11-win-smartscreen-2.png` | SmartScreen popup step 2 + "Esegui comunque" |
| 12 | `slides/v2/12-win-setup-bat.png` | Terminale CMD + output [OK] |
| 14 | `slides/v2/14-section-common.png` | Titolo "Ultimo passo" + Apple+Windows icone |
| 15 | `slides/v2/15-mic-permission.png` | Dialog permesso microfono cross-OS |
| 19 | `slides/v2/19-support.png` | Card supporto + email + link |
| 20 | `slides/v2/20-cta-finale.png` | Logo + tagline + benefit |
| 21 | `slides/v2/21-bumper.png` | Nero + logo piccolo |

---

## SCREENSHOT ESISTENTI DA RIUSARE (overlay Pillow)

| Scene | File | Uso |
|-------|------|-----|
| 07 | `landing/screenshots/01-dashboard.png` | macOS completato — overlay verde |
| 13 | `landing/screenshots/01-dashboard.png` | Windows completato — overlay blu |
| 16 | `landing/screenshots/11-impostazioni.png` | Setup wizard — overlay bullet |
| 17 | `landing/screenshots/08-voice.png` | Sara attiva — overlay onde |
| 18 | `landing/screenshots/01-dashboard.png` | Dashboard panoramica — overlay testo |

---

## TIMING COMPLETO

| Scene | Titolo | Start | End | Durata |
|-------|--------|-------|-----|--------|
| 01 | Hook: Mac o Windows? | 0:00 | 0:14 | 14s |
| 02 | Sezione macOS | 0:14 | 0:22 | 8s |
| 03 | macOS STEP 1: Download DMG | 0:22 | 0:38 | 16s |
| 04 | macOS STEP 2: Drag to Applications | 0:38 | 0:54 | 16s |
| 05 | macOS STEP 3a: Gatekeeper popup | 0:54 | 1:14 | 20s |
| 06 | macOS STEP 3b: Sblocca (ctrl+click/script) | 1:14 | 1:30 | 16s |
| 07 | macOS: App aperta | 1:30 | 1:42 | 12s |
| 08 | Sezione Windows | 1:42 | 1:50 | 8s |
| 09 | Windows STEP 1: Download MSI | 1:50 | 2:04 | 14s |
| 10 | Windows STEP 2a: SmartScreen warning | 2:04 | 2:20 | 16s |
| 11 | Windows STEP 2b: Esegui comunque | 2:20 | 2:32 | 12s |
| 12 | Windows STEP 3: setup-win.bat | 2:32 | 2:50 | 18s |
| 13 | Windows: App aperta | 2:50 | 3:00 | 10s |
| 14 | Sezione comune: Ultimo passo | 3:00 | 3:06 | 6s |
| 15 | Permesso microfono | 3:06 | 3:20 | 14s |
| 16 | Setup Wizard | 3:20 | 3:36 | 16s |
| 17 | Sara attiva | 3:36 | 3:52 | 16s |
| 18 | Dashboard panoramica | 3:52 | 4:02 | 10s |
| 19 | Problema? Supporto | 4:02 | 4:14 | 12s |
| 20 | CTA finale + logo | 4:14 | 4:28 | 14s |
| 21 | Bumper finale | 4:28 | 4:32 | 4s |
| | **TOTALE** | | | **4:32** |

> Nota: 4:32 rientra nel brief "3:00–3:30" solo se il video-copywriter compatta i voiceover.
> Taglio possibile portando Scene 18 a 6s, Scene 16 a 10s, Scene 17 a 12s → risparmi ~14s → **4:18**.
> Per arrivare a 3:30 il video-copywriter deve condensare i voiceover macOS/Win a frasi più brevi.
> Raccomandazione: target editoriale 4:00–4:30 (più realistico per flusso dual-OS) oppure tagliare Scene 18.

---

## NOTE TECNICHE PER video-editor

### ffmpeg pipeline suggerita
```bash
# 1. Genera tutte le slide Pillow (script Python separato)
# 2. Per ogni scena: immagine → video clip 30fps con Ken Burns opzionale
ffmpeg -loop 1 -i slide.png -c:v libx264 -t 14 -vf "zoompan=z='min(zoom+0.0005,1.03)':d=420:fps=30,scale=1920:1080" -pix_fmt yuv420p clip_01.mp4

# 3. Per screenshot: no zoompan, solo fade-in/out
ffmpeg -loop 1 -i screenshot.png -c:v libx264 -t 12 -vf "fade=in:0:15,fade=out:345:15,scale=1920:1080" -pix_fmt yuv420p clip_07.mp4

# 4. Voiceover per scena (Edge-TTS)
edge-tts --voice it-IT-IsabellaNeural --rate=-5% --text "testo scena" --write-media audio_01.mp3

# 5. Mux voiceover + clip
ffmpeg -i clip_01.mp4 -i audio_01.mp3 -c:v copy -c:a aac -b:a 192k scene_01.mp4

# 6. Concat tutte le scene (file list.txt)
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -c:a aac -movflags +faststart output_v2.mp4

# 7. Mix background music -18dB
ffmpeg -i output_v2.mp4 -i background-music.mp3 -filter_complex "[1:a]volume=0.1[bg];[0:a][bg]amix=inputs=2:duration=first" -c:v copy -c:a aac final_v2.mp4
```

### Crossfade tra scene (xfade filter)
```bash
# Per ogni coppia di scene consecutiva con crossfade 0.4s
ffmpeg -i scene_01.mp4 -i scene_02.mp4 -filter_complex "xfade=transition=fade:duration=0.4:offset=<end_scene01 - 0.4>" -c:a aac merged_01_02.mp4
```

### Directory output suggerita
```
landing/assets/video/
  slides/v2/          ← slide Pillow generate (PNG 1920x1080)
  clips/v2/           ← clip video per scena (MP4)
  audio/v2/           ← voiceover per scena (MP3)
  fluxion-tutorial-install-v2.mp4   ← output finale
  fluxion-tutorial-install-v2.srt   ← sottotitoli
```

---

## VOICEOVER COMPLETO (testo grezzo da raffinare con video-copywriter)

```
[01] Ciao. Hai appena acquistato FLUXION — ottima scelta. In tre minuti esatti ti mostro come installarlo, sia su Mac che su Windows. Scegli il tuo sistema e segui.

[02] Iniziamo da Mac.

[03] Vai sulla pagina di download di FLUXION — il link è nel tuo email di acquisto. Clicca su "Scarica per macOS". Il file DMG è circa settanta megabyte, ci vuole un minuto.

[04] Apri il file DMG con un doppio click. Si apre una finestra: vedi l'icona di FLUXION a sinistra e la cartella Applicazioni a destra. Trascina FLUXION dentro Applicazioni. Fatto — un secondo.

[05] Al primo avvio macOS mostra questo avviso. È normale — è la stessa cosa che vedi con Obsidian, con Figma, con centinaia di programmi professionali. Non cliccare OK. Invece, fai così.

[06] Opzione uno: tasto destro sull'icona di FLUXION, scegli "Apri", e nel popup clicca ancora "Apri". Una sola volta, poi parte sempre. Oppure — e questo è il metodo consigliato — fai doppio click su "setup-mac.command", il file che trovi nel DMG accanto all'app. Si apre il Terminale, inserisci la password del Mac, e rimuove l'avviso in automatico.

[07] Perfetto. FLUXION è aperto su Mac. Da adesso parte sempre senza chiedere niente.

[08] Ora Windows.

[09] Su Windows vai sulla stessa pagina di download e scegli il file MSI. Durante il download, Chrome — o Edge — ti mostra il file in basso.

[10] Windows mostra questo avviso SmartScreen. È la stessa cosa del Gatekeeper su Mac — segnala che il programma non ha una firma digitale a pagamento. È normale per software indipendenti. Non chiudere. Clicca su "Ulteriori informazioni".

[11] Ora compare il pulsante "Esegui comunque". Cliccaci. L'installer si apre, segui i passaggi normali — avanti, avanti, installa. Ci vogliono trenta secondi.

[12] Dopo l'installazione, avvia "setup-win.bat" che trovi nella stessa cartella del download — accetta la richiesta di amministratore. Lo script aggiunge FLUXION alle eccezioni di Defender e rimuove il mark-of-web in automatico. Vedi i messaggi OK in verde: tutto a posto.

[13] FLUXION è aperto. Da adesso parte dal menu Start o dal desktop, senza avvisi.

[14] Ora due passi finali, uguali su Mac e Windows.

[15] FLUXION chiede l'accesso al microfono. Devi cliccare Consenti — o OK su Windows — altrimenti Sara non sente niente. Questo vale sia su Mac che su Windows.

[16] Si apre il setup wizard. Ti chiede tre cose: nome della tua attività, settore — salone, palestra, officina, clinica — e gli orari. Ci metti meno di un minuto.

[17] Ora prova Sara. Dille: "Buongiorno, sono Marco, voglio un appuntamento per domani alle tre." Senti come risponde con voce naturale, prende l'appuntamento da sola, e manda la conferma su WhatsApp.

[18] FLUXION gestisce calendario, clienti, cassa, e risponditore vocale. Tutto sul tuo computer — i dati non escono mai.

[19] Se qualcosa non funziona, trovi la guida completa sulla pagina "Come installare" — il link è nel tuo email di acquisto. Oppure scrivi direttamente a noi: rispondiamo in italiano entro ventiquattr'ore.

[20] Benvenuto in FLUXION. Buon lavoro.

[21] (silenzio)
```

---

## CHECKLIST PRE-PRODUZIONE (video-editor)

- [ ] Pillow: palette brand confermata `#0f172a` / `#06b6d4` / `#fbbf24` / `#0078D4`
- [ ] Font Inter scaricato o sostituito con DejaVu (fallback zero-cost)
- [ ] Screenshot esistenti verificati (dimensione ≥ 1920x1080 o upscalabili senza artefatti)
- [ ] Edge-TTS `it-IT-IsabellaNeural` disponibile (`pip install edge-tts`)
- [ ] ffmpeg con libx264 + aac disponibile
- [ ] `landing/assets/background-music.mp3` presente
- [ ] Directory `landing/assets/video/slides/v2/` creata
- [ ] Versione v1 salvata come `fluxion-tutorial-install-v1.mp4` (gia' fatto)
