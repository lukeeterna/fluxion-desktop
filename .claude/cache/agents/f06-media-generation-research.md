# F06 — Media Generation per PMI Italiane: Research World-Class
## CoVe 2026 Deep Research — Standard Fotografici e Prompt FLUX

**Data ricerca**: 2026-03-07
**Obiettivo**: definire prompt FLUX ottimali per generare immagini demo/showcase di qualità professionale per FLUXION (gestionale desktop per PMI italiane).
**Metodo**: benchmark competitor world-class, analisi protocolli fotografici standard, identificazione gap mercato italiano, generazione prompt FLUX precisi.

---

## VERTICALE 1: FITNESS / PALESTRA

### 1.1 Standard Fotografici World-Class (Leader di Settore)

I leader mondiali (TrueCoach, ABC Trainerize, MyFitnessPal Coach, FitBudd) hanno definito un protocollo preciso per la documentazione visuale del progresso fisico:

**TrueCoach / ABC Trainerize:**
- Upload strutturato di progress photos direttamente nel profilo cliente
- Tracking visuale combinato con metriche (peso, composizione corporea, macro)
- Integrazione con wearable (Apple Health, Garmin, WHOOP, OURA, Fitbit)
- Timeline fotografica con confronto affiancato before/after
- Cadenza raccomandata: ogni 4 settimane

**Standard fotografico de-facto (personal training professionale):**
- **3 angolazioni obbligatorie**: frontale (0°), laterale destra (90°), posteriore (180°)
- **Angolazione opzionale avanzata**: diagonale a 45° per evidenziare obliqui e definizione
- **Abbigliamento**: indumenti aderenti e consistenti tra le sessioni (shorts + sport bra per donne, shorts per uomini)
- **Sfondo**: muro neutro (bianco, grigio chiaro) o backdrop monocromatico
- **Luce**: luce naturale diffusa da finestra frontale, OPPURE softbox a 45° con riflettore
- **Orario**: mattino presto, a stomaco vuoto, stessa ora in ogni sessione
- **Posa standard**: statura eretta, piedi alla larghezza delle anche, core rilassato (non aspirato, non contratto)
- **Posa muscolare separata**: sempre documentata come set dedicato (front double bicep, lat spread, side chest, ecc.)
- **Altezza camera**: altezza petto/ombelico, fotocamera perpendicolare al corpo

### 1.2 Tipi di Foto Tipici

| Tipo | Descrizione | Uso clinico/motivazionale |
|------|-------------|--------------------------|
| **Progress Before** | Prima foto della serie — corpo a riposo, 3 angolazioni | Baseline documentazione |
| **Progress After** | Foto confronto stesso giorno/mese successivo | Visualizzazione cambiamento |
| **Body Composition** | Con sovrapposizione annotazioni (grasso, muscolo) | Analisi scientifica |
| **Muscle Pose** | Set posa atletica/muscolare — contratta | Motivazione, social proof |
| **Measurement Photo** | Foto con nastro centimetrico su vita, fianchi, cosce | Documentazione misure |
| **Workout Action** | Cliente durante esercizio — forma tecnica documentata | Feedback posturale, marketing |
| **Monthly Comparison** | Grid 4-8 foto in serie temporale | Timeline trasformazione |

### 1.3 Protocollo Standard Professionale

```
SESSION PROTOCOL — FITNESS PROGRESS PHOTOGRAPHY

1. PREPARAZIONE
   - Stessa ora del giorno (preferibilmente mattina, 7-9 AM)
   - Stomaco vuoto o 2h dopo ultimo pasto
   - Non dopo allenamento (muscles pump altera la percezione)
   - Stessa illuminazione e locazione

2. SCATTO SET A — CORPO A RIPOSO
   - Frontale: piedi uniti o larghezza fianchi, braccia leggermente staccate
   - Laterale DX: profilo completo
   - Posteriore: specchio della frontale
   - Frame: testa inclusa, piedi inclusi

3. SCATTO SET B — POSE MUSCOLARI (atleti/bodybuilding)
   - Front Double Bicep
   - Side Chest (lato dominante)
   - Back Double Bicep
   - Vacuum pose (opzionale)

4. POST-PROCESSING
   - No filtri, no editing della forma corporea
   - Crop consistente sessione-su-sessione
   - Annotazione data + peso del giorno
```

### 1.4 Gap vs Competitor — PMI Italiane

| Area | Standard World-Class | Gap PMI Italia |
|------|---------------------|----------------|
| **Software tracking** | TrueCoach: timeline fotografica integrata nel profilo | Software italiani (XeniaSoft, TO.M.M.YS.) focalizzati su booking/pagamenti, zero gestione foto progress |
| **Protocollo codificato** | Trainerize fornisce guide fotografiche al PT e al cliente | Nessun PT italiano usa protocollo scritto standardizzato |
| **Confronto automatico** | App confronto affiancato before/after con slider | Confronto manuale (WhatsApp forward o cartelle condivise) |
| **Annotazioni metriche** | Overlay automatico peso + misure sulla foto | Dati tenuti separati (foglio Excel + foto su smartphone) |
| **Privacy GDPR** | Storage criptato, consenso digitale integrato | Foto spesso in galleria personale del PT o in chat WhatsApp |
| **Qualità foto** | Guida fotografica fornita al cliente nell'onboarding | Clienti scattano foto casuali in bagno con qualità variabile |

### 1.5 Prompt FLUX — Fitness / Palestra

