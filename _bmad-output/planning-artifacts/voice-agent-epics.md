---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-epic-design']
inputDocuments:
  - docs/PRD-VOICE-AGENT.md
  - docs/SARA-validation-report.md
  - docs/SARA-lifetime-spec.md
  - CLAUDE.md
  - voice-agent/docs/API.md
project_name: Voice Agent Sara
created: 2026-01-28
validation_source: Perplexity Research (1709 lines)
---

# Voice Agent Sara - Epic Breakdown

## Executive Summary

**Status**: Production validation (WIP)
**Current Issues**: 3 P0, 4 P1
**Current Metrics**: STT WER 21.7% (target <15%), Intent 85% (target >90%)
**Target Release**: v1.0 in 4 weeks

## Requirements Inventory

### Functional Requirements

| ID | Requirement | Source | Epic |
|----|-------------|--------|------|
| FR1 | Users can book appointment via voice in < 60 seconds (6-8 turns) | US-01 | E1 |
| FR2 | System searches client by name in DB | US-01 | E1 |
| FR3 | System creates booking record with `fonte_prenotazione='voice'` | US-01 | E1 |
| FR4 | New clients can register via voice conversation | US-02 | E2 |
| FR5 | System collects name, surname, phone for new registration | US-02 | E2 |
| FR6 | System disambiguates homonyms via birth date | US-03 | E3 |
| FR7 | System falls back to nickname if birth date fails | US-03 | E3 |
| FR8 | System falls back to phone as final disambiguation | US-03 | E3 |
| FR9 | Users can cancel appointments via voice | US-04 | E4 |
| FR10 | System calls `/api/appuntamenti/cancel` endpoint | US-04 | E4 |
| FR11 | Users can reschedule appointments via voice | US-05 | E4 |
| FR12 | System verifies availability before rescheduling | US-05 | E4 |
| FR13 | System answers FAQ questions (hours, prices, services) | US-06 | E5 |
| FR14 | System offers waitlist when slot unavailable | US-07 | E6 |
| FR15 | System creates waitlist record with priority | US-07 | E6 |

### Non-Functional Requirements

| ID | Requirement | Current | Target | Gap |
|----|-------------|---------|--------|-----|
| NFR1 | Intent classification latency | ~5ms | < 10ms | ✅ OK |
| NFR2 | Entity extraction latency | ~20ms | < 50ms | ✅ OK |
| NFR3 | HTTP Bridge lookup latency | ~300ms | < 500ms | ✅ OK |
| NFR4 | Groq LLM fallback latency | ~800ms | < 1000ms | ✅ OK |
| NFR5 | TTS synthesis latency | 150ms | < 500ms | ✅ OK |
| NFR6 | End-to-end voice latency | ~2.5s | < 3s | ✅ OK |
| NFR7 | Intent classification accuracy | 85% | > 90% | ❌ -5% |
| NFR8 | Entity extraction accuracy (name) | ~92% | > 95% | ❌ -3% |
| NFR9 | STT Word Error Rate | 21.7% | < 15% | ❌ +6.7% |
| NFR10 | Max "non ho capito" turns | 3 | 3 | ✅ OK |

### Priority Bug Matrix

| ID | Bug | Priority | Impact | Epic |
|----|-----|----------|--------|------|
| BUG1 | Fix client registration flow | P0 | New customers can't register | E2 |
| BUG2 | Activate Guided Dialog | P1 | No correction when OOS | E7 |
| BUG3 | Verify slot availability before confirm | P1 | Overbooking risk | E1 |
| BUG4 | Enable Layer 3 NLU (Sentence Transformers) | P2 | Intent accuracy 85% → 92% | E7 |
| BUG5 | Implement cancel/reschedule end-to-end | P1 | Can't exit conversation | E4 |
| BUG6 | Persist session state to DB | P2 | Session lost on restart | E7 |

---

## Epic List

### E1: Core Booking Flow (P0)

**Objective**: Complete voice booking in < 60 seconds (6-8 turns)
**Owner**: voice-engineer
**Sprint**: Week 1
**Stories**: 4

#### E1-S1: Fix Slot Availability Check (BUG3)

**As a** booking system
**I want** to verify slot availability before confirming
**So that** we prevent overbooking

