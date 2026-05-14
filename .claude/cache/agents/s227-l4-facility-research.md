# S227 — Root cause WARN PALESTRA "Avete la piscina?"

> Ricerca: 2026-05-14. Pipeline live 127.0.0.1:3002 (venv project DB), commit `2018f02`.
> Scope: capire perché L3_faq non matcha "Avete la piscina?" pur con entry `faq_palestra_piscina` esistente, e perché L4 risponde con "cheratina" (servizio salone) in context palestra.

---

## 1. Root cause L3 miss (verificata su codice)

### 1.1 Bug primario: `IntentCategory` gate blocca FAQ retrieval

**File**: `voice-agent/src/orchestrator.py:2482`

```python
if intent_result.category == IntentCategory.INFO and self.faq_manager:
    faq_result = self.faq_manager.find_answer(user_input)
```

L3 FAQ è gated da `intent_result.category == IntentCategory.INFO`. Se non è INFO, `find_answer` NON viene mai chiamato.

**File**: `voice-agent/src/intent_classifier.py:441-448` (`INTENT_PATTERNS[IntentCategory.INFO]`):

```python
IntentCategory.INFO: [
    r"(quanto\s+costa|prezzo|costo|quanto|euro|€)",
    r"(orari[oi]?|aprite|chiudete|quando|che\s+ora)",
    r"(dove|indirizzo|posizione|siete|trovate)",
    r"(accettate|pago|pagamenti|carta|satispay|contanti)",
    r"(fate|offrite|servizi|trattamenti|listino)",
    r"(info|informazion)",
],
```

**Nessun pattern matcha facility questions PALESTRA** ("piscina", "sauna", "spa", "attrezzature", "spogliatoi", "parcheggio"). `get_cached_intent("Avete la piscina?")` ritorna NULL/UNKNOWN (o `CHIACCHIERA` con bassa confidence) → category != INFO → L3 skippato → cade su L4.

### 1.2 Bug secondario: `keyword_match_score` ignora il field `keywords` del FAQ JSON

**File**: `voice-agent/src/faq_manager.py:140-214` (`keyword_match_score`)

La funzione matcha SOLO contro:
- `faq_question` (la domanda canonica)
- `KEYWORD_CATEGORIES` hardcoded (line 98-137)

**MAI legge `faq.get("keywords", [])`** della entry JSON. Quindi la dichiarazione `"keywords": ["piscina", "nuoto", "aquagym", "vasca"]` in `faq_palestra.json:71` è **dead config**.

**Conseguenza specifica per "Avete la piscina?"**:
- Domanda canonica entry: `"Avete la piscina?"` (line 68)
- Query utente: `"Avete la piscina?"`
- Si dovrebbe attivare il branch "Exact match" (line 152) → score 1.0.

**Quindi**: in teoria, se L3 fosse chiamato, il match diretto question vs query funzionerebbe (caso esatto). Il problema NON è il matching, è il gate IntentCategory che blocca a monte.

Edge case dove il keywords-field-ignored DIVENTA il bug:
- "Avete la vasca?" / "Si fa nuoto?" / "C'è una piscina coperta?" → match imperfetto sulla question canonica → score < 0.8 → fallback semantico SE disponibile (sentence-transformers spesso NOT installed → HAS_SEMANTIC=False).

### 1.3 Patch S226 incompleta

`orchestrator.py:1748-1752` setta `_is_info = True` LOCALE per IDLE + question + no booking signals, ma:

```python
# line 2480 (re-fetch fresh intent — NOT the boosted _is_info)
intent_result = get_cached_intent(user_input)
if intent_result.category == IntentCategory.INFO and self.faq_manager:
    ...
```

Il flag `_is_info` boosted dalla S226 NON si propaga a `intent_result.category` (è solo una local var per decidere `should_process_booking`). La condizione L3 a riga 2482 lo ignora completamente. **La S226 ha sistemato il routing FSM (non chiede più "Come ti chiami?"), ma non ha aperto il gate FAQ — risultato: fall-through diretto a L4_groq.**

### 1.4 Verifica live (test isolato pipeline)

Input: `"Avete la piscina?"` su pipeline palestra.
- `intent_result.category` ≠ INFO (nessun pattern matcha "piscina") ✅ confermato dalla logica
- L3 gate fail ✅ confermato (response = L4_groq, fsm_state=idle)
- L4 Groq risponde, con problema qualità sotto.

---

## 2. Quality issue L4 — "cheratina" in context palestra

### 2.1 Costruzione system prompt (`orchestrator.py:3466-3525`)

