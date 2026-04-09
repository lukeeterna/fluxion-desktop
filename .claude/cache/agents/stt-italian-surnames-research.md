# STT Italian Surnames Research — P0 Blocker

**Date**: 2026-04-09
**Context**: Groq Whisper transcribes founder's surname as "Grazie." 3/3 times during live phone test.
**Scope**: Why Whisper fails on Italian surnames, and how to fix it at zero cost.

---

## 1. ROOT CAUSE ANALYSIS

### 1A. Why Whisper Misrecognizes Italian Surnames

**Primary cause: Language Model Bias (Decoder Prior)**

Whisper is a sequence-to-sequence model. The decoder generates text token-by-token based on:
1. Audio features (encoder output)
2. Previously generated tokens (decoder auto-regression)
3. **Language model prior** — what text is "likely" in the training data

Italian surnames are **low-frequency tokens** in Whisper's training corpus (680,000 hours, mostly English media). The decoder's language model heavily favors common Italian words over rare proper nouns. When audio is ambiguous (telephony quality, 8kHz upsampled to 16kHz), the decoder defaults to high-probability Italian words.

Example: "Di Stasi" → the phonemes /di stazi/ are acoustically close to /graˈtsje/ ("Grazie") when:
- Telephone codec (G.711 u-law) strips frequencies above 3.4kHz
- Upsampling from 8kHz to 16kHz creates spectral gaps
- Short utterance = minimal context for decoder to disambiguate

**Secondary causes:**
- **Short utterance effect**: Surnames are often 1-3 words. Whisper hallucinates on short audio because the decoder has insufficient context to anchor predictions.
- **Punctuation hallucination**: "Grazie." with a period suggests Whisper treated it as a complete sentence, not a name fragment. The model's training on subtitled content creates a bias toward punctuated sentences.
- **VoIP audio degradation**: 8kHz narrowband telephony → audioop.ratecv upsample to 16kHz → Whisper trained on 16kHz wideband. The interpolated high frequencies are zero-energy, making the audio look like muffled/distorted speech.

### 1B. The "Grazie" Failure Mode Specifically

"Grazie" is one of the highest-frequency Italian words in Whisper's training data. When the decoder faces ambiguous audio:
1. It generates "Grazie" because P("Grazie") >> P("Di Stasi") in the language model
2. After generating "Grazie", the auto-regressive decoder adds "." (sentence end)
3. The model is now confident it has a complete transcription
4. This is **deterministic** — same audio + same model = same wrong output 3/3 times

---

## 2. GROQ WHISPER API PARAMETERS

### 2A. Available Parameters (Groq Audio Transcription API)

| Parameter | Current Value | Recommended | Impact |
|-----------|-------------|-------------|--------|
| `model` | `whisper-large-v3` | Keep | Best accuracy available on Groq |
| `language` | `"it"` | Keep | Already set, prevents language detection overhead |
| `prompt` | Set via NameCorrector | **Expand significantly** | **HIGH** — biases decoder toward expected words |
| `response_format` | `"text"` | `"verbose_json"` | Gives per-segment confidence + timestamps |
| `temperature` | Not set (default 0) | `0.0` explicitly | Deterministic output, no sampling randomness |

### 2B. The `prompt` Parameter — Most Critical Fix

**How it works**: Whisper's `prompt` (or `initial_prompt`) is fed as "previous context" to the decoder. The decoder treats it as text that came before the current audio. This **biases the language model prior** toward words/names in the prompt.

**Current implementation** (`name_corrector.py:76-101`):
```python
prefix = "Telefonata italiana per prenotazione appuntamento. Clienti: "
# Then appends client names from DB, max 400 chars
```

**Problem**: The prompt is good but:
1. Max 400 chars is conservative — Whisper supports ~224 tokens (~900 chars Italian)
2. The prefix "Telefonata italiana per prenotazione appuntamento" wastes prompt space
3. Client surnames should appear as standalone items, not in a comma list
4. The prompt doesn't include the business owner's name (who answers the phone)

**Recommended prompt format** (based on OpenAI Cookbook + Retell AI pattern):
```python
"Di Stasi, Rossi, Bianchi, Esposito, Romano. Prenotazione appuntamento salone."
```
Key changes:
- **Names first** — they must be in the last 224 tokens for decoder bias to work
- **Period-separated or comma-separated** — mimics how Whisper sees subtitles
- **Include business owner surname** — always in prompt since they often state their name
- **Remove verbose prefix** — wastes tokens

