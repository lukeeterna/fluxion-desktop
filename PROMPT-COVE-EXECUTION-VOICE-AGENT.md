# PROMPT COVE ESECUZIONE: Voice Agent 100% Completo
## Auto-Implementazione tramite Skills Claude

**Data**: 2026-02-12  
**Stato Iniziale**: 58/58 test passati, URL fixato, restaurant eliminato  
**Obiettivo**: Voice Agent perfettamente funzionante con 4 verticali completi  
**Metodologia**: CoVe Verification ad ogni step  

---

## 🎯 OBIETTIVO NON NEGOZIABILE

```
Voice Agent Enterprise v3.0
├── 4 Verticali: Salone, Medical, Palestra, Auto (NO RISTORAZIONE)
├── 58/58 Test Passati
├── Latenza P95 < 800ms  
├── WhatsApp Integration: Funzionante
├── VoIP EhiWeb Integration: Funzionante
└── Test Live: 0 errori
```

---

## 🧠 SKILL CLAUDE DA ATTIVARE

Attiva sequenzialmente queste skill:

### SKILL 1: CODE_ANALYZER
```
TASK: Analizza voice-agent/ vs SUB-PRD-VOICE-AGENT-ENTERPRISE.md
INPUT: 
  - Directory: voice-agent/
  - PRD: SUB-PRD-VOICE-AGENT-ENTERPRISE.md
OUTPUT: gap_analysis.json con:
  - Verticali mancanti
  - Skill incomplete
  - Test mancanti
  - Integrazioni da completare
```

### SKILL 2: VERTICAL_GENERATOR (×4)
```
TASK: Genera 4 verticali completi

VERTICALE 1: salone
- Servizi: taglio, colore, piega, barba, trattamento
- Schema: tipo_capelli, lunghezza, allergie_prodotti
- Intents: PRENOTAZIONE, CANCELLAZIONE, INFO_SERVIZI

VERTICALE 2: medical (odontoiatria/fisioterapia)
- Servizi: visita, trattamento, urgente
- Schema: anamnesi, patologie, allergie, contatto_emergenza
- Intents: + richiesta anamnesi

VERTICALE 3: palestra
- Servizi: lezione, pt, daypass
- Schema: abbonamento, obiettivi, livello_fitness
- Intents: + disponibilità corsi

VERTICALE 4: auto (officina)
- Servizi: tagliando, riparazione, gomme
- Schema: targa, modello, km, storico_interventi
- Intents: + urgenza, preventivo

OUTPUT PER OGNI VERTICALE:
- verticals/{name}/config.py
- verticals/{name}/intents.py  
- verticals/{name}/entities.py
- verticals/{name}/schema.py
- verticals/{name}/faqs.json
```

### SKILL 3: TEST_GENERATOR
```
TASK: Genera test suite completa

UNIT TESTS:
- tests/skills/test_vad_skill.py
- tests/skills/test_stt_skill.py
- tests/skills/test_nlu_skill.py
- tests/skills/test_tts_skill.py
- tests/skills/test_state_skill.py

INTEGRATION TESTS:
- tests/integration/test_vad_stt.py
- tests/integration/test_stt_nlu.py
- tests/integration/test_nlu_state.py
- tests/integration/test_state_tts.py
- tests/integration/test_full_pipeline.py

E2E TESTS:
- tests/e2e/test_salone_booking.py
- tests/e2e/test_medical_booking.py
- tests/e2e/test_palestra_booking.py
- tests/e2e/test_auto_booking.py

TARGET: 90% coverage
```

### SKILL 4: DEBUG_FIXER (LOOP)
```
TASK: Fixa tutti i test falliti

WORKFLOW:
1. Esegui: pytest tests/ -v
2. Per ogni test fallito:
   a. Analizza errore
   b. Identifica root cause
   c. Proponi fix (max 3 opzioni)
   d. Applica fix migliore
   e. Re-run test
3. Loop finché 58/58 test non passano

STOP CONDITION: All tests passed
```

