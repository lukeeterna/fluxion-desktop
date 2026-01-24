# 🚀 PROMPT RIPARTENZA - 26 GENNAIO 2026

**Copia-incolla questo prompt per riprendere la sessione:**

---

```
Leggi questi file in ordine per recuperare il contesto della sessione precedente:

1. /Volumes/MontereyT7/FLUXION/CLAUDE.md (stato progetto)
2. /Volumes/MontereyT7/FLUXION/docs/sessions/SESSION-2026-01-25-voice-agent-validation.md (decisioni prese)

## CONTESTO RAPIDO

Ieri abbiamo deciso la strategia per il Voice Agent (differenziatore principale di Fluxion):

### DECISIONE: Validation-First (48 ore)

Prima di investire 9 giorni di sviluppo, validare 3 assunzioni:

1. **Llama 3.2 3B** → Accuracy ≥85% su intent italiani?
2. **Piper TTS** → Latenza p95 <800ms su M1?
3. **Whisper.cpp** → WER <12% su italiano?

### DECISION MATRIX

- **GREEN** (tutti pass) → Start 9-day dev sprint
- **YELLOW** (alcuni warn) → Modify architecture (+1-2 giorni)
- **RED** (fail multipli) → Pivot a RASA CALM o Groq cloud

### FILE CHIAVE

- Validator scripts: `/Users/macbook/Downloads/validation-phase-cto.md`
- Stack proposto: Llama 3.2 3B + Whisper.cpp + Piper TTS (tutto offline)

## TASK OGGI

Esegui la validation su iMac (192.168.1.9):

1. Setup Ollama + `ollama pull llama3.2:3b`
2. Setup Piper TTS italiano
3. Setup Whisper.cpp
4. Run 3 validator script
5. Compila risultati
6. Decision GO/NO-GO

## BUG ANCORA APERTI (Voice Agent attuale)

1. Entity extraction rotta
2. Database path mismatch
3. Flusso sempre propone registrazione

Questi bug verranno risolti DOPO la validation, nel dev sprint.

## COMANDI UTILI

# Verifica servizi iMac
ssh imac "lsof -i :3001 -i :3002 | grep LISTEN"

# Installa Ollama su iMac
ssh imac "curl -fsSL https://ollama.com/install.sh | sh"

# Pull Llama 3.2 3B
ssh imac "ollama pull llama3.2:3b"

Procedi con la validation.
```

---

## 📋 CHECKLIST RIPARTENZA

- [ ] Leggi CLAUDE.md
- [ ] Leggi SESSION-2026-01-25-voice-agent-validation.md
- [ ] Verifica servizi iMac attivi
- [ ] Inizia validation

## 🔗 FILE IMPORTANTI

| File | Contenuto |
|------|-----------|
| `CLAUDE.md` | Stato progetto |
| `docs/sessions/SESSION-2026-01-25-voice-agent-validation.md` | Decisioni ieri |
| `/Users/macbook/Downloads/validation-phase-cto.md` | CTO Playbook + validator |
| `/Users/macbook/Downloads/voice-agent-complete.md` | Architettura (da rivedere) |

---

*Creato: 2026-01-25 sera*
