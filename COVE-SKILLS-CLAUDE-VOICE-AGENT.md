# COVE SKILLS CLAUDE - Voice Agent Auto-Implementation
## Sistema di Skill per Auto-Implementazione del Voice Agent

**Versione**: 1.0  
**Data**: 2026-02-12  
**Obiettivo**: Voice Agent 100% funzionante tramite skill Claude automatizzate

---

## 🧠 CONCETTO: Skills per Claude

Le **Skills Claude** sono capability modulari che permettono a Claude di:
1. Analizzare codice esistente autonomamente
2. Generare nuovo codice conforme al PRD
3. Eseguire test e validare risultati
4. Debuggare errori senza intervento umano
5. Integrare componenti tra loro

Ogni skill è un **sub-agent specializzato** che Claude può invocare.

---

## 🎯 SKILL SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE SKILL SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Skill: Code  │  │ Skill: Test  │  │ Skill: Debug │          │
│  │ Analyzer     │  │ Generator    │  │ Fixer        │          │
│  │              │  │              │  │              │          │
│  │ - Legge PRD  │  │ - Genera     │  │ - Analizza   │          │
│  │ - Analizza   │  │   test unit  │  │   errori     │          │
│  │   codebase   │  │ - Genera     │  │ - Propone    │          │
│  │ - Identifica │  │   test E2E   │  │   fix        │          │
│  │   gap        │  │ - Coverage   │  │ - Auto-apply │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Skill: Vertical│ │ Skill: Integration│ │ Skill: Deploy │     │
│  │ Generator    │  │ Tester       │  │ Manager      │          │
│  │              │  │              │  │              │          │
│  │ - Crea       │  │ - Test       │  │ - Deploy     │          │
│  │   vertical   │  │   cross-skill│  │   su iMac    │          │
│  │ - Genera     │  │ - Test       │  │ - Health     │          │
│  │   schema     │  │   API        │  │   check      │          │
│  │ - Configura  │  │ - Test       │  │ - Rollback   │          │
│  │   intents    │  │   vertical   │  │   se fail    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              COVE ORCHESTRATOR                           │  │
│  │  - Coordina esecuzione skill                            │  │
│  │  - Verifica risultati (CoVe verification)               │  │
│  │  - Gestisce dipendenze tra skill                        │  │
│  │  - Reporta progresso                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 SKILL 1: CODE ANALYZER

**Prompt per attivazione skill:**

```markdown
## SKILL: CODE_ANALYZER

Sei uno specialista nell'analisi di codebase Voice Agent.
Analizza il codice esistente e identifica:

1. **GAP rispetto al PRD**: Cosa manca vs SUB-PRD-VOICE-AGENT-ENTERPRISE.md?
2. **Inconsistenze**: Codice che non rispetta le specifiche
3. **Degradazione**: Feature che funzionavano e ora non più
4. **Opportunità**: Miglioramenti architetturali

### Input
- File: {file_path}
- PRD Reference: {section_prd}

### Output Format
```json
{
  "analysis": {
    "file": "voice-agent/src/orchestrator.py",
    "completeness": "75%",
    "issues": [
      {
        "type": "missing_implementation",
        "severity": "high",
        "description": "Manca integration con verticals/salone/config.py",
        "prd_reference": "Vertical Integration Section 4.1",
        "suggested_action": "Implementare caricamento dinamico vertical"
      }
    ],
    "code_quality": {
      "score": 8.5,
      "issues": ["Callback troppo lunga", "Manca type hint"]
    }
  }
}
```

### Esecuzione
```bash
# Analizza file specifico
python -m claude_skills.code_analyzer voice-agent/src/orchestrator.py

# Analizza progetto completo
python -m claude_skills.code_analyzer --project voice-agent/ --prd SUB-PRD-VOICE-AGENT-ENTERPRISE.md
```
```

---

## 🧪 SKILL 2: TEST GENERATOR

**Prompt per attivazione skill:**