```json
{
  "id": "fitness_001",
  "verticale": "fitness",
  "categoria": "progress_before",
  "prompt": "Professional fitness progress photo, athletic male client, 30s, front view, standing upright relaxed pose, neutral white wall background, even soft studio lighting, grey athletic shorts, bare chest, full body frame head to feet, clinical documentation style, realistic photography, 85mm lens, sharp focus, no artistic filters",
  "negative_prompt": "cartoon, anime, illustration, blurry, low quality, text, watermark, artistic filters, dramatic shadows, flexing pose, gym equipment visible, colored background",
  "uso": "Scheda fitness tab Media — foto progress BEFORE, angolazione frontale"
}
```

```json
{
  "id": "fitness_002",
  "verticale": "fitness",
  "categoria": "progress_after",
  "prompt": "Professional fitness transformation after photo, athletic male client, 30s, front view, standing upright, visible muscle definition improvement, neutral white wall background, consistent even lighting, grey athletic shorts, bare chest, full body frame, before-after comparison documentation style, realistic photography, high detail",
  "negative_prompt": "cartoon, anime, illustration, dramatic lighting for effect, excessive muscle, unrealistic proportions, oiled skin, competition bodybuilding lighting, colored gels, text, watermark",
  "uso": "Scheda fitness tab Media — foto progress AFTER frontale, confronto con before"
}
```

```json
{
  "id": "fitness_003",
  "verticale": "fitness",
  "categoria": "progress_lateral",
  "prompt": "Professional fitness progress photo, athletic female client, 35s, side lateral view, right profile, standing straight relaxed, neutral grey background, soft diffused window lighting, black sports bra, fitted shorts, full body frame, clinical body composition documentation, realistic photography, sharp detail",
  "negative_prompt": "cartoon, anime, overly sexualized, dramatic shadows, artistic pose, gym background, colored backdrop, blurry, text, watermark",
  "uso": "Scheda fitness tab Media — foto progress laterale DX, documentazione composizione corporea"
}
```

```json
{
  "id": "fitness_004",
  "verticale": "fitness",
  "categoria": "before_after_grid",
  "prompt": "Side-by-side fitness transformation comparison, same male client front view, left panel labeled BEFORE showing higher body fat, right panel labeled AFTER showing lean muscle definition, consistent white background both panels, identical pose and framing, professional documentation photography, gym management software screenshot style, clean UI layout, realistic",
  "negative_prompt": "cartoon, extreme bodybuilding, unrealistic proportions, stock photo cheesy, text overlay cluttered, different lighting between panels, colored backgrounds",
  "uso": "Dashboard riepilogo trasformazione cliente — widget confronto before/after"
}
```

```json
{
  "id": "fitness_005",
  "verticale": "fitness",
  "categoria": "workout_technique",
  "prompt": "Personal trainer observing client performing barbell squat with correct form, modern gym interior, professional gym lighting overhead LEDs, trainer standing beside client with clipboard, focus on form documentation, mid-action realistic photography, 35mm lens, high resolution, professional fitness coaching environment",
  "negative_prompt": "cartoon, anime, illustration, poor form, dangerous position, messy gym, blurry motion, stock photo style, watermark, text overlay",
  "uso": "Scheda esercizi tab Media — documentazione tecnica esecuzione esercizio"
}
```

```json
{
  "id": "fitness_006",
  "verticale": "fitness",
  "categoria": "body_measurement",
  "prompt": "Professional body measurement documentation photo, female client, fitness trainer measuring waist circumference with yellow measuring tape, neutral background, clinical bright lighting, both subjects professional attire, realistic medical/fitness documentation style, close-up medium shot",
  "negative_prompt": "cartoon, anime, inappropriate framing, blurry, casual smartphone photo style, text, watermark, dramatic lighting",
  "uso": "Scheda fitness tab Misure — foto documentazione misurazione corporea"
}
```

```json
{
  "id": "fitness_007",
  "verticale": "fitness",
  "categoria": "monthly_timeline",
  "prompt": "Fitness progress timeline grid, 3-month transformation series, same athletic male subject, front view in all three photos, January February March labels, consistent white background and lighting across all shots, visible gradual body composition improvement, professional documentation layout, realistic photography",
  "negative_prompt": "cartoon, dramatic before-after, unrealistic rapid transformation, different backgrounds, inconsistent lighting, text heavy, watermark",
  "uso": "Report mensile cliente — griglia timeline visuale progresso trimestrale"
}
```

---

## VERTICALE 2: FISIOTERAPIA / RIABILITAZIONE

### 2.1 Standard Fotografici World-Class (Leader di Settore)

I leader mondiali (Jane App, Cliniko, WebPT, Physiotec) e la letteratura clinica fisioterapica hanno definito protocolli fotografici precisi:

**Jane App:**
- Funzionalità di upload foto/video direttamente nel chart SOAP del paziente
- Note cliniche visivamente arricchite con immagini pre/post trattamento
- Storage sicuro HIPAA-compliant con accesso per paziente

**Standard fotografico clinico fisioterapia (Physiopedia / JEO / PubMed):**
- **Vista anteriore (AP)**: paziente in piedi, vista frontale completa, valutazione asimmetrie, altezza spalle, obliquità pelvica
- **Vista posteriore**: curvatura scoliotica, posizione scapole, simmetria glutei, allineamento achilleo
- **Vista laterale (destra e sinistra)**: cifosi toracica, lordosi lombare, proiezione del capo (FHP), allineamento orecchio-spalla-anca-malleolo
- **Marcatori anatomici**: etichette adesive bianche su grande trocantere, SIAS, SIPS, epicondilo laterale, acromioclaveare
- **Attrezzatura**: treppiede a altezza fissa, sfondo neutro (preferibilmente grigio scuro per contrasto), filo a piombo visibile come riferimento verticale
- **ROM Photography**: angolo articolare documentato con foto al range massimo attivo, confronto pre/post sessione o ciclo di terapia
- **Zona di dolore**: schema corporeo fotografico (body chart) annotato con area di dolore localizzata

