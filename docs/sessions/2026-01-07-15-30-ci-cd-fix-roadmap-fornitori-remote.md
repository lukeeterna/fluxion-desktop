# Sessione: CI/CD Fix + Roadmap Fornitori + Remote Assistance

**Data**: 2026-01-07T15:30:00
**Fase**: 7
**Agenti**: rust-backend, devops, architect

---

## Modifiche Completate

### 1. CI/CD Fix - SQLx Macros
**Problema**: `sqlx::query_scalar!` macros richiedono DATABASE_URL a compile-time, falliscono in CI/CD.

**File modificati**:
- `src-tauri/src/commands/cassa.rs` (3 fix)
- `src-tauri/src/commands/faq_template.rs` (aggiunto `data_nascita` a `ClienteMinimo`)

**Soluzione**: Convertito `query_scalar!` → `query_scalar::<_, Type>()` runtime queries.

**Risultato**: CI/CD Run SUCCESS 9/9 jobs su 3 OS.

### 2. Mock Data Cassa
**File**: `scripts/mock_data.sql`

Aggiunti:
- 5 metodi pagamento (contanti, carta, satispay, bonifico, assegno)
- 15 incassi mock (ultimi giorni)
- 3 chiusure cassa

### 3. Diagnosi Problema iMac
**Problema**: Pagina Fatture vuota su iMac.

**Root Cause**: Database iMac ha schema VECCHIO (pre-migration 007).
- Colonne mancanti: `tipo_documento`, `cliente_denominazione`, `imponibile_totale`, etc.
- `CREATE TABLE IF NOT EXISTS` non aggiorna tabelle esistenti.

**Soluzione**:
```bash
rm -rf ~/Library/Application\ Support/com.fluxion.desktop/
rm -rf src-tauri/target/
git pull && npm run tauri dev
```

### 4. Roadmap Fornitori + Comunicazione
**Salvato in CLAUDE.md** sezione `in_corso` → punto 6.

Schema DB:
- `email_providers` (Gmail, Libero, Outlook, Aruba, Yahoo, Custom)
- `email_config` (configurazione utente con password crittografata)
- `fornitori` (anagrafica con email + telefono WhatsApp)
- `ordini_template` (template ordini con variabili)

Flow:
1. Setup Wizard → seleziona provider → auto-compila SMTP
2. Crea fornitore → email/WhatsApp
3. Ordine → template → preview → invia

### 5. Roadmap Remote Assistance
**Salvato in CLAUDE.md** sezione `in_corso` → punto 7.

Decisione:
- **MVP**: Tailscale + SSH (gratuito, P2P, WireGuard)
- **Enterprise**: RustDesk self-hosted

Vantaggi Tailscale:
- Costo $0 (fino 100 device)
- Setup 1 minuto
- NAT traversal automatico
- Crittografia WireGuard

---

## Commit Effettuati

1. `6ad10e5` - fix(ci): quote test filter pattern for YAML compatibility
2. `3e78fa5` - fix(ci): correct cargo test filter syntax
3. `8d7f080` - fix(ci): convert sqlx query_as! macros to runtime queries
4. `63d877e` - docs: add Fornitori + Remote Assistance roadmap to CLAUDE.md

---

## TODO Prossima Sessione

1. **[PRIORITÀ]** Fix iMac database:
   ```bash
   rm -rf ~/Library/Application\ Support/com.fluxion.desktop/
   rm -rf src-tauri/target/
   git pull && npm run tauri dev
   ```

2. **Test su iMac**:
   - Pagina Cassa (registra incasso, chiudi cassa)
   - Pagina Fatture (crea bozza, emetti, download XML)
   - Import mock_data.sql

3. **Implementazione** (quando ready):
   - Migration 010: tabelle fornitori + email
   - fornitori.rs: Tauri commands CRUD
   - email.rs: invio SMTP con lettre
   - UI FornitoriPage + EmailSetup in Wizard

---

## Note Tecniche

### SQLx Runtime vs Compile-time
```rust
// COMPILE-TIME (richiede DATABASE_URL) - NON USARE IN CI/CD
let count = sqlx::query_scalar!("SELECT COUNT(*) FROM table").fetch_one(&pool).await?;

// RUNTIME (funziona sempre) - USA QUESTO
let count: i32 = sqlx::query_scalar("SELECT COUNT(*) FROM table")
    .fetch_one(&pool)
    .await?;
```

### Provider SMTP Italiani
| Provider | Host | Porta | Note |
|----------|------|-------|------|
| Libero | smtp.libero.it | 465 | SSL obbligatorio |
| Aruba | smtps.aruba.it | 465 | SSL obbligatorio |
| Gmail | smtp.gmail.com | 587 | App password richiesta |

---

## Screenshot
Nessuno (sessione di pianificazione).
