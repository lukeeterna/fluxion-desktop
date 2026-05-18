# Prompt ripartenza S263 — Bug Fatture + STEP 5-8 live verify S262

**Generato**: 2026-05-18 chiusura S262 @ context 61% (BLOCK_CRITICAL)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Last commit master**: `ede8b67 auto-close session ... @ 2026-05-18T17:47:52Z` (contiene fix LicenseManager Pro=1 verticale)
**Stato S262**: VERDE-CON-ASTERISCO. STEP 1-4 PASS verified, STEP 5-8 pending founder action. Fix piano Pro applicato. 2 bug Fatture nuovi scoperti (NON encryption-related).

---

## OUTCOME S262 (consegnato)

### Live verify S260 P4 impostazioni_fatturazione encryption
- **STEP 1 ✅ PASS** — marker DB `encrypt_impostazioni_fatturazione_pii_v1` applied_at=`2026-05-18 09:12:30`, rows_processed=1, backup_path tracked
- **STEP 2 ✅ PASS** — backup file `fluxion.db.pre-encrypt_impostazioni_fatturazione_pii_v1-bak-20260518-091230` (1.13MB)
- **STEP 3 ✅ PASS** — ciphertext Base64 confermato su 4 cols populated (denominazione/partita_iva/codice_fiscale/indirizzo), 4 vuote pass-through
- **STEP 4 ✅ PASS** — header tab Fatture screenshot s2 mostra `Automation Business - P.IVA 02159940762 - Regime Forfettario` plaintext = decrypt path UI confermato
- **STEP 5 ⏳ pending** — founder restart app → atteso log `🔐 PII migration (impostazioni_fatturazione): already applied`
- **STEP 6 ⏳ pending** — md5 baseline boot1 catturato `842b0b61ab437e565ac6c76e99b851db` → confronto post-boot2 atteso identità
- **STEP 7 ⏳ pending** — form UI Impostazioni save→reload roundtrip (founder modifica telefono → salva → chiude → riapre → verifica persistenza)
- **STEP 8 ⏳ pending** — XML SDI fattura test → atteso `<Denominazione>Automation Business</Denominazione>` plaintext nei tag

### Bonus discovery & fix S262

**FIX piano Pro: 1 LICENZA = 1 VERTICALE** (regola founder)
- Commit `ede8b67` (auto-close) contiene `src/components/license/LicenseManager.tsx`
- FEATURE_ROWS: rimosso `'3 Schede Verticali' → pro: true`
- `'1 Scheda Verticale'` ora `base: true, pro: true, clinic: false`
- Clinic resta `Verticali illimitate` (founder ha detto "puoi lasciarlo")
- Type-check 0 errori
- `types/license-ed25519.ts` già corretto (`max_verticals: z.number().default(1)`, features Pro array NON menzionano "3 verticali")
- Migration 020 commento SQL riga 41 (`-- pro: €399, 3 verticali`) NON user-facing, lasciato (sarebbe commit cosmetico)

### Bug Fatture scoperti (regressioni preesistenti, NON S260/S262)

Dagli screenshot iMac 2026-05-18 19:37 / 19:40:

1. **BUG-FATT-1 ERROR BOUNDARY** (s1 19:40):
   ```
   `TabsContent` must be used within `Tabs`
   ```
   ErrorBoundary catch in tab Fatture → pagina inutilizzabile. Causa: componente `<TabsContent>` Radix-UI usato fuori da wrap `<Tabs>` parent. Indagare in `src/pages/Fatture.tsx` o componenti figli.

2. **BUG-FATT-2 SCHEMA GAP** (s2 19:37:50):
   ```
   Errore caricamento fatture: error returned from database:
   (code: 1) no such column: deleted_at
   ```
   Query Rust referenzia colonna `deleted_at` su tabella `fatture` che non esiste in schema. Soft-delete pattern incompleto. Indagare `src-tauri/src/commands/fatture.rs` o repository fatture query, + migrations cronologia per capire se serve ADD COLUMN o se serve rimuovere `deleted_at` dalla query.

---