**Protocollo clinico SOAP con documentazione fotografica:**
- Fotografia integrata nella sezione **Objective** del SOAP note
- Confronto serie fotografica: pre-trattamento (T0), a metà ciclo (T1), post-ciclo (T2)
- Goniometria fotografica: misurazione angoli articolari da foto (validata scientificamente vs goniometro tradizionale)

### 2.2 Tipi di Foto Tipici

| Tipo | Descrizione | Protocollo |
|------|-------------|------------|
| **Postural Assessment** | 3 viste: AP, posteriore, laterale | Treppiede fisso, marcatori anatomici |
| **ROM Documentation** | Articolazione a massimo range attivo | Camera perpendicolare al piano di movimento |
| **Pain Area Mapping** | Corpo + annotazione zona dolore | Foto + overlay colorato o disegno body chart |
| **Edema/Swelling** | Documentazione gonfiore con metro centimetrico | Close-up + riferimento metrico |
| **Scar/Wound** | Cicatrice o ferita post-chirurgica | Close-up standardizzato con scala metrica |
| **Functional Test** | Squat test, single-leg balance, Trendelenburg | Video o sequenza fotografica multipla |
| **Pre/Post Session** | Confronto postura prima e dopo sessione | Stesso setup, stesse angolazioni |

### 2.3 Protocollo Standard Professionale

```
CLINICAL PHOTOGRAPHY PROTOCOL — PHYSIOTHERAPY

1. SETUP STANDARDIZZATO
   - Treppiede a altezza fissa (ombelico del paziente medio = ~100cm)
   - Sfondo neutro scuro (grigio antracite o blu navy)
   - Illuminazione: softbox frontale bilaterale o luce fluorescente uniforme
   - Filo a piombo visibile o griglia a pavimento come riferimento

2. MARCATORI ANATOMICI (adesivi bianchi circolari)
   - Grande trocantere (laterale)
   - SIAS (antero-superiore)
   - Acromion (superiore spalla)
   - Epicondilo laterale (gomito)
   - Malleolo laterale

3. SEQUENZA FOTOGRAFICA T0 (valutazione iniziale)
   - Vista anteriore: paziente in piedi, braccia lungo i fianchi
   - Vista posteriore: stessa posizione
   - Vista laterale DX: profilo completo
   - Vista laterale SX: profilo completo
   - Close-up area specifica di problema (se applicabile)

4. ROM DOCUMENTATION
   - Foto al range ZERO (posizione anatomica di partenza)
   - Foto al range MASSIMO ATTIVO
   - Entrambe con goniometro visibile OPPURE linee di riferimento tracciabili

5. FOLLOW-UP T1, T2
   - Identico setup, identiche angolazioni
   - Annotazione data + numero sessione
```

### 2.4 Gap vs Competitor — PMI Italiane

| Area | Standard World-Class | Gap PMI Italia |
|------|---------------------|----------------|
| **Documentazione visuale integrata** | Jane App/Cliniko: foto nel chart SOAP con timestamp | Fisioterapisti italiani: documentazione su carta + foto su smartphone personale non organizzate |
| **Goniometria fotografica** | Validata scientificamente, app dedicate (Meloq EasyAngle) | Ancora usato goniometro fisico senza documentazione fotografica |
| **Confronto pre/post trattamento** | Timeline fotografica strutturata nel software | Confronto mentale del terapista, nessuna documentazione visuale sistemata |
| **Marcatori anatomici standardizzati** | Protocollo scientifico con adesivi colorati | Assente nella pratica clinica tipica |
| **Privacy GDPR** | Storage cloud HIPAA/GDPR-compliant | Foto in galleria smartphone del terapista |
| **Comunicazione con paziente** | Report visuale inviato al paziente con confronto | Verbale, nessun report visuale |

### 2.5 Prompt FLUX — Fisioterapia / Riabilitazione

```json
{
  "id": "physio_001",
  "verticale": "fisioterapia",
  "categoria": "postural_assessment_anterior",
  "prompt": "Clinical physiotherapy postural assessment photo, male patient 40s standing upright, anterior frontal view, neutral dark grey background, bright uniform clinical lighting, patient wearing black shorts only, white anatomical markers on bilateral shoulders and hips, physiotherapy clinic setting, medical documentation photography style, full body frame, professional and clinical aesthetic",
  "negative_prompt": "cartoon, anime, dramatic shadows, colorful background, casual clothing, gym setting, artistic poses, text, watermark, blurry",
  "uso": "Scheda fisioterapia tab Valutazione — foto assessment posturale vista anteriore T0"
}
```

```json
{
  "id": "physio_002",
  "verticale": "fisioterapia",
  "categoria": "postural_assessment_lateral",
  "prompt": "Clinical physiotherapy lateral posture assessment, female patient 35s, right side profile view, standing straight, dark neutral background, clinical overhead lighting, anatomical markers on ear, shoulder, hip, knee and ankle, vertical plumb line reference visible on the side, physiotherapy clinic, medical documentation style, realistic photography, full body",
  "negative_prompt": "cartoon, artistic lighting, colorful background, casual setting, blurry, text, watermark, dramatic poses",
  "uso": "Scheda fisioterapia tab Valutazione — foto assessment posturale vista laterale con marcatori"
}
```

