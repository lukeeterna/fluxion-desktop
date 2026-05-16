# S248 — Cat 3 P0 #2 Master password flow + encryption wiring CRUD clienti

**Generato**: 2026-05-16 fine S247 (CLOSED GREEN — T1 commit `8ad8b39`)
**Repo**: master `8ad8b39` (MacBook + iMac sync OK)
**Pipeline iMac**: DOWN_OK
**Mandato S244**: NO MVP, NO lancio parziale, pre-launch full quality.

## S247 — Cosa è stato chiuso

**Decisioni CTO prese (no founder review, mandato S181)**:
- **D1 = D Asterisk ARI Docker** (8-16h) — drop pjsua2, 9 fix S232-S239 falsificati = bug strutturale binding
- **D2 = A Meta Business API (Pro) + B Baileys+consenso (Base)** — drop whatsapp-web.js (ToS violation = rischio civile)
- **D3 = docs update 8 macro / 50 micro** — codice `src/types/setup.ts` ha 8 macro + 50 micro reali (NON 17 come PRD outdated)

**Cat 3 P0 #1 fixato** (commit `8ad8b39`):
- `DEFAULT_SALT = b"FLUXION_GDPR_SALT_v1"` hardcoded → rimosso
- `get_or_create_salt()` legge da OS keychain (macOS Keychain Services / Windows Credential Manager via `keyring` 3.6)
- Prima init: genera 32-byte random `OsRng`, persiste in keychain
- Split `init_encryption` (prod, keychain) vs `init_encryption_with_salt` (test)
- 4/4 unit test verdi (`cargo test --lib encryption::` su iMac)

**Threat coperto**: rainbow-table cross-installazione su DB rubato → attaccante deve ora brute-force ogni vittima individualmente.

**Sentry founder action pending**: founder ha confermato che crea nuovo account Sentry con email alternativa (`fluxion.dev@gmail.com` o variant). Aspettare DSN + auth token prima di toccare `src-tauri/src/lib.rs` + `src/main.tsx` + GH secrets.

## S248 — Cosa fare

### Task 1 — D3 docs update (5min, file critico CLAUDE.md → fai a inizio sessione con context fresco <40%)

- `/Volumes/MontereyT7/FLUXION/CLAUDE.md` riga 263: `6 macro x 17 sotto-verticali` → `8 macro x 50 micro`
- Allineare se altri file menzionano counts errati: `grep -rn "9 verticali\|6 macro\|17 micro\|17 sotto" /Volumes/MontereyT7/FLUXION --include="*.md" | grep -v node_modules | grep -v ".claude/cache"`
- VOS canonical D-01 (~/venture-os/wiki/projects/FLUXION/DECISIONS.md) dice "9 verticali settori SMB" — disallineato anche lì. Riconciliare con D-NN nuova entry o nota.

### Task 2 — Cat 3 P0 #2 Master password flow (audit + decide)

**Problema**: `gdpr_init_encryption(master_password, device_id)` esposto come Tauri command. Mai chiamato dal frontend. Domande aperte:
- Chi sceglie la master_password? L'utente al setup wizard? Auto-generata e salvata in keychain?
- Se utente la sceglie: come la recupera se la dimentica? Recovery flow?
- Se auto-generata: come previene attacco insider su DB + keychain dump?

**Hypothesis CTO da validare**:
- **A** (consigliato): master_password = derivata da `license_email + machine_uid` via PBKDF2, salvata cifrata in keychain entry separata. Utente non vede mai password. Recovery = re-attivazione licenza.
- **B**: utente sceglie master password al setup wizard, mostrata 1 volta, recovery via reset (perdita PII).

**Output Task 2**: scegliere A o B, documentare in `.claude/cache/agents/s248/master-password-flow-decision.md` + research subagent `backend-architect` per implementazione canonical.

### Task 3 — Cat 3 P0 #2 Wiring encryption CRUD clienti

**Stato attuale**: `encrypt_field`/`decrypt_field` sono dead code (zero call site fuori da `encryption.rs` tests). PII in plaintext in SQLite.

