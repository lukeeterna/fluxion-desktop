# FLUXION Video V7 — "Come Ho Fatto Senza?"
## Proposta Storyboard per Approvazione Fondatore

**Target**: 4:45-5:15 | 1280x720 | H.264+AAC | PAS Formula
**Narrator**: Sara (IsabellaNeural -5%) | Cliente (DiegoNeural)

---

## PRINCIPI CREATIVI V7 (cosa cambia da V6)

| Problema V6 | Soluzione V7 |
|-------------|-------------|
| Clip AI ripetute (V10, V12 x2-3) | ZERO ripetizioni — tutte le clip usate una volta |
| Screenshot statici troppo lunghi (35s) | Max 12s per screenshot, break AI ogni 10-12s |
| Numeri solo nel voiceover | **Numeri animati a schermo** (bold, overlay scuro, fade-in) |
| Solo "odontoiatra" | **Tutte e 3**: scheda medica + odontoiatrica + fisioterapia |
| Media upload assente | Sezione dedicata con 21-trasformazioni-prima-dopo.png |
| Dialogo 35s su immagine fissa | **Sara ha un VOLTO** — clip Veo3 donna italiana, dialogo visivo reale |
| 5 clip inutilizzate | Tutte le 18+ clip distribuite con logica |
| Video troppo statico | Mai piu' di 12s senza cambio visivo. Ritmo cinematografico. |

---

## NUMERI ANIMATI — Design

Overlay semi-trasparente sulla clip AI corrente:
- Banda scura (rgba 0,0,0,0.65) nel terzo inferiore del frame
- Testo bianco grande, font Impact/bold, ombra leggera
- Animazione: fade-in 0.3s + leggero scale (95% -> 100%)
- Durata a schermo: 2.5s per numero
- Usati in: CH2 (problema) e CH9 (prezzo)

---

## CLIP VEO3 — Allocazione completa (23 clip: 18 esistenti + 5 nuove)

### Clip esistenti

| Clip | Dove usata | Trim | Ruolo |
|------|-----------|------|-------|
| V01_salone | CH5 intro parrucchiere | 4-8s | "Sei parrucchiere?" |
| V02_officina | CH5 intro officina | 4-8s | "Hai un'officina?" |
| V03_dentista | CH5 intro dentista | 4-8s | "Dentista?" |
| V04_palestra | CH1 hook | 0-2s | Montaggio rapido |
| V05_estetista | CH1 hook | 0-2s | Montaggio rapido |
| V06_nails | CH1 hook | 0-2s | Mani occupate nail art |
| V07_fisioterapista | CH5 intro fisioterapista | 3-7s | "Fisioterapista?" |
| V08_gommista | CH1 hook | 0-2s | Montaggio rapido |
| V09_elettrauto | CH2 problema | 3-8s | Numero "EUR900/mese" |
| V10_frustrazione | CH2 problema | 0-8s | Numeri "250 clienti" |
| V11_qrcode | CH7 fidelizzazione | 0-5s | QR code |
| V12_soddisfatta | CH9 prezzo | 0-8s | Numeri prezzo |
| V13_finale | CH10 chiusura | 0-8s | CTA finale |
| V6-03_proprietario | CH3 post-dialogo | 0-6s | "Non e' un risponditore" |
| V6-04_cliente_wa | CH7 visual break | 0-4s | Mani su WhatsApp |
| V6-05_imprenditrice | CH4 (0-3s) + CH8 (3-7s) | trim diversi | Visual break gestionale |
| V6-11_salone_sereno | CH9 prezzo Sara | 0-5s | Upsell Pro |
| V6-13_hook_missed | CH2 problema inizio | 0-8s | Chiamate perse |

### Clip NUOVE da generare (5)

