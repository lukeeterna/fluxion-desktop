# Onboarding Frictionless — Deep Research
> Data: 2026-02-27 | CoVe verificato codebase reale

## PROBLEMA CRITICO
All'installazione l'utente PMI (non tecnico) deve:
1. **Groq API key** → crea account + genera key (10-15 min, tecnico)
2. **Gmail app password** → attiva 2FA + genera password app (5 min, tecnico)
→ **Blocco immediato alle vendite — churn al primo avvio**

---

## 1. MAPPA DIPENDENZE

### GROQ_API_KEY — CRITICO (blocca startup)
- `voice-agent/main.py` righe 467-471 → `sys.exit(1)` se non presente
- `voice-agent/src/groq_client.py` righe 40-43 → `raise ValueError`
- Usato per: STT (Whisper large-v3, ~200ms) + LLM (llama-3.3-70b fallback L4)
- **Fallback STT**: FasterWhisper offline (già implementato)
- **Fallback LLM**: NESSUNO → critico

### Gmail SMTP — MEDIO (opzionale, non critico path)
- `src-tauri/src/commands/settings.rs` → SmtpSettings struct
- `src/components/impostazioni/SmtpSettings.tsx` → UI con "App Password"
- Tabella `impostazioni`: smtp_host/port/email/password (toggle abilitazione)
- **Usato solo per**: email fornitori (non prenotazioni) → non blocca voice agent

### WhatsApp — BASSO RISCHIO
- `voice-agent/src/whatsapp.py` → WhatsApp Web via Node.js + QR scan
- Nessuna API key richiesta, solo numero di telefono

---

## 2. SETUP WIZARD ATTUALE (SetupWizard.tsx)
6 step esistenti — **GROQ KEY NON RICHIESTA**:
1. Dati azienda (nome, P.IVA, email, telefono) ✅
2. Indirizzo ✅
3. Macro-categoria settore ✅
4. Micro-categoria ✅
5. Tier licenza + FLUXION_IA_KEY ✅
6. WhatsApp number + EhiWeb number ✅

**Gap**: nessuno step per Groq API key

---

## 3. DATABASE SCHEMA ATTUALE
Tabella `impostazioni` (key-value) — **groq_api_key NON PRESENTE**

Chiavi esistenti: nome_attivita, partita_iva, email, whatsapp_number,
smtp_host/port/password, license_tier, setup_completed...

---

## 4. SOLUZIONI CANDIDATE

### A — Bundle Fluxion Groq Key ⭐ RACCOMANDATO per PMI
**Come funziona**: Fluxion fornisce propria key Groq org embedded nel binary (crittografata)
- Costo stimato: ~€0.001-0.003 per chiamata → ~€300-600/mese a 50 PMI
- Utente: **zero configurazione**, funziona subito
- Pro: ✅ zero friction, ✅ vantaggio competitivo, ✅ best UX
- Contro: ❌ costo variabile Fluxion, ❌ key management sicuro
- **Effort**: 2-3 giorni

### B — Setup Wizard Guidato (Step 7) ⭐ MIGLIORE A COSTO ZERO
**Come funziona**: Step aggiuntivo nel wizard con deep-link a Groq + test connessione
```
Step 7: "Configura Sara (Voice Agent)"
  → Bottone "Crea account Groq (gratis)" → apre browser groq.com
  → Campo input per incollare key
  → Bottone "Testa connessione" → chiama /health
  → Skip possibile con warning
```
- Pro: ✅ zero costo Fluxion, ✅ user possiede key, ✅ Groq free tier abbondante
- Contro: ⚠️ 5-10 min extra setup, ⚠️ richiede uscita dall'app
- **Effort**: 9.5 ore (1-2 giorni)

**FILE DA MODIFICARE**:
| File | Modifica | Ore |
|------|----------|-----|
| `src/components/setup/SetupWizard.tsx` | Aggiungi Step 7 | 5h |
| `src-tauri/src/commands/setup.rs` | Salva groq_api_key in DB | 1h |
| `voice-agent/main.py` | Load key da DB via Bridge come fallback | 2h |
| `src-tauri/migrations/023_groq_setup.sql` | Colonna groq_api_key | 0.5h |
| `src-tauri/src/http_bridge.rs` | Esponi endpoint groq_api_key | 1h |

### C — Proxy Server Fluxion
**Come funziona**: backend che astrae le API key (SaaS-like per AI, desktop per dati)
- Pro: ✅ trasparente all'utente, ✅ rate limiting centralizzato
- Contro: ❌ infrastruttura €50-100/mese, ❌ viola offline-first, ❌ privacy concern
- **Effort**: 7-10 giorni
- **Quando**: solo se costi Groq > €3k/mese (milestone: 50 PMI)

---

## 5. RACCOMANDAZIONE FINALE: IBRIDO B→A

**v0.9.2 (immediato, ~2 giorni)**: Soluzione B
- Step 7 nel wizard: guided Groq setup con deep-link
- Base (€297) → Groq free tier (30 call/min, 14.4k/giorno — abbondante)
- Pro/Enterprise → stessa cosa ma with "use Fluxion managed key" option

**v1.0 (medio termine, ~3 giorni)**: Soluzione A per Pro/Enterprise
- Bundle key Fluxion per Pro (€497) e Enterprise (€897)
- Costo assorbito nel pricing (call cost ~€1-3/mese/PMI a regime normale)
- Toggle "Usa la tua Groq key" per utenti avanzati

**v1.1 (opzionale)**: Soluzione C solo se volume > 50 PMI attivi

---

## 6. FIX CRITICO IMMEDIATO (anche prima del wizard)
`voice-agent/main.py` deve fare soft-fail invece di `sys.exit(1)`:
```python
if not groq_api_key:
    logger.warning("GROQ_API_KEY non configurata — voice agent avviato in modalità offline")
    # Usa solo FasterWhisper locale, LLM disabilitato
    # Mostra warning in-app invece di crash silenzioso
```
Questo evita che l'app sembri "rotta" anche senza key.

---

## 7. GMAIL APP PASSWORD — PIANO
- NON critico per path principale (voice + booking)
- Usato solo per email fornitori
- **Soluzione**: rendere opzionale al 100% nell'UI (già toggle, ma migliorare messaging)
- "Configura email fornitori (opzionale)" — non menzionarlo nel wizard principale