```json
{
  "id": "physio_003",
  "verticale": "fisioterapia",
  "categoria": "rom_assessment",
  "prompt": "Physiotherapy range of motion documentation photo, male patient performing maximum shoulder flexion, physical therapist beside patient with goniometer measuring joint angle, clinical room white walls, bright even lighting, patient in grey shorts and t-shirt, close-medium shot showing arm elevation angle clearly, clinical measurement documentation, realistic medical photography",
  "negative_prompt": "cartoon, anime, blurry, casual setting, dark lighting, artistic style, text watermark",
  "uso": "Scheda fisioterapia tab ROM — documentazione range articolare spalla"
}
```

```json
{
  "id": "physio_004",
  "verticale": "fisioterapia",
  "categoria": "treatment_session",
  "prompt": "Professional physiotherapy treatment session, female therapist performing manual therapy on male patient lying on treatment table, modern physiotherapy clinic, clean white and blue color scheme, professional medical lighting, both wearing professional attire, clinical and professional environment, realistic photography, medium wide shot",
  "negative_prompt": "cartoon, anime, inappropriate contact, unprofessional setting, dim lighting, hospital gloomy, dramatic shadows, text, watermark",
  "uso": "Scheda fisioterapia tab Media — foto seduta trattamento manuale"
}
```

```json
{
  "id": "physio_005",
  "verticale": "fisioterapia",
  "categoria": "before_after_posture",
  "prompt": "Physiotherapy posture improvement comparison, same male patient side lateral view, left panel BEFORE showing forward head posture and rounded shoulders, right panel AFTER showing corrected upright posture, identical dark background both panels, same anatomical markers visible, clinical documentation layout, realistic medical photography, professional rehabilitation result",
  "negative_prompt": "cartoon, exaggerated before, unrealistic correction, different backgrounds, artistic style, text heavy, blurry, watermark",
  "uso": "Report fine ciclo — confronto posturale before/after ciclo riabilitativo"
}
```

```json
{
  "id": "physio_006",
  "verticale": "fisioterapia",
  "categoria": "exercise_rehabilitation",
  "prompt": "Patient performing therapeutic exercise in physiotherapy clinic, female patient 50s doing resistance band shoulder external rotation exercise, physical therapist supervising with correct form, modern rehabilitation gym with parallel bars visible, professional clinical lighting, clean modern clinic interior, realistic photography, motivating and clinical tone",
  "negative_prompt": "cartoon, anime, incorrect form, gym commercial style, dramatic lighting, text, watermark, blurry",
  "uso": "Scheda esercizi riabilitazione — documentazione esercizio terapeutico"
}
```

```json
{
  "id": "physio_007",
  "verticale": "fisioterapia",
  "categoria": "swelling_documentation",
  "prompt": "Clinical documentation photo of ankle swelling assessment, close-up of patient ankle with mild edema, yellow measuring tape around ankle circumference for girth measurement, clinical white background or treatment table, bright even medical lighting, medical documentation style, centimeter scale visible, professional clinical photography",
  "negative_prompt": "cartoon, gruesome, overly medical graphic, blurry, dark, artistic, text, watermark, colored background",
  "uso": "Scheda fisioterapia tab Misurazioni — foto documentazione edema con riferimento metrico"
}
```

---

## VERTICALE 3: ODONTOIATRICA / STUDIO DENTISTICO

### 3.1 Standard Fotografici World-Class (Leader di Settore)

I leader mondiali (Dentrix Ascend, Curve Dental, DentalIntel, Carestream) e le linee guida AACD (American Academy of Cosmetic Dentistry) hanno codificato un protocollo fotografico con 12 viste standard:

**AACD 12-View Protocol (gold standard internazionale):**

**EXTRAORAL (6 viste):**
1. Ritratto frontale sorriso (1:10) — macroelements valutazione
2. Frontale 1:2 con retractor — microelements
3. Laterale destra con sorriso (1:2)
4. Laterale sinistra con sorriso (1:2)
5. Fronto-laterale destra 45° (1:2)
6. Fronto-laterale sinistra 45° (1:2)

**INTRAORAL (6 viste):**
7. Frontale retracted (1:2) — arcate in occlusione
8. Laterale destra retracted
9. Laterale sinistra retracted
10. Occlusale arcata superiore (con specchio)
11. Occlusale arcata inferiore (con specchio)
12. Frontale a bocca leggermente aperta (separazione incisale)

**Attrezzatura standard:**
- Flash ring (luce anulare) per intraorali — eliminazione ombre nelle cavità orali
- Retractors labiali (divaricatori) per viste retracted
- Specchi intraorali in acciaio (occlusali + laterali) per viste del palato e mascellare
- Sfondo nero (contrasto denti bianchi su scuro)
- Macro lens (100mm) per intraorali
- Body position: paziente seduto a 45°, testa stabilizzata

**Dentrix Ascend / Curve Dental workflow:**
- Imaging integration: foto allegate direttamente alla cartella paziente nel software
- Insurance claim attachment: foto automaticamente allegate ai preventivi assicurativi
- Treatment presentation: slideshow before/after per presentazione piano di trattamento al paziente

### 3.2 Tipi di Foto Tipici