**Acceptance Criteria**:
- [ ] Before confirming, call `GET /api/appuntamenti/disponibilita?date=X&time=Y&operator=Z`
- [ ] If slot unavailable, offer alternatives (next 3 available slots)
- [ ] If no alternatives, trigger waitlist offer (E6)

**Technical Implementation**:
```python
# booking_state_machine.py - _handle_confirming()
async def _check_availability(self) -> bool:
    response = await self.http_bridge.get(
        f"/api/appuntamenti/disponibilita",
        params={
            "date": self.context.date,
            "time": self.context.time,
            "operator_id": self.context.operator_id
        }
    )
    return response.get("available", False)
```

**Effort**: 4 hours

---

#### E1-S2: Italian Date Extraction

**As a** user
**I want** to say dates naturally ("domani", "lunedì prossimo")
**So that** booking is conversational

**Acceptance Criteria**:
- [ ] Parse "oggi", "domani", "dopodomani"
- [ ] Parse "lunedì", "martedì", ... (this week or next)
- [ ] Parse "lunedì prossimo", "venerdì prossimo"
- [ ] Parse "il 15 febbraio", "15/02"
- [ ] Parse "fra due settimane"

**Technical Implementation**:
```python
# entity_extractor.py - ItalianDateExtractor
class ItalianDateExtractor:
    def __init__(self):
        self.today = datetime.now().date()
        self.relative_map = {
            "oggi": timedelta(days=0),
            "domani": timedelta(days=1),
            "dopodomani": timedelta(days=2),
            "tra due giorni": timedelta(days=2),
            "fra tre giorni": timedelta(days=3),
        }
        self.day_names_it = {
            "lunedì": "Monday", "martedì": "Tuesday",
            "mercoledì": "Wednesday", "giovedì": "Thursday",
            "venerdì": "Friday", "sabato": "Saturday",
            "domenica": "Sunday",
        }

    def extract_date(self, utterance: str) -> dict:
        utterance_lower = utterance.lower()

        # Try relative dates first
        for relative_text, delta in self.relative_map.items():
            if relative_text in utterance_lower:
                target_date = self.today + delta
                return {"date": target_date, "type": "relative"}

        # Try weekday names
        for day_it, day_en in self.day_names_it.items():
            if day_it in utterance_lower:
                if "prossimo" in utterance_lower:
                    target_date = self._next_weekday(day_en)
                else:
                    target_date = self._nearest_weekday(day_en)
                return {"date": target_date, "type": "weekday"}

        return None
```

**Test Cases**:
- "Vorrei un taglio domani" → 2026-01-29
- "Lunedì prossimo va bene?" → 2026-02-03
- "Il 15 febbraio preferibilmente" → 2026-02-15

**Effort**: 6 hours

---

#### E1-S3: Fuzzy Service Matching

**As a** user
**I want** to say services with typos or variants
**So that** recognition is robust

**Acceptance Criteria**:
- [ ] Match "taglio" → "Taglio capelli"
- [ ] Match "coloure" (typo) → "Colore"
- [ ] Handle ambiguous matches ("taglio" → uomo vs donna?)
- [ ] Threshold: 80% similarity score

**Technical Implementation**:
```python
# entity_extractor.py - ServiceMatcher
from fuzzywuzzy import fuzz, process

class ServiceMatcher:
    def __init__(self, db_services: list):
        self.db_services = db_services

    def match(self, user_service: str, threshold: int = 80) -> dict:
        matches = process.extract(
            user_service, self.db_services,
            scorer=fuzz.token_sort_ratio, limit=3
        )

        results = [
            {"service": s, "confidence": score/100}
            for s, score in matches if score >= threshold
        ]

        if len(results) == 1:
            return results[0]
        elif len(results) > 1:
            return {"ambiguous": True, "candidates": results}
        return None
```

**Effort**: 4 hours

---

#### E1-S4: Field Mapping Python → Rust

**As a** system
**I want** correct field names in API calls
**So that** HTTP Bridge accepts requests

**Current Bug**: Python uses `service`, Rust expects `servizio`

**Mapping Table**:
| Python | Rust | Status |
|--------|------|--------|
| service | servizio | ✅ Fixed |
| date | data | ✅ Fixed |
| time | ora | ✅ Fixed |
| client_id | cliente_id | ✅ Fixed |
| operator_id | operatore_id | ✅ Fixed |
| source | fonte_prenotazione | ⚠️ Verify |

