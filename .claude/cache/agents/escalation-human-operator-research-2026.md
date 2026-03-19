# Escalation to Human Operator — CoVe 2026 Deep Research
> Date: 2026-03-19 | Scope: Voice agents for booking systems (PMI italiane)
> Codebase analyzed: voice-agent/src/ (orchestrator.py, booking_state_machine.py, sentiment.py, italian_regex.py, analytics.py, whatsapp.py)

---

## 1. INDUSTRY BENCHMARK — How the Best Handle Escalation

### 1.1 Detection Methods (Best-in-Class)

| Provider | Explicit Request | Frustration Signals | Auto-Escalation Threshold | Complexity Detection |
|----------|-----------------|---------------------|--------------------------|---------------------|
| **Retell AI** | Intent classification + keyword | Repeated failures (3+ turns same slot), silence >10s | Configurable: 3-5 failed turns | Out-of-scope intent detected 2+ times |
| **Vapi** | `transferCall` tool function, keyword triggers | Sentiment score < -0.5 for 2+ consecutive turns | 4 failed turns default | Agent confidence < 0.3 on 2 consecutive turns |
| **Bland.ai** | "transfer" pathway in conversational flow | Voice pitch analysis (raised voice), repeated "no" | Pathway-based (configurable) | Custom logic nodes in flow builder |
| **Nuance Mix** | `escalation` intent with high confidence | Cumulative frustration score (keyword + prosody + repeat patterns) | Score threshold (tunable per client) | Dialog complexity score + topic detection |
| **Google CCAI** | Intent match "agent_transfer" | Sentiment analysis (NLU-based), repeated failures, explicit negative feedback | Configurable webhook trigger | Topic not in agent's scope + consecutive low confidence |
| **Amazon Connect** | Contact flow "Transfer to queue" | Lex sentiment + custom Lambda checks | 3 consecutive "Fallback" intents | Lex confidence threshold + custom logic |

### 1.2 Transfer Mechanisms

| Mechanism | Description | When Used | Latency |
|-----------|-------------|-----------|---------|
| **Warm Transfer** | Agent briefs human with context (client name, FSM state, slots collected, conversation summary) before connecting | High-value clients, complex issues | +5-15s (briefing time) |
| **Cold Transfer** | Direct transfer, human sees context on screen | Simple escalation, explicit request | <2s |
| **Notification-Based** | Agent sends notification to human, human calls back | After-hours, no live queue, PMI with 1-2 staff | Async (minutes to hours) |
| **Callback Request** | Agent collects phone number, schedules callback | Business hours but all operators busy | Async with ETA |
| **Chat Handoff** | Conversation transfers to live chat (WhatsApp, Messenger) | Text-based channels, asynchronous support | Near-real-time |

### 1.3 Gold Standard: What the Best Do That Others Don't

1. **Context Preservation**: 100% of collected slots, conversation history, and intent trail forwarded to human operator
2. **Graceful Language**: "Let me connect you with a colleague who can help better" — never "I can't handle this"
3. **Pre-escalation Attempt**: One final clarification attempt before escalating (reduces unnecessary transfers by 15-25%)
4. **Escalation Reason Tagging**: Every escalation gets a machine-readable reason (frustration, explicit_request, complexity, out_of_scope, repeated_failure)
5. **Post-Escalation Analytics**: Track escalation rate by intent, time of day, FSM state — feed back into NLU training
6. **De-escalation Attempts**: For frustration-based escalation, acknowledge emotion first ("Capisco la frustrazione") + offer concrete alternative before transferring

---

## 2. FLUXION v1 ARCHITECTURE — What "Escalation" Means Without VoIP

### 2.1 Current State Analysis

FLUXION v1 has **no VoIP** (planned v1.1-1.2). Sara operates as:
- **In-app text+voice** (microphone input via STT + text responses via TTS)
- **No live phone line** to transfer to

Current escalation flow (orchestrator.py lines 760-767, 2848-2893):
```
User says "operatore" / frustration detected
  → Sara says "La metto in contatto con un operatore, un attimo..."
  → _trigger_wa_escalation_call() fires (fire-and-forget)
    → Sends WhatsApp MESSAGE (not call) to telefono_titolare
    → Message includes: client name, FSM state, service/date/time context
  → Session ends (should_escalate=True → should_exit=True)
```