**Implementare**:
- Patch `src-tauri/src/commands/clienti.rs` (e/o repository layer) per cifrare in scrittura/decifrare in lettura i campi `SENSITIVE_FIELDS`: `nome, cognome, telefono, email, codice_fiscale, partita_iva, indirizzo, cap, citta, pec, data_nascita`
- Auto-init `init_encryption(...)` allo startup app (Tauri setup hook) — usando flow scelto in Task 2
- Migration SQLite per dati esistenti: leggi plaintext → cifra → write back. Atomic transaction + backup pre-migration.
- Test E2E: crea cliente, verifica DB SQLite ha campi base64 (non plaintext), legge cliente, verifica decrypt OK.

**Effort stimato Task 2+3**: ~10-15h. Multi-commit (audit doc → master password flow → wiring → migration → E2E test).

### Task 4 — Sentry DSN update (se founder ha già attivato nuovo trial)

- Aggiornare `src-tauri/src/lib.rs` e `src/main.tsx` con nuovo DSN env var
- Update GH secrets `SENTRY_DSN` + `SENTRY_AUTH_TOKEN`
- Enable Business features 14gg: `tracesSampleRate: 0.1`, `replaysSessionSampleRate: 0.1`, `profilesSampleRate: 0.1`
- Calendar reminder ~2026-05-30: revert sample rates a 0.0 pre-downgrade

## Roadmap pre-launch restante (post-S247)

Audit `.claude/cache/agents/s245/PRE-LAUNCH-AUDIT.md` (376 righe, 6/6 cat, 31 P0).

| Fase | Cat | Effort | Stato |
|------|-----|--------|-------|
| B (Security/Perf/Compliance) | 3 P0 #1 salt keychain | ~3h | ✅ S247 done |
| B | 3 P0 #2 master pw flow + wiring | ~10-15h | ⏭ S248 |
| B | 3 P0 #3 CSP Tauri | ~2h | pending |
| B | 3 P0 #4 cargo audit CI | ~2h | pending |
| B | 3 P0 #5 HTTP Bridge auth | ~3-4h | pending |
| B | 4 P0 ipc_bench live | ~1h | pending |
| B | 5 P0 #1-#5 GDPR/FatturaPA | ~14-20h | pending |
| C | 1 Build/Distribution 8 P0 | ~12-16h | pending |
| C | 2 Functional E2E 7 P0 | ~30-50h | pending (post D1/D2 fix) |
| C | 6 Customer Success 5 P0 | ~12-17h | pending |
| D | Pre-launch validation | ~8-12h | pending |

**Totale residuo**: ~77-100h sequential (~60-75h con 2 stream paralleli).

## Vincoli mantenuti

- Verifiche reali, no claim a memoria (es. S247 verified `keyring::Error::NoEntry` via docs.rs)
- Sequential atomic commits per P0
- CTO decide P0/P1/P2 senza review
- A 50-70% context: NO edit file critici (schema, config, rules, CLAUDE.md, PLAN.md)
- A 70%+ context: closing only
- A 80%+: hard stop
- Test E2E obbligatorio per ogni fix
- Zero costi

## Comando ripartenza S248

```bash
cd /Volumes/MontereyT7/FLUXION
git log -1 --format="%h %s"
# Atteso: 8ad8b39 feat(S247): per-installation PBKDF2 salt in OS keychain
cat .claude/NEXT_SESSION_PROMPT.manual.md
# Task 1: D3 docs update CLAUDE.md riga 263 (context <40% required)
# Task 2: audit master password flow → scegliere A o B → doc cache
# Task 3: wiring encryption CRUD clienti + migration + E2E
# Task 4 (se DSN arrivato): Sentry update
```

## Stato repo fine S247

- Commit `8ad8b39` pushed origin/master, iMac sync OK
- Pipeline iMac DOWN_OK
- Cat 3 P0 #1 ✅ done; P0 #2 ⏭ next
- Tech debt minore: `tools/VectCutAPI` dirty submodule (ignorato)
