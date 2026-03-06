# CoVe 2026 Research — Schede Cliente: Media Upload (Foto/Video)
> Ricerca: 2026-03-05 | Agente: UI Designer / Researcher
> Scope: upload foto/video nelle schede cliente di FLUXION per PMI italiane

---

## 1. COMPETITOR ANALYSIS

### Fresha (ex Shedul) — Gold Standard Salone
- **Avatar cliente**: upload singolo, crop circolare, max 5MB JPEG/PNG
- **Before/After**: NON nativo nella scheda cliente — relegato a "Gallery" del profilo business
- **Video**: assente nelle schede cliente (solo marketing gallery)
- **UX**: drag-drop zona + click-to-browse; preview immediata inline; nessuna lightbox avanzata
- **Gap critico**: nessun before/after slider, nessuna gestione GDPR consenso per le foto

### Mindbody — Fitness/Wellness
- **Progress photos**: presente ma rudimentale — upload singolo per data, no overlay corporeo
- **Body metrics timeline**: separata dalla galleria foto (non integrata visivamente)
- **Video**: solo link esterno YouTube/Vimeo — non upload diretto
- **UX**: vecchia, non drag-drop, modal pesante; nessuna compressione client-side visibile
- **Gap critico**: no compressione automatica, no before/after comparator, no GDPR flag per foto

### Jane App — Fisioterapia/Clinica
- **Clinical images**: upload multiplo con flag "visible to patient" / "internal only"
- **GDPR/consent**: form separato ma non integrato nella galleria immagini
- **Annotations**: nessuna annotation nativa su immagini
- **Video**: assente
- **Gap critico**: nessun before/after, no timeline visiva, consent sparso in form separato

### Phorest — Salone Premium
- **Gallery cliente**: upload multiplo drag-drop, lightbox nativa, tag per servizio/data
- **Before/After**: presente come "Transformation" — due foto side-by-side statico (NON slider)
- **Video**: assente
- **GDPR**: checkbox "consent to share on social" — base ma integrato
- **Questo è il miglior competitor attuale per saloni**
- **Gap critico**: before/after statico (non slider interattivo), no video, no compressione client-side

### Conclusione Gap Analysis
Nessun competitor nel segmento PMI offre simultaneamente:
1. Before/after slider interattivo (tutti hanno side-by-side statico o niente)
2. Video con thumbnail auto-generata
3. GDPR consent integrato nella galleria (non in form separato)
4. Compressione client-side automatica trasparente
5. Progress timeline cronologica con body overlay (Fitness)
6. Clinical image con access control per role

**FLUXION ha l'opportunità di essere world-class su tutti e 5 questi punti.**

---

## 2. UX GOLD STANDARD 2026

### 2.1 Drag-Drop Upload Zone
Pattern raccomandato (ispirato a Linear + Vercel Dashboard):
```
┌─────────────────────────────────────────────────┐
│                                                 │
│   [ icona upload ]  Trascina foto/video qui     │
│          oppure  [ Sfoglia file ]               │
│                                                 │
│   JPG/PNG/HEIC max 5MB · MP4/MOV max 50MB      │
└─────────────────────────────────────────────────┘
```
- **Hover state**: bordo teal animato + background teal/5% opacity
- **Drag-over state**: bordo solid teal 2px + scale(1.01) + sfondo teal/10%
- **Feedback errore**: inline (non toast) — "File troppo grande (8.2MB > 5MB)"
- **Multi-file**: drag multipli accettati (max 10 per sessione)

### 2.2 Preview Inline Post-Upload
- Preview 4:3 ratio con object-fit: cover
- Overlay gradient bottom: nome file + data upload + azioni (elimina, ruota)
- Loading skeleton durante compressione (mostra percentuale: "Ottimizzazione... 65%")
- Errori bloccanti in overlay rosso sul thumbnail

