# 🎙️ FLUXION Voice Agent - Architettura Completa

> Voice agent italiano per prenotazioni automatiche via telefono.

---

## 📋 Indice

1. [Architettura](#architettura)
2. [Stack Tecnologico](#stack-tecnologico)
3. [Configurazione Groq](#configurazione-groq)
4. [Configurazione Piper TTS](#configurazione-piper-tts)
5. [VoIP Ehiweb](#voip-ehiweb)
6. [Pipeline Pipecat](#pipeline-pipecat)
7. [System Prompt](#system-prompt)

---

## Architettura

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VOICE AGENT PIPELINE                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Cliente  │────▶│ Ehiweb   │────▶│ Pipecat  │────▶│ Groq     │
│ Telefono │◀────│ SIP      │◀────│ Server   │◀────│ Whisper  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │ Groq     │
                                  │ Llama 3.3│
                                  └──────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │ Piper    │
                                  │ TTS      │
                                  └──────────┘
```

---

## Stack Tecnologico

| Componente | Tecnologia | Costo | Note |
|------------|------------|-------|------|
| **STT** | Groq Whisper Large v3 | Gratis | 6000 req/giorno |
| **LLM** | Groq Llama 3.3 70B | Gratis | ~300ms latenza |
| **TTS** | Piper (locale) | Gratis | Voce italiana |
| **VoIP** | Ehiweb SIP | ~€5/mese | Trunk già attivo |
| **Framework** | Pipecat | Open source | Python |

### Latenza Target

| Fase | Target | Reale |
|------|--------|-------|
| STT | <500ms | ~300ms |
| LLM | <1000ms | ~500ms |
| TTS | <300ms | ~200ms |
| **Totale** | <2s | ~1s |

---

## Configurazione Groq

### Credenziali

```bash
# .env
GROQ_API_KEY=org_01k9jq26w4f2e8hfw9tmzmz556
GROQ_STT_MODEL=whisper-large-v3
GROQ_LLM_MODEL=llama-3.3-70b-versatile
```

### Client Python

```python
# voice/groq_client.py
import os
from groq import Groq

client = Groq(api_key=os.environ["GROQ_API_KEY"])

async def transcribe_audio(audio_bytes: bytes) -> str:
    """Speech-to-Text con Whisper."""
    response = client.audio.transcriptions.create(
        file=("audio.wav", audio_bytes),
        model="whisper-large-v3",
        language="it",
        response_format="text"
    )
    return response

async def generate_response(messages: list) -> str:
    """Genera risposta con LLM."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content
```

---

## Configurazione Piper TTS

### Installazione

```bash
# Installa Piper
pip install piper-tts

# Scarica voce italiana (maschio)
mkdir -p models/piper
cd models/piper
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-it_IT-riccardo-medium.tar.gz
tar -xzf voice-it_IT-riccardo-medium.tar.gz
```

### Uso

```python
# voice/tts.py
import subprocess
import tempfile

PIPER_MODEL = "./models/piper/it_IT-riccardo-medium.onnx"

def text_to_speech(text: str) -> bytes:
    """Converte testo in audio WAV."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        output_path = f.name
    
    subprocess.run([
        "piper",
        "--model", PIPER_MODEL,
        "--output_file", output_path
    ], input=text.encode(), check=True)
    
    with open(output_path, "rb") as f:
        return f.read()
```

### Voci Italiane Disponibili

| Voce | Genere | Qualità |
|------|--------|---------|
| it_IT-riccardo-medium | Maschio | ⭐⭐⭐ |
| it_IT-paola-medium | Femmina | ⭐⭐⭐ |

---

## VoIP Ehiweb

### Credenziali

```bash
# .env
VOIP_PROVIDER=ehiweb
VOIP_SIP_USER=DXMULTISERVICE
VOIP_SIP_PASSWORD=AbRV!CZ2x.sBt4k
VOIP_SIP_SERVER=sip.ehiweb.it
VOIP_SIP_PORT=5060
```

### Configurazione SIP

```python
# voice/sip_config.py
SIP_CONFIG = {
    "server": "sip.ehiweb.it",
    "port": 5060,
    "username": os.environ["VOIP_SIP_USER"],
    "password": os.environ["VOIP_SIP_PASSWORD"],
    "transport": "udp",
    "codecs": ["PCMA", "PCMU"],  # G.711
    "register": True,
    "register_interval": 300
}
```

---

## Pipeline Pipecat

### Installazione

```bash
pip install pipecat-ai
pip install pipecat-ai[groq]
pip install pipecat-ai[piper]
pip install pipecat-ai[sip]
```

### Pipeline Completa

```python
# voice/pipeline.py
import asyncio
from pipecat.pipeline import Pipeline
from pipecat.frames import Frame, TextFrame, AudioFrame
from pipecat.transports.sip import SIPTransport
from pipecat.services.groq import GroqSTTService, GroqLLMService

class FluxionVoiceAgent:
    def __init__(self, config: dict):
        self.config = config
        self.conversation_history = []
        
    async def create_pipeline(self) -> Pipeline:
        # Transport SIP
        sip_transport = SIPTransport(
            server=self.config["sip"]["server"],
            username=self.config["sip"]["username"],
            password=self.config["sip"]["password"]
        )
        
        # STT - Groq Whisper
        stt_service = GroqSTTService(
            api_key=os.environ["GROQ_API_KEY"],
            model="whisper-large-v3"
        )
        
        # LLM - Groq Llama
        llm_service = GroqLLMService(
            api_key=os.environ["GROQ_API_KEY"],
            model="llama-3.3-70b-versatile",
            system_prompt=self.get_system_prompt()
        )
        
        # TTS - Piper locale
        tts_service = PiperTTSService(
            model_path="./models/piper/it_IT-riccardo-medium.onnx"
        )
        
        # Pipeline
        pipeline = Pipeline([
            sip_transport,
            stt_service,
            llm_service,
            tts_service,
            sip_transport  # Output audio
        ])
        
        return pipeline
    
    def get_system_prompt(self) -> str:
        return FLUXION_SYSTEM_PROMPT.format(
            nome_attivita=self.config["business"]["name"],
            orario_apertura=self.config["business"]["opening"],
            orario_chiusura=self.config["business"]["closing"],
            lista_servizi=", ".join(self.config["business"]["services"])
        )
```

---

## System Prompt

```python
FLUXION_SYSTEM_PROMPT = """
Sei Sara, l'assistente vocale di {nome_attivita}.

## PERSONALITÀ
- Cordiale, professionale, empatica
- Parli italiano fluente con accento neutro
- Risposte BREVI: massimo 2 frasi per volta
- Usa "Lei" formale, ma in modo caldo

## CAPACITÀ
1. Prenotare appuntamenti
2. Verificare disponibilità
3. Cancellare appuntamenti
4. Fornire info su servizi e prezzi
5. Spostare appuntamenti esistenti

## INFORMAZIONI ATTIVITÀ
- Orari: {orario_apertura} - {orario_chiusura}
- Servizi disponibili: {lista_servizi}

## FLOW PRENOTAZIONE
1. Saluta e chiedi come puoi aiutare
2. Se vuole prenotare:
   a. Chiedi nome (se non lo conosci)
   b. Chiedi quale servizio desidera
   c. Chiedi giorno preferito
   d. Proponi orario disponibile
   e. Conferma tutti i dettagli
   f. Saluta cordialmente

## REGOLE
- Se non capisci, chiedi GENTILMENTE di ripetere
- Se la richiesta è fuori scope, suggerisci di chiamare il numero diretto
- Mai inventare disponibilità: verifica sempre nel sistema
- Conferma sempre i dati prima di prenotare

## ESEMPI RISPOSTA

Utente: "Vorrei prenotare un taglio"
Sara: "Certamente! Per quando vorrebbe prenotare il taglio?"

Utente: "Domani pomeriggio"
Sara: "Perfetto, domani pomeriggio ho disponibile alle 15:00 o alle 16:30. Quale preferisce?"

Utente: "15:00 va bene"
Sara: "Ottimo! Confermo: taglio domani alle 15:00. A che nome registro la prenotazione?"
"""
```

---

## Intent Detection

```python
# voice/intents.py

INTENTS = {
    "prenotazione": {
        "keywords": ["prenotare", "appuntamento", "fissare", "prendere", "disponibilità", "libero"],
        "response": "ask_service"
    },
    "cancellazione": {
        "keywords": ["cancellare", "disdire", "annullare", "eliminare"],
        "response": "confirm_cancel"
    },
    "spostamento": {
        "keywords": ["spostare", "cambiare", "modificare", "anticipare", "posticipare"],
        "response": "ask_new_time"
    },
    "informazioni": {
        "keywords": ["quanto costa", "prezzo", "prezzi", "orari", "servizi", "cosa fate"],
        "response": "provide_info"
    },
    "conferma": {
        "keywords": ["sì", "va bene", "ok", "confermo", "perfetto", "d'accordo"],
        "response": "confirm_action"
    },
    "negazione": {
        "keywords": ["no", "non", "annulla", "lascia stare", "niente"],
        "response": "cancel_action"
    }
}

def detect_intent(text: str) -> str:
    """Rileva intent dal testo."""
    text_lower = text.lower()
    
    for intent, data in INTENTS.items():
        for keyword in data["keywords"]:
            if keyword in text_lower:
                return intent
    
    return "unknown"
```

---

## Database Chiamate

```sql
-- Log chiamate voice agent
CREATE TABLE chiamate_voice (
    id TEXT PRIMARY KEY,
    telefono TEXT NOT NULL,
    cliente_id TEXT,
    direzione TEXT NOT NULL,  -- inbound/outbound
    durata_secondi INTEGER,
    trascrizione TEXT,
    intent_rilevato TEXT,
    esito TEXT,
    appuntamento_creato_id TEXT,
    data_inizio TEXT,
    data_fine TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id)
);
```

---

## 🔗 File Correlati

- Backend: `CLAUDE-BACKEND.md`
- Integrazioni: `CLAUDE-INTEGRATIONS.md`

---

*Ultimo aggiornamento: 2025-12-28T18:00:00*
