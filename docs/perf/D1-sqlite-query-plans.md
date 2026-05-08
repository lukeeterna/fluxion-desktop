# S190 D-1 — SQLite EXPLAIN QUERY PLAN audit `clienti` (1000 record)

**Generato**: 2026-05-08 19:58:50 UTC

**DB test**: `/tmp/fluxion-perf.db` (fresh from migrations)

**Seed**: 1000 clienti italiani realistici (deterministic, seed=42)

**Benchmark**: 100 iterazioni con warmup 5

**SQLite version**: 3.53.0


## SLO target

- P95 lista clienti `< 50ms`

- P95 lookup PK `< 5ms`

- P95 search free-text `< 50ms` (con LIKE wildcard, NB: nessun indice possibile su `LIKE %x%` — soluzione long-term FTS5)


## Indici esistenti su `clienti`

```sql
-- idx_clienti_deleted_at
CREATE INDEX idx_clienti_deleted_at ON clienti(deleted_at);
-- idx_clienti_email
CREATE INDEX idx_clienti_email ON clienti(email);
-- idx_clienti_is_vip
CREATE INDEX idx_clienti_is_vip ON clienti(is_vip);
-- idx_clienti_loyalty
CREATE INDEX idx_clienti_loyalty ON clienti(loyalty_visits, loyalty_threshold);
-- idx_clienti_nome
CREATE INDEX idx_clienti_nome ON clienti(nome, cognome);
-- idx_clienti_referral
CREATE INDEX idx_clienti_referral ON clienti(referral_cliente_id);
-- idx_clienti_soprannome
CREATE INDEX idx_clienti_soprannome ON clienti(soprannome);
-- idx_clienti_telefono
CREATE INDEX idx_clienti_telefono ON clienti(telefono);
```


## Risultati audit

| Query | P50 ms | P95 ms | P99 ms | SLO ms | Verdict |
|-------|--------|--------|--------|--------|---------|
| `Q1-list-all` | 14.59 | 24.50 | 32.53 | 50 | PASS |
| `Q2-get-by-id` | 0.03 | 0.07 | 0.23 | 5 | PASS |
| `Q3-search-like` | 0.97 | 1.55 | 2.04 | 50 | PASS |
| `Q4-count-active` | 0.06 | 0.11 | 0.15 | 10 | PASS |
| `Q5-count-vip` | 0.07 | 0.10 | 0.20 | 10 | PASS |
| `Q6-list-export` | 4.64 | 10.25 | 16.50 | 50 | PASS |
| `Q7-by-telefono` | 0.03 | 0.04 | 0.06 | 5 | PASS |
| `Q8-by-email` | 0.03 | 0.03 | 0.03 | 5 | PASS |

## Dettaglio per query

### Q1-list-all — Lista clienti pagina principale (ORDER BY cognome, nome)

**Origin Rust**: `commands/clienti.rs:117 get_clienti`

**Verdict**: PASS

**SQL**:
```sql
SELECT * FROM clienti WHERE deleted_at IS NULL ORDER BY cognome ASC, nome ASC
```

**EXPLAIN QUERY PLAN**:
```
id=4 parent=0 | SEARCH clienti USING INDEX idx_clienti_deleted_at (deleted_at=?)
id=46 parent=0 | USE TEMP B-TREE FOR ORDER BY
```

**Bench**: min=8.90ms p50=14.59ms p95=24.50ms p99=32.53ms max=43.95ms

### Q2-get-by-id — Lookup cliente by id (PK)

**Origin Rust**: `commands/clienti.rs:134 get_cliente`

**Verdict**: PASS

**SQL**:
```sql
SELECT * FROM clienti WHERE id = ? AND deleted_at IS NULL
```

**EXPLAIN QUERY PLAN**:
```
id=3 parent=0 | SEARCH clienti USING INDEX sqlite_autoindex_clienti_1 (id=?)
```

**Bench**: min=0.03ms p50=0.03ms p95=0.07ms p99=0.23ms max=0.26ms

### Q3-search-like — Search free-text con LIKE %x% su 4 colonne

**Origin Rust**: `commands/clienti.rs:357 search_clienti`

**Verdict**: PASS