| Tipo | Viste | Uso clinico |
|------|-------|-------------|
| **New Patient Records** | 12-view AACD completo | Documentazione baseline, medicolegale |
| **Smile Design Pre** | Frontale sorriso, 45° bilaterale | Digital Smile Design (DSD) |
| **Intraoral Survey** | 5 viste intraorali | Diagnosi carie, parodontale |
| **Treatment Before** | Frontale retracted + occlusali | Baseline prima del trattamento |
| **Treatment After** | Identiche viste post-trattamento | Confronto risultato |
| **Shade Selection** | Close-up denti con tab colore Vita | Comunicazione al laboratorio |
| **Orthodontic Progress** | Serie mensile occlusali + frontale | Tracking movimento dentale |
| **Cosmetic Case Presentation** | Before/after sorriso + 45° | Marketing, presentazione preventivo |

### 3.3 Protocollo Standard Professionale

```
DENTAL PHOTOGRAPHY PROTOCOL — AACD STANDARD

SETUP
- Flash ring montato sul macro lens 100mm
- Sfondo: riflettore nero o linguetta nera intraorali, sfondo grigio per extraorali
- Illuminazione: luce anulare diretta non diffusa (AACD specifica NO softbox per accreditamento)
- Paziente: seduto a 45°, testa su appoggiatesta, occhi chiusi per intraorali
- Team: paziente + fotografo (dentista/assistente) + assistente che regge i retractors

SEQUENZA EXTRAORALE
1. Full face a riposo
2. Full face sorriso naturale
3. 3/4 destra
4. 3/4 sinistra
5. Profilo destro
6. Close-up sorriso (lip frame)

SEQUENZA INTRAORALI
7. Frontale retracted in occlusione (specchio posteriore sotto la lingua)
8. Laterale destra (small mirror)
9. Laterale sinistra (small mirror)
10. Occlusale superiore (grande specchio occlusale)
11. Occlusale inferiore (grande specchio occlusale)
12. Frontale a bocca aperta 3-4mm

QUALITA'
- No saliva (aspirazione prima della foto)
- No debris (pulizia profilattica preventiva alla sessione foto)
- No aloni da condensa (riscaldare specchi prima dell'uso)
- Denti asciutti per colore accurato (usare dry shield o cotone)
```

### 3.4 Gap vs Competitor — PMI Italiane

| Area | Standard World-Class | Gap PMI Italia |
|------|---------------------|----------------|
| **Protocollo 12 viste** | AACD standard codificato e insegnato nella formazione ECM | Maggior parte degli studi dentistici italiani: foto occasionale solo per ortodonzia/estetica, non routine |
| **Integrazione software** | Dentrix/Curve: foto collegate direttamente al dente nel chart digitale | Software italiani (Easyvisit, DentalManager) spesso con imaging separato non integrato |
| **Shade photography** | Foto con tab Vita + calibrazione colore per comunicazione con laboratorio | Comunicazione verbale o sketches al laboratorio |
| **Case presentation** | Slideshow automatizzato before/after per preventivo al paziente | Preventivi testuali, zero visual storytelling |
| **Patient marketing** | Before/after sorriso come strumento di acquisizione marketing | Reticenza italiana alla pubblicazione di foto pazienti (privacy) |
| **Intraoral camera routine** | IOC usata su ogni paziente | Usata solo su richiesta o in studi premium |

### 3.5 Prompt FLUX — Odontoiatrica / Studio Dentistico

```json
{
  "id": "dental_001",
  "verticale": "odontoiatrica",
  "categoria": "smile_before",
  "prompt": "Professional dental before photo, patient frontal smile, retracted lips showing full dentition, grey studio background, ring flash dental photography lighting, slight crowding and discoloration visible, clinical documentation style, sharp focus on teeth, 1:2 magnification ratio, realistic dental photography, AACD standard",
  "negative_prompt": "cartoon, anime, perfect white teeth in before photo, blurry, dramatic lighting, dark background, stock photography smile, watermark, text",
  "uso": "Scheda paziente tab Foto — smile frontale retracted BEFORE"
}
```

```json
{
  "id": "dental_002",
  "verticale": "odontoiatrica",
  "categoria": "smile_after",
  "prompt": "Professional dental after photo, patient frontal retracted smile showing full dentition post-cosmetic treatment, grey studio background, ring flash dental photography lighting, beautifully aligned and whitened teeth, veneer work visible, clinical documentation AACD standard, sharp dental detail, realistic dental photography",
  "negative_prompt": "cartoon, anime, unrealistic hyper-white teeth, blurry, different lighting from before photo, artistic filter, watermark, text",
  "uso": "Scheda paziente tab Foto — smile frontale retracted AFTER, confronto trattamento"
}
```

```json
{
  "id": "dental_003",
  "verticale": "odontoiatrica",
  "categoria": "smile_portrait_before_after",
  "prompt": "Side-by-side dental smile transformation, patient portrait, left panel BEFORE showing stained and slightly crooked smile, right panel AFTER showing beautiful cosmetic dentistry result, both panels with identical neutral grey background and professional soft lighting, consistent head position, realistic dental photography, cosmetic case presentation style",
  "negative_prompt": "cartoon, different lighting between panels, unrealistic whitening, text cluttered, stock photo, watermark, blurry",
  "uso": "Presentazione piano di trattamento estetico — confronto before/after sorriso"
}
```

```json
{
  "id": "dental_004",
  "verticale": "odontoiatrica",
  "categoria": "intraoral_retracted",
  "prompt": "Clinical intraoral dental photo, retracted frontal view of patient dentition, both arches in occlusion, lip retractors visible holding lips open, black contrasting background, ring flash lighting eliminating shadows, slight wear patterns visible on enamel, sharp macro detail of all teeth, 1:2 clinical magnification, professional dental documentation photography",
  "negative_prompt": "cartoon, saliva visible, blurry, dark exposure, artistic framing, colored background, text, watermark, dramatic shadow",
  "uso": "Scheda paziente tab Foto — vista intraorali frontale retracted in occlusione"
}
```