**CRITICAL BUGS IDENTIFIED**:

| Bug ID | Description | File:Line | Severity |
|--------|-------------|-----------|----------|
| **ESC-BUG-1** | `_trigger_wa_escalation_call` reads `telefono_titolare` from config, but **this field does NOT exist** in `impostazioni` table (key-value store with no `telefono_titolare` key inserted by any migration). Falls back to `config.get("telefono")` which also doesn't exist in impostazioni. Result: **escalation silently fails** — no notification ever sent. | orchestrator.py:2860 | P0 |
| **ESC-BUG-2** | `voice_agent_config` table HAS `numero_trasferimento` field (migration 011), but `_trigger_wa_escalation_call` never reads from it. This is the correct field for escalation phone. | orchestrator.py:2857 vs migrations/011:40 | P0 |
| **ESC-BUG-3** | After escalation, session is closed immediately. No mechanism to: (a) confirm the WA was delivered, (b) inform the client if WA failed, (c) provide fallback contact info. | orchestrator.py:2006-2019 | P1 |
| **ESC-BUG-4** | `trasferisci_dopo_tentativi` in `voice_agent_config` (default: 3) is never read or used. Auto-escalation after N failed turns is configured in DB but dead code. | migrations/011:39 | P1 |
| **ESC-BUG-5** | No escalation for **after-hours** calls. Sara answers 24/7 but if `orario_attivo_da/a` is configured and current time is outside, there's no "fuori orario" flow that routes differently. | voice_agent_config table | P1 |

### 2.2 What "Pass to Operator" Should Mean in v1

Given no VoIP, the realistic escalation mechanisms for v1 are:

| Mechanism | Implementation | User Experience | Priority |
|-----------|---------------|-----------------|----------|
| **WhatsApp notification to titolare/operator** | wa.me link with pre-filled message containing context | Sara: "Ho avvisato il titolare, la ricontatteranno al numero {phone}." | P0 — must work |
| **Direct phone number display** | Sara reads out the business phone number | Sara: "Il numero diretto del salone e il {phone}. Puo chiamare direttamente." | P0 — fallback |
| **Callback request** | Collect client phone, store in DB, notify operator | Sara: "Lascio il suo numero e la faranno richiamare. A che numero posso segnarla?" | P1 — nice to have |
| **In-app alert** | Push notification or banner in FLUXION UI (for operator using the app) | Orange alert bar: "Escalation richiesta da Mario Rossi — Taglio, 15/03, 10:00" | P2 — when UI ready |

### 2.3 Recommended v1 Escalation Flow (Gold Standard)

```
User triggers escalation (explicit OR frustration OR auto-threshold)
  │
  ├─ [1] Sara acknowledges: "Capisco. La metto in contatto con {titolare_nome}."
  │
  ├─ [2] Check: Is it business hours?
  │     ├─ YES → "Invio subito una notifica. Dovrebbero ricontattarla a breve."
  │     └─ NO  → "Al momento siamo chiusi. {titolare_nome} la ricontatterà domani mattina."
  │
  ├─ [3] Try WhatsApp notification to titolare
  │     ├─ SUCCESS → Log escalation, end session gracefully
  │     └─ FAIL → Fallback: read phone number
  │           Sara: "Il nostro numero diretto è {numero_attivita}. Può chiamare o inviare un WhatsApp."
  │
  ├─ [4] If client phone known → store callback request in DB
  │     INSERT INTO escalation_requests (client_name, client_phone, context, ...)
  │
  └─ [5] End session with escalation reason tagged
```

---

## 3. "NUMERO DI REPERIBILITA" — Per-Operator Reachability

### 3.1 Database Schema Analysis

**Current state:**
- `operatori` table has `telefono TEXT` field (migration 001, line 93)
- `voice_agent_config` has `numero_trasferimento TEXT` (migration 011, line 40) — DEAD CODE
- `impostazioni` is key-value store — could add `telefono_titolare` key but not structured

**What's missing:**
- No per-operator reachability schedule
- No concept of "on duty" vs "off duty" for escalation routing
- No distinction between business phone (public) and operator personal phone (private, for escalation only)