**V16_sara_intro** — IL VOLTO DI SARA
```
Prompt: "Beautiful Italian woman in her early 30s, warm brown eyes,
dark wavy hair, wearing a sleek professional headset with microphone,
sitting at a modern minimalist desk, looking directly at camera with
a warm confident smile, modern office with soft plants and natural light,
warm golden Mediterranean lighting, cinematic documentary, shallow depth of field"
```
Uso: CH3 scena 09 — Sara si presenta ("Mi chiamo Sara")

**V17_sara_dialogo** — SARA CHE PARLA
```
Prompt: "Beautiful Italian woman in her early 30s with professional headset,
actively speaking on a call with natural expressions, gesturing gently with one hand,
nodding and smiling, same modern office setting, warm golden lighting,
close-up medium shot, cinematic documentary style, natural and engaging"
```
Uso: CH3 scene 11+13 — Sara risponde al cliente (alternanza visiva)

**V14_medico_paziente** — MEDICO IMPEGNATO CON PAZIENTE
```
Prompt: (vedi sezione CLIP VEO3 DA GENERARE — medico che visita paziente, mani occupate, telefono che squilla sullo sfondo)
```
Uso: CH5 scena 22 — "Uno studio medico?"

**V15_foto_portfolio** — MEDIA UPLOAD
```
Prompt: "Close-up of woman's hands scrolling through a photo gallery on a modern
tablet showing before and after beauty treatment results, warm golden ambient light,
hair salon interior with soft bokeh in background, gentle movements,
cinematic documentary style"
```
Uso: CH6 scena 25 — intro portfolio/prima-dopo

---

## STORYBOARD SCENA PER SCENA

### CH1: La Tua Giornata (0:00-0:08) — 4 verticali in 8s
> Montaggio rapido. ZERO voiceover. Solo musica energica. Il viewer si riconosce.

| # | Clip | Trim | VO | Transition | Musica |
|---|------|------|----|-----------|--------|
| 01 | V04_palestra | 0-2s | — | cut | 0.30 |
| 02 | V08_gommista | 0-2s | — | cut | 0.30 |
| 03 | V05_estetista | 0-2s | — | cut | 0.30 |
| 04 | V06_nails | 0-2s | — | cut | 0.30 |

> 4 verticali diverse (palestra, auto, beauty, nails). Ritmo: BAM-BAM-BAM-BAM. Tutte mani occupate.

---

### CH2: Il Problema (0:08-0:45) — frustrazione + NUMERI ANIMATI
> Il viewer sente il dolore. I numeri rendono il problema TANGIBILE e VISCERALE.

| # | Clip | Trim | VO | Overlay animato | Transition |
|---|------|------|----|----------------|-----------|
| 05 | V6-13_hook_missed | 0-8s | "Tu lo sai com'e'. Sei li' che lavori. Le mani occupate. E il telefono squilla. Squilla ancora." | — | crossfade 1.0s |
| 06 | V10_frustrazione | 0-8s | "Un cliente perso al giorno sono duecentocinquanta clienti all'anno. A trenta euro di media: settemilacinquecento euro." | **"250 clienti persi"** (2.5s) poi **"EUR 7.500 / anno"** (2.5s) | crossfade 0.8s |
| 07 | V09_elettrauto | 3-8s | "E una segretaria? Novecento euro al mese. Ogni mese." | **"EUR 900 / mese"** (2.5s) | crossfade 0.8s |

> V6-13 usata per intero (0-8s) solo qui. In CH1 ora c'e' V06_nails al suo posto.

---

### CH3: Ti Presento Sara (0:45-1:55) — SARA HA UN VOLTO + dialogo dinamico
> La svolta emotiva. Sara ha un viso: bellissima, calda, rassicurante, professionale.
> Il dialogo ALTERNA visivamente il volto di Sara (V16/V17) e il cliente (V6-04).
> Lo spettatore VEDE due persone che parlano. Non uno screenshot fisso.