```markdown
## SKILL: TEST_GENERATOR

Sei uno specialista in testing automatico per Voice Agent.
Genera test completi per ogni componente.

### Capabilities
1. **Unit Test**: Per ogni funzione/metodo
2. **Integration Test**: Per interazione tra componenti
3. **E2E Test**: Per flussi utente completi
4. **Property Test**: Per invarianti del sistema

### Input
- Componente: {component_name}
- Tipo test: {unit|integration|e2e}
- Coverage target: {percentage}%

### Output
File test generato in `voice-agent/tests/`

### Esempio Esecuzione

**Per VAD Skill:**
```python
# tests/skills/test_vad_skill.py
import pytest
from voice_agent.skills.vad_skill import VADSkill

class TestVADSkill:
    """Test completo VAD Skill - Generato automaticamente da SKILL:TEST_GENERATOR"""
    
    @pytest.fixture
    def vad():
        return VADSkill(sensitivity=0.5)
    
    def test_speech_detection(self, vad):
        """CoVe: VAD deve rilevare inizio parlato in <50ms"""
        audio = load_test_audio("speech_sample.wav")
        event = vad.process(audio)
        assert event.type == "SPEECH_START"
        assert event.latency_ms < 50
    
    def test_silence_no_trigger(self, vad):
        """VAD non deve triggerare su silenzio"""
        audio = load_test_audio("silence_3s.wav")
        event = vad.process(audio)
        assert event is None
    
    def test_interruption_detection(self, vad):
        """VAD deve rilevare interruzione durante TTS"""
        # Setup: TTS in riproduzione
        vad.set_state("PLAYING_TTS")
        audio = load_test_audio("barge_in.wav")
        event = vad.process(audio)
        assert event.type == "INTERRUPTION"
```

### Comando
```bash
# Genera test per componente
python -m claude_skills.test_generator --component VADSkill --type unit --coverage 90

# Genera test E2E per flusso
python -m claude_skills.test_generator --flow "booking_complete" --type e2e
```
```

---

## 🐛 SKILL 3: DEBUG FIXER

**Prompt per attivazione skill:**

```markdown
## SKILL: DEBUG_FIXER

Sei uno specialista nel debug e fix automatico di errori Voice Agent.
Analizza errori e propone/applica fix.

### Input
- Error log: {stack_trace}
- Componente: {component}
- Test fallito: {test_name}

### Processo
1. Analizza stack trace
2. Identifica root cause
3. Propone fix (max 3 opzioni)
4. Applica fix selezionato
5. Verifica con test

### Output Format
```json
{
  "error_analysis": {
    "type": "AttributeError",
    "component": "BookingStateMachine",
    "root_cause": "Manca metodo handle_input_with_confidence",
    "confidence": 95
  },
  "fixes": [
    {
      "option": 1,
      "description": "Aggiungere metodo mancante",
      "code_patch": "def handle_input_with_confidence(...): ...",
      "risk": "low",
      "estimated_time": "5min"
    }
  ],
  "applied_fix": 1,
  "verification": {
    "test_passed": true,
    "regression_test": "passed"
  }
}
```

### Esempio Esecuzione

**Errore: Test fallito test_phonetic_disambiguation**
```
AssertionError: Deve chiedere disambiguazione per Mario/Maria
```

**Analisi SKILL:DEBUG_FIXER:**
```
Root Cause: Il test usa Mock su db_lookup ma il codice usa sqlite3 direttamente.
Il mock non viene mai chiamato perché il codice fa query diretta al DB.

Fix: Implementare dependency injection per db_lookup
```

**Fix applicato:**
```python
# In BookingStateMachine.__init__
self.db_lookup: Optional[callable] = None

# In _check_name_disambiguation
if self.db_lookup is not None:
    clients = self.db_lookup(input_name, input_surname)
    ...
```

### Comando
```bash
# Auto-fix da test fallito
python -m claude_skills.debug_fixer --test test_phonetic_disambiguation --apply

# Analisi errore senza applicare fix
python -m claude_skills.debug_fixer --log error.log --analyze-only
```
```

---

## 🏢 SKILL 4: VERTICAL GENERATOR

**Prompt per attivazione skill:**