### 2C. `response_format="verbose_json"` — Confidence Access

Switching from `"text"` to `"verbose_json"` returns:
```json
{
  "text": "Grazie.",
  "segments": [{
    "text": "Grazie.",
    "avg_logprob": -0.8,
    "no_speech_prob": 0.3,
    "compression_ratio": 0.5
  }]
}
```

**Actionable signals:**
- `avg_logprob < -0.7` → low confidence, likely misrecognition
- `no_speech_prob > 0.5` → silence/noise, discard
- `compression_ratio < 0.8` → repetitive/hallucinated

When confidence is low AND FSM expects a name (WAITING_NAME state), we can:
1. Retry with `temperature=0.4` (explore alternatives)
2. Apply phonetic correction more aggressively
3. Ask user to repeat

---

## 3. POST-PROCESSING STRATEGIES

### 3A. State-Aware STT Correction (Highest Impact, Zero Cost)

The FSM knows WHEN it expects a name. Use this:

```python
# In orchestrator.py process_audio():
fsm_state = self.booking_sm.current_state
if fsm_state in (BookingState.WAITING_NAME, BookingState.IDLE):
    # Name-biased prompt with surnames at the end (decoder recency bias)
    stt_prompt = self._name_corrector.get_prompt() if self._name_corrector else None
else:
    # Generic prompt for service/date/time slots
    stt_prompt = "Prenotazione appuntamento. Sì, no, lunedì, martedì, mercoledì."
```

### 3B. Confidence-Based Retry (Medium Impact)

```python
# Pseudocode for confidence-gated retry
result = await groq.transcribe(audio, prompt=name_prompt, response_format="verbose_json")
if result.avg_logprob < -0.7 and fsm_expects_name:
    # Retry with temperature > 0 to get alternative hypothesis
    result2 = await groq.transcribe(audio, prompt=name_prompt, temperature=0.4)
    # Pick the one with more name-like tokens
    result = pick_best_name_candidate(result, result2)
```

**Cost**: 1 extra Groq API call on ~10% of turns. Groq free tier = 14,400 req/day = plenty.

### 3C. Enhanced Phonetic Post-Processing

Current `WhisperCorrector` only handles service names. Add surname-specific rules:

```python
# Common Whisper mishears for Italian surnames
SURNAME_MISHEARS = {
    "grazie": None,        # Never a surname — flag for re-evaluation
    "prego": None,         # Same
    "buongiorno": None,    # Same
    "arrivederci": None,   # Same
}

# After STT, if FSM expects name AND output is a common word:
if transcription.lower().strip().rstrip('.!?') in SURNAME_MISHEARS:
    # This is almost certainly a mishear — ask to repeat
    return "Non ho capito bene il cognome. Puo ripeterlo per favore?"
```

### 3D. Jaro-Winkler Aggressive Mode During Name States