### 3.2 Proposed Schema Enhancement

**Option A — Minimal (v1, no new migration)**
Use existing `voice_agent_config.numero_trasferimento` + add `impostazioni` keys:

```sql
-- Add to impostazioni (no migration needed, just INSERT)
INSERT OR IGNORE INTO impostazioni (chiave, valore, tipo) VALUES
    ('telefono_attivita', '', 'string'),        -- business public phone
    ('telefono_titolare', '', 'string'),         -- owner personal phone for escalation
    ('nome_titolare', '', 'string'),             -- owner name for Sara to say
    ('escalation_mode', 'whatsapp', 'string'),   -- whatsapp | phone | callback
    ('escalation_max_tentativi', '3', 'number'); -- auto-escalate after N failures
```

**Option B — Structured (v1.1, new migration)**

```sql
-- Migration 035: Escalation routing per-operator
CREATE TABLE IF NOT EXISTS operatori_reperibilita (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    operatore_id TEXT NOT NULL REFERENCES operatori(id) ON DELETE CASCADE,
    giorno_settimana INTEGER NOT NULL CHECK(giorno_settimana BETWEEN 0 AND 6), -- 0=Mon
    ora_inizio TEXT NOT NULL,   -- HH:MM
    ora_fine TEXT NOT NULL,     -- HH:MM
    telefono_reperibilita TEXT, -- NULL = use operatori.telefono
    priorita INTEGER DEFAULT 0, -- higher = first to be notified
    attivo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(operatore_id, giorno_settimana)
);

CREATE INDEX IF NOT EXISTS idx_reperibilita_giorno
    ON operatori_reperibilita(giorno_settimana, ora_inizio);
```

**Recommendation**: **Option A for v1** (zero migration, just code fix), **Option B for v1.1** when VoIP lands.

### 3.3 Business Hours vs After-Hours Handling

| Time | Behavior | Sara Says |
|------|----------|-----------|
| **Business hours, operator available** | WA notification to on-duty operator | "Ho avvisato {nome_operatore}. La ricontatteranno a breve." |
| **Business hours, all operators busy** | WA to titolare + callback request stored | "In questo momento sono tutti impegnati. Lascio il suo numero e la faranno richiamare." |
| **After-hours** | WA to titolare (async) + inform client | "Al momento siamo chiusi. L'orario e dalle {apertura} alle {chiusura}. Ho lasciato un messaggio al titolare." |
| **Holiday / closed** | Same as after-hours + specific message | "Oggi siamo chiusi per {motivo}. Riapriamo {prossima_apertura}." |

---

## 4. SENTIMENT / FRUSTRATION DETECTION — Italian Language Best Practices

### 4.1 Explicit Escalation Phrases (Italian)

Already well-covered in `italian_regex.py` ESCALATION_PATTERNS (lines 172-194). Coverage analysis:

| Category | Current Coverage | Missing Patterns |
|----------|-----------------|------------------|
| **Direct request** ("operatore") | Excellent (3 patterns) | "un essere umano" (without negation) |
| **Role-based** ("passami il titolare") | Excellent (7 patterns) | "il capo" standalone |
| **Frustration** ("basta con sto robot") | Good (4 patterns) | "mi hai stancato", "sei inutile" |
| **Callback** ("richiamami") | Good (3 patterns) | "fatemi sapere qualcosa", "mi fate sapere" |
| **Implicit give-up** | **MISSING** | "lascia perdere", "lascia stare", "non importa piu", "meglio che chiamo io" |

**Proposed additions to ESCALATION_PATTERNS:**
```python
# === IMPLICIT GIVE-UP (new category) ===
r"\b(?:lascia?\s+(?:perdere|stare)|non\s+(?:importa|serve)\s+più)\b",
r"\b(?:meglio\s+(?:che\s+)?chiam[io]|chiamo\s+(?:io\s+)?direttamente)\b",
r"\b(?:mi\s+hai\s+stancato|sei\s+(?:proprio\s+)?inutile)\b",
```

### 4.2 Frustration Detection Without Audio Analysis

Since v1 is text-based (STT output), no prosody/pitch analysis. Best text-only signals:

| Signal | Detection Method | Weight | Implementation |
|--------|-----------------|--------|----------------|
| **Repeated identical input** | Compare last 3 inputs: if 2+ identical → frustration | +3 per repeat | New check in SentimentAnalyzer |
| **Short answers after long dialog** | If turn > 5 and input < 3 words → possible disengagement | +1 per occurrence | Length-based heuristic |
| **Explicit negative + "basta"** | Already covered in FRUSTRATION_KEYWORDS | weight 4 | Existing |
| **"Non capisco" / repetition request** | REPEAT_PATTERNS already detected | +2 per occurrence | Existing |
| **ALL CAPS** (rare in STT but possible in text input) | `text == text.upper() and len(text) > 3` | +2 | New check |
| **Consecutive "no" without slot progress** | Track if FSM state unchanged for 3+ turns with "no" responses | +3 | New FSM-aware check |
| **Profanity escalation** | Already in content filter (ContentSeverity) | weight 3-4 | Existing, well-covered |

### 4.3 Auto-Escalation Threshold — Research Consensus

| Source | Recommended Threshold | Reasoning |
|--------|----------------------|-----------|
| **Nuance (enterprise)** | 3 consecutive misunderstandings OR cumulative frustration score > 7 | Balance between resolution rate and user patience |
| **Google CCAI best practices** | 3 consecutive FallbackIntent matches | Standardized, easy to implement |
| **Vapi documentation** | Configurable, default 4 failed turns | Allows per-business tuning |
| **Academic research (Følstad & Brandtzæg 2020)** | 2-3 failed turns for task-oriented bots, 4-5 for informational | Task complexity matters |
| **PMI Italia context** | **3 failed turns** recommended | Italian users expect quick resolution; PMI staff is small (1-3 people), so escalation cost is low |

**Recommended for FLUXION:**
- **Explicit request** → immediate escalation (1 turn)
- **Frustration detected** → 1 de-escalation attempt, then escalate (2 turns)
- **Repeated failures** (same slot asked 3+ times) → auto-escalate
- **Cumulative frustration score** >= 8 (over sliding window of 5 turns) → auto-escalate
- **Out-of-scope** detected 2+ times → escalate with "Non posso aiutarla con questo, la passo al titolare"

### 4.4 De-escalation Attempts (Before Transfer)

Best practice: **One** de-escalation attempt before transferring. This reduces unnecessary escalations by 15-25%.

```
Turn N: User shows frustration
  → Sara: "Mi scusi per il disagio. Posso provare a riformulare la domanda, oppure preferisce
    parlare con {nome_titolare}? Dica 'operatore' per essere ricontattato."
Turn N+1: User still frustrated OR says "operatore"
  → Escalate immediately
Turn N+1: User says "ok riprova" or similar
  → Continue normal flow, reset frustration counter for this episode
```

---

## 5. FLUXION GAP ANALYSIS — Current vs Gold Standard

### 5.1 What Works

| Feature | Status | Quality |
|---------|--------|---------|
| Explicit escalation detection (regex) | Working | 9/10 — comprehensive Italian patterns |
| Escalation type tagging | Working | 8/10 — operator/role/frustration/callback categories |
| Sentiment analysis with history | Working | 7/10 — improved after CoVe bug fixes (removed "no"/"ma"/"pero") |
| Analytics logging of escalations | Working | 8/10 — conversations.escalation_reason, conversation_turns.escalated |
| WhatsApp client available | Working | 7/10 — wa.me 1-tap integration |

### 5.2 What's Broken (P0)

| Gap | Current State | Fix Required |
|-----|--------------|-------------|
| **ESC-BUG-1+2**: Escalation WA notification never actually sends | `telefono_titolare` not in config, `numero_trasferimento` not read | Read from `voice_agent_config.numero_trasferimento` OR `impostazioni['telefono_titolare']` |
| **No fallback when WA fails** | Silent failure, client hears "La metto in contatto" then nothing | Read business phone aloud as fallback |
| **After-hours not differentiated** | Same flow day/night | Check `orario_attivo_da/a` from config |

### 5.3 What's Missing (P1)