### SKILL 5: INTEGRATION_TESTER
```
TASK: Verifica integrazioni complete

INTEGRATION MATRIX:
✓ VAD → STT (audio flow)
✓ STT → NLU (transcription → intent)
✓ NLU → State (intent → action)
✓ State → TTS (response → audio)
✓ Orchestrator → Verticals
✓ Voice Agent → WhatsApp API
✓ Voice Agent → VoIP EhiWeb
✓ Frontend → Voice Agent (192.168.1.7:3002)

TEST API:
- POST /api/voice/process (text)
- POST /api/voice/process (audio)
- POST /api/voice/tts
- GET /api/verticals/{name}/config
- GET /health

VERIFICA: Tutte le API rispondono correttamente
```

### SKILL 6: DEPLOY_MANAGER
```
TASK: Deploy su iMac e verifica live

DEPLOY STEPS:
1. SSH to 192.168.1.7
2. cd /Volumes/MacSSD\ -\ Dati/fluxion
3. git pull origin master
4. cd voice-agent
5. pip install -r requirements.txt
6. pkill -f "python.*main.py"
7. sleep 2
8. export GROQ_API_KEY=...
9. nohup python main.py --port 3002 > logs/voice-agent.log 2>&1 &

POST-DEPLOY VERIFICATION:
1. curl http://192.168.1.7:3002/health
2. python scripts/smoke_test.py
3. python scripts/test_cross_machine.py
4. Latenza benchmark < 800ms

ROLLBACK: Se qualsiasi verifica fallisce
```

---

## 📋 CHECKLIST COVE VERIFICATION

Per ogni fase, verifica questi criteri:

### Fase 1: Analisi
- [ ] gap_analysis.json generato
- [ ] Lista completa verticali mancanti
- [ ] Lista skill da implementare
- [ ] Lista test mancanti

### Fase 2: Verticali
- [ ] 4 verticali generati
- [ ] Ogni verticale ha config.py
- [ ] Ogni verticale ha intents.py
- [ ] Ogni verticale ha entities.py
- [ ] Ogni verticale ha schema.py
- [ ] Ogni verticale ha faqs.json

### Fase 3: Test
- [ ] Unit test per ogni skill
- [ ] Integration test per ogni coppia
- [ ] E2E test per ogni verticale
- [ ] Coverage ≥ 90%

### Fase 4: Debug
- [ ] 0 test falliti
- [ ] 58/58 test passati

### Fase 5: Integrazione
- [ ] Pipeline VAD→STT→NLU→State→TTS OK
- [ ] WhatsApp API OK
- [ ] VoIP EhiWeb OK
- [ ] Frontend cross-machine OK

### Fase 6: Deploy
- [ ] Deploy su iMac riuscito
- [ ] Health check OK
- [ ] Smoke test OK
- [ ] Latenza < 800ms

---

## 🚀 WORKFLOW ESECUZIONE

```yaml
workflow: VoiceAgent_100_Percent
version: 1.0

phase_1_analyze:
  skill: CODE_ANALYZER
  input: [voice-agent/, SUB-PRD-VOICE-AGENT-ENTERPRISE.md]
  output: gap_analysis.json
  verify: gap_analysis.json exists and not empty
  
phase_2_verticals:
  parallel:
    - skill: VERTICAL_GENERATOR
      name: salone
    - skill: VERTICAL_GENERATOR
      name: medical
    - skill: VERTICAL_GENERATOR
      name: palestra
    - skill: VERTICAL_GENERATOR
      name: auto
  verify: 
    - verticals/salone/config.py exists
    - verticals/medical/config.py exists
    - verticals/palestra/config.py exists
    - verticals/auto/config.py exists
    
phase_3_tests:
  skill: TEST_GENERATOR
  input: gap_analysis.json
  output: tests/ directory completa
  verify:
    - tests/skills/ exists
    - tests/integration/ exists
    - tests/e2e/ exists
    
phase_4_debug:
  skill: DEBUG_FIXER
  loop: until tests pass
  condition: test failures > 0
  max_iterations: 50
  verify:
    - pytest tests/ -v returns 0
    - 58/58 tests passed
    
phase_5_integration:
  skill: INTEGRATION_TESTER
  test: all
  verify:
    - All API endpoints OK
    - WhatsApp integration OK
    - VoIP integration OK
    
phase_6_deploy:
  skill: DEPLOY_MANAGER
  target: 192.168.1.7
  verify:
    - curl http://192.168.1.7:3002/health OK
    - smoke_test.sh OK
    - test_cross_machine.py OK
    - latency < 800ms
```