```json
{
  "id": "dental_005",
  "verticale": "odontoiatrica",
  "categoria": "occlusal_upper",
  "prompt": "Dental occlusal view of upper arch, patient mouth open wide, large occlusal mirror reflecting maxillary arch from above, clinical ring flash lighting, all upper teeth visible including molars, black background, sharp dental macro photography, AACD documentation standard, no condensation on mirror, clean and dry dentition",
  "negative_prompt": "cartoon, blurry mirror, condensation, saliva, dark exposure, artistic effect, text, watermark",
  "uso": "Scheda paziente tab Foto — vista occlusale arcata superiore"
}
```

```json
{
  "id": "dental_006",
  "verticale": "odontoiatrica",
  "categoria": "treatment_in_progress",
  "prompt": "Dental treatment in progress photo, dentist working on patient with dental handpiece, dental assistant retracting, modern dental operatory with overhead dental light, professional clinical setting, equipment visible including saliva ejector and mirror, realistic medical documentation photography, clinical and professional atmosphere",
  "negative_prompt": "cartoon, anime, dramatic scary perspective, blurry, blood visible, dark room, amateur photo, text, watermark",
  "uso": "Scheda paziente tab Media — documentazione seduta trattamento in corso"
}
```

```json
{
  "id": "dental_007",
  "verticale": "odontoiatrica",
  "categoria": "lateral_smile_45",
  "prompt": "Professional dental portrait, patient 3/4 view showing smile at 45 degrees, natural soft studio lighting, neutral grey background, natural genuine smile showing upper and lower teeth, cosmetic dentistry showcase, professional photography quality, sharp detail on teeth and lips, patient appears comfortable and confident",
  "negative_prompt": "cartoon, stiff posed smile, over-retouched, blurry, dramatic shadows, colored background, stock photo cheesy expression, text, watermark",
  "uso": "Scheda paziente tab Foto — ritratto 45 gradi sorriso per presentazione caso estetico"
}
```

---

## VERTICALE 4: VEICOLI / OFFICINA

### 4.1 Standard Fotografici World-Class (Leader di Settore)

I leader mondiali (Mitchell1 Manager SE, CCC ONE, Shop-Ware, Audatex/Qapter) hanno integrato la documentazione fotografica come parte centrale del workflow di ispezione e riparazione:

**Mitchell1 Manager SE Inspections (lancio recente 2025-2026):**
- Tecnico scatta foto con tablet/smartphone durante ispezione
- Annotazione su immagine: cerchi, frecce, note testo
- Report digitale inviato al cliente via SMS/email con foto annotate
- Approvazione o rifiuto dei lavori in tempo reale tramite portal cliente
- Integrazione automatica: ispezione → preventivo → ordine lavoro

**CCC ONE Repair Workflow:**
- Upload foto da mobile con tagging visibilità (cliente vs assicurazione)
- Documentation fotografica pre-consegna (post-repair quality check)
- Confronto foto intake vs consegna per protezione responsabilità legale

**Standard fotografico industria carrozzeria/officina (protocollo de-facto assicurativo):**
- **8 scatti minimi per veicolo**: 4 angoli esterni (FR, FL, RR, RL), motore aperto, interni, dashboard, e area danno close-up
- Approccio 45° sugli angoli: fotografia da 45° da ogni angolo del veicolo cattura due lati contemporaneamente
- **VIN Label**: sempre documentare il numero telaio
- **Odometer reading**: chilometraggio al momento dell'ingresso
- **Dashboard warnings**: eventuali spie accese documentate
- **Crush zone photo protocol**: scatto direttamente dall'alto (90° dal suolo) per misurare profondità d'impatto
- **Close-up damage**: scatto frontale perpendicolare all'area danneggiata, evitare angoli obliqui che creano distorsioni riflettive
- **Pre-delivery post-repair**: stesso protocollo intake per documentare stato alla consegna

### 4.2 Tipi di Foto Tipici

| Tipo | Descrizione | Momento |
|------|-------------|---------|
| **Pre-Intake Walk-Around** | 8+ scatti esterni + interni prima di prendere in consegna | Accettazione veicolo |
| **Damage Close-Up** | Ogni area di danno: perpendicolare, con riferimento metrico | Accettazione + stima |
| **VIN + Odometer** | Targa, VIN, km, spie dashboard | Prima documentazione |
| **Underhood** | Vano motore aperto, danni strutturali visibili | Diagnostica |
| **Repair Progress** | Passo dopo passo: smontaggio, scocca, primer, verniciatura | Tracciabilità lavori |
| **Parts Documentation** | Ricambi usati/nuovi con numero OEM visibile | Tracciabilità parti |
| **Post-Repair Quality Check** | Stessi angoli del pre-intake, verifica colore e allineamento | Consegna |
| **Customer Approval** | Set foto inviate al cliente per approvazione preventivo | Pre-lavorazione |

### 4.3 Protocollo Standard Professionale

