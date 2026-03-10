# P0.5 Onboarding Research — Sessione 44

## Decisione: Opzione B (Setup Wizard) — NON Opzione A (key bundled)

### Perché NO all'Opzione A (key AES embedded)
1. **Groq ToS**: condivisione chiave API vieta distribuzione in binari (violations → ban account)
2. **Security theater**: AES-256 nel binario è trivialmente reversibile (strings, Ghidra, ltrace)
3. **Legal exposure**: responsabilità per abuso quota da parte di utenti malevoli
4. **Rate limits**: 3 key free tier × condivise tra N utenti = fallimento garantito

### Perché SÌ all'Opzione B (Wizard)
1. Il wizard esisteva già con 8 step e step 8 già brandizzato "Fluxion AI" (nasconde Groq)
2. Voice agent già legge key da SQLite DB (main.py linea 628-629) — infrastruttura pronta
3. Groq free tier: 14.400 req/giorno per utente — più che sufficienti

## Stato Wizard Pre-P0.5
- 8 step totali, Step 8 = Groq setup
- Branding: "Fluxion AI" (non menziona Groq — ottimo per PMI)
- Test: FINTO — solo check formato gsk_ + ping http://127.0.0.1:3002/health
- Istruzioni già buone: link diretto + 3 passi numerati + skip option

## Gap Critico Risolto in s44
Test Groq: **fake → reale**
- Nuovo comando Tauri `test_groq_key` (setup.rs)
- Chiama GET https://api.groq.com/openai/v1/models con Bearer token
- 401 → "❌ Chiave non valida"
- 200 → "✅ Fluxion AI attivo! Sara è pronta"
- timeout → "❌ Nessuna connessione internet"

## File Modificati
- `src-tauri/src/commands/setup.rs`: +test_groq_key command
- `src-tauri/src/lib.rs`: +registrazione comando
- `src/hooks/use-setup.ts`: +useTestGroqKey hook
- `src/components/setup/SetupWizard.tsx`: Step 8 usa test reale

## Gap Residui (NON critici per vendite autonome)
- Gmail/SMTP: step non nel wizard (configurabile dopo in Impostazioni → SMTP)
- Step 2 (Sede Legale): skippable ma non prominentemente — accettabile
- 8 step totali: molti ma con skip disponibile — accettabile

## Verdict P0.5
Con il fix del test reale, un utente PMI può:
1. Aprire wizard → nome attività (1 min)
2. Categoria/specializzazione (1 min)
3. Licenza + firma contratto (2 min)
4. Groq: clic link → crea account → copia chiave → incolla → "✅ Sara pronta" (3-5 min)
**Target < 5 minuti → raggiungibile per utente motivato**

HEAD: 82fdd87