### 2.3 Galleria Lightbox
Ispirata a Cloudinary Media Library:
- Click thumbnail → overlay fullscreen animato (scale-in 0.2s)
- Navigazione frecce sinistra/destra (anche tastiera)
- Metadati pannello laterale: data, dimensione originale vs compressa, consenso GDPR
- Download originale (se permesso dal ruolo)
- Swipe gesture su touch (per futura versione iPad)
- Tasto ESC per chiudere

### 2.4 Before/After Slider
Ispirato a ImgComparison (usato da Adobe, Figma show-cases):
```
┌─────────────────────────────────────────────────┐
│         PRIMA      │      DOPO                  │
│                    ↕ (slider verticale)         │
│  [immagine prima]  │  [immagine dopo]           │
│                    │                            │
│         ◄──── 50% ────►                        │
└─────────────────────────────────────────────────┘
```
- Handle circolare con grip lines, draggable orizzontalmente
- Label "PRIMA" / "DOPO" fissi in corner superiori
- Touch support (pointer events)
- Keyboard: frecce sinistra/destra muovono di 5%
- Bottone "Assegna come Before/After" nella galleria per selezionare coppia

### 2.5 Progress Timeline (Fitness)
- Layout verticale cronologico (newest on top)
- Ogni entry: foto thumbnail + data + metriche del giorno (peso, BF%, misure)
- Overlay corporeo opzionale: silhouette SVG scalabile con punti di misura
- Filtro per range di date
- Export PDF "Report Progressi" con tutte le foto + grafico metriche

---

## 3. ARCHITETTURA TAURI DESKTOP

### 3.1 Filesystem Locale VS SQLite BLOB — Decisione

**Raccomandazione: FILESYSTEM LOCALE con path relativo nel DB.**

Motivazioni:
- SQLite con BLOB diventa lento e si gonfia oltre i 100MB (PMI con 500+ clienti, 3 foto/cliente = 150+ foto)
- I file su filesystem sono accessibili direttamente senza query (apertura in preview nativa macOS)
- Backup SQLite resta leggero; le foto si backuppano separatamente (F13 SQLite Backup)
- SQLite BLOB: problemi di WAL mode con file grandi, rischio corruzione

**Schema percorso file:**
```
AppData/fluxion/
  media/
    clienti/
      {cliente_id}/
        foto/
          {uuid}.jpg          ← foto compressa (storage principale)
          {uuid}_orig.jpg     ← originale (opzionale, se utente vuole)
        video/
          {uuid}.mp4
          {uuid}_thumb.jpg    ← thumbnail auto-generata
```

**DB Column**: `media_path TEXT` — path relativo da AppData root:
```sql
-- Esempio: "media/clienti/42/foto/abc123.jpg"
media_path TEXT NOT NULL
```

Il Rust command risolve il path assoluto con `app.path().app_data_dir()`.

### 3.2 Compressione Client-Side con Canvas API

Flusso React (client-side, prima di invoke Tauri):
```
File selezionato → FileReader → Image element → Canvas drawImage
→ canvas.toBlob(blob, 'image/jpeg', 0.85)
→ Uint8Array → tauri invoke 'save_media'
```

Parametri compressione:
- **Immagini**: max 1200px (lato lungo), 85% quality JPEG → ~150-250KB da 5MB originale
- **HEIC** (iPhone): browser non supporta nativo — usare `heic2any` npm lib per conversione prima del canvas
- **PNG con trasparenza**: mantieni PNG, comprimi solo dimensione (niente JPEG conversion)
- **Orientamento EXIF**: leggi EXIF orientation e ruota canvas prima di salvare (problema classico iPhone)

```typescript
// Pseudocode compressione
async function compressImage(file: File, maxPx = 1200, quality = 0.85): Promise<Uint8Array> {
  const img = await loadImage(file);
  const { width, height } = calculateDimensions(img, maxPx);
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d')!;
  // Applica rotazione EXIF se necessario
  applyExifOrientation(ctx, img, exifOrientation);
  ctx.drawImage(img, 0, 0, width, height);
  return new Promise(resolve => {
    canvas.toBlob(blob => {
      blob!.arrayBuffer().then(buf => resolve(new Uint8Array(buf)));
    }, 'image/jpeg', quality);
  });
}
```

