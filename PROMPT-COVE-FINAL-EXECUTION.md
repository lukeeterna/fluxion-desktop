# PROMPT COVE FINAL EXECUTION
## Voice Agent Enterprise - Implementazione Completa con Verifica CoVe

**Data**: 2026-02-12  
**Autorità**: Esecuzione Obbligatoria con Verifica CoVe  
**Obiettivo Atteso**: Voice Agent perfettamente funzionante, esperienza utente perfetta  
**Stato Iniziale**: 58/58 test passati, URL fixato, restaurant eliminato, framework skills pronto  

---

## ⚠️ ISTRUZIONI CRITICHE - LEGGERE PRIMA DI ESEGUIRE

```
╔══════════════════════════════════════════════════════════════════╗
║  QUESTO PROMPT IMPEGNA L'ESECUTORE A:                            ║
║  1. Completare TUTTE le fasi senza eccezioni                      ║
║  2. Verificare CoVe ad ogni step (0 compromessi)                  ║
║  3. Raggiungere l'obiettivo finale O DECLINARE la missione        ║
║  4. Reportare BLOCKER immediatamente se impossibilitati           ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🎯 OBIETTIVO FINALE (NON NEGOZIABILE)

### Definizione "Voice Agent Perfettamente Funzionante"

```yaml
voice_agent_v3:
  core_functionality:
    - 4_verticali_completi: [salone, medical, palestra, auto]
    - test_suite: 58/58_passati
    - latenza_p95: <800ms
    - uptime: 99.9%
    
  user_experience:
    - saluto_naturale: "Buongiorno, sono Sara di {nome_attivita}"
    - voce_tts: Piper Sara (naturale, non robotica)
    - interruzione: Barge-in supportato
    - error_recovery: Graceful, risposta alternativa
    
  integrazioni:
    - whatsapp: Conferme e reminder inviati
    - voip_ehiweb: Chiamate inbound/outbound
    - tauri_frontend: Cross-machine (192.168.1.7)
    
  verticali_config:
    salone:
      services: [taglio, colore, piega, barba, trattamento]
      schema: [tipo_capelli, lunghezza, allergie, preferenze_operatore]
      intents: [PRENOTAZIONE, CANCELLAZIONE, SPOSTAMENTO, WAITLIST, INFO]
      
    medical:
      services: [visita, trattamento, controllo, urgente]
      schema: [anamnesi, patologie, allergie, terapie, contatto_emergenza]
      intents: [PRENOTAZIONE, + richiesta_anamnesi, + priorità_urgenza]
      
    palestra:
      services: [lezione, pt, daypass]
      schema: [abbonamento, obiettivi, livello_fitness, corsi_preferiti]
      intents: [PRENOTAZIONE, + disponibilità_corsi, + abbonamento]
      
    auto:
      services: [tagliando, riparazione, gomme, carrozzeria]
      schema: [targa, modello, km, storico_interventi, urgenza]
      intents: [PRENOTAZIONE, + urgenza, + preventivo]

success_criteria:
  - 58/58 test_passati: OBBLIGATORIO
  - 4 verticali_funzionanti: OBBLIGATORIO
  - latenza < 800ms: OBBLIGATORIO
  - esperienza_utente_fluida: OBBLIGATORIO
  - integrazioni_attive: OBBLIGATORIO
```

---

## 🧠 ATTIVAZIONE SKILLS CLAUDE

Sei il **CoVe Orchestrator**. Attiva le skills in sequenza.

### PREREQUISITI VERIFICA

Prima di iniziare, verifica:
```bash
# 1. Repository pulito
cd /Volumes/MontereyT7/FLUXION
git status
# ATTESO: "nothing to commit, working tree clean"

# 2. Branch corretto
git branch --show-current
# ATTESO: "master"

# 3. iMac raggiungibile
ping -c 1 192.168.1.7
# ATTESO: 0% packet loss