**Effort**: 2 hours

---

### E2: Client Registration (P0)

**Objective**: Register new clients via voice conversation
**Owner**: voice-engineer
**Sprint**: Week 1
**Stories**: 3
**Blocks**: E1 (can't book without client)

#### E2-S1: Fix Registration State Machine (BUG1)

**As a** new customer
**I want** to register via voice
**So that** I can book appointments

**Current Bug**: State machine doesn't complete registration flow

**Acceptance Criteria**:
- [ ] Collect: nome, cognome, telefono
- [ ] Optional: email, data_nascita
- [ ] Create client record via `POST /api/clienti/create`
- [ ] Verify record created in DB
- [ ] Return client_id for booking

**State Flow**:
```
REGISTERING_NAME → "Come ti chiami?"
    ↓
REGISTERING_SURNAME → "E il cognome?"
    ↓
REGISTERING_PHONE → "Mi lasci un numero di telefono?"
    ↓
REGISTERING_CONFIRM → "Ho registrato Mario Rossi, 333..."
    ↓
→ Continue to WAITING_SERVICE
```

**Technical Fix**:
```python
# booking_state_machine.py
async def _handle_registering_confirm(self, utterance: str) -> StateMachineResult:
    if self._is_affirmative(utterance):
        # Create client in DB
        response = await self.http_bridge.post(
            "/api/clienti/create",
            json={
                "nome": self.context.client_name,
                "cognome": self.context.client_surname,
                "telefono": self.context.client_phone,
                "email": self.context.client_email,
            }
        )

        if response.get("success"):
            self.context.client_id = response["id"]
            self.state = BookingState.WAITING_SERVICE
            return StateMachineResult(
                response="Perfetto! Quale servizio desidera?",
                state=self.state
            )

    # Handle rejection...
```

**Effort**: 8 hours

---

#### E2-S2: Name Sanitization (STT Artifacts)

**As a** system
**I want** to clean STT name artifacts
**So that** names are stored correctly

**Examples**:
- "Rossi." → "Rossi" (trailing punctuation)
- "Antonio Vorrei" → "Antonio" (trailing verb)
- "Gianluca Distasi" → name="Gianluca", surname="Distasi"

**Already Implemented**: `sanitize_name()`, `sanitize_name_pair()`

**Test Cases**:
- [ ] "MARIO." → "Mario"
- [ ] "rossi" → "Rossi"
- [ ] "Antonio Vorrei" → "Antonio"
- [ ] "Gianluca Distasi" → ("Gianluca", "Distasi")

**Effort**: 2 hours (verification)

---

#### E2-S3: Email Validation

**As a** system
**I want** to validate email format
**So that** we store valid emails

**Acceptance Criteria**:
- [ ] Validate email regex
- [ ] Handle STT email variations ("mario chiocciola gmail punto com")
- [ ] Optional field - can skip

**Effort**: 2 hours

---

### E3: Client Disambiguation

**Objective**: Resolve homonyms correctly
**Owner**: voice-engineer
**Sprint**: Week 2
**Stories**: 2

#### E3-S1: Birth Date Disambiguation

**As a** system
**I want** to disambiguate by birth date
**So that** correct client is selected

**Flow**:
```
"Prenotazione per Mario Rossi"
    ↓
Found 2 clients: Mario Rossi (1980), Mario Rossi (1992)
    ↓
"Ho trovato 2 clienti. Mi può dire la sua data di nascita?"
    ↓
"10 gennaio 1980"
    ↓
Match found → continue
```

**Effort**: 4 hours

---

#### E3-S2: Nickname Fallback

**As a** system
**I want** to fallback to nickname
**So that** disambiguation succeeds

**Flow**:
```
Birth date doesn't match any client
    ↓
"Non ho trovato questa data. Mario o Marione?"
    ↓
"Marione"
    ↓
Match client with soprannome="Marione"
```

**Effort**: 4 hours

---

### E4: Appointment Management

**Objective**: Cancel and reschedule via voice
**Owner**: voice-engineer
**Sprint**: Week 1
**Stories**: 3
**Fixes**: BUG5

#### E4-S1: Cancel Appointment (End-to-End)

**As a** customer
**I want** to cancel my appointment via voice
**So that** I don't need to call

**Acceptance Criteria**:
- [ ] Detect CANCELLAZIONE intent
- [ ] Lookup customer's upcoming appointments
- [ ] Confirm which appointment to cancel
- [ ] Call `POST /api/appuntamenti/cancel`
- [ ] Confirm cancellation to customer

**Intent Patterns**:
- "Voglio annullare"
- "Disdico l'appuntamento"
- "Non posso più venire"
- "Cancello la prenotazione"

**Effort**: 6 hours

---

#### E4-S2: Reschedule Appointment (End-to-End)

**As a** customer
**I want** to reschedule my appointment
**So that** I can change date/time

**Acceptance Criteria**:
- [ ] Detect SPOSTAMENTO intent
- [ ] Lookup customer's appointment
- [ ] Ask for new date/time
- [ ] Verify availability
- [ ] Call `POST /api/appuntamenti/reschedule`
- [ ] Confirm new booking

**Intent Patterns**:
- "Posso spostare?"
- "Cambiami la data"
- "Vorrei anticipare/posticipare"
- "Meglio un altro giorno"

**Effort**: 8 hours

---

#### E4-S3: Mid-Conversation Corrections

**As a** customer
**I want** to correct my input mid-conversation
**So that** mistakes can be fixed

**Triggers**:
- "No aspetta, meglio venerdì"
- "Cambio idea, colore invece di taglio"
- "Sbagliato, ho detto 15 non 16"

**Technical Implementation**:
```python
class ConversationMemory:
    def handle_correction(self, utterance: str) -> dict:
        correction_patterns = [
            "no aspetta", "sbagliato", "cambio idea",
            "meglio", "invece", "la volta prossima"
        ]

        is_correction = any(p in utterance.lower() for p in correction_patterns)

        if is_correction:
            new_values = self._extract_slots(utterance)
            for slot, value in new_values.items():
                if value:
                    self.slots[slot] = value
            return {"is_correction": True, "corrected_slots": self.slots}

        return {"is_correction": False}
```

**Effort**: 6 hours

---

### E5: FAQ System

**Objective**: Answer common questions
**Owner**: voice-engineer
**Sprint**: Week 2
**Stories**: 1

#### E5-S1: Vertical-Specific FAQ

**As a** customer
**I want** to ask about hours, prices, services
**So that** I get quick answers

**FAQ per Vertical**:

**Salone**:
- "Quanto costa un taglio?" → "€15-25 dipende dal tipo"
- "Che orari fate?" → "Lunedì-Sabato 09:00-19:00"
- "Fate extension?" → "Sì, clip-in o incollate"

**Palestra**:
- "Quanto costa l'abbonamento?" → "€60/mese senza vincolo"
- "Posso fare una prova?" → "Sì, una lezione gratuita"
- "Servono asciugamani?" → "Inclusi nell'abbonamento"

**Medical**:
- "Quanto costa una visita?" → "€50-100 dipende dallo specialista"
- "Accettate assicurazioni?" → "Sì, Unipol, Allianz, Zurich"
- "Tempo medio attesa?" → "15-30 minuti"

**Auto**:
- "Quanto costa un tagliando?" → "€80-150 dipende dal modello"
- "Auto sostitutiva?" → "Sì, gratuita per riparazioni >€100"
- "Che garanzie date?" → "Pezzo 12 mesi, lavoro 3 mesi"

**Effort**: 4 hours

---

### E6: Waitlist

**Objective**: Offer waitlist when slot unavailable
**Owner**: voice-engineer
**Sprint**: Week 2
**Stories**: 1

#### E6-S1: Waitlist Integration

**As a** customer
**I want** to join waitlist if no slots available
**So that** I get notified when slot opens

**Flow**:
```
Slot unavailable
    ↓
"Mi dispiace, non ho posti. Vuole che la inserisca in lista d'attesa?"
    ↓
"Sì"
    ↓
Create waitlist record with priority
    ↓
"L'ho inserita in lista. La contattiamo appena si libera un posto."
```

**Effort**: 4 hours

---

### E7: Reliability & Quality (P1-P2)

**Objective**: Improve accuracy and robustness
**Owner**: voice-engineer
**Sprint**: Week 2-3
**Stories**: 4

#### E7-S1: Replace Whisper Groq with whisper.cpp (BUG - WER 21.7%)

**As a** system
**I want** offline STT with better accuracy
**So that** WER < 15%

**Root Cause**: Groq API uses lossy audio compression (Opus?)

**Solution**: whisper.cpp local with raw PCM

**Model Selection**:
| Model | Size | WER IT | Latency | RAM |
|-------|------|--------|---------|-----|
| Tiny | 75MB | 15-18% | 0.5-1s | 500MB |
| **Small** | 461MB | **9-11%** | 2-3s | 1.5GB | ← BEST |
| Base | 972MB | 8-10% | 4-5s | 2.5GB |

**Technical Implementation**:
```python
# voice-agent/src/stt.py
class WhisperOfflineSTT:
    def __init__(self):
        self.whisper_exe = "./resources/whisper.cpp/main"
        self.model_path = "./resources/whisper.cpp/models/ggml-small.bin"
        self.lang = "it"

    def transcribe(self, audio_path: str) -> dict:
        result = subprocess.run([
            self.whisper_exe,
            "-m", self.model_path,
            "-l", self.lang,
            "-f", audio_path,
            "--output-format", "json",
            "--no-prints"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            output = json.loads(result.stdout)
            return {
                "text": output["result"][0]["text"],
                "confidence": 0.92,
                "language": "it"
            }
```

**Expected Improvement**: WER 21.7% → 9-11%

**Effort**: 8 hours

---

#### E7-S2: Add Sentence Transformers (NLU 85% → 92%)

**As a** system
**I want** semantic intent classification
**So that** paraphrases are recognized

**Current Problem**: spaCy pattern-based misses paraphrases

**Examples**:
- "Vorrei un taglio" → ✅ detected
- "Mi piacerebbe che mi facessi un taglio" → ❌ MISSED

**Solution**: Sentence Transformers (ONNX, no PyTorch)

**Technical Implementation**:
```python
# voice-agent/src/nlu/semantic_classifier.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticIntentClassifier:
    def __init__(self):
        self.model = SentenceTransformer(
            'sentence-transformers/distiluse-base-multilingual-cased-v2'
        )

        self.intents = {
            "booking_request": [
                "Vorrei prenotare un taglio",
                "Voglio un appuntamento",
                "Mi faresti un taglio domani?",
            ],
            "cancellation": [
                "Annullo l'appuntamento",
                "Non posso più venire",
                "Disdico la prenotazione",
            ],
            "date_change": [
                "Mi sposti a giovedì?",
                "Posso venire lunedì invece?",
                "Puoi cambiarmi la data?",
            ],
        }

        # Encode examples once
        self.intent_embeddings = {}
        for intent, examples in self.intents.items():
            embeddings = self.model.encode(examples)
            self.intent_embeddings[intent] = embeddings.mean(axis=0)

    def classify(self, user_text: str) -> dict:
        user_embedding = self.model.encode(user_text)

        scores = {}
        for intent, intent_emb in self.intent_embeddings.items():
            similarity = cosine_similarity([user_embedding], [intent_emb])[0][0]
            scores[intent] = similarity

        best_intent = max(scores, key=scores.get)
        return {"intent": best_intent, "confidence": scores[best_intent]}
```

**Expected Improvement**: Intent accuracy 85% → 92%+

**Effort**: 4 hours

---

#### E7-S3: Activate Guided Dialog (BUG2)

**As a** system
**I want** guided dialog when user goes off-track
**So that** conversation recovers

**Trigger**: 2 consecutive failed turns

**Flow**:
```
User: "Qual è il tempo oggi?"
Sara: "Non ho capito. Parliamo della prenotazione."
User: "Ma quanto costa il petrolio?"
Sara: "Per aiutarti, dimmi: vuoi prenotare, cancellare, o informazioni?"
    ↓
[Guided menu]
```

**Effort**: 4 hours

---

#### E7-S4: Replace TEN VAD with Silero VAD

**As a** system
**I want** better voice activity detection
**So that** noisy environments work

**Comparison**:
| VAD | Latency | Accuracy | Noise Handling |
|-----|---------|----------|----------------|
| TEN | 50ms | 92% | Fair |
| **Silero** | 100ms | **95%** | **Good** |
| WebRTC | 20ms | 88% | Poor |

**Technical Implementation**:
```python
from silero_vad import load_silero_vad

class SileroVAD:
    def __init__(self):
        self.vad_model = load_silero_vad(onnx=True)
        self.threshold = 0.5

    def is_speech(self, audio_chunk: bytes) -> bool:
        confidence = self.vad_model(
            torch.frombuffer(audio_chunk, dtype=torch.float32),
            sr=16000
        ).item()
        return confidence > self.threshold
```

**Barge-in Detection**:
```python
class BargeinDetector:
    def handle_barge_in(self, audio_chunk: bytes) -> bool:
        if self.is_sara_speaking and self.vad.is_speech(audio_chunk):
            return True  # User interrupted
        return False
```

**Effort**: 6 hours

---

## Domain Data (4 Verticals)

### Salone Bellezza

```json
{
  "services": [
    {"name": "Taglio capelli", "variants": ["taglio", "tagliati i capelli"], "duration_min": 20, "price_range": "€15-25", "frequency": 35},
    {"name": "Colore", "variants": ["colore", "tinta", "colorazione"], "duration_min": 60, "price_range": "€40-80", "frequency": 18},
    {"name": "Piega", "variants": ["piega", "messa in piega"], "duration_min": 30, "price_range": "€15-20", "frequency": 12},
    {"name": "Meches", "variants": ["meches", "highlights", "colpi di sole"], "duration_min": 90, "price_range": "€50-100", "frequency": 6},
    {"name": "Balayage", "variants": ["balayage", "sombre", "degradé"], "duration_min": 120, "price_range": "€70-150", "frequency": 2}
  ]
}
```

### Palestra/Fitness

```json
{
  "services": [
    {"name": "Personal Trainer", "variants": ["PT", "personal", "allenamento personalizzato"], "duration_min": 60, "price_range": "€40-80/sessione", "frequency": 25},
    {"name": "Yoga", "variants": ["yoga", "lezione di yoga", "hatha yoga"], "duration_min": 60, "price_range": "Incluso", "frequency": 18},
    {"name": "Spinning", "variants": ["spinning", "bike", "ciclo indoor"], "duration_min": 45, "price_range": "Incluso", "frequency": 16},
    {"name": "Pilates", "variants": ["pilates", "matwork", "reformer"], "duration_min": 50, "price_range": "€15-20", "frequency": 12},
    {"name": "CrossFit", "variants": ["crossfit", "WOD", "functional"], "duration_min": 75, "price_range": "€15-20", "frequency": 10}
  ]
}
```

### Studio Medico

```json
{
  "services": [
    {"name": "Visita generica", "variants": ["visita", "controllo", "check-up"], "duration_min": 20, "price_range": "€50-100", "frequency": 30},
    {"name": "Pulizia denti", "variants": ["pulizia", "igiene", "detartrasi"], "duration_min": 30, "price_range": "€60-80", "frequency": 22},
    {"name": "Otturazione", "variants": ["otturazione", "carie", "riempimento"], "duration_min": 30, "price_range": "€60-150", "frequency": 15},
    {"name": "Devitalizzazione", "variants": ["cura canalare", "devitalizzazione", "root canal"], "duration_min": 60, "price_range": "€200-400", "frequency": 8},
    {"name": "Visita cardiologica", "variants": ["cardiologia", "cuore", "cardiologo"], "duration_min": 30, "price_range": "€80-120", "frequency": 5}
  ]
}
```

### Officina Auto

```json
{
  "services": [
    {"name": "Tagliando", "variants": ["tagliando", "revisione", "service", "manutenzione"], "duration_min": 45, "price_range": "€80-150", "frequency": 40},
    {"name": "Cambio gomme", "variants": ["gomme", "pneumatici", "ruote", "cambio stagionale"], "duration_min": 30, "price_range": "€40-80", "frequency": 18},
    {"name": "Freni", "variants": ["freni", "pastiglie", "dischi freno"], "duration_min": 60, "price_range": "€150-300", "frequency": 12},
    {"name": "Batteria", "variants": ["batteria", "accumulatore"], "duration_min": 15, "price_range": "€60-150", "frequency": 6},
    {"name": "Diagnosi motore", "variants": ["diagnosi", "error check", "OBD"], "duration_min": 30, "price_range": "€50-100", "frequency": 8}
  ]
}
```

---

## 4-Week Roadmap

### Week 1 (IMMEDIATE) - P0 Fixes

| Day | Task | Owner | Status |
|-----|------|-------|--------|
| Mon | E2-S1: Fix registration flow | voice-engineer | 🔴 TODO |
| Mon | E1-S1: Slot availability check | voice-engineer | 🔴 TODO |
| Tue | E4-S1: Cancel end-to-end | voice-engineer | 🔴 TODO |
| Wed | E4-S2: Reschedule end-to-end | voice-engineer | 🔴 TODO |
| Thu | E7-S1: whisper.cpp (WER fix) | voice-engineer | 🔴 TODO |
| Fri | Testing + Bug fixes | voice-engineer | 🔴 TODO |

**Week 1 Goal**: All P0 bugs fixed, WER 21.7% → 11%

### Week 2 - P1 Improvements

| Day | Task | Owner | Status |
|-----|------|-------|--------|
| Mon | E1-S2: Italian date extraction | voice-engineer | 🔴 TODO |
| Mon | E1-S3: Fuzzy service matching | voice-engineer | 🔴 TODO |
| Tue | E7-S2: Sentence Transformers NLU | voice-engineer | 🔴 TODO |
| Wed | E7-S3: Activate Guided Dialog | voice-engineer | 🔴 TODO |
| Thu | E5-S1: FAQ per vertical | voice-engineer | 🔴 TODO |
| Fri | E6-S1: Waitlist integration | voice-engineer | 🔴 TODO |

**Week 2 Goal**: Intent 85% → 92%, slots accurate

### Week 3 - Quality

| Day | Task | Owner | Status |
|-----|------|-------|--------|
| Mon | E7-S4: Silero VAD | voice-engineer | 🔴 TODO |
| Tue | E4-S3: Mid-conversation corrections | voice-engineer | 🔴 TODO |
| Wed | E3-S1: Birth date disambiguation | voice-engineer | 🔴 TODO |
| Thu | E3-S2: Nickname fallback | voice-engineer | 🔴 TODO |
| Fri | Integration testing | voice-engineer | 🔴 TODO |

**Week 3 Goal**: Disambiguation complete, VAD improved

### Week 4 - Release

| Day | Task | Owner | Status |
|-----|------|-------|--------|
| Mon | GDPR audit trail | voice-engineer | 🔴 TODO |
| Tue | Data retention policy | voice-engineer | 🔴 TODO |
| Wed | Regression testing | voice-engineer | 🔴 TODO |
| Thu | Documentation | voice-engineer | 🔴 TODO |
| Fri | **v1.0 Release** | voice-engineer | 🔴 TODO |

---

## Success Metrics (v1.0)

| Metric | Current | Target | Method |
|--------|---------|--------|--------|
| STT WER | 21.7% | < 12% | whisper.cpp offline |
| Intent Accuracy | 85% | > 90% | Sentence Transformers |
| Slot Accuracy | ~90% | > 95% | ItalianDateExtractor + fuzzy |
| E2E Latency | 2.5s | < 3s | Maintain |
| Booking Success Rate | ~60% | > 85% | Fix P0 bugs |
| Registration Success | 0% | > 90% | Fix state machine |

---

## GDPR Compliance

### Consent Model (Two-Tier)

```
Tier 1: Local Processing (default)
├─ Consent: "Registra qui sul mio computer"
├─ GDPR basis: Legitimate interest + consent
└─ Audio deleted after transcription

Tier 2: Cloud Fallback (optional)
├─ Additional consent required
├─ GDPR basis: Explicit consent
└─ Only if local fails
```

### Data Retention

| Data Type | Retention | Auto-Delete |
|-----------|-----------|-------------|
| Raw audio | 14 days | ✅ |
| Transcripts | 90 days | ✅ |
| Conversation history | 1 year | ✅ |
| Booking records | Indefinite | Anonymize on request |

### Right to Delete

```python
class DSARHandler:
    def handle_deletion_request(self, customer_phone: str):
        # Delete: conversations, transcripts, audio
        # Anonymize: bookings (keep for records)
        # Confirm to customer
```

---

*Document generated by BMAD v6.0.0-Beta.2*
*Last update: 2026-01-28*
*Next step: Story implementation (Week 1)*