## TASK S263 — Bug Fatture fix + STEP 5-8 live verify

### Sequenza S263 (context fresco, ordine consigliato)

```
1. Read .claude/NEXT_SESSION_PROMPT.manual.md (questo file)
2. Founder restart app iMac → STEP 5 + STEP 6 atomic verify (founder action + ssh md5)
3. Investigate BUG-FATT-2 deleted_at:
   - Grep "deleted_at" in src-tauri/src/commands/fatture.rs + repos
   - Read migrations Fatture cronologia (probabilmente missing ADD COLUMN deleted_at su fatture)
   - DECISIONE: aggiungere migration `041_fatture_deleted_at.sql` OPPURE rimuovere clause dalla query (preferire migration: soft-delete pattern coherent cross-entity)
   - Test E2E: ssh imac sqlite3 schema check + cargo test + tab Fatture loads
4. Investigate BUG-FATT-1 TabsContent crash:
   - Read src/pages/Fatture.tsx + sub-components Tabs/TabsContent imports
   - Trovare TabsContent senza Tabs wrap (probabile root layout fix)
   - Test E2E: tab Fatture renders senza ErrorBoundary
5. STEP 7 founder UI roundtrip (modifica telefono Impostazioni)
6. STEP 8 founder fattura test → XML inspect tag plaintext
7. CLOSE VERDE se tutto PASS
```

### Acceptance Criteria S263

- BUG-FATT-1: tab Fatture renders senza error boundary
- BUG-FATT-2: lista fatture carica (anche se vuota, 0 risultati OK)
- STEP 5: log `already applied` su 2nd boot
- STEP 6: md5 boot1=`842b0b61ab437e565ac6c76e99b851db` = md5 boot2
- STEP 7: telefono modificato persiste post-restart (encrypt write + decrypt read roundtrip)
- STEP 8: XML SDI contiene tag plaintext denominazione/partita IVA

### Vincoli S263

- **Context budget**: S263 inizia ~17% boot. Bug Fatture entrambi richiedono edit schema/query Rust + componente React → mantenere < 50% prima di edit `src-tauri/src/commands/fatture.rs` (file critico).
- **REGOLA #9 (S253)**: leggere migration history fatture cronologia PRIMA di pianificare fix `deleted_at` per identificare se è add-column vs remove-from-query.
- **MAI revert encryption**: i 4 runner sono live, mai DROP marker o restore backup `.pre-encrypt_*`.
- **DECISIONE CTO autonoma** (regola #3, no liste A/B su tecniche).

---

## PROMPT START S263 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S263:

Step 1: chiedere founder "App FLUXION attualmente UP su iMac via GUI?"
  - SE NO → guidare relaunch fisicamente per STEP 5/6/7/8 disponibili
  - SE SI → STEP 5 atteso "already applied" log + STEP 6 md5 check

Step 2 (parallel): investigate BUG-FATT-2 (deleted_at column missing)
  - Grep "deleted_at" in src-tauri/src/commands/fatture.rs + repos
  - Read migrations cronologia fatture
  - DECIDERE: add migration 041_fatture_deleted_at.sql vs remove from query
  - Vincolo: pattern soft-delete coerente cross-entity (controllare clienti/operatori/suppliers)

Step 3: investigate BUG-FATT-1 (TabsContent fuori da Tabs)
  - Read src/pages/Fatture.tsx tree
  - Localizzare TabsContent orphan → wrap in <Tabs>

Step 4: applicare fix + type-check + cargo test + sync iMac

Step 5: founder restart app → verify Fatture renders + STEP 5-8 live

CLOSE VERDE se BUG-FATT-1+2 fix + STEP 5-8 PASS.
Commit unico: fix(S263): Fatture deleted_at schema + TabsContent wrap + S262 live verify 8/8
```

---

**Provenienza S262 close**: VERDE-CON-ASTERISCO @ context 61% (BLOCK_CRITICAL preventive, vincolo #7). 4/8 live verify hard-confirmed + 1 fix bonus piano Pro + 2 bug Fatture documentati per context fresco S263.