| # | Tipo | Source | VO | Dur | Transition |
|---|------|--------|----|-----|-----------|
| 08 | clip AI | **V16_sara_intro** (0-8s) | "E se ti dicessi che c'e' qualcuno che risponde per te? Sempre. Anche di notte. Anche di domenica." | ~8s | crossfade 0.8s |
| 09 | screenshot | 08-voice.png | "Mi chiamo Sara. Sono la tua assistente vocale. Parlo italiano, capisco cosa vogliono i tuoi clienti, e prenoto per loro." | ~10s | crossfade 0.6s |
| 10 | clip AI | **V18_cliente_telefono** (0-4s) | Cliente (Diego): "Buongiorno, vorrei prenotare un taglio per domani mattina." | ~3s | cut |
| 11 | clip AI | **V17_sara_dialogo** (0-4s) | Sara: "Buongiorno Marco! L'ultima volta taglio e barba con Roberto — vuole ripetere?" | ~5s | cut |
| 12 | clip AI | **V18_cliente_telefono** (4-7s) | Cliente: "Si', perfetto!" | ~2s | cut |
| 13 | clip AI | **V17_sara_dialogo** (4-8s) | Sara: "Roberto e' disponibile domani alle dieci e trenta. Prenotato! Le mando conferma su WhatsApp." | ~5s | crossfade 0.8s |
| 14 | clip AI | V6-03_proprietario (0-6s) | "Non e' un risponditore automatico. Sara conosce i tuoi clienti. Il nome, l'ultimo servizio, le preferenze." | ~12s | crossfade 1.0s |

> **Effetto**: Il viewer vede Sara "parlare" in V16/V17, poi il cliente in V6-04.
> Il ping-pong visivo crea l'illusione di un dialogo reale.
> Lo screenshot 08-voice.png (scena 09) mostra l'interfaccia FLUXION — la "prova" che Sara e' software, non solo un video.

---

### CH4: Tutto in un Colpo d'Occhio (1:55-2:25) — dashboard + calendario
> Sezione gestionale core. Ritmo: screenshot → break AI → screenshot.

| # | Tipo | Source | VO | Dur | Transition |
|---|------|--------|----|-----|-----------|
| 15 | screenshot | 01-dashboard.png | "Appena apri FLUXION, vedi tutto. Appuntamenti di oggi, clienti del mese, fatturato, il servizio piu' richiesto. Chiaro, in italiano." | ~12s | crossfade 0.6s |
| 16 | clip AI | V6-05_imprenditrice (0-3s) | — (visual break, musica) | 3s | cut |
| 17 | screenshot | 02-calendario.png | "Il calendario. Un nuovo appuntamento in due click. Il promemoria WhatsApp parte da solo ventiquattro ore prima." | ~10s | crossfade 0.6s |

---

### CH5: La Scheda Per la Tua Attivita' (2:25-3:30) — 5 schede verticali + selector
> Pattern: clip intro settore (3-4s) → screenshot scheda (10s). Ritmo incalzante.
> TUTTE le schede sanitarie mostrate: medica generica + odontoiatrica + fisioterapia.

| # | Tipo | Source | VO | Dur | Transition |
|---|------|--------|----|-----|-----------|
| 18 | clip AI | V01_salone (4-8s) | "Sei parrucchiere?" | ~2s VO, 4s clip | cut 0.3s |
| 19 | screenshot | 12-scheda-parrucchiere.png | "Tipo di capello, colore preferito, allergie ai prodotti. La prossima volta non chiedi — sai gia'." | ~10s | crossfade 0.6s |
| 20 | clip AI | V02_officina (4-8s) | "Hai un'officina?" | ~2s VO, 4s clip | cut 0.3s |
| 21 | screenshot | 18-scheda-veicoli.png | "Targa, marca, modello, tagliandi, scadenza revisione e assicurazione. Sara salva tutto." | ~10s | crossfade 0.6s |
| 22 | clip AI | **V14_medico_paziente** (0-4s) | "Uno studio medico?" | ~2s VO, 4s clip | cut 0.3s |
| 23 | screenshot | 15-scheda-medica.png | "Anamnesi completa. Allergie, farmaci in corso, piano terapeutico. Dal medico di base allo specialista — tutto in una scheda." | ~10s | crossfade 0.6s |
| 24 | clip AI | V03_dentista (4-8s) | "Dentista?" | ~2s VO, 4s clip | cut 0.3s |
| 25 | screenshot | 17-scheda-odontoiatrica.png | "Odontogramma digitale, storia clinica, abitudini igieniche. Sara sa che il paziente e' allergico al lattice prima ancora che si sieda." | ~10s | crossfade 0.6s |
| 26 | clip AI | V07_fisioterapista (3-7s) | "Fisioterapista?" | ~2s VO, 4s clip | cut 0.3s |
| 27 | screenshot | 16-scheda-fisioterapia.png | "Diagnosi, sedute completate, scala del dolore, progressi nel tempo. Sai esattamente a che punto e' il percorso riabilitativo." | ~10s | crossfade 0.6s |
| 28 | screenshot | 20-scheda-selector.png | "Estetica, palestra, carrozzeria... qualunque sia la tua attivita', FLUXION ha la scheda giusta." | ~5s | crossfade 0.6s |