```
VEHICLE DOCUMENTATION PROTOCOL — AUTO REPAIR / CARROZZERIA

PRE-INTAKE (all'accettazione del veicolo)
1. WALK-AROUND 8 SCATTI:
   - Front-Right 45° (angolo anteriore destro)
   - Front-Left 45° (angolo anteriore sinistro)
   - Rear-Right 45° (angolo posteriore destro)
   - Rear-Left 45° (angolo posteriore sinistro)
   - Frontale centrale
   - Posteriore centrale
   - Laterale sinistra
   - Laterale destra

2. DOCUMENTAZIONE IDENTIFICATIVA:
   - VIN label (montante porta conducente)
   - Odometer reading (cruscotto)
   - Tutte le spie warning accese
   - Targa anteriore e posteriore

3. DANNI SPECIFICI:
   - Overview shot dell'area danneggiata (contesto)
   - Close-up perpendicolare a 90° (profondità ammaccatura)
   - Close-up da 45° (estensione laterale)
   - Crush zone: fotografia dall'alto verticalmente

4. INTERNI:
   - Sedili, plancia (airbag)
   - Tappetini/pavimento
   - Specchietto retrovisore interno

REPAIR PROGRESS (durante lavorazione)
- Smontaggio parti (documentare prima dello smontaggio)
- Stato scocca dopo raddrizzatura (prima del fondo)
- Applicazione primer/fondo
- Verniciatura completata

POST-REPAIR (consegna)
- Stesso set di 8 scatti walk-around del pre-intake
- Close-up zone riparate (abbinamento colore, allineamento pannelli)
- Interni (pulizia, nessun danno accidentale)

LIGHTING STANDARD:
- Luce diffusa naturale o softbox laterale — evitare luce solare diretta (riflessi)
- Per close-up ammaccature: luce radente laterale (evidenzia la profondità)
- Per verniciatura: luce ambientale uniforme (mostra il finish del colore)
```

### 4.4 Gap vs Competitor — PMI Italiane

| Area | Standard World-Class | Gap PMI Italia |
|------|---------------------|----------------|
| **DVI integrata** | Mitchell1/Shop-Ware: ispezione digitale con foto da tablet direttamente in OdL | Carrozzerie italiane: rullino fotografico su WhatsApp, nessun protocollo |
| **Customer approval digitale** | Cliente approva/rifiuta lavori da link SMS in real-time | Approvazione telefonica o di persona |
| **Foto annotate** | Cerchi e frecce su foto per spiegare il danno al cliente | Screenshot senza annotazioni |
| **Pre/post confronto automatico** | Software abbina automaticamente foto intake con post-repair | Confronto manuale, spesso non fatto |
| **Tracciabilità ricambi** | Foto ricambi con codice OEM per assicurazione | Scontrini cartacei |
| **Protezione legale** | Walk-around documentato protegge shop da claim danni pre-esistenti | Assenza documentazione genera dispute frequenti |
| **Integrazione assicurativa** | CCC ONE: foto vanno direttamente al perito assicurativo via piattaforma | Email con PDF, foto allegati pesanti |

### 4.5 Prompt FLUX — Veicoli / Officina

```json
{
  "id": "vehicle_001",
  "verticale": "veicoli_officina",
  "categoria": "damage_documentation_front",
  "prompt": "Professional vehicle damage documentation photo, silver sedan front-right 45 degree angle, visible front bumper damage and crumpled hood after collision, auto body shop intake photography, bright overcast daylight or diffused workshop lighting, clean concrete floor, technical documentation style, sharp focus across full vehicle, realistic automotive photography",
  "negative_prompt": "cartoon, dramatic shadows, studio glamour, blurry, unrealistic damage, burning fire effects, dark background, text, watermark",
  "uso": "Scheda veicolo tab Foto — walk-around pre-intake angolo anteriore destro"
}
```

```json
{
  "id": "vehicle_002",
  "verticale": "veicoli_officina",
  "categoria": "damage_closeup",
  "prompt": "Close-up vehicle damage documentation, perpendicular straight-on view of rear quarter panel dent and scratch, measuring tape placed beside damage for scale reference, auto body shop documentation, diffused workshop lighting showing dent depth, technical collision repair photography, high detail, no distortion",
  "negative_prompt": "cartoon, artistic bokeh, dramatic lighting, blurry damage area, angled distortion, reflective glare obscuring damage, text, watermark",
  "uso": "Scheda veicolo tab Foto — close-up danno con riferimento metrico"
}
```

```json
{
  "id": "vehicle_003",
  "verticale": "veicoli_officina",
  "categoria": "engine_underhood",
  "prompt": "Vehicle underhood inspection documentation photo, car hood open showing engine bay, technician visible on right side of frame examining engine with flashlight, modern auto workshop with overhead lighting, professional workshop environment, technical inspection photography, sharp detail across engine bay, realistic automotive documentation",
  "negative_prompt": "cartoon, dark unclear photo, greasy dramatic style, blurry, artistic lighting, text, watermark",
  "uso": "Scheda veicolo tab Foto — ispezione vano motore"
}
```

```json
{
  "id": "vehicle_004",
  "verticale": "veicoli_officina",
  "categoria": "repair_progress",
  "prompt": "Auto body repair progress documentation, technician in grey coveralls using pneumatic sanding tool on car body panel, auto body shop environment, red vehicle with visible primer grey patches where repair in progress, bright workshop fluorescent lighting, professional realistic workshop photography, technical progress documentation",
  "negative_prompt": "cartoon, anime, sparks flying dramatically, dangerous unsafe posture, blurry, dark, text, watermark, artistic composition",
  "uso": "Scheda veicolo tab Media — foto progress lavorazione carrozzeria"
}
```

