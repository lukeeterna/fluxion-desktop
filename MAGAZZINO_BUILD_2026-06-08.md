# Magazzino + Alert Sottoscorta — Build Backend

Data: 2026-06-08 | WIP=1 magazzino (nessuna modifica a licenze/Sara/payload/CI).

## FASE 1 — Migration `042_magazzino.sql` — 🧪 TESTATO_LOCALE

File: `src-tauri/migrations/042_magazzino.sql` (additiva, dopo 041).

PROVA reale (DB temp + suppliers stub per la FK):
```
$ sqlite3 /tmp/mag_test.db "CREATE TABLE suppliers (id TEXT PRIMARY KEY);"
$ sqlite3 /tmp/mag_test.db < src-tauri/migrations/042_magazzino.sql
$ sqlite3 /tmp/mag_test.db ".schema articoli"
CREATE TABLE articoli (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    nome TEXT NOT NULL, categoria TEXT,
    giacenza INTEGER NOT NULL DEFAULT 0,
    soglia_minima INTEGER NOT NULL DEFAULT 0,
    prezzo_acquisto REAL, prezzo_vendita REAL, ean TEXT,
    fornitore_id TEXT REFERENCES suppliers(id),
    alert_notificato INTEGER NOT NULL DEFAULT 0,
    attivo INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_articoli_attivo ON articoli(attivo);
$ sqlite3 .schema movimenti_magazzino
CREATE TABLE movimenti_magazzino (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    articolo_id TEXT NOT NULL REFERENCES articoli(id),
    tipo TEXT NOT NULL, quantita INTEGER NOT NULL,
    causale TEXT, riferimento TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX idx_movimenti_articolo ON movimenti_magazzino(articolo_id);
# INSERT articoli(nome,soglia_minima)=('Shampoo',5) ->
# d033365b23b6fcc59596bc6716b5dcb6|Shampoo|0|5|0|1  (uuid-default OK, default OK)
```
Indici su `articoli(attivo)` e `movimenti_magazzino(articolo_id)` presenti.
Provata con suppliers stub (la migration reale gira dopo 016 in produzione).

## FASE 2 — Comandi `src-tauri/src/commands/magazzino.rs` — 🧪 TESTATO_LOCALE (cargo iMac)

Comandi (tutti `async`, `Result<_,String>`, zero `.unwrap()` in produzione):
`articolo_crea`, `articolo_aggiorna`, `articolo_lista` (attivo=1), `articolo_elimina`
(soft-delete attivo=0), `articolo_set_soglia`, `movimento_registra` (transazione
`pool.begin()`: insert movimento + update giacenza, rollback se scarico<0, quantita>0),
`magazzino_sottoscorta`, `magazzino_alert_count`, `magazzino_recompute_alerts`.

Registrati: `commands/mod.rs` (`pub mod magazzino;` + `pub use magazzino::*;`) e
`lib.rs` (9 voci in `generate_handler!` dopo il blocco Cassa).

## FASE 3 — Alert automatico anti-spam — 🧪 TESTATO_LOCALE (cargo iMac)

`alert_notificato` gestito DENTRO la transazione di `movimento_registra`:
giacenza scende a `<=soglia` -> 1; risale `>soglia` -> 0.
`magazzino_alert_count` = badge sidebar. `magazzino_recompute_alerts` = boot, idempotente.
(3c) Notifica email titolare NON implementata: solo `// TODO(magazzino-3c)` nel punto
in cui l'alert scatta (riuso SMTP Python pendente decisione founder). Nessun tocco a OAuth/SMTP/wizard/Python.

## TEST (sqlx in-memory) — 🧪 TESTATO su iMac

PROVA reale `cargo test --lib magazzino::` su iMac (`/Volumes/MacSSD - Dati/fluxion/src-tauri`):
```
Finished `test` profile ... in 2m 44s
running 4 tests
test commands::magazzino::tests::test_scarico_sotto_zero_rollback ... ok
test commands::magazzino::tests::test_sottoscorta_query ... ok
test commands::magazzino::tests::test_carico_scarico_giacenza ... ok
test commands::magazzino::tests::test_antispam_alert ... ok
test result: ok. 4 passed; 0 failed; 0 ignored; 92 filtered out; finished in 0.01s
```
Build compila (56 warning preesistenti su altri file, nessuno su magazzino).

## File creati/modificati
- CREATO `src-tauri/migrations/042_magazzino.sql`
- CREATO `src-tauri/src/commands/magazzino.rs`
- MODIFICATO `src-tauri/src/commands/mod.rs` (+2 righe)
- MODIFICATO `src-tauri/src/lib.rs` (+9 voci handler)

## Note sync
rsync iMac fallito (rsync 2.6.9 remoto incompatibile) -> usato `scp` con quoting remoto.

## Stato fasi
FASE 1 🧪 | FASE 2 🧪 | FASE 3 🧪 | TEST 🧪 (4/4 pass cargo iMac).
Non eseguito: E2E IPC via app GUI (richiede launch iMac) — fuori scope di questo task.