> **5 schede mostrate**: parrucchiere, veicoli, medica generica, odontoiatrica, fisioterapia
> **Poi selector**: mostra che ce ne sono ancora altre (iceberg effect)
> Ritmo: clip 4s → screenshot 10s → clip 4s → screenshot 10s (mai noioso)

---

### CH6: Cattura i Momenti (3:30-3:50) — media upload + prima/dopo
> Feature differenziante. Nessun competitor PMI ha portfolio integrato.

| # | Tipo | Source | VO | Dur | Transition |
|---|------|--------|----|-----|-----------|
| 29 | clip AI | **V15_foto_portfolio** (0-5s) | "I risultati del tuo lavoro meritano di essere visti." | ~4s VO, 5s clip | crossfade 0.8s |
| 30 | screenshot | 21-trasformazioni-prima-dopo.png | "Foto prima e dopo, galleria lavori, il portfolio della tua attivita'. I clienti lo vedono. E tornano." | ~8s | crossfade 0.6s |

> **Nota**: V15 mostra mani che sfogliano portfolio su tablet. Se non generata, fallback V06_nails (3-7s).

---

### CH7: Fidelizza Senza Rincorrere (3:50-4:10) — QR + pacchetti
> Il cliente paga e torna. Feature chiave per upsell Base → Pro.

| # | Tipo | Source | VO | Dur | Transition |
|---|------|--------|----|-----|-----------|
| 31 | clip AI | V11_qrcode (0-5s) | "Il QR code sul bancone. Il cliente lo scansiona e resta in contatto con te." | ~5s | cut |
| 32 | clip AI | V6-04_cliente_wa (0-4s) | — (visual break: mani su WhatsApp, notifica conferma) | 4s | crossfade 0.5s |
| 33 | screenshot | 22-pacchetti.png | "Pacchetti fedelta'. Cinque sedute colore a prezzo scontato. Il cliente paga oggi e torna sempre. Sara propone il pacchetto al momento giusto." | ~10s | crossfade 0.8s |

---

### CH8: Gestione Completa (4:10-4:25) — cassa + analytics
> FLUXION non e' solo calendario. E' gestionale completo.

| # | Tipo | Source | VO | Dur | Transition |
|---|------|--------|----|-----|-----------|
| 34 | screenshot | 07-cassa.png | "La cassa. Quanto hai incassato oggi. Contanti, carte, Satispay. Ogni euro tracciato." | ~8s | crossfade 0.5s |
| 35 | clip AI | V6-05_imprenditrice (3-7s) | — (visual break: imprenditrice serena che guarda lo schermo, concentrata e soddisfatta) | 4s | cut |
| 36 | screenshot | 10-analytics.png | "Fatturato mensile, top servizi, classifica operatori. Senza fogli Excel." | ~7s | crossfade 0.6s |

---

### CH9: Quanto Costa Non Averlo (4:25-5:00) — NUMERI ANIMATI prezzo
> Loss framing. I numeri animati rendono il confronto VISCERALE.