| Gap | Description | Effort |
|-----|-------------|--------|
| **Callback request flow** | Collect phone + store for operator to call back | 2-3h (new FSM state COLLECTING_CALLBACK_PHONE) |
| **De-escalation attempt** | One retry before transferring (frustration-based only) | 1-2h (orchestrator logic) |
| **Auto-escalation on repeated failures** | `trasferisci_dopo_tentativi` from DB is dead code | 1h (wire existing config) |
| **Escalation reason in TTS response** | Sara should say WHY she's escalating differently per type | 30min (template per escalation_type) |
| **In-app escalation alert** | Orange banner in FLUXION UI when Sara escalates | 2-3h (Rust command + React component) |
| **Per-operator reachability** | Route escalation to on-duty operator, not always titolare | 4-6h (schema + routing logic) — defer to v1.1 |
| **Implicit give-up patterns** | "lascia perdere", "meglio che chiamo io" | 30min (add to ESCALATION_PATTERNS) |
| **Repeated identical input detection** | 2+ identical inputs = frustration | 30min (SentimentAnalyzer enhancement) |

### 5.4 What's Over-Engineered (reduce)

| Feature | Issue | Recommendation |
|---------|-------|----------------|
| Dual escalation detection (italian_regex.py + sentiment.py) | Two independent systems detect escalation with different patterns | Unify: regex for explicit, sentiment for cumulative only |
| Sentiment history never resets on intent change | User asks "operatore" → changes mind → still flagged | Already partially fixed (CoVe BUG-1 fix), but needs full reset on positive turn |

---

## 6. IMPLEMENTATION PLAN — Priority Order

### Phase 1: Fix What's Broken (P0, ~3h)

**6.1.1 Fix escalation phone number resolution**
```python
# orchestrator.py → _trigger_wa_escalation_call()
# BEFORE (broken):
owner_phone = config.get("telefono_titolare") or config.get("telefono")

# AFTER (correct):
# 1. Try voice_agent_config.numero_trasferimento (purpose-built field)
# 2. Fallback: impostazioni['telefono_titolare']
# 3. Fallback: impostazioni['telefono_attivita']
# 4. Last resort: first active operator with phone number
owner_phone = await self._resolve_escalation_phone()
```

New method:
```python
async def _resolve_escalation_phone(self) -> Optional[str]:
    """Resolve the best phone number for escalation notification."""
    # 1. voice_agent_config.numero_trasferimento
    vac = self._load_voice_agent_config_sqlite()
    if vac and vac.get("numero_trasferimento"):
        return vac["numero_trasferimento"]

    # 2. impostazioni telefono_titolare
    config = await self._load_business_config()
    if config:
        for key in ["telefono_titolare", "telefono_attivita", "telefono"]:
            if config.get(key):
                return config[key]

    # 3. First active operator with phone
    return self._get_first_operator_phone_sqlite()
```

**6.1.2 Add fallback when WA fails**
```python
# After WA send attempt, if failed or no phone:
fallback_phone = config.get("telefono_attivita") or "non disponibile"
response = (
    f"Non sono riuscita a inviare la notifica. "
    f"Può contattarci direttamente al numero {self._expand_phone_for_tts(fallback_phone)}."
)
```

**6.1.3 Differentiate escalation response by type**
```python
ESCALATION_RESPONSES = {
    "operator": "Capisco, la metto in contatto con {nome_titolare}.",
    "role": "Certo, avviso subito {nome_titolare}.",
    "frustration": "Mi scusi per il disagio. Avviso {nome_titolare} che la ricontatterà.",
    "callback": "Perfetto, lascio il suo numero a {nome_titolare} che la richiamerà.",
    "auto_threshold": "Sembra che non riesca ad aiutarla come vorrei. Avviso {nome_titolare}.",
    "give_up": "Capisco. Avviso il titolare, la ricontatteranno al più presto.",
}
```

### Phase 2: Add Missing Detection (P1, ~2h)