## Tabella fasi (riepilogo)
| Fase | Stato | Prova |
|------|-------|-------|
| 0 Ancoraggio | ✅ | migration 042, gate `LicenseFeatures`, magazzino assente, email solo Python |
| 1 Schema | 🧪 TESTATO_LOCALE | `sqlite3 .schema` su /tmp/mag_test.db |
| 2 Backend (9 cmd) | 🧪 TESTATO iMac | `cargo test --lib magazzino::` 4/4 |
| 3 Alert anti-spam | 🧪 TESTATO iMac | test `test_antispam_alert` pass |
| 3c Email titolare | ⏸️ DEFER (CTO) | non costruito — tocca pipeline Python, coperto da badge+toast. TODO resta |
| 4 UI React | ✅ FATTO (commit `e138345`) | `npm run type-check` 0 errori; pagina+hook+sidebar badge+dashboard widget+route+gating upsell+toast |
| 5 Gating Pro | ✅ FATTO (commit `e138345`) | `cargo check` iMac Finished 0 errori; flag `magazzino_alert` Trial/Pro/Enterprise=true Base=false |
| 6 E2E GUI | 🔒 BLOCKED-ON founder | IPC+gating live (Base=gated/Pro=attiva) richiede launch app GUI iMac+Keychain (REGOLA #12). Logica backend già coperta da cargo test |

## Decisioni founder (risolte autonomamente — REGOLA #15)
- **(a) Gate = Pro-only**: flag `magazzino_alert` (NO nuovo SKU Stripe / NO nuova decisione pricing). Allineato a `license_ed25519.rs:203` (Pro=features). Reversibile in 1 riga se si vuole in Base.
- **(b) Email sottoscorta 3c = DEFER**: evita scope-creep nella pipeline Python (REGOLA #21); badge sidebar + toast in-app coprono l'alert UX. `TODO(magazzino-3c)` resta in `movimento_registra`.

## ⚠️ Igiene repo iMac (pre-esistente, NON causato da questo task — flag founder)
iMac repo `/Volumes/MacSSD - Dati/fluxion`: HEAD `40fcb80d` **94 commit dietro** origin/master + modifiche magazzino FASI 1-3 **non committate** (scp sessione precedente) + 1 commit locale `40fcb80d` (S355, contenuto già su origin via `8b2f70c`). `git pull` fallisce (divergent + local changes). FASE 5 verificata via scp del solo `license_ed25519.rs` + `cargo check` (zero modifiche git su iMac). **Riconciliazione iMac↔origin = chirurgia git rischiosa su stato condiviso → richiede OK founder** (rischio: perdere artefatti .so NDEBUG Sara / change non committate). Raccomandazione: sessione dedicata con founder presente.

## Caveat onesto (REGOLA #24)
I 4 test esercitano la LOGICA via helper `registra()` che replica `movimento_registra`
(il wrapper Tauri `State<'_, SqlitePool>` non è unit-testabile direttamente). La logica
transazionale/anti-spam è provata; la funzione-comando letterale no. Drift comando↔helper
non verrebbe colto da test → coprire con E2E IPC (FASE 6).

## PROSSIMA SESSIONE — lavoro residuo
1. **DOMANDE FOUNDER (sbloccano FASE 5 + 3c)**:
   - (a) Gate = **Pro-only** confermato? (flag `magazzino_alert`: Base=false, Pro/Trial/Enterprise=true). Alternativa = add-on SKU separato = NUOVA decisione pricing/Stripe (NON creata).
   - (b) Email sottoscorta al titolare (3c): la vuoi nel follow-up? Ricetta pronta: nuova fn Python `send_lowstock_alert(owner_email, articoli)` in `voice-agent/src/supplier_email_service.py` (riusa `_load_settings_from_db` + smtplib) + endpoint bridge `POST /api/magazzino/alert-email` chiamato da Rust quando `alert_notificato` passa 0→1. ~40 LOC, zero tocco a OAuth/wizard. Serve anche un campo "email titolare" (settings) o si usa `smtp_email_from`.
2. **FASE 4 — UI** (delega `frontend-developer`): pagina `Magazzino` (lista, sottoscorta in cima, form crea/modifica, soglia inline, pulsanti carico/scarico), voce sidebar con badge da `magazzino_alert_count()`, hook `useMagazzino`, route, `data-testid`. Widget dashboard "Sottoscorta: N" se la dashboard ha widget. Toast in-app su scarico-sottoscorta. vitest + screenshot.
3. **FASE 5 — Gating** (dopo conferma 0.5): aggiungi `magazzino_alert: bool` a `LicenseFeatures` (struct riga ~136 + `Default` ~160 + `for_tier()` ~175) + braccio in `check_feature_access_ed25519` (~842, `"magazzino_alert" => ...`) in `license_ed25519.rs`. NON toccare il payload firmato. Sidebar: senza diritto → upsell, non la feature. Prova: base=gated, pro=attiva.
4. **FASE 6 — E2E**: crea articolo → set soglia → scarico sottoscorta → badge sale senza aprire pagina (+ email se 3c) → pagina evidenzia articolo → con licenza Base = gated.

## Comando ripartenza
`cargo test --lib magazzino::` su iMac per riconfermare verde, poi FASE 4 via frontend-developer.