| # | Tipo | Source | VO | Overlay animato | Dur |
|---|------|--------|----|----------------|-----|
| 37 | clip AI | V12_soddisfatta (loop) | "Facciamo due conti. Un gestionale in abbonamento ti costa centoventi euro al mese. Ogni mese. Per sempre. In tre anni: quattromilatrecentoventi euro. E non e' mai tuo. Se smetti di pagare, perdi tutto." | **"EUR 120 / mese"** (2.5s) → **"EUR 4.320 in 3 anni"** (2.5s) → **"MAI TUO."** (2s, rosso) | ~22s |
| 38 | clip AI | V6-11_salone_sereno (loop) | "FLUXION costa quattrocentonovantasette euro. Una volta sola. Per sempre tuo. Vuoi anche Sara? Ottocentonovantasette euro. Si ripaga in tre settimane." | **"EUR 497 — UNA VOLTA. PER SEMPRE."** (3s, verde/teal) → **"+ Sara: EUR 897"** (2s) | ~13s |

> I numeri COMPAIONO a schermo in sincrono col voiceover.
> "MAI TUO" in rosso per loss framing. "UNA VOLTA. PER SEMPRE." in teal FLUXION per gain framing.

---

### CH10: Come Ho Fatto Senza? (5:00-5:20) — CTA + endcard
> Chiusura emotiva. Garanzia. La domanda del titolo come ultima frase.

| # | Tipo | Source | VO | Dur | Transition |
|---|------|--------|----|-----|-----------|
| 39 | clip AI | V13_finale (loop) | "Parrucchieri, officine, dentisti, fisioterapisti, centri estetici, palestre. Non importa qual e' la tua attivita'. FLUXION e' il partner che ti mancava. Trenta giorni soddisfatti o rimborsati." | ~15s | crossfade 1.2s |
| 40 | clip AI | V16_sara_intro (4-8s) | "FLUXION. Paghi una volta. Usi per sempre. E ti chiederai... come ho fatto senza?" | ~8s | crossfade 1.5s |
| 41 | endcard | endcard-animated.mp4 | — | 5s | fade_to_black 2.0s |

> Scena 39: Sara chiude il video col suo volto. Chiusura circolare (Sara apre CH3, Sara chiude CH10).

---

## RIEPILOGO

| Metrica | V6 | V7 |
|---------|----|----|
| Scene totali | 27 | **41** |
| Durata stimata | 5:53 | **5:00-5:20** |
| Clip AI usate | 8/18 | **23/23 (tutte)** |
| Clip ripetute | 3 | **0** |
| Screenshot max consecutivi | 3 | **1** |
| Numeri animati | 0 | **6** |
| Feature mostrate | 8 | **12** |
| Schede sanitarie | 0 | **3** (medica + odontoiatrica + fisioterapia) |
| Sara ha un volto | No | **Si' (2 clip Veo3 dedicate)** |
| Media upload | No | **Si'** |
| Clip Veo3 nuove | 0 | **5** (Sara + Cliente + Medico + Portfolio) |

### Feature coperte nel video (12):
1. Dashboard (CH4)
2. Calendario + WhatsApp reminder (CH4)
3. Sara voice agent + dialogo (CH3)
4. Scheda parrucchiere (CH5)
5. Scheda veicoli (CH5)
6. Scheda medica generica con anamnesi (CH5)
7. Scheda odontoiatrica con odontogramma (CH5)
8. Scheda fisioterapia con scala dolore (CH5)
9. Portfolio foto prima/dopo (CH6)
10. Pacchetti fedelta' (CH7)
11. Cassa (CH8)
12. Analytics (CH8)

---

## CLIP VEO3 DA GENERARE (4)