### 3.3 Video: Thumbnail Auto-generata

Il browser non può generare thumbnail video server-side da Tauri (no FFmpeg bundlato).
Soluzione client-side nativa:

```typescript
async function extractVideoThumbnail(file: File): Promise<Uint8Array> {
  const video = document.createElement('video');
  video.src = URL.createObjectURL(file);
  video.currentTime = 1; // cattura al secondo 1
  await new Promise(resolve => video.addEventListener('seeked', resolve, { once: true }));
  const canvas = document.createElement('canvas');
  canvas.width = 640;
  canvas.height = Math.round(video.videoHeight * (640 / video.videoWidth));
  canvas.getContext('2d')!.drawImage(video, 0, 0, canvas.width, canvas.height);
  URL.revokeObjectURL(video.src);
  return canvasToUint8Array(canvas, 0.80);
}
```

**Limiti video**:
- Max 30 secondi di durata — validazione JS: `video.duration <= 30`
- Max 50MB file originale — validazione JS prima del upload
- Formato accettato: MP4, MOV (H.264) — HEVC/H.265 non garantito su tutti i macOS
- Nessuna compressione video lato JS (troppo pesante) — il file va a Tauri as-is
- Thumbnail compressa a 640px wide, 80% quality JPEG

### 3.4 Limiti Definitivi

| Tipo | Limit | Nota |
|------|-------|------|
| Immagini (originale) | 5 MB | Validazione client prima di compressione |
| Immagini (compressa salvata) | ~200 KB | 1200px, 85% quality |
| Video | 50 MB | No compressione — salvato as-is |
| Video durata | 30 secondi | Validazione JS su `video.duration` |
| Per cliente | 50 foto + 10 video | Soft limit configurabile in Impostazioni |
| Formati foto | JPG, PNG, HEIC, WebP | HEIC → conversione via heic2any |
| Formati video | MP4, MOV | H.264 only per compatibilità |

---

## 4. VERTICALI SPECIFICI

### 4.1 Parrucchiere / Estetica — Before/After Comparator

**Funzionalità core**:
- Upload coppia foto "Prima/Dopo" per ogni appuntamento (o manuale)
- Slider interattivo (drag handle orizzontale)
- Tag automatico col nome del servizio eseguito (es. "Colorazione balayage")
- Condivisione opzionale su Instagram (se consenso GDPR attivo) — deep link all'app
- Gallery "Trasformazioni" filtrabile per: servizio, operatore, mese, tag

**Etichette UI**:
- "Prima" / "Dopo" (non "Before/After" — PMI italiane)
- "Aggiungi trasformazione" — CTA principale
- "Seleziona immagine Prima" / "Seleziona immagine Dopo"

**Schema DB aggiuntivo**:
```sql
CREATE TABLE scheda_media_trasformazioni (
  id INTEGER PRIMARY KEY,
  cliente_id INTEGER NOT NULL REFERENCES clienti(id),
  appuntamento_id INTEGER REFERENCES appuntamenti(id),
  foto_prima_path TEXT NOT NULL,
  foto_dopo_path TEXT NOT NULL,
  servizio_tag TEXT,
  note TEXT,
  consenso_social INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  operatore_id INTEGER REFERENCES operatori(id)
);
```

### 4.2 Fitness — Progress Photos con Timeline

**Funzionalità core**:
- Upload foto progress ogni sessione (o manuale con data)
- Timeline verticale cronologica con miniature
- Integrazione visiva con metriche del giorno (peso, BF% dalla scheda fitness)
- Overlay corporeo SVG opzionale (silhouette con punti di misura: vita, fianchi, petto, braccia)
- Comparazione "Inizio vs Oggi" — before/after slider tra prima foto e ultima
- Export PDF "Report Progressi" (tabella metriche + foto selezionate)