```markdown
## SKILL: VERTICAL_GENERATOR

Sei uno specialista nella creazione di verticali Voice Agent.
Genera un verticale completo dato il settore.

### Input
- Nome vertical: {name}
- Settore: {industry}
- Servizi: {list}
- Slot richiesti: {list}
- Schema dati: {schema}

### Output
Struttura completa in `voice-agent/verticals/{name}/`

### Files Generati
```
verticals/{name}/
├── config.py              # Configurazione vertical
├── intents.py             # Pattern intent specifici
├── entities.py            # Entity extractor custom
├── faqs.json              # FAQ settore
├── schema.py              # Schema dati cliente
└── tests/
    ├── test_intents.py
    ├── test_entities.py
    └── test_e2e.py
```

### Esempio: Generazione Salone

**Input:**
```json
{
  "name": "salone",
  "settore": "Beauty/Hair",
  "servizi": ["taglio", "colore", "piega", "barba", "trattamento"],
  "slots": ["data", "ora", "servizio", "operatore"],
  "schema": ["tipo_capelli", "lunghezza", "allergie_prodotti"]
}
```

**Output generato:**

```python
# verticals/salone/config.py
SALONE_CONFIG = {
    "name": "Salone di Bellezza",
    "services": {
        "taglio": ["taglio", "tagliare", "tagliarsi"],
        "colore": ["colore", "tinta", "tingere"],
        "piega": ["piega", "asciugare", "phon"],
        "barba": ["barba", "rasatura"],
        "trattamento": ["trattamento", "maschera", "cura"]
    },
    "slots": ["data", "ora", "servizio", "operatore"],
    "required_slots": ["data", "ora", "servizio"],
    "greeting": "Buongiorno, sono Sara di {nome_attivita}. Come posso aiutarla?",
    "closing": "Grazie per aver chiamato {nome_attivita}. A presto!"
}

# verticals/salone/intents.py
INTENT_PATTERNS_SALONE = {
    "PRENOTAZIONE": [
        r"(vorrei|voglio|posso)\s+(prenotare|fissare|prendere)",
        r"(taglio|colore|piega|barba|trattamento)",
        r"(mi\s+serve|ho\s+bisogno\s+di)\s+(un\s+)?(taglio|colore)"
    ],
    "CANCELLAZIONE": [
        r"(cancellare|annullare|disdire)\s+(la\s+)?prenotazione",
        r"non\s+(posso|riesco)\s+(più\s+)?venire"
    ],
    "INFO_SERVIZI": [
        r"(quanto\s+costa|prezzo)\s+(il\s+)?(taglio|colore)",
        r"(che\s+servizi|cosa)\s+(offrite|fate)"
    ]
}

# verticals/salone/schema.py
@dataclass
class SchedaSalone:
    cliente_id: str
    tipo_capelli: Optional[str]  # "lisci", "ricci", "mossi"
    lunghezza: Optional[str]      # "corti", "medi", "lunghi"
    colorazione_precedente: Optional[str]
    allergie_prodotti: List[str]
    preferenze_operatore: Optional[str]
    frequenza_visite: str
    prodotti_usati: List[str]
```

### Comando
```bash
# Genera verticale completo
python -m claude_skills.vertical_generator --config salone_config.json

# Genera da descrizione testuale
python -m claude_skills.vertical_generator --describe "Centro estetico con depilazione, manicure, pedicure"
```
```

---

## 🔌 SKILL 5: INTEGRATION TESTER

**Prompt per attivazione skill:**

```markdown
## SKILL: INTEGRATION_TESTER

Sei uno specialista in integration testing per Voice Agent.
Verifica che tutti i componenti funzionino insieme.

### Test Matrix

| Componente A | Componente B | Test Type |
|--------------|--------------|-----------|
| VAD Skill | STT Skill | Audio flow |
| STT Skill | NLU Skill | Text→Intent |
| NLU Skill | State Skill | Intent→Action |
| State Skill | TTS Skill | Response→Audio |
| Orchestrator | Vertical | Full pipeline |
| Voice Agent | WhatsApp | Notification |
| Voice Agent | VoIP EhiWeb | Call handling |

### Esempio Test: VAD → STT Integration

```python
# tests/integration/test_vad_stt.py
class TestVADSTTIntegration:
    """Verifica flusso audio: VAD detection → STT transcription"""
    
    async def test_speech_detected_and_transcribed(self):
        """Test completo: audio → VAD → STT → testo"""
        pipeline = VoicePipeline()
        
        # Simula audio stream
        audio_chunks = load_audio_stream("test_speech.wav")
        
        # Processa
        result = await pipeline.process_audio_stream(audio_chunks)
        
        # Verifiche
        assert result.vad_events[0].type == "SPEECH_START"
        assert result.transcription.text == "Vorrei prenotare un taglio"
        assert result.transcription.confidence > 0.9
        assert result.total_latency_ms < 500