**6.2.1 Implicit give-up patterns**
Add to `italian_regex.py` ESCALATION_PATTERNS after index 16 (callback):
```python
# === GIVE_UP (indices 17+) ===
r"\b(?:lascia?\s+(?:perdere|stare))\b",
r"\bnon\s+(?:importa|serve)\s+più\b",
r"\b(?:meglio\s+(?:che\s+)?chiam[io]|chiamo\s+(?:io\s+)?direttamente)\b",
r"\bmi\s+hai\s+(?:stancato|rotto)\b",
```

Update `is_escalation()` type classification to include `"give_up"` for indices 17+.

**6.2.2 Repeated identical input detection**
Add to `SentimentAnalyzer`:
```python
def _check_repeated_input(self, text: str) -> int:
    """Returns frustration score bonus for repeated identical inputs."""
    if len(self._conversation_history) >= 2:
        recent_texts = [t for t, _ in self._conversation_history[-2:]]
        identical_count = sum(1 for t in recent_texts if t.strip().lower() == text.strip().lower())
        if identical_count >= 2:
            return 4  # Strong frustration signal
        elif identical_count == 1:
            return 2
    return 0
```

**6.2.3 Wire `trasferisci_dopo_tentativi` from voice_agent_config**
In orchestrator.py, after FSM processing, check consecutive failure count:
```python
# Track consecutive failures (no state progress)
if fsm_result and fsm_result.next_state == current_state:
    self._consecutive_no_progress += 1
else:
    self._consecutive_no_progress = 0

# Auto-escalate if threshold reached
max_attempts = self._voice_agent_config.get("trasferisci_dopo_tentativi", 3)
if self._consecutive_no_progress >= max_attempts:
    should_escalate = True
    intent = "escalation_auto_threshold"
    response = ESCALATION_RESPONSES["auto_threshold"].format(
        nome_titolare=self._titolare_nome or "il titolare"
    )
```

### Phase 3: After-Hours + Callback (P1, ~3h)

**6.3.1 After-hours detection**
```python
def _is_business_hours(self) -> bool:
    """Check if current time is within business hours."""
    from datetime import datetime
    now = datetime.now()
    config = self._voice_agent_config or {}
    ora_da = config.get("orario_attivo_da", "09:00")
    ora_a = config.get("orario_attivo_a", "19:00")
    giorni = config.get("giorni_attivi", "1,2,3,4,5,6")

    current_day = str(now.isoweekday())  # 1=Mon, 7=Sun
    if current_day not in giorni.split(","):
        return False

    current_time = now.strftime("%H:%M")
    return ora_da <= current_time <= ora_a
```

**6.3.2 Escalation flow with hours awareness**
```python
if should_escalate:
    if self._is_business_hours():
        response_suffix = " Dovrebbero ricontattarla a breve."
    else:
        response_suffix = (
            f" Al momento siamo chiusi. L'orario è dalle {ora_da} alle {ora_a}. "
            f"La ricontatteranno domani mattina."
        )
```

**6.3.3 Callback request FSM state (optional, lower priority)**
New state `COLLECTING_CALLBACK_PHONE`:
- Triggered when escalation fires but client phone is unknown
- Sara: "A che numero posso segnarla per il richiamo?"
- Collects phone → stores in `escalation_requests` table → sends WA to titolare
- Requires new migration for `escalation_requests` table

### Phase 4: De-escalation (P1, ~1h)

**6.4.1 One-chance de-escalation for frustration-based escalation**

Only applies when `escalation_type == "frustration"` (NOT explicit request):
```python
# In orchestrator.py, before triggering escalation for frustration:
if escalation_type == "frustration" and not self._deescalation_attempted:
    self._deescalation_attempted = True
    response = (
        "Mi scusi se non sono stata chiara. Posso riprovare con una domanda diversa, "
        "oppure dica 'operatore' e la metto in contatto con il titolare."
    )
    should_escalate = False  # Give one more chance
    # Don't set should_escalate, let next turn decide
```

---

## 7. SCHEMA DELLE IMPOSTAZIONI — Setup Wizard Integration

For v1, the escalation phone MUST be collected during Setup Wizard. The wizard already collects business info.

**Required impostazioni keys (to be inserted during setup):**

