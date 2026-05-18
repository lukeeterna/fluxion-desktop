# Prompt ripartenza S259 — VERDE-CON-ASTERISCO close S258

**Generato**: 2026-05-18 (sessione S258 close)
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Stato S258**: VERDE-CON-ASTERISCO. Encryption suppliers PII (S257 `d652060`) **LIVE VERIFY PASS** su iMac. Gap UX `Fornitori.tsx` missing `toast.error` documentato come scope S259 P3.a (non blocker encryption).

---

## RIASSUNTO S258 (closed)

**Live verify S257 P2 (suppliers PII encryption) — 6/6 PASS**:

| Check | Risultato |
|---|---|
| Branch iMac sync | `d652060` ✓ |
| Seed 3 row plaintext (Acme/Beta/Gamma) | ✓ DB pre-boot1 |
| Boot1 (cargo tauri dev) — migration runner | ✓ `applied_at=2026-05-18 07:54:31`, `rows_processed=3` |
| Ciphertext on-disk seed-1/2/3 | ✓ Base64 (no plaintext "Acme"/"IT") |
| Backup file pre-encryption | ✓ `fluxion.db.pre-encrypt_suppliers_pii_v1-bak-20260518-075431` |
| seed-3 partita_iva NULL preserved | ✓ encrypt_opt skip su NULL |
| Boot2 idempotency log level | ✓ `🔐 PII migration (suppliers): already applied (encrypt_suppliers_pii_v1)` |
| Boot2 idempotency DB level (byte-for-byte) | ✓ ciphertext identico boot1↔boot2 su seed-1/2/3, rows_processed=3 unchanged, applied_at unchanged |

**UI test funzionale Fornitori (founder fisico iMac)**:

| Test | Risultato | Note |
|---|---|---|
| 2.1 list 3 nomi plaintext | ✓ | "Acme Srl"/"Beta SpA"/"Gamma Snc" visibili |
| 2.2 dup nome esatto "Acme Srl" | ✓ backend block (console.error confermato) | UI gap: no toast |
| 2.3 dup partita_iva "IT12345678901" | (skip implicito — 2.2/2.4 coprono dedupe logic + console path) | — |
| 2.4 normalizzazione `  acme srl  ` (trim+lower) | ✓ backend block (console: "Esiste già un fornitore con nome 'acme srl'") | UI gap: no toast |
| 2.5 update collision (rename Beta→Acme) | skip | Feature gap pre-S258 noto |
| 2.6 search "acme" → match seed-1 | ✓ UI visibile | decrypt-then-search OK |
| 2.7 search "12345" → match seed-1 (substring piva) | ✓ UI visibile | tier-1 in-memory search OK |
| 2.8 search vuota → 3 row | ✓ UI visibile | — |

**DB final state**: COUNT(suppliers)=3, solo seed timestamps `2026-05-18 07:52:08`. Tutti i test dedupe hanno bloccato correttamente backend-side (no row aggiunto in nessun test). UI ha mostrato form rimasto aperto col campo compilato ma **nessun toast error** → gap UX pre-esistente.

---

## GAP UX IDENTIFICATO (root cause + fix in 5 righe)

**File**: `src/pages/Fornitori.tsx:112-123`
```typescript
const handleSubmit = async (data: CreateSupplierInput | UpdateSupplierInput) => {
  try {
    if ('id' in data) {
      await updateMutation.mutateAsync(data as UpdateSupplierInput);
    } else {
      await createMutation.mutateAsync(data as CreateSupplierInput);
    }
    setDialogOpen(false);
  } catch (error) {
    console.error('Failed to save fornitore:', error);
    // ← MISSING: toast.error(String(error)) per visibilità utente
  }
};
```

Stesso pattern anche in `handleConfirmDelete` (line 132-134). `toast` da `'sonner'` già importato line 8 — fix triviale.