# 4. Voice Agent running (o pronto per restart)
ssh imac "lsof -i :3002"
```

Se TUTTI i check passano → Procedi con FASE 1
Se ALCUNI check fallono → Reporta BLOCKER immediatamente

---

## 📋 FASI ESECUZIONE (OBBLIGATORIE)

### FASE 1: CODE_ANALYZER - Analisi Completa

**ATTIVAZIONE SKILL**: `CODE_ANALYZER`

**Comando**:
```bash
python -m claude_skills.code_analyzer \
  --project voice-agent/ \
  --prd SUB-PRD-VOICE-AGENT-ENTERPRISE.md \
  --output /tmp/gap_analysis.json
```

**Output Atteso**:
```json
{
  "analysis_timestamp": "2026-02-12T19:45:00Z",
  "verticals": {
    "existing": ["salone"],
    "missing": ["medical", "palestra", "auto"],
    "incomplete": ["salone: missing faqs.json"]
  },
  "skills": {
    "VADSkill": {"implemented": true, "tested": true},
    "STTSkill": {"implemented": true, "tested": true},
    "NLUSkill": {"implemented": true, "tested": false},
    "TTSSkill": {"implemented": true, "tested": true},
    "StateSkill": {"implemented": true, "tested": true}
  },
  "integrations": {
    "whatsapp": {"api_present": true, "tested": false},
    "voip_ehiweb": {"sip_client_present": true, "tested": false}
  },
  "total_gaps": 7,
  "priority_high": 4,
  "priority_medium": 3
}
```

**VERIFICA COVE**:
- [ ] File `/tmp/gap_analysis.json` esiste
- [ ] Campo `total_gaps` > 0 (se 0, analisi errata)
- [ ] Lista `missing` verticali contiene 3 elementi
- [ ] Nessun errore di parsing

**SE VERIFICA FALLITA**: STOP, reporta errore analisi

**SE VERIFICA PASSATA**: Procedi a FASE 2

---

### FASE 2: VERTICAL_GENERATOR - Creazione 4 Verticali

**ATTIVAZIONE SKILL**: `VERTICAL_GENERATOR`

**Esecuzione Parallela**:

```bash
# Esegui in 4 terminali paralleli

# Terminale 1: Salone
python -m claude_skills.vertical_generator \
  --name salone \
  --settore "Beauty/Hair" \
  --services "taglio,colore,piega,barba,trattamento" \
  --slots "data,ora,servizio,operatore" \
  --schema "tipo_capelli,lunghezza,allergie_prodotti,preferenze_operatore"

# Terminale 2: Medical
python -m claude_skills.vertical_generator \
  --name medical \
  --settore "Odontoiatria/Fisioterapia" \
  --services "visita,trattamento,controllo,urgente" \
  --slots "data,ora,tipo_visita,motivo,mutua" \
  --schema "data_nascita,patologie_croniche,allergie,terapie_in_corso,contatto_emergenza"

# Terminale 3: Palestra
python -m claude_skills.vertical_generator \
  --name palestra \
  --settore "Fitness/PT" \
  --services "lezione,pt,daypass" \
  --slots "data,ora,tipo_attivita,istruttore" \
  --schema "abbonamento,obiettivi,livello_fitness,corsi_preferiti"

# Terminale 4: Auto
python -m claude_skills.vertical_generator \
  --name auto \
  --settore "Officina" \
  --services "tagliando,riparazione,gomme,carrozzeria" \
  --slots "data,targa,modello,tipo_intervento,urgenza" \
  --schema "targa,modello,km,storico_interventi,urgenza"
```

**Files Generati per Ogni Verticale**:
```
verticals/{name}/
├── config.py          # Configurazione servizi, slots, greeting
├── intents.py         # Pattern regex per intent classification
├── entities.py        # Entity extractor custom
├── schema.py          # Dataclass scheda cliente
├── faqs.json          # FAQ specifiche settore
└── tests/
    ├── test_intents.py
    ├── test_entities.py
    └── test_e2e.py