**Privacy**: foto progress sono SEMPRE "internal only" — non condivisibili senza azione esplicita

**Schema DB**:
```sql
CREATE TABLE scheda_media_progress (
  id INTEGER PRIMARY KEY,
  cliente_id INTEGER NOT NULL REFERENCES clienti(id),
  data TEXT NOT NULL,
  foto_path TEXT NOT NULL,
  peso_kg REAL,
  bf_percent REAL,
  note TEXT,
  visibilita TEXT NOT NULL DEFAULT 'private' -- 'private' | 'share_cliente'
);
```

### 4.3 Medica / Fisioterapia — Clinical Images con GDPR

**Funzionalità core**:
- Upload immagini cliniche: radiografie, foto pre/post intervento, documentazione ferite
- Access control: "Solo medico" | "Medico + paziente" | "Tutto lo staff"
- Flag GDPR obbligatorio prima del primo upload: "Ho ottenuto consenso scritto del paziente"
- Watermark opzionale: nome clinica + data in overlay semi-trasparente
- Nessuna condivisione esterna (no link, no social) — blocked by design
- Annotazioni su immagine (tool freccia + testo) — per note cliniche

**Consenso GDPR**: modal obbligatoria al primo upload per ogni cliente:
```
"Confermo di avere il consenso scritto del paziente [Nome Cognome]
per raccogliere e conservare immagini cliniche ai sensi dell'Art. 9
GDPR. Data consenso: [____]  Firma digitale: [Firma in-app]"
```

**Schema DB**:
```sql
CREATE TABLE scheda_media_clinica (
  id INTEGER PRIMARY KEY,
  cliente_id INTEGER NOT NULL REFERENCES clienti(id),
  foto_path TEXT NOT NULL,
  tipo TEXT, -- 'pre_intervento' | 'post_intervento' | 'rx' | 'documentazione'
  visibilita TEXT NOT NULL DEFAULT 'medico_only', -- 'medico_only' | 'staff' | 'paziente'
  gdpr_consenso INTEGER NOT NULL DEFAULT 0,
  gdpr_data TEXT,
  gdpr_firma_path TEXT, -- path firma digitale raccolta in-app
  watermark INTEGER NOT NULL DEFAULT 1,
  note_cliniche TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  operatore_id INTEGER NOT NULL REFERENCES operatori(id)
);
```

### 4.4 Carrozzeria — Foto Danni per Preventivo

**Funzionalità core**:
- Upload multiplo (fino a 20 foto per veicolo) al momento dell'accettazione
- Workflow: "Entrata" → foto danni → "Lavorazione" → progress foto → "Uscita" → foto post
- Annotazioni su immagine: cerchio/freccia per indicare zona danno
- Collegamento a preventivo (uno-a-uno: preventivo_id in ogni foto)
- PDF "Rapporto fotografico" per il cliente con prima/dopo comparazione
- Timeline per veicolo (storico interventi con foto)