---

## 🎬 PROMPT DI ESECUZIONE

Copia e incolla questo prompt per eseguire:

```markdown
## ESECUZIONE COVE: Voice Agent 100%

Sei il CoVe Orchestrator. Esegui il workflow completo.

### CONTESTO
- Repository: /Volumes/MontereyT7/FLUXION
- iMac: 192.168.1.7
- Branch: master
- Stato iniziale: 58/58 test passati, URL fixato, restaurant eliminato

### FASE 1: ANALISI
Esegui SKILL:CODE_ANALYZER
- Input: voice-agent/, SUB-PRD-VOICE-AGENT-ENTERPRISE.md
- Output: /tmp/gap_analysis.json

Attendi completamento, poi procedi.

### FASE 2: GENERAZIONE VERTICALI (PARALLELO)
Esegui in parallelo:
- SKILL:VERTICAL_GENERATOR --name salone
- SKILL:VERTICAL_GENERATOR --name medical
- SKILL:VERTICAL_GENERATOR --name palestra
- SKILL:VERTICAL_GENERATOR --name auto

Ogni verticale deve avere:
- config.py con services, slots, greeting
- intents.py con pattern regex
- entities.py con entity extractor
- schema.py con dataclass cliente
- faqs.json con FAQ settore

### FASE 3: GENERAZIONE TEST
Esegui SKILL:TEST_GENERATOR
- Genera unit tests per tutte le skill
- Genera integration tests
- Genera E2E tests per ogni verticale
- Target coverage: 90%

### FASE 4: DEBUG LOOP
Esegui ciclo:
1. pytest tests/ -v --tb=short
2. Se test falliti → SKILL:DEBUG_FIXER --auto-apply
3. Ripeti finché 58/58 test non passano

Max 50 iterazioni.

### FASE 5: INTEGRATION TEST
Esegui SKILL:INTEGRATION_TESTER --all
Verifica:
- Pipeline audio completa
- API WhatsApp
- API VoIP EhiWeb
- Frontend cross-machine

### FASE 6: DEPLOY
Esegui SKILL:DEPLOY_MANAGER --deploy --target 192.168.1.7
Verifica post-deploy:
- curl http://192.168.1.7:3002/health
- python scripts/smoke_test.py
- python scripts/test_cross_machine.py

### CRITERI DI SUCCESSO
- [ ] gap_analysis.json generato
- [ ] 4 verticali creati
- [ ] 58/58 test passati
- [ ] Integration tests OK
- [ ] Deploy su iMac OK
- [ ] Health check OK
- [ ] Latenza < 800ms

ESEGUI ORA. REPORTA PROGRESSO AD OGNI FASE.
```

---

## 📊 FORMATO REPORT

Per ogni fase, reporta in questo formato:

```markdown
## FASE X: {NOME_FASE}
**Status**: ✅ Completato | 🔄 In corso | ❌ Fallito
**Durata**: {X} minuti

### Output
- {file/risultato generato}

### Verifica CoVe
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

### Prossima Azione
{descrizione prossima fase}
```

---

## 🚨 HANDLING ERRORI

Se una fase fallisce:

1. **Retry automatico** (max 3 tentativi)
2. **Fallback a strategia alternativa**
3. **Escalation a umano** se ancora fallito

```
IF phase.status == FAILED AND retries < 3:
    retry_phase()
ELIF phase.status == FAILED:
    try_alternative_strategy()
ELSE:
    escalate_to_human()
```

---

## ✅ DEFINIZIONE "COMPLETATO"

Il Voice Agent è **COMPLETATO** quando:

```python
assert verticals_count == 4  # salone, medical, palestra, auto
assert test_passed == 58
assert test_failed == 0
assert latency_p95 < 800  # ms
assert whatsapp_integration == True
assert voip_integration == True
assert health_check == "ok"
assert cross_machine_test == "passed"

print("✅ Voice Agent Enterprise v3.0 COMPLETATO")
```

---

**FINE PROMPT. ESEGUI ORA.**