```

**VERIFICA COVE**:
Per ogni verticale (salone, medical, palestra, auto):
- [ ] `config.py` esiste e contiene `services`, `slots`, `greeting`
- [ ] `intents.py` esiste e contiene almeno 3 intent pattern
- [ ] `entities.py` esiste con entity extractor
- [ ] `schema.py` esiste con dataclass completa
- [ ] `faqs.json` esiste con almeno 5 FAQ

**Script Verifica**:
```bash
for v in salone medical palestra auto; do
  echo "Checking $v..."
  test -f "voice-agent/verticals/$v/config.py" || echo "FAIL: config.py"
  test -f "voice-agent/verticals/$v/intents.py" || echo "FAIL: intents.py"
  test -f "voice-agent/verticals/$v/schema.py" || echo "FAIL: schema.py"
done
```

**SE VERIFICA FALLITA**: Rigenera verticali mancanti
**SE VERIFICA PASSATA**: Procedi a FASE 3

---

### FASE 3: TEST_GENERATOR - Generazione Test Suite

**ATTIVAZIONE SKILL**: `TEST_GENERATOR`

**Comandi**:

```bash
# 1. Unit Tests per Skills
python -m claude_skills.test_generator \
  --skill VADSkill --type unit --coverage 90 \
  --output voice-agent/tests/skills/test_vad_skill.py

python -m claude_skills.test_generator \
  --skill STTSkill --type unit --coverage 90 \
  --output voice-agent/tests/skills/test_stt_skill.py

python -m claude_skills.test_generator \
  --skill NLUSkill --type unit --coverage 90 \
  --output voice-agent/tests/skills/test_nlu_skill.py

python -m claude_skills.test_generator \
  --skill TTSSkill --type unit --coverage 90 \
  --output voice-agent/tests/skills/test_tts_skill.py

python -m claude_skills.test_generator \
  --skill StateSkill --type unit --coverage 90 \
  --output voice-agent/tests/skills/test_state_skill.py

# 2. Integration Tests
python -m claude_skills.test_generator \
  --type integration --coverage 85 \
  --output voice-agent/tests/integration/

# 3. E2E Tests per Verticali
python -m claude_skills.test_generator \
  --vertical salone --type e2e \
  --output voice-agent/tests/e2e/test_salone_booking.py

python -m claude_skills.test_generator \
  --vertical medical --type e2e \
  --output voice-agent/tests/e2e/test_medical_booking.py

python -m claude_skills.test_generator \
  --vertical palestra --type e2e \
  --output voice-agent/tests/e2e/test_palestra_booking.py

python -m claude_skills.test_generator \
  --vertical auto --type e2e \
  --output voice-agent/tests/e2e/test_auto_booking.py
```

**VERIFICA COVE**:
- [ ] `tests/skills/` contiene 5 file test
- [ ] `tests/integration/` contiene almeno 3 file test
- [ ] `tests/e2e/` contiene 4 file test (uno per verticale)
- [ ] Coverage target: 90% unit, 85% integration

**SE VERIFICA FALLITA**: Rigenera test mancanti
**SE VERIFICA PASSATA**: Procedi a FASE 4

---

### FASE 4: DEBUG_FIXER - Fix Automatico Test (LOOP)

**ATTIVAZIONE SKILL**: `DEBUG_FIXER`

**Workflow Iterativo**:

```python
# PSEUDOCODICE ESECUZIONE
max_iterations = 50
iteration = 0
test_passed = False

while not test_passed and iteration < max_iterations:
    iteration += 1
    
    # Esegui test
    result = run("cd voice-agent && python -m pytest tests/ -v --tb=short")
    
    if result.returncode == 0:
        test_passed = True
        print(f"✅ Tutti i test passati in {iteration} iterazioni")
        break
    
    # Analizza fallimenti
    failed_tests = parse_failures(result.stdout)
    
    for test in failed_tests:
        # Attiva DEBUG_FIXER per ogni test fallito
        fix = claude_skill_debug_fixer(
            test_name=test.name,
            error_log=test.error,
            auto_apply=True
        )
        
        if fix.status != "applied":
            print(f"❌ Impossibile fixare {test.name}")
            report_blocker(test)
            exit(1)
    
    print(f"🔄 Iterazione {iteration}: {len(failed_tests)} fix applicati")