```json
{
  "id": "vehicle_005",
  "verticale": "veicoli_officina",
  "categoria": "before_after_repair",
  "prompt": "Vehicle collision repair before and after comparison, same silver SUV rear quarter panel, left panel BEFORE showing deep dent and paint scratch, right panel AFTER showing perfect repair with matching paint, identical 45 degree angle both panels, professional workshop exterior lighting, automotive repair quality documentation, realistic photography",
  "negative_prompt": "cartoon, different lighting between panels, unrealistic perfect reflection, different angle panels, artistic filter, text heavy, watermark",
  "uso": "Report lavorazione completata — confronto danno prima/dopo riparazione"
}
```

```json
{
  "id": "vehicle_006",
  "verticale": "veicoli_officina",
  "categoria": "post_repair_delivery",
  "prompt": "Newly repaired car ready for customer delivery, clean white sedan, professional auto body shop exterior, front-left 45 degree angle, vehicle freshly washed and polished, perfect panel alignment visible, bright daylight, professional automotive photography, quality control documentation style, sharp and clean",
  "negative_prompt": "cartoon, dirty background, cluttered shop, dramatic shadows, blurry, artistic style, text, watermark",
  "uso": "Scheda veicolo tab Foto — walk-around post-riparazione consegna cliente"
}
```

```json
{
  "id": "vehicle_007",
  "verticale": "veicoli_officina",
  "categoria": "vin_documentation",
  "prompt": "Close-up documentation photo of vehicle VIN plate on driver door jamb, sharp macro focus on VIN number plate, clean detail visible, car door open showing door jamb, neutral natural light, technical vehicle documentation photography, no artistic effects, flat clear documentation style",
  "negative_prompt": "cartoon, blurry VIN, dark exposure, artistic bokeh background, angled distortion, glare obscuring numbers, text overlay, watermark",
  "uso": "Scheda veicolo tab Dati — foto documentazione numero telaio VIN"
}
```

```json
{
  "id": "vehicle_008",
  "verticale": "veicoli_officina",
  "categoria": "dashboard_inspection",
  "prompt": "Vehicle interior dashboard documentation photo, close-up of car instrument cluster and infotainment screen, driver seat perspective, showing mileage odometer reading clearly, dashboard warning lights visible, realistic automotive interior photography, bright interior lighting, technical intake documentation style, no glare on screen",
  "negative_prompt": "cartoon, blurry display, dark exposure, dramatic shadows, artistic framing, glare obscuring odometer, text, watermark",
  "uso": "Scheda veicolo tab Foto — documentazione cruscotto: km + spie warning"
}
```

---

## RIEPILOGO STRATEGICO — GAP ANALYSIS MERCATO ITALIANO PMI

### Patologia comune a tutti e 4 i verticali

Le PMI italiane nei 4 verticali condividono lo stesso pattern di sottoutilizzo della documentazione fotografica:

1. **Nessun protocollo codificato**: la fotografia è occasionale, non sistematica
2. **Storage non strutturato**: foto in galleria smartphone, WhatsApp, cartelle desktop non indicizzate
3. **Zero integrazione con il gestionale**: foto separate dal record del cliente/paziente/veicolo
4. **Qualità inconsistente**: nessun standard di illuminazione, angolazione, sfondo
5. **Nessun confronto strutturato**: before/after fatto mentalmente o con collage manuali
6. **Problema GDPR ignorato**: foto pazienti su dispositivi personali senza consenso
7. **Zero valorizzazione commerciale**: le foto non vengono usate per presentazioni preventivi, marketing, o fidelizzazione

### Opportunità per FLUXION

FLUXION può differenziarsi **non solo come repository fotografico**, ma come:
- **Guida fotografica integrata**: checklist in-app che guida il professionista negli scatti corretti (come Trainerize o Mitchell1)
- **Template per angolazioni**: overlay guida nell'app fotocamera
- **Confronto automatico before/after**: abbinamento temporale automatico
- **Report visuale per il cliente**: export PDF o link condivisibile con le foto del servizio
- **Firma digitale + consenso GDPR** contestuale alla prima foto del paziente/cliente

---

## NOTE PER IL NOTEBOOK KAGGLE — GENERAZIONE IMMAGINI

### Setup consigliato per FLUX

- **Modello**: FLUX.1-dev o FLUX.1-schnell per prototipazione veloce, FLUX.1-pro per qualità massima
- **Dimensioni consigliate**: 1024x1024 (quadrato) per progress/comparison; 1216x832 (landscape) per vehicle walk-around; 832x1216 (portrait) per fitness/physio
- **Steps**: 20-30 per schnell, 30-50 per dev
- **Guidance scale**: 3.5-4.5 (FLUX è ottimizzato per guidance bassa, al contrario di SD)
- **Seed fisso**: usare stesso seed per before/after dello stesso soggetto → maggiore consistenza

### Strategie di prompting per FLUX

1. **Specificità tecnica** prima di aggettivi qualitativi: "ring flash dental photography" > "well-lit dental photo"
2. **Stile fotografico esplicito**: sempre specificare "realistic photography", "documentation style", "medical/clinical/automotive photography"
3. **NO MAGIC WORDS**: FLUX non ha bisogno di "masterpiece, best quality, 8k" come SD1.5 — anzi penalizza prompt troppo gonfiati
4. **Negative prompt leggero**: FLUX risponde meno ai negative prompt che SD/SDXL — tenerli corti e specifici
5. **Consistenza personaggio**: per before/after stesso soggetto, usare img2img o ControlNet reference piuttosto che solo prompt

---

*Ricerca completata: 2026-03-07 | Fonte: WebSearch benchmark competitor + letteratura clinica + guide fotografiche professionali*
