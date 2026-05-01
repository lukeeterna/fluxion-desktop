# Video Tutorial Bypass Installazione — Script (S184 α.2 STEP 3)

**Durata target**: 3 minuti  
**Strumento registrazione**: OBS Studio (free, https://obsproject.com)  
**Output**: 1080p 30fps, audio mono microfono integrato OK  
**Hosting**: Vimeo unlisted (free 500MB/settimana, no watermark)  
**Embed finale**: `landing/come-installare.html` sezione `#video-tutorial`

---

## Setup OBS prima della registrazione

1. Scene → **+ Cattura schermo** (intero monitor o singola finestra)
2. Audio → **Cattura input audio (microfono)** — disattiva tutti gli altri input
3. Output → MP4, encoder x264, qualità "Indistinguibile"
4. Tastiera Mac: silenzia notifiche (Focus → Non disturbare)

---

## Storyboard (3 scene)

### Scena 1 — Intro (0:00 → 0:15)

**Visual**: Schermo desktop pulito, sfondo neutro. Logo FLUXION in alto-sinistra (overlay PNG opzionale).

**Voiceover**:
> "Ciao. Ti mostro come installare FLUXION sul tuo Mac in due minuti.
> Servono solo tre passaggi e niente comandi complicati."

---

### Scena 2 — macOS install + Gatekeeper (0:15 → 1:50)

**0:15** — Apri browser su `https://github.com/lukeeterna/fluxion-desktop/releases/tag/v1.0.1`

**Voiceover**:
> "Vai sulla pagina dei download di FLUXION e clicca sul file con estensione .dmg per Mac."

**0:30** — Click su `Fluxion_1.0.1_x64.dmg` → download Finder

**Voiceover**:
> "Si scarica un file di circa 70 megabyte. Non chiudere il browser ancora — ti serve."

**0:45** — Doppio-click sul DMG → si apre finestra con Fluxion.app

**Voiceover**:
> "Apri il DMG con un doppio-click. Dentro vedi l'icona di FLUXION. Trascinala nella cartella Applicazioni."

**1:00** — Drag Fluxion.app → /Applications

**1:10** — Doppio-click su Fluxion in Applicazioni → **avviso Gatekeeper appare**

**Voiceover**:
> "Al primo avvio il Mac ti dice che FLUXION 'non puo' essere aperto perche' lo sviluppatore non e' identificato'. È normale, è una sicurezza Apple per app non firmate con certificato a pagamento."

**1:25** — Click destro (o Control+click) su Fluxion → menu → "Apri" → click

**Voiceover**:
> "Per sbloccare: clicca col tasto destro sull'icona di FLUXION, scegli 'Apri'. Il Mac chiede conferma una volta sola — clicca 'Apri' e basta. Da adesso FLUXION parte senza chiedere piu' nulla."

**1:45** — Fluxion app si apre → Setup Wizard primo avvio

---

### Scena 3 — Primo avvio Sara (1:50 → 3:00)

**1:50** — Setup Wizard FLUXION → completa step rapidamente (nome attivita', vertical, ecc.)

**Voiceover**:
> "Al primo avvio FLUXION ti chiede pochi dati per configurare la tua attività. Ci metti meno di un minuto."

**2:30** — Naviga a Voice Agent (Sara)

**2:35** — Click "Inizia conversazione" → mic permission popup macOS → Concedi

**Voiceover**:
> "L'unica cosa importante: quando FLUXION ti chiede l'autorizzazione al microfono, dai 'OK'. Senza microfono Sara non può sentirti."

**2:45** — Parla: "Buongiorno, sono Marco Rossi"

**Voiceover** (subito dopo):
> "Ed eccola Sara. Risponde con voce naturale, gestisce gli appuntamenti via voce 24 ore su 24. Hai finito."

**2:55** — Logo FLUXION + URL `fluxion-landing.pages.dev`

**Voiceover**:
> "Per Windows trovi le istruzioni complete su FLUXION-landing punto pages punto dev slash come-installare. Buon lavoro."

**3:00** — Fade out

---

## Post-produzione

1. Esporta da OBS → MP4 1080p
2. Controlla audio: nessun pop, no clip > -3dB
3. Carica su Vimeo → impostazioni:
   - Privacy: **Hide from Vimeo (Unlisted)**
   - Embed: solo dominio `fluxion-landing.pages.dev` (whitelist)
   - No download, no like, no comments

4. Copia VIMEO_ID dall'URL (es. `https://vimeo.com/1234567890` → `1234567890`)

5. Sostituisci in `landing/come-installare.html` sezione `#video-tutorial` (cerca commento `Sostituire con:`):
   ```html
   <iframe
     src="https://player.vimeo.com/video/VIMEO_ID?autoplay=0&dnt=1"
     class="absolute inset-0 w-full h-full"
     frameborder="0"
     allow="autoplay; fullscreen; picture-in-picture"
     allowfullscreen
   ></iframe>
   ```
   Sostituisci `VIMEO_ID` col numero reale.

6. Deploy CF Pages: commit + push master → auto-deploy.

---

## Versione Windows (futura — α.3 con VM UTM iMac)

Stesso storyboard adattato:
- Scena 2: download MSI, doppio-click → SmartScreen "Ulteriori informazioni" → "Esegui comunque"
- Tutto il resto identico

---

## Costi

| Item | Costo |
|------|-------|
| OBS Studio | €0 (open source) |
| Vimeo Free | €0 (500MB/sett, sufficiente per 3 video/mese) |
| Microfono Mac built-in | €0 |
| **Totale** | **€0** |

Mantiene guardrail ZERO COSTI di CLAUDE.md.
