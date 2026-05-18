# Prompt ripartenza S260 — VERDE close S259

**Generato**: 2026-05-18 (sessione S259 close)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Last commit S259**: `93a0073 fix(S259 P3.a): toast.error su mutation catch — 4 pages, 10 sites (REGOLA #11)`
**Stato S259**: VERDE. P3.a UX toast fix landed + iMac sync. P3.b audit decision: next encryption target = `impostazioni_fatturazione`.

---

## RIASSUNTO S259 (closed VERDE)

### P3.a — UX `toast.error` fix mutation catch (✅ DONE)
- **Audit cross-entity completo** su `src/pages/`: 10 catch sites missing `toast.error` su 4 files.
- **Fix applicati** (commit `93a0073`):
  - `Clienti.tsx`: handleSubmit (save) + handleConfirmDelete + import `toast` da sonner
  - `Fornitori.tsx`: handleSubmit, handleConfirmDelete, handleCreateOrder, handleUpdateOrderStatus, handleSendOrder
  - `Cassa.tsx`: registraIncasso + eliminaIncasso (chiusura cassa già aveva toast)
  - `Fatture.tsx`: handleConfirmDelete (emetti/inviaSdi già avevano toast)
- **Pattern**: `toast.error('Errore <azione>', { description: String(error) })` (italian copy, consistent con `Cassa.tsx::handleChiudiCassa` pre-esistente).
- **Out of scope motivato**:
  - `VoiceAgent.tsx` (3 sites) — usa `addError()` chip dedicato voice errors, pattern intenzionale.
  - `Analytics.tsx::handleGeneraPdf` — usa `setPdfError` state locale, pattern intenzionale.
  - `Impostazioni.tsx::deleteOrario/deleteFestivo` — no try/catch (propaga RQ default toast).
- **Verify**: `tsc --noEmit` 0 errors, lint 0 errors (17 warnings pre-esistenti su `e2e-tests/`), pre-commit gate verde.
- **Sync iMac**: `93a0073` fast-forward su `/Volumes/MacSSD - Dati/fluxion` ✓.
- **E2E retest manuale** (Fornitori 2.2/2.4 dup nome) **deferred a S260 live boot** — backend path invariato, no regression risk.

### P3.b — Audit next encryption target (✅ DONE)

**Tabelle scannerizzate** (ssh imac sqlite3 row count + table_info):

| Tabella | Cols PII | Rows | UNIQUE/Search | Effort | Priority |
|---|---|---|---|---|---|
| **impostazioni_fatturazione** | 8 (P.IVA, C.F., IBAN, indirizzo, tel, email, pec, denominazione) | **1** | None | trivial | **P0** ⭐⭐ |
| **fatture** (denorm snapshot) | 9 (cliente_denominazione, cliente_partita_iva, cliente_codice_fiscale, cliente_indirizzo, cliente_cap, cliente_comune, cliente_provincia, cliente_codice_sdi, cliente_pec) | 0 | None | trivial | P1 |
| messaggi_whatsapp | 2 (telefono, contenuto) | 0 | None | medium (tier-1 search) | P2 |
| chiamate_voice | 4 (telefono, trascrizione, note, sentiment) | 0 | None | medium (tier-1 search trascrizione) | P3 |
| voice_sessions | 2 (caller_number, caller_name) | 0 | None | trivial | P4 |
| appuntamenti | 2 (note, note_interne) | 46 | None | trivial | P5 |
| schede_* (medical/estetica/parrucchiere/fitness/veicoli/etc) | varie | 0 (tutti) | – | defer fino uso reale | — |
| license_cache | licensee_email | 1 | **gating compare** ⚠️ | SKIP (richiesto plaintext per gating) | — |
| whatsapp_templates | nome (template definition) | 378 | NO customer PII | SKIP | — |
| gdpr_consents/requests | – | 1/0 | – | scope GDPR separato | defer |

### Raccomandazione S260: **`impostazioni_fatturazione`**

Motivazione:
1. **Severity TOP attiva NOW**: 1 row con dato founder reale (PII azienda) già populated in DB → **IBAN + P.IVA + C.F.** = loss class "bank fraud / identity theft".
2. **Effort minimo**: singleton (id='default'), no UNIQUE su cols PII, no LIKE search, no view dipendente.
3. **Pattern S255 (operatori) replicabile diretto**: runner `encrypt_impostazioni_fatturazione_pii_v1` via `encrypt_table_pii` helper già refactored S255.
4. **Audit 4-point fast pass pre-verified**:
   - Views: ✓ (none referencing PII cols su questa tabella)
   - UNIQUE: ✓ (solo PK `id`)
   - LIKE search: ✓ (form read singleton)
   - FE types: ✓ (`ImpostazioniFatturazione` invariato)

---

## TASK S260 (proposto)

### P4 — Encryption `impostazioni_fatturazione` PII (~45-60 min)