Current threshold: 0.85 (conservative). During WAITING_NAME:
- Lower to 0.75 for surnames (they're expected)
- Compare against FULL names (nome + cognome), not just individual parts

### 3E. Dual-Engine Cross-Validation (Advanced, Zero Cost)

When FSM expects a name:
1. Groq Whisper (primary, ~200ms)
2. FasterWhisper tiny (fallback, ~3.8s on iMac)
3. If results disagree AND one looks like a name → pick that one
4. If both are common words → ask to repeat

**Cost**: Extra 3.8s latency on name turns only. Acceptable for a P0 fix.

---

## 4. GROQ WHISPER vs LOCAL WHISPER.CPP FOR SURNAMES

| Factor | Groq (whisper-large-v3) | FasterWhisper tiny (local) | FasterWhisper base (local) |
|--------|------------------------|---------------------------|---------------------------|
| Model size | 1.5B params | 39M params | 74M params |
| Italian WER (general) | ~12% | ~18% | ~14% |
| Proper noun accuracy | **Better** (larger model) | Worse | Moderate |
| Telephony audio | Lossy re-encode hurts | Raw PCM = cleaner | Raw PCM = cleaner |
| `initial_prompt` support | Yes (`prompt` param) | Yes (`initial_prompt`) | Yes |
| Latency | ~200ms | ~3.8s (iMac i5) | ~4.7s (iMac i5) |
| Confidence output | `verbose_json` | Per-segment logprob | Per-segment logprob |

**Key insight**: Groq has the better model (large-v3) but worse audio quality (re-encoded). Local has worse model but pristine audio. For proper nouns, the **prompt bias matters more than model size** — a well-prompted tiny model can outperform a poorly-prompted large model on expected vocabulary.

**Recommendation**: Keep Groq primary but fix the prompt. Add local FasterWhisper as cross-validation for name states only.

---

## 5. BEST PRACTICES FOR STT OF PROPER NOUNS IN ITALIAN TELEPHONY

### Industry Gold Standard (Retell AI, Vapi, Bland AI)

1. **Vocabulary priming**: Always include expected proper nouns in `initial_prompt`
2. **Hotwords/biasing** (not available in Whisper, but achievable via prompt): Place critical names at END of prompt (decoder recency bias)
3. **Contextual prompting**: Change prompt based on conversation state
4. **Confirmation loop**: After name recognition, always read back: "Ho capito Marco Rossi, corretto?"
5. **Spelling fallback**: If name fails 2x, ask: "Puo sillabare il cognome?"
6. **Database lookup**: After rough STT, fuzzy-match against client DB before confirming

### Telephony-Specific

1. **G.711 codec**: Strips >3.4kHz. Consonants /s/, /f/, /z/ become ambiguous. Vowels survive better.
2. **VAD trimming**: Don't cut too aggressively at start/end — name onset is in the first 100ms
3. **Upsample quality**: `audioop.ratecv` is good (anti-aliased). The gap is 3.4-8kHz which is silence — Whisper handles this ok with large-v3.
4. **Padding**: Add 200ms silence before/after the audio chunk sent to STT — Whisper works better with a small buffer.

---

## 6. CONCRETE IMPLEMENTATION PLAN

### FIX 1: Enhanced Prompt (P0, <1 hour) — `name_corrector.py`

```python
def build_whisper_prompt(client_names: List[str], 
                         business_owner: str = "",
                         max_chars: int = 800) -> str:
    """
    Costruisce prompt ottimale per Whisper.
    Nomi alla fine del prompt (decoder recency bias).
    Max ~224 token = ~800 char italiano.
    """
    # Context sentence at the start (will be pushed out of 224-token window
    # if we have many names — that's fine, names matter more)
    context = "Telefonata per prenotazione."
    
    names = []
    if business_owner:
        names.append(business_owner)
    names.extend(client_names)
    
    # Deduplicate preserving order
    seen = set()
    unique_names = []
    for n in names:
        key = n.lower().strip()
        if key not in seen:
            seen.add(key)
            unique_names.append(n)
    
    # Build: context + names (names at end for recency)
    name_str = ", ".join(unique_names)
    result = f"{context} {name_str}."
    
    # Truncate from start if over limit (keep names, drop context)
    if len(result) > max_chars:
        result = name_str[:max_chars]
    
    return result
```

### FIX 2: State-Aware Prompt (P0, 30 min) — `orchestrator.py`

```python
# In process_audio(), before STT call:
fsm_state = self.booking_sm.current_state if self.booking_sm else None
name_states = {BookingState.IDLE, BookingState.WAITING_NAME, 
               BookingState.WAITING_SURNAME}

if self._name_corrector and fsm_state in name_states:
    stt_prompt = self._name_corrector.get_prompt()
else:
    stt_prompt = "Prenotazione appuntamento salone. Si, no, confermo, annullo."
```

### FIX 3: verbose_json + Confidence Gate (P1, 1 hour) — `stt.py` + `groq_client.py`

```python
# In GroqSTT.transcribe():
create_kwargs = dict(
    file=("audio.wav", audio_file),
    model="whisper-large-v3",
    language=language,
    response_format="verbose_json",  # Changed from "text"
    temperature=0.0,
)
if stt_prompt:
    create_kwargs["prompt"] = stt_prompt

transcription = await self.client.audio.transcriptions.create(**create_kwargs)

# Extract text + confidence
text = transcription.text.strip()
segments = transcription.segments or []
avg_logprob = segments[0].avg_logprob if segments else 0.0

return {
    "text": text,
    "confidence": min(1.0, max(0.0, 1.0 + avg_logprob)),  # logprob is negative
    "avg_logprob": avg_logprob,
    "no_speech_prob": segments[0].no_speech_prob if segments else 0.0,
    ...
}
```

### FIX 4: Common-Word Rejection During Name States (P1, 30 min) — `orchestrator.py`

```python
_COMMON_ITALIAN_WORDS = {
    "grazie", "prego", "buongiorno", "buonasera", "arrivederci",
    "ciao", "salve", "scusi", "perfetto", "benissimo", "certamente",
    "allora", "ecco", "quindi", "comunque",
}

# In process_audio(), after STT + name_corrector.correct():
if fsm_state in name_states:
    cleaned = transcription.lower().strip().rstrip('.!?,;:')
    if cleaned in _COMMON_ITALIAN_WORDS:
        # Almost certainly a mishear — prompt the user
        return {
            "audio_response": tts("Non ho capito bene il nome. Puo ripeterlo?"),
            "text": "Non ho capito bene il nome. Puo ripeterlo?",
            "should_exit": False,
            "transcription": f"[rejected:{transcription}]",
        }
```

### FIX 5: Audio Padding (P2, 15 min) — `orchestrator.py`

```python
# In process_audio(), before STT:
# Add 200ms silence padding (improves Whisper accuracy on short utterances)
import struct
padding = b'\x00\x00' * int(16000 * 0.2)  # 200ms at 16kHz, 16-bit
padded_wav = _build_wav(padding + audio_bytes + padding)
```

### FIX 6: Spelling Fallback (P2, 30 min) — `booking_state_machine.py`

```python
# Track name retry count per session
if self._name_retry_count >= 2:
    return StateMachineResult(
        next_state=BookingState.WAITING_NAME,
        response="Non riesco a capire il cognome. Puo sillabare lettera per lettera?"
    )
```

---

## 7. IMPLEMENTATION PRIORITY

| # | Fix | Impact | Effort | Files |
|---|-----|--------|--------|-------|
| 1 | Enhanced prompt (800 chars, names at end) | **HIGH** | 30min | `name_corrector.py` |
| 2 | State-aware prompt (different prompt per FSM state) | **HIGH** | 30min | `orchestrator.py` |
| 3 | Common-word rejection during name states | **HIGH** | 30min | `orchestrator.py` |
| 4 | `verbose_json` + confidence gate | **MEDIUM** | 1hr | `stt.py`, `groq_client.py` |
| 5 | Audio padding for short utterances | **MEDIUM** | 15min | `orchestrator.py` |
| 6 | Spelling fallback after 2 failures | **LOW** | 30min | `booking_state_machine.py` |
| 7 | Dual-engine cross-validation | **LOW** | 2hr | `orchestrator.py`, `stt.py` |

**Recommended order**: Fix 1 + 2 + 3 together (immediate P0 fix, ~1.5 hours total).
Then Fix 4 + 5 in a follow-up session.

---

## 8. KEY FINDINGS SUMMARY

1. **Root cause is decoder language model bias**, not audio quality. Whisper's decoder assigns P("Grazie") >> P("Di Stasi") because "Grazie" appears millions of times in training data while "Di Stasi" appears near-zero times.

2. **The `prompt` parameter is the single most impactful fix.** It directly biases the decoder's token probabilities. Current implementation wastes prompt budget on context words instead of maximizing surname coverage.

3. **State-aware prompting is a force multiplier.** When FSM knows it's waiting for a name, the STT prompt should be 100% names, not generic booking context.

4. **Common-word rejection is a cheap safety net.** "Grazie" is never a valid answer to "Come si chiama?" — reject it deterministically.

5. **`verbose_json` unlocks confidence-based retry** which can catch remaining failures, but is not the primary fix.

6. **The VoIP audio path is adequate.** `audioop.ratecv` upsampling is proper anti-aliased resampling. The 8kHz→16kHz gap hurts consonant discrimination but the prompt fix compensates.

7. **Local FasterWhisper is not better for this problem.** The tiny model has worse Italian accuracy. The base model is better but 4.7s latency is too slow for primary use. Groq large-v3 with a good prompt is the right choice.