**SQL**:
```sql
SELECT * FROM clienti WHERE deleted_at IS NULL AND (nome LIKE ? OR cognome LIKE ? OR telefono LIKE ? OR email LIKE ?) ORDER BY cognome ASC, nome ASC LIMIT 50
```

**EXPLAIN QUERY PLAN**:
```
id=5 parent=0 | SEARCH clienti USING INDEX idx_clienti_deleted_at (deleted_at=?)
id=64 parent=0 | USE TEMP B-TREE FOR ORDER BY
```

**Bench**: min=0.96ms p50=0.97ms p95=1.55ms p99=2.04ms max=2.70ms

### Q4-count-active — Dashboard count clienti attivi

**Origin Rust**: `commands/dashboard.rs:73`

**Verdict**: PASS

**SQL**:
```sql
SELECT COUNT(*) FROM clienti WHERE deleted_at IS NULL
```

**EXPLAIN QUERY PLAN**:
```
id=3 parent=0 | SEARCH clienti USING COVERING INDEX idx_clienti_deleted_at (deleted_at=?)
```

**Bench**: min=0.05ms p50=0.06ms p95=0.11ms p99=0.15ms max=0.17ms

### Q5-count-vip — Dashboard count VIP attivi

**Origin Rust**: `commands/dashboard.rs:80`

**Verdict**: PASS

**SQL**:
```sql
SELECT COUNT(*) FROM clienti WHERE is_vip = 1 AND deleted_at IS NULL
```

**EXPLAIN QUERY PLAN**:
```
id=4 parent=0 | SEARCH clienti USING INDEX idx_clienti_is_vip (is_vip=?)
```

**Bench**: min=0.07ms p50=0.07ms p95=0.10ms p99=0.20ms max=0.23ms

### Q6-list-export — Lista completa clienti per export GDPR

**Origin Rust**: `commands/support.rs:733 (GDPR export)`

**Verdict**: PASS

**SQL**:
```sql
SELECT id, nome, cognome, email, telefono FROM clienti WHERE deleted_at IS NULL ORDER BY cognome, nome
```

**EXPLAIN QUERY PLAN**:
```
id=4 parent=0 | SEARCH clienti USING INDEX idx_clienti_deleted_at (deleted_at=?)
id=18 parent=0 | USE TEMP B-TREE FOR ORDER BY
```

**Bench**: min=2.30ms p50=4.64ms p95=10.25ms p99=16.50ms max=20.20ms

### Q7-by-telefono — Match cliente by telefono (voice agent)

**Origin Rust**: `voice agent lookup (HTTP bridge)`

**Verdict**: PASS

**SQL**:
```sql
SELECT * FROM clienti WHERE telefono = ? AND deleted_at IS NULL
```

**EXPLAIN QUERY PLAN**:
```
id=3 parent=0 | SEARCH clienti USING INDEX idx_clienti_telefono (telefono=?)
```

**Bench**: min=0.03ms p50=0.03ms p95=0.04ms p99=0.06ms max=0.09ms

### Q8-by-email — Match cliente by email

**Origin Rust**: `registrazione/login lookup`

**Verdict**: PASS

**SQL**:
```sql
SELECT * FROM clienti WHERE email = ? AND deleted_at IS NULL
```

**EXPLAIN QUERY PLAN**:
```
id=3 parent=0 | SEARCH clienti USING INDEX idx_clienti_email (email=?)
```

**Bench**: min=0.03ms p50=0.03ms p95=0.03ms p99=0.03ms max=0.03ms


## Conclusioni e azioni

- PASS: 8 | WARN: 0 | FAIL: 0


### Note tecniche
- `LIKE '%x%'` (Q3 search) NON è ottimizzabile con indice B-tree standard. Soluzione long-term: FTS5 virtual table su (nome, cognome, telefono, email). Tech debt P2 — accettabile sotto 10k clienti, P95 < SLO con full scan.
- `ORDER BY cognome, nome` su lista completa: SQLite usa `idx_clienti_nome` se compatibile con WHERE clause, altrimenti SCAN+SORT.
- `idx_clienti_deleted_at` (migration 036) coprire WHERE deleted_at IS NULL ma per filtri `IS NULL` SQLite spesso preferisce table scan se selettività bassa.

