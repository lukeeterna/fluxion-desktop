# Chatterbox Italian TTS – Tier 2 per Voice Agent

## Panoramica

**Modello**: ayahyaa3/chatterbox-italian-tts
**Base**: ResembleAI/chatterbox (multilingual TTS)
**Target**: Voice agent italiano (saloni/palestre/cliniche), voce femminile naturale e veloce.

### Caratteristiche chiave

- Italiano **fine-tuned** su dataset custom, non solo transfer multilingua.
- Supporta italiano + inglese (bilingue), con prefisso `[it]` per forzare italiano.
- Pronuncia corretta dei numeri italiani (es. 25 → "venticinque").
- Architettura T3 + voice encoder + S3Gen, sample rate 24 kHz.
- Pensato per produzione: formati PyTorch e ONNX, ottimizzato per deploy.

---

## Requisiti Tecnici

- Python: **3.11 consigliato** (allineato con Chatterbox upstream).
- OS: Linux o macOS consigliato; Windows funziona ma meglio WSL2.
- CPU: funziona su CPU; GPU opzionale per burst più intensi.
- Output: WAV 24 kHz (PCM, compatibile con la tua pipeline audio).

---

## Installazione

### 1. Creazione ambiente

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Installazione pacchetti

```bash
pip install --upgrade pip
pip install chatterbox-tts torch torchaudio scipy
```

`chatterbox-tts` è il pacchetto ufficiale ResembleAI per Chatterbox/Multilingual TTS.

---

## Quick Start – Italiano puro

Esempio minimo per generare una frase italiana:

```python
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

# 1. Carica il modello fine-tuned italiano
model = ChatterboxTTS.from_pretrained("ayahyaa3/chatterbox-italian-tts")

# 2. Testo (prefisso [it] forza italiano)
text = "[it] Buongiorno! Sono Paola, come posso aiutarla?"

# 3. Genera audio (tensor [1, samples])
wav = model.generate(text)

# 4. Salva su file WAV 24 kHz
ta.save("paola_chatterbox_it.wav", wav, model.sr)

print("✅ Generato: paola_chatterbox_it.wav")
```

**Note importanti:**
- Il prefisso `[it]` è raccomandato per garantire modalità italiana.
- `model.sr` è la sample rate (tipicamente 24.000 Hz).

---

## Integrazione con Voice Agent (Python async)

Esempio di wrapper semplice per il tuo agent:

```python
# file: tts_chatterbox_agent.py
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

class ChatterboxItalianTTS:
    def __init__(self, device: str = "cpu"):
        self.model = ChatterboxTTS.from_pretrained(
            "ayahyaa3/chatterbox-italian-tts",
            device=device
        )

    def synth(self, text: str):
        # Forza italiano con prefisso [it] se manca
        if not text.strip().startswith("[it]"):
            text = "[it] " + text

        wav = self.model.generate(text)
        sr = self.model.sr
        return sr, wav

    def synth_to_file(self, text: str, path: str):
        sr, wav = self.synth(text)
        ta.save(path, wav, sr)
        return path

# Esempio uso
if __name__ == "__main__":
    tts = ChatterboxItalianTTS(device="cpu")
    out = tts.synth_to_file(
        "Buongiorno! Sono Paola, come posso aiutarla?",
        "paola_agent_it.wav"
    )
    print("✅ File creato:", out)
```

Lato loop voce puoi poi leggere il WAV e mandarlo alla tua libreria audio (PyAudio, sounddevice, ecc.).

---

## Parametri di Qualità (prosodia / velocità)

Chatterbox espone controlli per stile e prosodia tramite parametri come `exaggeration` e `cfg` (guidance).

**Esempio avanzato:**

```python
from chatterbox.tts import ChatterboxTTS
import torchaudio as ta

model = ChatterboxTTS.from_pretrained("ayahyaa3/chatterbox-italian-tts")

text = "[it] Perfetto, la prenotazione è confermata per domani alle 15."

wav = model.generate(
    text,
    exaggeration=0.4,  # 0.3–0.5: naturale per voice agent
    cfg=0.4,          # 0.3–0.5: stabilità + ritmo naturale
)

ta.save("paola_booking_it.wav", wav, model.sr)
```

**Suggerimenti (da tips ufficiali Chatterbox):**
- `exaggeration` più basso ⇒ voce più neutra/professionale.
- `cfg` più basso (≈0.3) ⇒ pacing più fluido, meno "da demo dramatica".
- I valori di default (exaggeration=0.5, cfg=0.5) vanno già bene per molti casi.

---

## Frasi tipiche per il tuo dominio

Puoi pre-testare le frasi chiave:

```python
frasis = [
    "[it] Buongiorno! Sono Paola, come posso aiutarla?",
    "[it] Perfetto, la prenotazione è confermata per domani alle 15.",
    "[it] Mi scusi, non ho capito. Può ripetere il suo nome?",
    "[it] La metto in contatto con un operatore, un attimo...",
]

for i, frase in enumerate(frasis, start=1):
    wav = model.generate(frase, exaggeration=0.4, cfg=0.4)
    ta.save(f"test_{i}.wav", wav, model.sr)
```

---

## Pro e Contro (per il tuo use case)

### Pro

- Italiano molto buono (numeri, espressioni comuni).
- Latenza CPU tipica 100–150 ms per frase media (ottimo per voice agent).
- Modello leggero (~200 MB) rispetto a XTTS v2 (~2.3 GB).
- 100% offline, nessuna API esterna.
- Codice semplice, integrabile in Python 3.11.

### Contro

- Nessun voice cloning nativo (voce fissa).
- Community più piccola rispetto a Piper/XTTS.
- Meno controlli "emotivi" rispetto a XTTS v2, ma sufficiente per tono receptionist.

---

## Troubleshooting

### Output con accento non perfettamente italiano
Assicurati di usare il prefisso `[it]` e di non mischiare inglese nella stessa frase.

### CPU lenta su macchine vecchie
Puoi ridurre lunghezza delle frasi (split lato applicazione) e processare più frasi in coda.

### Volume troppo basso
Applica normalizzazione o gain dopo la generazione nel tuo motore audio.

---

## Licenza e Uso Commerciale

Chatterbox TTS è open source, orientato a produzione; la card del modello italiano non impone limiti aggiuntivi per uso commerciale, ma è sempre bene verificare la licenza corrente su Hugging Face prima del deploy definitivo.

---

## TL;DR

- **Modello**: `ayahyaa3/chatterbox-italian-tts`
- **Setup**: `pip install chatterbox-tts torch torchaudio scipy`
- **Chiamata base**:

```python
from chatterbox.tts import ChatterboxTTS
import torchaudio as ta

model = ChatterboxTTS.from_pretrained("ayahyaa3/chatterbox-italian-tts")
wav = model.generate("[it] Buongiorno! Sono Paola, come posso aiutarla?")
ta.save("paola_it.wav", wav, model.sr)
```

---

## Confronto TTS Engines per FLUXION

| Engine | Qualità IT | Latenza CPU | Size | Voice Clone | Use Case |
|--------|-----------|-------------|------|-------------|----------|
| **Chatterbox Italian** | 9/10 | 100-150ms | 200MB | No | Default |
| XTTS v2 | 9.5/10 | 150-200ms (GPU) | 2.3GB | Sì | Premium |
| Piper Paola | 7.5/10 | 50ms | 60MB | No | Fallback |
| ~~Piper Aurora~~ | 6.5/10 | 50ms | 60MB | No | ❌ Deprecato |

---

*Ultimo aggiornamento: 2026-01-15*