**Schema DB**:
```sql
CREATE TABLE scheda_media_veicoli (
  id INTEGER PRIMARY KEY,
  cliente_id INTEGER NOT NULL REFERENCES clienti(id),
  veicolo_targa TEXT,
  preventivo_id INTEGER,
  foto_path TEXT NOT NULL,
  fase TEXT NOT NULL, -- 'entrata_danno' | 'lavorazione' | 'uscita_completato'
  zona_danno TEXT, -- 'frontale' | 'posteriore' | 'laterale_dx' | 'laterale_sx' | 'tetto'
  annotazione_json TEXT, -- Array di {x, y, tipo, testo} per overlay
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

---

## 5. GDPR — Consenso Foto in Scheda

### 5.1 Principi Base
- Art. 9 GDPR: foto cliniche = dato sensibile → consenso esplicito SEMPRE
- Art. 6 GDPR: foto non cliniche (parrucchiere, fitness) = legittimo interesse oppure consenso
- Raccomandazione: consenso esplicito per TUTTE le foto biometriche/identificative

### 5.2 Implementazione Consenso
Tre livelli:
1. **Implicito** (flag nella scheda cliente — default): "Cliente ha autorizzato raccolta dati fotografici in sede" — per uso interno
2. **Esplicito social** (checkbox opzionale): "Cliente acconsente alla pubblicazione su canali social del business"
3. **Esplicito clinico** (firma in-app obbligatoria): solo per verticali medica/fisioterapia

**Flag nel DB clienti** (aggiunta alla tabella esistente):
```sql
ALTER TABLE clienti ADD COLUMN media_consenso_interno INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_social INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_clinico INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_data TEXT;
```

### 5.3 Watermark Opzionale
- Testo: "[Nome Business] — [Data]" in basso a destra
- Opacity: 30%
- Font: 14px bianco con text-shadow nero (leggibile su qualsiasi sfondo)
- Generato lato client via Canvas prima del salvataggio
- Configurabile in Impostazioni > Media > "Watermark automatico"

### 5.4 Accesso Role-Based
| Ruolo | Foto Interne | Foto Cliniche | Foto Social |
|-------|-------------|---------------|-------------|
| Titolare | Vede tutto | Vede tutto | Vede tutto |
| Operatore senior | Vede del proprio cliente | No | No |
| Operatore base | Solo proprie sessioni | No | No |
| Cliente (futuro) | Proprie foto | Solo se flaggate | No |

---

## 6. COMPONENTI REACT NECESSARI

### Componenti Nuovi da Creare

```
src/components/media/
  MediaUploadZone.tsx          ← drag-drop zone riutilizzabile
  MediaGallery.tsx             ← griglia thumbnail + lightbox
  MediaLightbox.tsx            ← overlay fullscreen navigabile
  BeforeAfterSlider.tsx        ← slider comparazione interattivo
  VideoThumbnail.tsx           ← player minimale con thumbnail
  MediaConsentModal.tsx        ← modal GDPR consenso foto
  ProgressTimeline.tsx         ← timeline cronologica (Fitness)
  ImageAnnotator.tsx           ← annotazioni su immagine (Carrozzeria)
  MediaUploadButton.tsx        ← bottone upload singolo (avatar cliente)
```

### Integrazione in Schede Esistenti

```
src/components/schede/
  SchedaParrucchiere.tsx       ← aggiungere sezione "Trasformazioni" con BeforeAfterSlider
  SchedaFitness.tsx            ← aggiungere "Progress Photos" con ProgressTimeline
  SchedaMedica.tsx             ← aggiungere "Immagini Cliniche" con MediaConsentModal
  SchedaFisioterapia.tsx       ← come SchedaMedica
  SchedaVeicoli.tsx            ← aggiungere "Foto Veicolo" con ImageAnnotator
  SchedaCarrozzeria.tsx        ← workflow entrata/lavorazione/uscita
  SchedaEstetica.tsx           ← aggiungere "Trasformazioni" (identico a Parrucchiere)
```

### Dipendenze NPM

```json
{
  "heic2any": "^0.0.4",          // HEIC → JPEG conversione client-side
  "exifr": "^7.1.3"              // EXIF orientation reading (fix rotazione iPhone)
}
```

Note: NO librerie per slider before/after (implementazione custom ~100 righe per controllo totale) e NO lightbox library (troppo peso per funzionalità che usiamo).

---

## 7. RUST COMMANDS NECESSARI

```rust
// src-tauri/src/commands/media.rs

/// Salva immagine compressa sul filesystem
/// Riceve: cliente_id, bytes compressi, metadata
/// Restituisce: path relativo salvato nel DB
#[tauri::command]
pub async fn save_media_image(
    state: State<'_, AppState>,
    app: AppHandle,
    cliente_id: i64,
    bytes: Vec<u8>,
    file_name: String,
    media_type: String, // "foto" | "video"
) -> Result<String, String>

