# Fluxion Bug Tracker

## Bug Aperti e Funzionalita NON Funzionanti

> ATTENZIONE: Questa lista contiene problemi REALI verificati.
> NON marcare come risolto senza test E2E + verifica DB!

### Criterio per marcare RISOLTO

```
1. Codice scritto e deployato
2. Test manuale: conversazione completa funziona
3. Verifica DB: SELECT conferma record creati
4. Test E2E passa (se applicabile)
```

### CRITICI (P0) - Voice Agent

| ID | Descrizione | Status | Fix Date |
|----|-------------|--------|----------|
| VA-01 | Client search non triggera | RISOLTO | 2026-01-23 |
| VA-02 | Client create non funziona | RISOLTO | 2026-01-23 |
| VA-03 | Booking create non funziona | RISOLTO | 2026-01-23 |
| VA-04 | Campo names mismatch (service vs servizio) | RISOLTO | 2026-01-23 |

### ALTI (P1) - Funzionalita core

| ID | Descrizione | Status | Fix Date |
|----|-------------|--------|----------|
| VA-05 | Cancella appuntamento | RISOLTO | 2026-01-27 |
| VA-06 | Sposta appuntamento | RISOLTO | 2026-01-27 |
| VA-07 | Lista d'attesa | RISOLTO | 2026-01-23 |
| VA-08 | Guided Dialog | RISOLTO | 2026-01-21 |

### MEDI (P2) - UX e robustezza

| ID | Descrizione | Status | Note |
|----|-------------|--------|------|
| VA-09 | Operatore preferenza | Aperto | Da verificare flusso |
| VA-10 | Disambiguazione E2E | Aperto | Richiede 2+ clienti omonimi |
| VA-11 | Disponibilita slot alternatives | Aperto | Da migliorare UX |

### RISOLTI (storico)

| ID | Descrizione | Priority | Data Fix |
|----|-------------|----------|----------|
| BUG-V5 | Voice UI: microfono non si ferma | P1 | 2026-01-22 |
| BUG-V2 | Voice UI si blocca dopo prima frase | P1 | 2026-01-15 |
| BUG-V3 | Paola ripete greeting | P1 | 2026-01-15 |
| BUG-V4 | "mai stato" interpretato come nome "Mai" | P1 | 2026-01-15 |

### Bloccante: macOS Compatibility

- Tauri 2.9.5 NON funziona su macOS Big Sur (11.x)
  - Crash: `webView:requestMediaCapturePermissionForOrigin:` (API macOS 12+)
  - Workaround: Sviluppo su MacBook, test su iMac (Monterey 12.7.4)

- Python 3.13 Limitazioni
  - No PyTorch: Chatterbox TTS e FAISS disabilitati
  - Workaround: SystemTTS (macOS say) + keyword search