```

### Esempio Test: Full Pipeline

```python
# tests/integration/test_full_pipeline.py
class TestFullPipeline:
    """Test E2E: Input audio → Output audio"""
    
    async def test_booking_flow_e2e(self):
        """Flusso completo prenotazione"""
        pipeline = VoicePipeline(vertical="salone")
        
        # Turn 1
        response1 = await pipeline.process("Vorrei prenotare")
        assert "quando" in response1.audio_text
        
        # Turn 2
        response2 = await pipeline.process("Domani")
        assert "ora" in response2.audio_text
        
        # Turn 3
        response3 = await pipeline.process("Alle 15")
        assert "servizio" in response3.audio_text
        
        # ... fino a conferma
```

### Comando
```bash
# Test specifica integrazione
python -m claude_skills.integration_tester --from VAD --to STT

# Test tutte le integrazioni
python -m claude_skills.integration_tester --all

# Test con vertical specifico
python -m claude_skills.integration_tester --vertical salone
```
```

---

## 🚀 SKILL 6: DEPLOY MANAGER

**Prompt per attivazione skill:**

```markdown
## SKILL: DEPLOY_MANAGER

Sei uno specialista in deployment Voice Agent su iMac.
Gestisce deploy, health check, e rollback.

### Capabilities
1. **Deploy**: Push codice su iMac, restart servizio
2. **Health Check**: Verifica tutti i componenti
3. **Smoke Test**: Test rapido post-deploy
4. **Rollback**: Ripristina versione precedente se fail

### Workflow Deploy

```
1. Pre-deploy checks
   ├── Git status clean
   ├── Tests passati
   └── TypeScript check OK

2. Deploy
   ├── SSH to iMac (192.168.1.7)
   ├── Git pull origin master
   ├── Install dependencies
   └── Restart voice-agent service

3. Post-deploy verification
   ├── Health check http://192.168.1.7:3002/health
   ├── Smoke test API
   ├── Test cross-machine
   └── Latency benchmark

4. Se fail → Automatic rollback
```

### Comandi

```bash
# Deploy completo
python -m claude_skills.deploy_manager --deploy

# Solo health check
python -m claude_skills.deploy_manager --health

# Smoke test
python -m claude_skills.deploy_manager --smoke

# Rollback
python -m claude_skills.deploy_manager --rollback --to-commit <hash>
```

### Output
```json
{
  "deploy": {
    "status": "success",
    "commit": "19d2e35",
    "timestamp": "2026-02-12T19:30:00Z",
    "steps": [
      {"step": "git_pull", "status": "ok"},
      {"step": "dependencies", "status": "ok"},
      {"step": "restart", "status": "ok"},
      {"step": "health_check", "status": "ok"},
      {"step": "smoke_test", "status": "ok"}
    ]
  },
  "verification": {
    "health": "ok",
    "api": "ok",
    "latency_p95": "780ms"
  }
}
```
```

---

## 🎛️ COVE ORCHESTRATOR

Il **CoVe Orchestrator** coordina l'esecuzione delle skill per raggiungere l'obiettivo finale.

### Workflow Auto-Implementation

```yaml
workflow: "Voice Agent 100% Completion"

phases:
  1_analyze:
    skill: CODE_ANALYZER
    input: 
      - "voice-agent/"
      - "SUB-PRD-VOICE-AGENT-ENTERPRISE.md"
    output: "gap_analysis.json"
    
  2_generate_missing:
    parallel:
      - skill: VERTICAL_GENERATOR
        for: ["salone", "medical", "palestra", "auto"]
        
      - skill: TEST_GENERATOR
        for: ["VAD", "STT", "NLU", "TTS", "State"]
        
  3_implement:
    skill: CODE_GENERATOR  # (nuova skill)
    input: "gap_analysis.json"
    output: "code_patches/"
    
  4_test:
    skill: INTEGRATION_TESTER
    dependencies: ["3_implement"]
    
  5_debug:
    skill: DEBUG_FIXER
    condition: "if tests failed"
    loop: "until all tests pass"
    
  6_verify:
    skill: INTEGRATION_TESTER
    test: "E2E live"
    
  7_deploy:
    skill: DEPLOY_MANAGER
    condition: "if all tests pass"
```