Schema S260:
1. **STEP 1 — Schema check**: verificare `impostazioni_fatturazione` no UNIQUE constraints da rimuovere (vs S257 supplier che richiedeva Migration 040 drop UNIQUE). Pre-flight: `sqlite3 ... ".schema impostazioni_fatturazione"`.
2. **STEP 2 — Migration N+1** (probabilmente 041): no DROP UNIQUE necessario (verificato sopra). Skip migration table-rebuild → solo runner registrato.
3. **STEP 3 — Runner**: `encrypt_impostazioni_fatturazione_pii_v1` via `encrypt_table_pii` (refactor S255), cols target: `denominazione, partita_iva, codice_fiscale, indirizzo, telefono, email, pec, iban` (8 cols).
4. **STEP 4 — Wire `lib.rs`**: trigger post-encrypt_operatori_pii_v1, pre-encrypt_suppliers_pii_v1 (ordine: clienti → operatori → impostazioni_fatturazione → suppliers).
5. **STEP 5 — Commands & http_bridge**:
   - `commands/impostazioni_fatturazione.rs` (o file esistente): encrypt su `save`/`update`, decrypt su `get`.
   - `http_bridge.rs`: `maybe_decrypt_impostazioni_fatturazione_row` su GET endpoint.
   - **XML SDI generator path**: VERIFICARE che `generate_xml_fattura` legga via decrypted path (probabile: usa same query/cache di commands → OK).
6. **STEP 6 — Audit 4-point obbligatorio** (REGOLA #8):
   - Views: grep migrations `v_*` referencing impostazioni_fatturazione cols
   - UNIQUE: re-verify post-implementation
   - LIKE: grep `LIKE %imp` su rust queries
   - FE types: `src/types/*.ts` interface invariato + verificare path Form/Read
7. **STEP 7 — Test parallel**: `data_migration::test_encrypt_impostazioni_fatturazione_*` pattern S255.
8. **STEP 8 — Live verify su iMac** post-boot:
   - Boot1 migration runner OK (marker `encrypt_impostazioni_fatturazione_pii_v1` in `encryption_migration_state`)
   - Ciphertext on-disk (sqlite3 raw query `SELECT iban FROM impostazioni_fatturazione` → Base64)
   - Backup pre-encryption salvato (`fluxion.db.pre-encrypt_impostazioni_fatturazione_pii_v1-bak-*`)
   - HTTP/IPC GET impostazioni → plaintext decrypted correttamente
   - Boot2 idempotency log + DB byte-for-byte identità
   - Form UI Impostazioni save/load roundtrip (NO regression)
   - XML SDI generation roundtrip (decrypt path → XML corretto)

### P5 (backlog, opzionale) — fatture denorm snapshot
- Encryption applicare PRIMA della prima fattura emessa (0 row attuali = zero-cost migration).
- Pattern identico S260 ma 9 cols + path XML generation review più ampio.

### P6 (backlog) — tier-1 blind-index `clienti.cellulare` (S255 tech debt)
Non priority S260.

---

## STATO REPO (fine S259)

- `master` ultimo commit: `93a0073` (S259 P3.a) — verde, type-check + lint passati, sync iMac.
- iMac `/Volumes/MacSSD - Dati/fluxion` ff su `93a0073`.
- DB iMac: 3 supplier encrypted (S257) + 30 clienti (S254) + 2 operatori (S255) — tutti boot2-idempotent verified S256/S258.
- App FLUXION iMac: HTTP Bridge :3001 attivo (boot2 S258 ancora up se non ricyclata). Voice Pipeline :3002 NOT required per S260 P4.

---

## START S260 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S260 P4:
encryption impostazioni_fatturazione PII (8 cols, pattern S255 replicato).

Pre-flight S260:
1. Verifica iMac sync `git log --oneline -1` su master (expect `93a0073` S259).
2. App FLUXION iMac probabilmente still up da S258/S259. Voice Pipeline :3002 non required, ignorare hook.
3. Context expected boot ~20-22% (sotto WARN 40%, headroom ~30%).

Inizia da STEP 1 (schema check `impostazioni_fatturazione` no UNIQUE) →
STEP 2 (decidi se Migration 041 necessaria) → STEP 3 (runner) → STEP 4-7
(code + audit + test) → STEP 8 (live verify).
```

---

## VINCOLI HARD (riconferma S260)

- Vincolo #6 zero tolleranza ARANCIONE: VERDE / VERDE* / HANDOFF rosso.
- Vincolo #7 context budget: WARN 40%, BLOCK CRITICAL 50%, CLOSING 70%.
- Vincolo #8 (REGOLA MEMORY #8): audit 4-point PII encryption per table obbligatorio.
- Vincolo #9 (REGOLA MEMORY #9): test live = leggere gating site (license_cache populated) PRIMA di pianificare.
- Vincolo #11 (REGOLA MEMORY #11): toast.error cross-entity completo S259 P3.a, no follow-up gap noto su `src/pages/`. Components dialog (`src/components/**/*.tsx`) NON auditati S259 — backlog opzionale se gap UX scoperti in retest.
- Pre-action check DECISIONS FLUXION: D-01..D-05 scan prima di proposte tecniche S260 P4. D-05 (ephemeral port HTTP Bridge) NON toccato da encryption.

---

**Provenienza prompt S260**: S259 P3.a UX fix CLEAN + P3.b audit completo con matrice priorità data-driven (row count + schema info reali iMac DB). VERDE chiuso 2026-05-18.