**Verifica scope**: gap NON è encryption-related (backend `create_supplier` ritorna error correttamente, mutation throw correttamente, catch riceve l'error correttamente). È un missing UX feedback. Stesso fix pattern potrebbe esistere su altre entità (clienti/operatori/servizi) — audit incluso in S259 P3.a.

---

## TASK S259 (proposto, da rifinire founder)

### P3.a — UX fix missing `toast.error` (~30 min, trivial)
1. Audit grep frontend pages: `grep -rn "console.error('Failed to" src/pages/` → identifica TUTTI i `try/catch` mutation che mancano `toast.error`.
2. Patch ognuno: aggiungere `toast.error(typeof error === 'string' ? error : (error as Error).message || 'Errore sconosciuto')` dopo `console.error`.
3. E2E retest su Fornitori: ripeti 2.2/2.4 → verifica toast visibile.
4. Type-check + cargo check (frontend-only change, backend non toccato).
5. Commit + push.

### P3.b — Audit next encryption target (~1h, deep research)

Eseguire STEP 4 originale del plan S258 (rinviato per context budget):

```bash
# (1) Grep PII columns su tutte le migrations (skip encrypt/backup/index/FK righe)
ssh imac 'cd "/Volumes/MacSSD - Dati/fluxion" && rg -n \
  "(cliente|customer|email|telefono|nome|cognome|indirizzo|partita_iva|fiscale|note|transcript|body|message)" \
  src-tauri/migrations/*.sql | rg -v "(encrypt|backup|index|FOREIGN KEY)" | sort -u | head -50'

# (2) Lista tabelle attive
ssh imac 'sqlite3 "$HOME/Library/Application Support/com.fluxion.desktop/fluxion.db" "SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name;"'

# (3) Per ogni candidato (es. fatture, whatsapp_messages, appointments, audit_log, voice_sessions):
ssh imac 'sqlite3 "$HOME/Library/Application Support/com.fluxion.desktop/fluxion.db" "SELECT COUNT(*) FROM <table>; PRAGMA table_info(<table>);"'
```

**Matrice priorità P3**:
| Tabella | PII volume (righe × cols) | Esposizione (UI/export/API?) | Effort refactor |

Effort hint:
- **trivial**: colonne denormalizzate snapshot tipo `fatture.cliente_*` (no UNIQUE, no LIKE search)
- **medium**: tier-1 in-memory search richiesto (es. `whatsapp_messages.body`)
- **hard**: freetext con FTS o JOIN cross-table su PII

Output S259 P3.b: scelta motivata next target encryption + pattern S257 replicabile (schema check, migration N+1, runner wrapper, wire `lib.rs`, encrypt/decrypt + dedupe app-layer/tier-1 search se necessario).

### P3.c (opzionale) — Tier-2 blind-index HMAC su `suppliers.nome` + `partita_iva`
- Solo se >500 supplier reali OR perf degrado su dedupe app-layer.
- Tracked S257 commit `d652060` come tech debt accettato (no in-session fix).
- NOT priority S259, lasciare in backlog.

---

## STATO REPO (verde fine S258)

- `master` ultimo commit: `d652060` (S257) — verde, LIVE VERIFY PASS.
- Sessione S258 ha generato solo doc (`.claude/NEXT_SESSION_PROMPT.manual.md` aggiornato), nessun code change. Commit S258 = solo docs close.
- iMac: app FLUXION running (HTTP Bridge :3001 attivo, PID assegnato dal `cargo tauri dev` boot2). Voice Pipeline :3002 NOT required for S258 — ignorare hook warning.
- DB iMac: 3 supplier seed encryptati + backup file preservato.

---

## START S259 (copia-incolla)

```
Leggi .claude/NEXT_SESSION_PROMPT.manual.md ed esegui S259 secondo
il piano P3.a (UX fix toast) + P3.b (audit next encryption target).

Pre-flight S259:
1. Verifica iMac sync `git log --oneline -1` su master (expect head S258 docs commit).
2. App FLUXION iMac probabilmente still up da S258. Voice Pipeline :3002 non required, ignorare hook.
3. Context expected boot ~20-22% (sotto WARN 40%, headroom ~30%).

Inizia da P3.a STEP 1 (grep frontend pages per pattern console.error missing toast).
```

---

## VINCOLI HARD (riconferma S259)

- Vincolo #6 zero tolleranza ARANCIONE: VERDE / VERDE* / HANDOFF rosso.
- Vincolo #7 context budget: WARN 40%, BLOCK CRITICAL 50%, CLOSING 70%.
- Vincolo #2 audit fattuale: STEP P3.b deve eseguire grep migrations + table count REALI, NO TODO mono-fonte.
- Pre-action check DECISIONS FLUXION: scan D-01..D-05 prima di proposte tecniche P3.b. D-05 (ephemeral port HTTP Bridge) non toccato da fix UX P3.a.
- Trade-off tier-1 dedupe/search S257 confermati accettati, P3.c tier-2 blind-index NON priority.

---

**Provenienza prompt S259**: S258 live verify PASS (founder reports console.error confermato su 2.2+2.4, search 2.6/2.7/2.8 OK UI) + Claude diagnosi gap UX `Fornitori.tsx:120-122` missing `toast.error`. VERDE-CON-ASTERISCO chiuso 2026-05-18.