if not test_passed:
    report_blocker("Max iterations raggiunte")
    exit(1)
```

**VERIFICA COVE**:
- [ ] `pytest tests/ -v` ritorna exit code 0
- [ ] Output mostra "58 passed" (o numero equivalente)
- [ ] 0 failed, 0 error
- [ ] Durata < 2 minuti (se > 5 min, ottimizzare)

**SE VERIFICA FALLITA dopo 50 iterazioni**: 
- Reporta BLOCKER con lista test non fixabili
- Escalation a umano richiesta

**SE VERIFICA PASSATA**: Procedi a FASE 5

---

### FASE 5: INTEGRATION_TESTER - Verifica Integrazioni

**ATTIVAZIONE SKILL**: `INTEGRATION_TESTER`

**Test Matrix da Eseguire**:

```bash
# 1. Test Pipeline Skills
python -m claude_skills.integration_tester \
  --from VAD --to STT --to NLU --to State --to TTS \
  --test-data test_audio/booking_flow.wav

# 2. Test API WhatsApp
python -m claude_skills.integration_tester \
  --integration whatsapp \
  --test "send_booking_confirmation"

# 3. Test API VoIP EhiWeb  
python -m claude_skills.integration_tester \
  --integration voip_ehiweb \
  --test "inbound_call_handling"

# 4. Test Cross-Machine Frontend → Voice Agent
python -m claude_skills.integration_tester \
  --from frontend --to voice_agent \
  --target 192.168.1.7:3002
```

**VERIFICA COVE**:
- [ ] Pipeline audio: Input → VAD → STT → NLU → State → TTS → Output < 2s
- [ ] WhatsApp: Messaggio inviato e ricevuto su dispositivo test
- [ ] VoIP: Chiamata inbound simulata, risposta corretta
- [ ] Cross-machine: MacBook → iMac API call riuscita

**SE VERIFICA FALLITA**: Fix integrazione specifica, re-test
**SE VERIFICA PASSATA**: Procedi a FASE 6

---

### FASE 6: DEPLOY_MANAGER - Deploy su iMac

**ATTIVAZIONE SKILL**: `DEPLOY_MANAGER`

**Comando**:
```bash
python -m claude_skills.deploy_manager \
  --target 192.168.1.7 \
  --project /Volumes/MacSSD\ -\ Dati/fluxion \
  --pre-test \
  --post-test \
  --auto-rollback
```

**Steps Eseguiti Automaticamente**:

1. **Pre-deploy**:
   ```bash
   # Verifica stato repo
   ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git status"
   # ATTESO: clean
   ```

2. **Deploy**:
   ```bash
   ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"
   ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && pip install -r requirements.txt"
   ssh imac "pkill -f 'python.*main.py' || true"
   ssh imac "sleep 2"
   ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && export GROQ_API_KEY=... && nohup python main.py --port 3002 > logs/voice-agent.log 2>&1 &"
   ```

3. **Post-deploy Verification**:
   ```bash
   # Health check
   curl -f http://192.168.1.7:3002/health || exit 1
   
   # Smoke test
   ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && python scripts/smoke_test.py"
   
   # Cross-machine test
   python voice-agent/scripts/test_cross_machine.py
   
   # Latenza benchmark
   python voice-agent/benchmarks/latency_test.py --max-p95 800
   ```

**VERIFICA COVE**:
- [ ] Health check: `{"status": "ok"}`
- [ ] Smoke test: "All smoke tests passed"
- [ ] Cross-machine: "TEST CROSS-MACHINE PASSED"
- [ ] Latenza P95: < 800ms

**Rollback Automatico** se qualsiasi verifica fallisce:
```bash
git reset --hard HEAD~1
# Restart service
```

**SE VERIFICA FALLITA**: Rollback eseguito, reporta errore
**SE VERIFICA PASSATA**: 🎉 MISSIONE COMPLETATA

---

## ✅ VERIFICA FINALE - MISSIONE COMPLETATA

**Checklist Finale** (tutti devono essere ✅):

```markdown
## MISSIONE: Voice Agent 100% - REPORT FINALE