/// Salva video sul filesystem (no compressione, file as-is)
#[tauri::command]
pub async fn save_media_video(
    state: State<'_, AppState>,
    app: AppHandle,
    cliente_id: i64,
    video_bytes: Vec<u8>,
    thumb_bytes: Vec<u8>,
    file_name: String,
) -> Result<MediaVideoResult, String> // { video_path, thumb_path }

/// Recupera lista media per un cliente
#[tauri::command]
pub async fn get_cliente_media(
    state: State<'_, AppState>,
    cliente_id: i64,
    tipo: Option<String>, // filtra per "foto"|"video"|"trasformazione"|"clinica"
) -> Result<Vec<MediaRecord>, String>

/// Elimina media (file + record DB)
#[tauri::command]
pub async fn delete_media(
    state: State<'_, AppState>,
    app: AppHandle,
    media_id: i64,
) -> Result<(), String>

/// Legge bytes di un file media (per lightbox / before-after)
/// Evita di passare path assoluti al frontend per sicurezza
#[tauri::command]
pub async fn read_media_file(
    state: State<'_, AppState>,
    app: AppHandle,
    relative_path: String,
) -> Result<Vec<u8>, String>

/// Aggiorna consenso GDPR media di un cliente
#[tauri::command]
pub async fn update_media_consent(
    state: State<'_, AppState>,
    cliente_id: i64,
    consenso_interno: bool,
    consenso_social: bool,
    consenso_clinico: bool,
) -> Result<(), String>