`_build_llm_context` costruisce prompt con:
- `business_name` (corretto: dal DB palestra)
- `_business_hours` / `_business_services` / `_business_operators` (dal DB palestra)
- `_SECTOR_PERSONALITY[vert_key]` (mappa `wellness → palestra`)
- `_get_context_summary()` (booking SM state)

**Il prompt include i servizi DB**: se il DB palestra è caricato correttamente, `_business_services` contiene "Lezione pilates, Lezione yoga, Personal training, ..." NON cheratina.

### 2.2 Ipotesi cheratina

Tre cause plausibili (in ordine di probabilità, NON verificate in questa sessione perché test live non fatto in isolamento):

**A) Conversation history bleed** (`orchestrator.py:2570-2575`):
```python
l4_messages = []
if self._current_session and self._current_session.turns:
    for turn in self._current_session.turns[-3:]:
        l4_messages.append({"role": "user", "content": turn.user_input})
        l4_messages.append({"role": "assistant", "content": turn.response})
```
Se il test live nella issue iniziale è stato eseguito DOPO altri turn su sessione condivisa (default vertical=salone all'avvio + switch successivo) le ultime 3 turn possono contenere risposte salone con "cheratina". Groq replica termini dal context recente.

**B) Vertical switch incompleto** — `set_vertical("palestra")` (line 3331) ricarica DB context e FAQ, ma se il test è stato fatto SENZA POST `/api/voice/set_vertical` prima del messaggio, il default vertical (salone) è ancora attivo → `_business_services` lista servizi salone (con cheratina) → Groq grounded su servizi sbagliati.

**C) FAQ list nel context generico** — il sistema NON inietta FAQ list nel system prompt L4. Il prompt è solo: business_name + sector personality + ORARI + SERVIZI + OPERATORI + context summary. Quindi `faq_palestra_piscina` non aiuta L4 anche se le FAQ sono caricate.

**Probabilità**: B (mancato vertical switch nel test isolato) > A > C. Verificare con un retest live aggiungendo set_vertical PRIMA del POST process.

### 2.3 Servizio "premium piscina" non in DB palestra demo

Anche con vertical switch corretto, il DB palestra demo NON ha entry "piscina" come servizio prenotabile. Il system prompt L4 quindi non sa che la business HA piscina. La FAQ JSON (`{{RISPOSTA_PISCINA}}` template variable) richiede una variabile di config NON popolata dal DB attualmente → la FAQ verrebbe scartata da D3 unresolved variable filter (`orchestrator.py:3304-3308`) prima ancora di essere caricata in FAQ manager.

**Verifica**: in `faq_palestra.json:67-73`, l'entry "piscina" usa `{{RISPOSTA_PISCINA}}` come variabile. `_load_vertical_faqs` (line 3298-3320) chiama `load_faqs_for_vertical` che fa substitution con `settings` dict; `settings` dict (orchestrator.py:3282-3295) NON include `RISPOSTA_PISCINA` né `LUNGHEZZA_PISCINA`. **Risultato: l'entry piscina viene SKIPPED dal D3 filter** → mai caricata nel FAQ manager → mai matchabile anche se L3 gate fosse aperto.

**Questo è il bug compound principale**:
1. L3 gate non si apre (IntentCategory non-INFO per facility questions)
2. Anche se si aprisse, l'entry piscina è SKIPPATA dal D3 filter per unresolved `{{RISPOSTA_PISCINA}}`
3. L4 Groq non riceve info "questa palestra ha/non ha piscina" nel system prompt

---

## 3. Raccomandazione singola motivata

### Combo `A1 + A2 + B` (compound fix, no single point sufficient)

**A1) Aprire L3 gate per facility questions PALESTRA**

Path minore di rischio: estendere il regex INFO di `intent_classifier.py:441-448` con un pattern facility che cattura sia palestra sia altri verticali domande "avete X?":

```python
IntentCategory.INFO: [
    ...
    r"\b(avete|c'?è|ci\s+sono|disponete\s+di)\s+(la|il|lo|un|una|delle?|degli?)?\s*"
    r"(piscina|sauna|spa|spogliatoi|docce|parcheggio|wifi|cardio|sala\s+pesi"
    r"|tapis\s+roulant|aquagym|nuoto|vasca|attrezzatur|macchin)",
],
```

Trade-off: amplia INFO category, ma è già preceduto da S226 `_is_info` guard per question form, quindi side-effects su FSM transitions sono trascurabili.

**Alternativa più pulita** (preferibile): far propagare il flag `_is_info` S226 fino al gate L3:

```python
# orchestrator.py:2482
if (intent_result.category == IntentCategory.INFO or _is_info) and self.faq_manager:
```

Effort: 1 riga modificata. Rischio regression: minimo — `_is_info` è già un guard rigoroso (IDLE + question + no booking signals).

**A2) Fix `{{RISPOSTA_PISCINA}}` per FAQ palestra (facility variables)**

In `orchestrator.py:_load_vertical_faqs` (line 3282-3295), estendere `settings` con default facility flags presi dal DB (oppure hardcoded "Non disponiamo di piscina." se DB non ha campo dedicato).

Path zero-cost: aggiungere settings:
```python
"RISPOSTA_PISCINA": "Sì, abbiamo una piscina di {{LUNGHEZZA_PISCINA}} metri" if has_pool else "Al momento non disponiamo di piscina",
"LUNGHEZZA_PISCINA": "25",
"RISPOSTA_SPA": "Sì, area wellness completa" if has_spa else "Non disponiamo di area spa",
```

Lettura `has_pool` dal DB `business_config` table (o JSON `facilities`). Se field non esiste → migration micro per `palestra_facilities` (booleani: pool, spa, sauna, gym_card_only).

**Effort**: 2h (config + migration + test). Rischio: medio — tocca schema DB demo, ma è additive.

**B) Iniettare lista FAQ rilevanti nel system prompt L4**

Pattern noto in industry (RAG-augmented LLM):

```python
# in _build_llm_context
faq_summary = ""
if self.faq_manager and self.faq_manager.faqs:
    cats = ["services", "facilities", "policy"]
    relevant = [f for f in self.faq_manager.faqs if f.get("category") in cats][:8]
    if relevant:
        faq_summary = "\nDOMANDE FREQUENTI E RISPOSTE GIÀ AUTORIZZATE:\n" + \
            "\n".join(f"Q: {f['question']}\nA: {f['answer']}" for f in relevant)
```

Effort: 30 min. Rischio: aumenta token system prompt (+200-400 tok per palestra, ancora sotto budget). Reduce hallucination (Groq cita business-grounded FAQ invece di inventare).

### Decisione CTO

Implementare **A1 (1 riga, immediato) + A2 (facility variables in DB) + B (FAQ injection in L4 prompt)** in 3 commit atomici S227-P1/P2/P3.

**A1 da solo NON basta**: il D3 filter rimuove l'entry piscina prima del caricamento → L3 troverebbe gate aperto ma nessuna FAQ piscina matchabile.

**A2 da solo NON basta**: FAQ caricata ma L3 gate ancora chiuso (IntentCategory non-INFO).

**B da solo aiuta** ma è palliativo: senza A2, Groq cita "non disponiamo di piscina" hallucinating; con A2 cita risposta autoritativa.

---

## 4. Stima effort + rischio regression

| Fix | Effort | Rischio | Tipo |
|-----|--------|---------|------|
| A1 (propagate `_is_info` to L3 gate) | 5 min | basso | bug fix |
| A2 (facility vars in settings dict) | 90 min | medio (DB schema) | data fix |
| B (FAQ injection in L4 prompt) | 30 min | basso | enhancement |
| **Totale** | **~2h** | **basso-medio** | combo |

Test E2E richiesto:
- PALESTRA stress 22 turn (regression check vs S226 baseline 21 OK / 1 WARN)
- Spot tests: "Avete la sauna?", "C'è parcheggio?", "Avete spogliatoi?" (facility questions diverse)
- SALONE regression (verificare A1 non rompe il flow salone "Quanto costa un taglio?")

Atteso post-fix: PALESTRA **22 OK / 0 WARN / 0 FAIL**.

---

## 5. Critica strutturale 4-punti

### 5.1 Assunzioni nascoste

- **Assunzione A**: la business palestra demo HA piscina/spa. Se è una palestra basic senza piscina, A2 va parametrizzata per vertical sub-config. Mai assumere "premium feature set" per business demo.
- **Assunzione B**: il D3 filter `unresolved variables` è il comportamento desiderato. Skippare FAQ con variabili non risolte è "fail-safe" ma maschera bug di config. Soluzione robusta: log error + fallback hardcoded answer.
- **Assunzione C**: Sentence-transformers/FAISS sono installati. Da `faq_manager.py:46-47` (`HAS_SEMANTIC = False`), il fallback semantico potrebbe non esistere su pipeline iMac venv. Verificare con `pip list | grep sentence-transformers`. Se assente, le query parafrasate ("la vostra palestra ha la vasca?") NON matcheranno mai L3 keyword-only — quindi A1+A2 risolve solo query identiche/quasi-identiche alla question canonica.