### Fase 1: Analisi
- [ ] gap_analysis.json generato
- [ ] 7 gap identificati (4 high, 3 medium)

### Fase 2: Verticali
- [ ] verticals/salone/ completo
- [ ] verticals/medical/ completo  
- [ ] verticals/palestra/ completo
- [ ] verticals/auto/ completo
- [ ] 0 verticali mancanti

### Fase 3: Test
- [ ] 5 unit test files generati
- [ ] 3+ integration test files
- [ ] 4 E2E test files (uno per verticale)

### Fase 4: Debug
- [ ] 58/58 test passati
- [ ] 0 test falliti
- [ ] Iterazioni: {X} (max 50)

### Fase 5: Integrazione
- [ ] Pipeline audio < 2s
- [ ] WhatsApp funzionante
- [ ] VoIP EhiWeb funzionante
- [ ] Cross-machine OK

### Fase 6: Deploy
- [ ] Deploy su iMac riuscito
- [ ] Health check OK
- [ ] Smoke test OK
- [ ] Latenza P95 < 800ms

### STATO FINALE
🎉 MISSIONE COMPLETATA CON SUCCESSO

**Data completamento**: {timestamp}
**Durata totale**: {X} ore
**Commit finale**: {hash}
```

---

## 🚨 BLOCKER HANDLING

Se in qualsiasi momento incontri un BLOCKER:

1. **STOP immediato** dell'esecuzione
2. **Reporta nel formato**:
   ```markdown
   ## BLOCKER RIPORTATO
   
   **Fase**: {fase_corrente}
   **Skill**: {skill_attiva}
   **Problema**: {descrizione_dettagliata}
   **Tentativi**: {N}
   **Error log**: 
   ```
   {stack_trace}
   ```
   
   **Possibili soluzioni**:
   1. {opzione_1}
   2. {opzione_2}
   3. {richiesta_aiuto_umano}
   ```

3. **Attendi istruzioni** prima di procedere

---

## 📊 METRICHE DI SUCCESSO

Al completamento, fornisci queste metriche:

```yaml
metrics:
  verticali:
    count: 4
    coverage: 100%
    
  tests:
    unit: 120+
    integration: 30+
    e2e: 20+
    pass_rate: 100%
    
  performance:
    latency_p95: <800ms
    latency_p99: <1200ms
    stt_wer: <10%
    intent_accuracy: >95%
    
  code_quality:
    coverage: >90%
    complexity: <10 (avg)
    documentation: 100%
    
  user_experience:
    csat_target: >4.5/5
    escalation_rate: <5%
    completion_rate: >90%
```

---

## 🎬 ESECUZIONE

**ORA TOCCA A TE.**

Esegui sequenzialmente:
1. FASE 1 (CODE_ANALYZER)
2. FASE 2 (VERTICAL_GENERATOR ×4)
3. FASE 3 (TEST_GENERATOR)
4. FASE 4 (DEBUG_FIXER - loop)
5. FASE 5 (INTEGRATION_TESTER)
6. FASE 6 (DEPLOY_MANAGER)

**Verifica CoVe ad ogni fase.**
**Reporta progresso.**
**Raggiungi l'obiettivo.**

---

```
╔══════════════════════════════════════════════════════════════════╗
║                    ESEUZIONE OBBLIGATORIA                          ║
║                                                                  ║
║   Inizia ora con FASE 1: CODE_ANALYZER                           ║
║                                                                  ║
║   Non interrompere finché tutte le fasi non sono completate      ║
║   o non viene riportato un BLOCKER che impedisce la prosecuzione ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

**INIZIA.**