/// Genera PDF rapporto fotografico (Carrozzeria / Fitness progress)
/// Usa printpdf Rust crate
#[tauri::command]
pub async fn export_media_pdf(
    state: State<'_, AppState>,
    app: AppHandle,
    cliente_id: i64,
    tipo_report: String, // "progress" | "veicolo" | "trasformazioni"
) -> Result<String, String> // path PDF generato
```

### Tabella Media Unificata (migration 030)

```sql
-- migration: 030_cliente_media.sql
CREATE TABLE IF NOT EXISTS cliente_media (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  cliente_id    INTEGER NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
  media_path    TEXT NOT NULL,          -- path relativo da AppData
  thumb_path    TEXT,                   -- solo per video
  tipo          TEXT NOT NULL,          -- 'foto' | 'video'
  categoria     TEXT NOT NULL DEFAULT 'generale',
    -- 'generale' | 'trasformazione_prima' | 'trasformazione_dopo'
    -- | 'progress' | 'clinica' | 'danno_veicolo' | 'post_intervento'
  appuntamento_id INTEGER REFERENCES appuntamenti(id),
  operatore_id  INTEGER REFERENCES operatori(id),
  dimensione_bytes INTEGER,
  larghezza_px  INTEGER,
  altezza_px    INTEGER,
  durata_sec    INTEGER,                -- solo video
  consenso_gdpr INTEGER NOT NULL DEFAULT 0,
  visibilita    TEXT NOT NULL DEFAULT 'interno',
    -- 'interno' | 'staff' | 'paziente' | 'social'
  watermark     INTEGER NOT NULL DEFAULT 0,
  note          TEXT,
  tag           TEXT,                   -- JSON array: ["colorazione", "balayage"]
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_cliente_media_cliente ON cliente_media(cliente_id);
CREATE INDEX IF NOT EXISTS idx_cliente_media_categoria ON cliente_media(categoria);
CREATE INDEX IF NOT EXISTS idx_cliente_media_appuntamento ON cliente_media(appuntamento_id);

-- Tabella trasformazioni before/after (coppia di media)
CREATE TABLE IF NOT EXISTS cliente_media_trasformazioni (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  cliente_id      INTEGER NOT NULL REFERENCES clienti(id) ON DELETE CASCADE,
  media_prima_id  INTEGER NOT NULL REFERENCES cliente_media(id),
  media_dopo_id   INTEGER NOT NULL REFERENCES cliente_media(id),
  appuntamento_id INTEGER REFERENCES appuntamenti(id),
  servizio_tag    TEXT,
  consenso_social INTEGER NOT NULL DEFAULT 0,
  note            TEXT,
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Consenso GDPR media per cliente (aggiunte alla tabella clienti)
-- NB: usare ALTER TABLE nella migration
ALTER TABLE clienti ADD COLUMN media_consenso_interno INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_social  INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_clinico INTEGER NOT NULL DEFAULT 0;
ALTER TABLE clienti ADD COLUMN media_consenso_data    TEXT;
```

**IMPORTANTE**: questa migration 030 va aggiunta al custom runner in `lib.rs` come tutti i precedenti.

---

## 8. ACCEPTANCE CRITERIA MISURABILI

### AC-1: Upload Base
- [ ] Drag-drop di un JPG 4MB → compressa a <250KB → salvata in AppData/fluxion/media/clienti/{id}/foto/
- [ ] Upload di un HEIC da iPhone → convertita in JPEG, compressa, salvata correttamente
- [ ] Immagine iPhone rotazione EXIF corretta (non ruotata di 90 gradi)
- [ ] File >5MB → errore inline "File troppo grande (X.XMB > 5MB)" — nessun crash
- [ ] Upload 10 foto consecutive → tutte salvate, galleria mostra 10 thumbnail
- [ ] TypeScript: 0 errori `npm run type-check`

### AC-2: Video
- [ ] Upload MP4 30s / 45MB → salvato as-is, thumbnail generata in <3s
- [ ] Video >50MB → errore inline prima del transfer
- [ ] Video >30s → errore "Video troppo lungo (32s > 30s)"
- [ ] Thumbnail cliccabile apre player nativo (via Tauri shell open)

### AC-3: Before/After Slider
- [ ] Drag handle funziona fluido su mouse (no jank, 60fps)
- [ ] Keyboard: freccia sinistra/destra sposta handle di 5%
- [ ] Label "Prima" / "Dopo" sempre visibili indipendentemente dalla posizione handle
- [ ] Mobile/touch: pointer events funzionano correttamente

### AC-4: Galleria Lightbox
- [ ] Click thumbnail → lightbox aperta con animazione scale-in <200ms
- [ ] Navigazione freccia sinistra/destra tra tutte le foto del cliente
- [ ] ESC chiude lightbox
- [ ] Metadati visibili: data upload, dimensione, operatore, categoria

### AC-5: GDPR
- [ ] Prima foto clinica → modal GDPR obbligatoria — impossibile bypassare
- [ ] Flag consenso salvato nel DB con data
- [ ] Foto cliniche non visibili a operatori "base" (solo "senior" e "titolare")
- [ ] Watermark applicato se impostazione attiva — verificabile visivamente nel PNG salvato

### AC-6: Performance
- [ ] Compressione 5MB JPEG → completata in <3s su MacBook (canvas API)
- [ ] Galleria con 50 foto → render in <500ms (thumbnail, non originali)
- [ ] Lightbox naviga tra foto senza latency percepita (<100ms per switch)

### AC-7: Verticali
- [ ] SchedaParrucchiere: sezione "Trasformazioni" con before/after slider visibile
- [ ] SchedaFitness: "Progress Photos" mostra timeline cronologica con metriche affiancate
- [ ] SchedaMedica: "Immagini Cliniche" richiede consenso GDPR al primo upload
- [ ] SchedaCarrozzeria: workflow "Entrata / Lavorazione / Uscita" con 3 categorie foto distinte

---

## 9. STIMA EFFORT TOTALE

| Componente | Effort | Priorità |
|-----------|--------|----------|
| Migration 030 + Rust commands (5 commands) | 3h | P0 |
| `MediaUploadZone.tsx` + compressione canvas | 2h | P0 |
| `MediaGallery.tsx` + `MediaLightbox.tsx` | 2h | P0 |
| `BeforeAfterSlider.tsx` | 1.5h | P1 |
| `MediaConsentModal.tsx` (GDPR) | 1h | P0 |
| `ProgressTimeline.tsx` (Fitness) | 2h | P1 |
| `ImageAnnotator.tsx` (Carrozzeria) | 3h | P2 |
| `VideoThumbnail.tsx` + extract thumbnail | 1.5h | P1 |
| Integrazione in 7 schede esistenti | 3h | P1 |
| Export PDF rapporto fotografico | 2h | P2 |
| Test TypeScript + Playwright | 2h | P0 |
| **TOTALE P0** | **~11h** | |
| **TOTALE P0+P1** | **~16h** | |
| **TOTALE COMPLETO** | **~23h** | |

### Sprint raccomandato
- **Sprint A (P0, ~11h)**: Infrastruttura media (migration, Rust, upload zone, gallery, lightbox, GDPR modal) + integrazione base in SchedaParrucchiere e SchedaMedica
- **Sprint B (P1, ~5h)**: BeforeAfterSlider, ProgressTimeline (Fitness), VideoThumbnail + integrazione in SchedaFitness
- **Sprint C (P2, ~7h)**: ImageAnnotator (Carrozzeria), export PDF, integrazione completa tutte le schede

---

## 10. DESIGN SYSTEM — COLORI E CLASSI

Seguendo il design system FLUXION:

```tsx
// Upload zone idle
className="border-2 border-dashed border-border hover:border-primary
           bg-card/30 hover:bg-primary/5 transition-all rounded-xl p-8
           cursor-pointer"

// Upload zone drag-over
className="border-2 border-solid border-primary bg-primary/10
           scale-[1.01] transition-all rounded-xl p-8"

// Thumbnail card
className="relative aspect-[4/3] rounded-lg overflow-hidden
           bg-card hover:scale-[1.03] transition-transform cursor-pointer
           group"

// Overlay azioni thumbnail (visible on hover)
className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent
           opacity-0 group-hover:opacity-100 transition-opacity
           flex items-end p-2 gap-1"

// Before/after handle
className="absolute top-0 bottom-0 w-0.5 bg-white cursor-ew-resize
           drop-shadow-lg z-10"

// Handle circle
className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2
           w-8 h-8 rounded-full bg-white shadow-lg
           flex items-center justify-center text-slate-700"

// GDPR consent modal header
className="bg-gradient-to-r from-amber-500/20 to-orange-500/20
           border-b border-amber-500/30 p-4"
```

---

## 11. CONSIDERAZIONI SPECIALI TAURI

### Sicurezza Path
- Il frontend NON deve mai ricevere path assoluti del filesystem (security)
- Tauri command `read_media_file` prende `relative_path` e risolve internamente
- Tauri convert: bytes → `data:image/jpeg;base64,...` per src immagini in React
- In alternativa: Tauri `convertFileSrc` API per servire file locali con schema `asset://`

### `asset://` Protocol (alternativa ai bytes)
Tauri 2.x supporta `convertFileSrc(absolutePath)` → URL `asset://localhost/...`
```typescript
import { convertFileSrc } from '@tauri-apps/api/core';
const assetUrl = convertFileSrc(absoluteMediaPath);
// <img src={assetUrl} /> funziona direttamente
```
Questo approccio è più performante per la galleria (no base64 in RAM).
Richiede: `"asset": true` in `tauri.conf.json` protocol config.

### Permissions Tauri 2.x
```json
// tauri.conf.json — aggiungere:
{
  "plugins": {
    "fs": {
      "scope": {
        "allow": ["$APPDATA/fluxion/media/**"],
        "deny": []
      }
    }
  }
}
```

---

*Research completata: 2026-03-05 | Pronta per /gsd:execute-phase*