---

## 📋 PROMPT ESECUZIONE COMPLETA

Per eseguire tutto il sistema, usa questo prompt:

```markdown
## MISSIONE: Voice Agent 100% Completo

Esegui il workflow CoVe completo per rendere il Voice Agent perfettamente funzionante.

### Obiettivo
Voice Agent Enterprise v3.0 con:
- 4 verticali completi: salone, medical, palestra, auto (NO ristorazione)
- Tutti i test passati (58/58)
- Latenza <800ms
- Integrazione WhatsApp funzionante
- Integrazione VoIP EhiWeb funzionante

### Fase 1: Analisi
1. Esegui SKILL:CODE_ANALYZER su voice-agent/
2. Identifica TUTTI i gap rispetto a SUB-PRD-VOICE-AGENT-ENTERPRISE.md
3. Genera report gap_analysis.json

### Fase 2: Generazione Verticali
1. Esegui SKILL:VERTICAL_GENERATOR per ogni verticale mancante
2. Genera: config.py, intents.py, entities.py, faqs.json, schema.py
3. Verifica coerenza con PRD

### Fase 3: Generazione Test
1. Esegui SKILL:TEST_GENERATOR per ogni skill
2. Genera: unit test, integration test, E2E test
3. Target coverage: 90%+

### Fase 4: Fix Automatici
1. Esegui tutti i test
2. Per ogni test fallito: esegui SKILL:DEBUG_FIXER
3. Loop finché tutti i test non passano

### Fase 5: Integration Testing
1. Esegui SKILL:INTEGRATION_TESTER --all
2. Verifica: VAD→STT→NLU→State→TTS pipeline
3. Verifica integrazione WhatsApp e VoIP

### Fase 6: Deploy e Verifica
1. Esegui SKILL:DEPLOY_MANAGER --deploy
2. Esegui test live su iMac (192.168.1.7)
3. Verifica latenza <800ms

### Criteri di Successo (CoVe)
- [ ] 58/58 test passati
- [ ] 4 verticali completi
- [ ] Latenza P95 <800ms
- [ ] Health check OK
- [ ] Smoke test OK
- [ ] Test cross-machine OK

ESEGUI ORA.
```

---

## 🎯 SKILL CLAUDE ATTIVAZIONE

Per attivare le skill, usa questi comandi:

```bash
# Setup skill system
pip install claude-skills-framework

# Attiva skill specifica
claude-skill activate CODE_ANALYZER
claude-skill activate TEST_GENERATOR
claude-skill activate DEBUG_FIXER
claude-skill activate VERTICAL_GENERATOR
claude-skill activate INTEGRATION_TESTER
claude-skill activate DEPLOY_MANAGER

# Esegui workflow completo
claude-orchestrator run workflow/voice-agent-completion.yaml
```

---

## 📊 MONITORING SKILL EXECUTION

```json
{
  "orchestrator": {
    "status": "running",
    "current_phase": "3_implement",
    "completed_phases": ["1_analyze", "2_generate_missing"],
    "active_skills": ["CODE_GENERATOR"],
    "progress": "45%",
    "estimated_completion": "2026-02-13T10:00:00Z"
  },
  "skills_executed": [
    {"skill": "CODE_ANALYZER", "status": "completed", "duration": "5m"},
    {"skill": "VERTICAL_GENERATOR", "status": "completed", "duration": "15m", "generated": 4},
    {"skill": "TEST_GENERATOR", "status": "completed", "duration": "20m", "tests": 120}
  ]
}
```

---

**Questo sistema permette a Claude di auto-implementare il Voice Agent in modo autonomo, con verifica CoVe ad ogni step.**