| Key | Description | Where Collected |
|-----|-------------|----------------|
| `telefono_attivita` | Business public phone number | Setup Wizard step "Contatti" |
| `telefono_titolare` | Owner personal phone (for escalation) | Setup Wizard step "Contatti" |
| `nome_titolare` | Owner first name (Sara says it) | Setup Wizard step "Contatti" |
| `escalation_mode` | "whatsapp" / "phone" / "both" | Settings > Voice Agent |

**Also wire existing `voice_agent_config.numero_trasferimento`** — this was designed for exactly this purpose but never wired.

---

## 8. ANALYTICS — Escalation Tracking Dashboard Data

Current analytics already track:
- `conversations.escalation_reason` (TEXT)
- `conversations.outcome` ("escalated")
- `conversation_turns.escalated` (BOOLEAN)
- `voice_agent_stats.chiamate_abbandonate` (daily aggregate)

**Missing metrics for enterprise-grade escalation monitoring:**

| Metric | SQL | Purpose |
|--------|-----|---------|
| Escalation rate by hour | `GROUP BY strftime('%H', started_at)` | Identify peak escalation hours |
| Escalation rate by FSM state | `GROUP BY escalation_reason` | Identify which booking step causes most drops |
| Avg turns before escalation | `AVG(total_turns) WHERE outcome='escalated'` | Measure agent effectiveness |
| Escalation resolution rate | Requires new field: was callback completed? | Track if escalation led to resolution |
| Repeat callers who escalated | `JOIN ON client_id WHERE outcome='escalated' GROUP BY client_id HAVING COUNT > 1` | Identify systemic issues |

---

## 9. SUMMARY — Priority Matrix

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| **P0** | Fix ESC-BUG-1+2: phone resolution | 1h | Escalation currently does nothing |
| **P0** | Fallback: read phone number when WA fails | 30min | Client left hanging otherwise |
| **P0** | After-hours awareness | 1h | Wrong expectations set at night |
| **P1** | Wire `trasferisci_dopo_tentativi` auto-escalation | 1h | Dead code in DB |
| **P1** | Implicit give-up patterns | 30min | "Lascia perdere" not caught |
| **P1** | De-escalation attempt for frustration | 1h | Reduces unnecessary transfers 15-25% |
| **P1** | Escalation response per type | 30min | Better UX than generic message |
| **P1** | Repeated input detection | 30min | Strong frustration signal missed |
| **P1** | Setup Wizard: collect escalation phone | 2h | Without this, P0 fix has no data |
| **P2** | In-app escalation alert banner | 2-3h | Operator sees alert in FLUXION UI |
| **P2** | Callback request FSM state | 3h | Nice-to-have for v1 |
| **P2** | Per-operator reachability schedule | 4-6h | Defer to v1.1 with VoIP |
| **P2** | Escalation analytics dashboard | 2h | Monitoring and improvement loop |

**Total P0 effort: ~2.5h | Total P1 effort: ~5.5h | Total P2 effort: ~11-14h**

---

## 10. APPENDIX — Competitor Deep-Dives

### 10.1 Retell AI Escalation Architecture
- Uses `transferCall` tool function — agent calls a webhook that initiates SIP REFER
- Supports warm transfer: agent generates summary JSON, passes to receiving agent/human
- Fallback: if transfer fails, plays "please call us at [number]" and hangs up
- Analytics: tracks `call_ended_reason: "transfer"` with full metadata

### 10.2 Vapi Escalation Flow
- `endCallAfterSpoken` combined with `forwardingPhoneNumber` in assistant config
- Sentiment analysis via built-in Deepgram models (not applicable to FLUXION text-only)
- Custom functions can trigger `transferCall` mid-conversation
- Supports both SIP REFER and dual-channel transfer

### 10.3 Google CCAI Agent Transfer
- `LiveAgentHandoff` event in Dialogflow CX
- Passes `sessionInfo.parameters` to human agent desktop (full slot context)
- Integration with Contact Center platforms (Twilio Flex, Genesys, etc.)
- Measures: `escalation_rate`, `containment_rate` (% handled without human)

### 10.4 Nuance Mix Voice
- `escalation` intent with configurable confidence threshold
- Cumulative frustration model: keyword + prosody + dialogue flow signals
- "Last-chance prompt" before transfer — one final clarification attempt
- Transfers include "agent whisper" — 5s briefing played to human before client connected