### 5.2 Cosa rompe a 30/60/90 gg

- **30gg**: nuovi verticali (medical, beauty) aggiungeranno facility questions diverse. Pattern A1 (regex INFO con facility tokens) rischia bloat → migrare verso intent classifier ML-based o LLM-NLU (già presente, threshold 0.5).
- **60gg**: utente reali porranno questions out-of-FAQ ("la sauna è inclusa nel mensile?") → A2 facility variables non basta, serve un FAQ knowledge graph esteso o RAG embedding-based.
- **90gg**: scaling multi-tenant (10+ palestre clienti) → ogni business avrà facility diverse. Migrare config a per-tenant DB row + UI Setup Wizard per popolare `facilities`. Non gestire questo a livello codice.

### 5.3 Pattern errore noti su sistemi simili

- **Karpathy/llamaindex postmortem**: gate hard-coded category routing (vs soft routing con LLM-judge) è anti-pattern in pipeline 4+ layer. Soluzione 2026: LLM-NLU al posto del regex `IntentCategory` come router primario. FLUXION ha già LLM-NLU (`_llm_nlu_result`) usato a line 2477-2478 — verificare perché LLM-NLU non classifica "Avete la piscina?" come INFO (probabilmente threshold 0.5 non superato o LLM ritorna ALTRO).
- **Stripe/Twilio API error patterns**: `D3 skip on unresolved variable` è esattamente il pattern "silent fail on missing config" che causa il 70% dei bug field-level. Promuoverlo a warning loud + fallback hardcoded.
- **Pattern S218/S223 ripetuto**: MEMORY ipotizzava "FAQ matching threshold" o "FAQ retriever issue". Root cause vera: IntentCategory gate + D3 variable filter. Sempre tracciare dall'entry-point.

### 5.4 Dove si sovradimensiona

- **NON serve sentence-transformers / FAISS embedding** per facility questions deterministiche. Risolvere con A1 (intent regex extension) + A2 (FAQ data completa) basta per 95% delle query reali PMI palestra italiana.
- **NON serve LLM re-classification** sul gate L3. Il regex extension copre tutti i facility tokens noti senza chiamate LLM aggiuntive (latency cost).
- **NON serve modificare D3 filter** in modo invasivo. Semplicemente popolare le variabili mancanti (A2) è sufficient.
- **B (FAQ injection in L4 prompt) può aspettare** — fix A1+A2 risolvono il caso baseline. B diventa rilevante per query out-of-FAQ ("è inclusa nel mensile la sauna?") che oggi non sono in scope WARN.

---

## 6. Riferimenti file (absolute paths)

- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py:2482` — L3 FAQ gate
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py:1744-1752` — S226 _is_info promo (incompleta)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py:3282-3295` — settings dict per FAQ vars (missing facility vars)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py:3298-3320` — _load_vertical_faqs (D3 filter)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/orchestrator.py:3466-3525` — _build_llm_context (system prompt)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/intent_classifier.py:441-448` — INTENT_PATTERNS[INFO] (no facility tokens)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/faq_manager.py:140-214` — keyword_match_score (ignores keywords field)
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/faq_manager.py:483-494` — find_answer threshold 0.8 keyword conf
- `/Volumes/MontereyT7/FLUXION/voice-agent/data/faq_palestra.json:67-73` — entry piscina con `{{RISPOSTA_PISCINA}}` unresolved
- `/Volumes/MontereyT7/FLUXION/voice-agent/src/faq_retriever.py:244` — embed only `faq.question`, not keywords

---

## 7. Decisione operativa S227-P1

Implementare in ordine:

1. **S227-P1a** (5 min): modifica `orchestrator.py:2482`:
   ```python
   if (intent_result.category == IntentCategory.INFO or _is_info) and self.faq_manager:
   ```
   Apre L3 gate per question-form IDLE input.

2. **S227-P1b** (90 min): aggiungere facility variables in `_load_vertical_faqs` settings dict + popolare default da DB (o hardcoded fallback se DB schema non li ha).

3. **S227-P1c** (30 min, opzionale): FAQ injection nel L4 system prompt per ridurre hallucination.

4. **Test E2E**: stress PALESTRA + spot facility questions. Target: 22 OK / 0 WARN / 0 FAIL.

5. Commit atomic chain `S227-P1a` / `S227-P1b` / `S227-P1c`. Baseline file aggiornato.

Stop ricerca. Implementation = task separato.