### V16_sara_intro — IL VOLTO DI SARA
```
Prompt: "Stunningly beautiful Italian woman in her early 30s, captivating warm brown eyes,
dark wavy hair falling softly past her shoulders, radiant olive skin,
wearing a sleek modern wireless headset, fitted elegant blouse in soft cream color,
sitting at a modern minimalist desk, looking directly at camera with a magnetic smile
that is simultaneously warm, confident, subtly alluring and deeply reassuring,
she radiates the energy of someone you instantly trust and want to talk to,
modern office with soft green plants and warm natural light streaming through sheer curtains,
golden hour Mediterranean lighting, cinematic documentary,
shallow depth of field, medium close-up shot, 4K quality"
```

### V17_sara_dialogo — SARA CHE PARLA AL TELEFONO
```
Prompt: "Same stunningly beautiful Italian woman with wireless headset,
actively speaking on a phone call with naturally expressive face,
her eyes light up as she recognizes the caller, warm genuine smile,
she gestures elegantly with one hand while speaking,
nodding reassuringly with perfect composure and warmth,
her manner is both professionally competent and personally caring,
same modern office with golden natural light,
close-up to medium shot, cinematic documentary style,
the viewer feels instantly reassured just watching her, 4K quality"
```

### V18_cliente_telefono — IL CLIENTE CHE CHIAMA
```
Prompt: "Handsome Italian man in his late 30s, well-groomed dark hair and short beard,
wearing a fitted casual blazer over a crisp white shirt, talking on his smartphone
with a slightly impatient but polite expression, he is busy and demanding but not rude,
standing in a bright modern Italian street or cafe terrace,
warm Mediterranean daylight, his expression gradually softens into a pleased smile
as he gets the answer he wanted, cinematic documentary style,
medium close-up shot, shallow depth of field, 4K quality"
```
Uso: CH3 scene 10+12 — Il cliente che chiama Sara (sostituisce V6-04_cliente_wa nel dialogo)

### V14_medico_paziente — MEDICO IMPEGNATO CON PAZIENTE
```
Prompt: "Interior of a modern Italian medical clinic, male doctor in white coat
carefully examining a patient sitting on the exam table, focused and attentive,
his hands are busy with the patient, a smartphone on the desk in the background
glows with an incoming call he cannot answer, warm natural light from large window,
clean professional environment, cinematic documentary, medium shot,
the scene conveys a doctor who is dedicated to his patient and cannot be interrupted"
```

### V15_foto_portfolio — PORTFOLIO PRIMA/DOPO
```
Prompt: "Close-up of woman's hands scrolling through a photo gallery on a modern
tablet showing before and after beauty treatment results,
warm golden ambient light, hair salon interior with soft bokeh in background,
gentle natural movements, cinematic documentary style"
```

**Tutti**: 8s | Senza audio generato (generateAudio=false) | 720p | ZERO "Kodak/film grain"

> **Sara e il Cliente sono i PERSONAGGI del video.**
> Sara: bellissima, sexy ma professionale, accogliente — il viewer la vuole come assistente.
> Cliente: bell'uomo esigente e indaffarato — il viewer si identifica.
> Il dialogo CH3 mostra Sara che rassicura il cliente con competenza e calore.
> Effetto: "Io voglio Sara nella mia attivita'."

---

## BUG FIX: Audio che salta dopo min 3

**Causa**: Sample rate mismatch nella concatenazione. Clip AI hanno audio diverso (o nessuno) vs voiceover 48kHz.
**Fix**: Nella fase normalize, forzare `-af aresample=48000` + `-ar 48000 -ac 2` su OGNI clip senza eccezione.

---

## APPROVAZIONE

- [ ] Struttura 10 capitoli OK
- [ ] Sara ha un volto (V16 + V17) OK
- [ ] Dialogo alternato Sara/Cliente OK
- [ ] 3 schede sanitarie (medica + odontoiatrica + fisioterapia) OK
- [ ] Numeri animati: design + colori OK
- [ ] Media upload portfolio (CH6) OK
- [ ] 4 clip Veo3 nuove: prompt OK
- [ ] Voiceover testi OK
- [ ] Durata target 5:00-5:20 OK
