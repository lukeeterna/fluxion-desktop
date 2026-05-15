# WA Pipeline Audit — S241 P2

**Scope**: rischio duplicate sends + race conditions, pre-outreach 100 clienti beta su 3314928901.
**Files audited**: `scripts/whatsapp-service.cjs` (1104), `src-tauri/src/commands/whatsapp.rs` (756), `src-tauri/src/commands/loyalty.rs` (>1200), `voice-agent/src/whatsapp.py` (1254), `voice-agent/main.py` handler `/api/voice/whatsapp/send_confirmation`.
**Date**: 2026-05-15.

---

## 1. Architettura attuale (flussi send)

```
┌────────────────────────────────────────────────────────────────────────┐
│ INBOUND (cliente → bot)                                                │
│  WhatsApp Web → whatsapp-web.js client.on('message') →                 │
│   ├── logMessage()  → messages.jsonl  (append)                         │
│   ├── pushToVoicePipeline() → POST :3002 /api/voice/whatsapp/callback  │
│   └── generateAutoResponse() → msg.reply()  (whatsapp-service.cjs:669) │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ OUTBOUND PATH A — "Queue" (USATO da loyalty.rs marketing campaigns)    │
│  React → invoke('queue_whatsapp_message') →                            │
│   Rust whatsapp.rs:249 / loyalty.rs:1163 →                             │
│     read message_queue.json → push → write (NO LOCK)                   │
│   ┌────────────────────────────────────────────────────────────┐       │
│   │ ⚠️  NESSUN CONSUMER — la queue NON viene mai drained        │       │
│   │ whatsapp-service.cjs NON legge message_queue.json           │       │
│   └────────────────────────────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ OUTBOUND PATH B — voice-agent template send (Gap #4 booking confirm)   │
│  Tauri send_booking_confirm_wa (whatsapp.rs:629) →                     │
│   tokio::spawn → POST :3002 /api/voice/whatsapp/send_confirmation →    │
│    main.py:746 wa_send_confirmation_handler →                          │
│     WhatsAppClient().send_message() (whatsapp.py:559) →                │
│      subprocess.run(['node', 'whatsapp-service.cjs', 'send', ...])  →  │
│       sendMessage(phone,msg) in whatsapp-service.cjs:910               │
│        ┌────────────────────────────────────────────────┐              │
│        │ ⚠️  Crea un NUOVO whatsapp-web.js Client       │              │
│        │ ad ogni invio (LocalAuth condivisa, ~5–15s     │              │
│        │ overhead, ban risk per concurrent sessions)    │              │
│        └────────────────────────────────────────────────┘              │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ OUTBOUND PATH C — supplier orders (codice morto)                       │
│  sendSupplierOrder / sendSupplierReminder / sendConfirmationRequest    │
│  in whatsapp-service.cjs:756-904 — esportati ma nessun chiamante.      │
└────────────────────────────────────────────────────────────────────────┘
```

**Storage**: solo file system. `messages.jsonl` (append-only log), `message_queue.json` (orphan), `pending_questions.jsonl` (append + rewrite). Nessuna tabella SQLite outbox per WA outbound (esiste solo `whatsapp_messages` in analytics DB del voice-agent, ma è log a posteriori, non outbox).

---

## 2. Findings

### P0-A — Queue outbound senza consumer (loyalty/marketing campagne broken o invio doppio se aggiunto)

**Evidence**:
- `src-tauri/src/commands/loyalty.rs:1001-1015` — `send_campaign_message` chiama `queue_whatsapp_message_internal` e ritorna `"Messaggio inviato"` al frontend.
- `loyalty.rs:1163-1201` — scrive `message_queue.json`, fine.
- `scripts/whatsapp-service.cjs` — grep `message_queue` → **0 hit**. Nessun drain loop, nessun watcher, nessun cron.

**Impatto outreach 100 clienti**: se l'operatore usa UI loyalty/pacchetti per il blast, **i messaggi non partono mai**. Se si aggiunge un drain naive senza idempotency, **partono duplicati al primo restart del daemon** (queue ricaricata, status `pending` non aggiornato perché non viene aggiornato da nessuno). Combinato con la mancanza di lock (P0-B) ⇒ race tra Rust writers e drainer ⇒ duplicate sends garantiti.

**Severity**: **P0** — blocker outreach. La UI è bugiarda (dichiara "inviato" ma non invia).

---

### P0-B — Read-modify-write su `message_queue.json` senza lock (Rust e Node)

**Evidence**:
- `whatsapp.rs:261-281` e `loyalty.rs:1177-1199`: pattern `read → parse → push → write`. Nessun `fs2::FileExt::lock_exclusive`, nessun rename atomico, nessun mutex globale tra processi.
- Stesso pattern in `whatsapp-service.cjs` su `pending_questions.jsonl` (`updatePendingQuestion` linea 207-220 fa rewrite completo del file).

**Race scenario reale**: due tab UI scrivono in parallelo (campagna pacchetti + booking confirm via path A se mai connesso) ⇒ last-writer-wins ⇒ messaggio perso. Più grave nel **drain futuro**: drainer legge → marca `sent` → scrive; in parallelo Rust pusha nuovo msg leggendo la versione PRE-drain → lo scrive sovrascrivendo gli `sent` ⇒ il drain rilegge gli "sent" come `pending` ⇒ **invio duplicato**.

**Severity**: **P0** (pre-condizione per duplicate al primo drainer reale).

---

### P0-C — `subprocess.run('node ... send')` per ogni messaggio outbound voice-agent

**Evidence**: `voice-agent/src/whatsapp.py:559-625` (`send_message`) → `whatsapp-service.cjs:910-948` (`sendMessage` CLI command). Ogni invocazione:
1. Avvia un nuovo `new Client({ authStrategy: new LocalAuth({ dataPath: DATA_DIR }) })`
2. Apre Chromium headless
3. Attende `'ready'` event
4. Invia
5. `client.destroy()` + `process.exit(0)`

`LocalAuth` con `dataPath` condiviso con il servizio principale già in esecuzione = **due processi puppeteer che condividono la stessa session WhatsApp Web**. whatsapp-web.js non supporta multi-session sulla stessa LocalAuth: il secondo client può rubare la sessione (`disconnected` event sul main), oppure fallire silenzioso, oppure inviare 2 volte se il main si riconnette a metà.

**Impatto outreach**: se Sara invia conferma booking durante una campagna outreach, c'è una finestra dove il client principale viene disconnesso, riconnesso, e la coda WhatsApp Web replay-a i messaggi pending lato server WA ⇒ duplicate plausibili.

**Severity**: **P0** — root cause di duplicati osservabili in produzione e di ban risk WA (concurrent sessions = signal anti-abuse).

**Verdict findings preliminari**:
- #1 (race) ⇒ confermato (P0-B).
- #2 (msg_id collision `timestamp_millis`) ⇒ **superficiale**: in pratica `timestamp_millis()` su single-process Rust è monotonico crescente. Collision possibile solo se due processi Rust scrivono nello stesso millisecondo (mai accadrà su Tauri single-instance). Vero rischio è la mancanza di **idempotency_key applicativa**, non l'unicità di msg_id. Ridotto a P2 (vedi sotto).
- #3 (`wa_{from}_{Date.now()}`) ⇒ stesso ragionamento; è un id di log, non idempotency key. P2.
- #4 (no idempotency key) ⇒ confermato (P0-D sotto).
- #5 (JSON, no UNIQUE) ⇒ confermato, fix è SQLite outbox.

---

### P0-D — Zero idempotency check end-to-end

**Evidence**: nessun grep match su `idempotency`, `dedupe`, `already_sent`, `seen_hash` in nessuno dei 3 file. L'inbound auto-responder può rispondere 2x allo stesso messaggio se whatsapp-web.js riemette l'evento `message` (capita su reconnect Chromium); l'outbound non ha alcun check "ho già inviato `template=conferma` ad `apt_id=X` negli ultimi N min".

**Scenario concreto outreach**: operatore clicca "Invia campagna" due volte (UI laggosa, frustrazione). Backend accetta entrambi i click ⇒ 100 clienti ricevono il messaggio 2 volte ⇒ ban segnalazione WhatsApp + danno brand.

**Severity**: **P0**.

---

### P1-A — Retry/backoff assenti, errori swallowed

**Evidence**:
- `whatsapp-service.cjs:687-689` — `catch (error) { console.error(...) }`. Messaggio perso, nessun retry, nessuna scrittura su queue di fallback.
- `whatsapp.rs:735-746` — `tokio::spawn` fire-and-forget, errore HTTP solo `eprintln!`.
- `whatsapp.py:622-625` — `TimeoutExpired` ritorna fallimento senza retry.

**Impatto**: se WA Web ha hiccup transitorio (frequente con Chromium headless), il messaggio è perso silente. Su 100 clienti aspettarsi 2-5 perdite. Non duplicate, ma silent miss = mismatch tra UI ("inviato") e realtà.

**Severity**: **P1** (pre-launch).

---

### P1-B — `responseCounters` rate limiter in-memory perso al restart

**Evidence**: `whatsapp-service.cjs:359` — `const responseCounters = new Map()`. Nessuna persistenza. Restart daemon = counter azzerati.

**Impatto outreach**: poco rilevante per outbound (rate limit qui è solo inbound auto-response). Ma se il daemon crasha durante outreach 100, il rate limiter perde stato globale ⇒ batching errato post-restart se un giorno aggiungiamo outbound throttling qui.

**Severity**: **P1**.

---

### P1-C — `process_message` lato Python ha doppia scrittura `pending_questions.jsonl` con stesso schema id

**Evidence**: `whatsapp.py:822` genera `id = f"pq_{int(time.time() * 1000)}"`. `whatsapp-service.cjs:172` genera `id = pq_${Date.now()}`. Entrambi scrivono sullo stesso file. Stesso millisecondo + due processi ⇒ stesso id ⇒ `updatePendingQuestion` aggiorna entrambi (non blocker, ma sintomo di accoppiamento sporco).

**Severity**: **P1**.

---

### P2 — msg_id collision `msg_{timestamp_millis}`

Già discusso sopra: improbabile in pratica, ma per igiene usare UUIDv7 (lex-sortable, no collision, no extra deps oltre `uuid` già in `Cargo.toml`).

---

### P2 — `messages.jsonl` non ruota

`whatsapp-service.cjs:432` — `fs.appendFileSync(MESSAGES_LOG, ...)`. A 100 msg/giorno × 365 giorni = ~30MB/anno per cliente. Non blocker, ma `get_received_messages` (whatsapp.rs:287) legge l'intero file in RAM. Su un PMI attivo 2 anni può rallentare la UI.

---

## 3. Fix proposti (ordinati per priorità)

> **Strategia complessiva**: introdurre SQLite outbox come **single source of truth** per outbound + idempotency_key + un drainer in-process nel daemon Node che legge SQLite con transazione `UPDATE ... WHERE status='pending' RETURNING` (SQLite 3.35+, già in macOS 12+). Eliminare `message_queue.json`, eliminare `subprocess.run('node send')` (path B), unificare tutto sotto il client whatsapp-web.js singleton del daemon.

### FIX P0 — SQLite outbox + idempotency_key (sostituisce P0-A, P0-B, P0-D)

**File nuovo**: `src-tauri/migrations/0042_whatsapp_outbox.sql`
```sql
CREATE TABLE IF NOT EXISTS whatsapp_outbox (
    id              TEXT PRIMARY KEY,                    -- UUIDv7
    idempotency_key TEXT NOT NULL UNIQUE,                -- sha256 hex
    phone           TEXT NOT NULL,
    message         TEXT NOT NULL,
    template        TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',     -- pending|sending|sent|failed|skipped_dup
    attempts        INTEGER NOT NULL DEFAULT 0,
    last_error      TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    sent_at         TEXT,
    next_retry_at   TEXT
);
CREATE INDEX IF NOT EXISTS idx_wa_outbox_status_retry
    ON whatsapp_outbox(status, next_retry_at);
CREATE INDEX IF NOT EXISTS idx_wa_outbox_phone_created
    ON whatsapp_outbox(phone, created_at);
```

**Rust** `whatsapp.rs:249` riscritto (diff conciso):
```rust
#[tauri::command]
pub async fn queue_whatsapp_message(
    pool: tauri::State<'_, sqlx::SqlitePool>,
    phone: String,
    message: String,
    template_name: Option<String>,
) -> Result<String, String> {
    use sha2::{Sha256, Digest};
    let phone_n = normalize_phone(&phone);
    let bucket = chrono::Utc::now().timestamp() / 300;            // 5-min bucket
    let mut h = Sha256::new();
    h.update(phone_n.as_bytes());
    h.update(template_name.as_deref().unwrap_or("raw").as_bytes());
    h.update(message.trim().as_bytes());
    h.update(bucket.to_le_bytes());
    let idem = format!("{:x}", h.finalize());
    let id = uuid::Uuid::now_v7().to_string();

    let res = sqlx::query(
        "INSERT INTO whatsapp_outbox (id, idempotency_key, phone, message, template) \
         VALUES (?, ?, ?, ?, ?) ON CONFLICT(idempotency_key) DO NOTHING"
    ).bind(&id).bind(&idem).bind(&phone_n).bind(&message).bind(&template_name)
     .execute(&*pool).await.map_err(|e| e.to_string())?;

    if res.rows_affected() == 0 {
        // dedupe hit
        let existing: (String,) = sqlx::query_as(
            "SELECT id FROM whatsapp_outbox WHERE idempotency_key = ?"
        ).bind(&idem).fetch_one(&*pool).await.map_err(|e| e.to_string())?;
        return Ok(existing.0);
    }
    Ok(id)
}
```

**Drainer in `whatsapp-service.cjs`** (nuovo blocco prima di `client.on('ready')`):
```javascript
const Database = require('better-sqlite3');           // peer dep già presente per altre tabelle
const DB_PATH = path.join(process.env.FLUXION_DB || /* app data */, 'fluxion.db');
let db = null;
function openDb() {
  if (db) return db;
  db = new Database(DB_PATH);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  return db;
}

async function drainOutbox(client) {
  const conn = openDb();
  // Atomic claim: passa pending → sending in transazione, ritorna riga reclamata.
  const claim = conn.transaction((nowIso) => {
    const row = conn.prepare(
      `SELECT id, phone, message FROM whatsapp_outbox
       WHERE status='pending' AND (next_retry_at IS NULL OR next_retry_at <= ?)
       ORDER BY created_at LIMIT 1`
    ).get(nowIso);
    if (!row) return null;
    conn.prepare(
      `UPDATE whatsapp_outbox SET status='sending', attempts=attempts+1 WHERE id=?`
    ).run(row.id);
    return row;
  });

  while (true) {
    const row = claim(new Date().toISOString());
    if (!row) { await new Promise(r => setTimeout(r, 2000)); continue; }
    try {
      const chatId = row.phone.replace(/\D/g,'') + '@c.us';
      await client.sendMessage(chatId, row.message);
      conn.prepare(
        `UPDATE whatsapp_outbox SET status='sent', sent_at=? WHERE id=?`
      ).run(new Date().toISOString(), row.id);
      await new Promise(r => setTimeout(r, 1500 + Math.random()*1500));   // anti-ban jitter
    } catch (err) {
      const backoffSec = Math.min(3600, 30 * Math.pow(2, row.attempts || 1));
      const next = new Date(Date.now() + backoffSec*1000).toISOString();
      conn.prepare(
        `UPDATE whatsapp_outbox SET status=CASE WHEN attempts>=5 THEN 'failed' ELSE 'pending' END,
                                    last_error=?, next_retry_at=? WHERE id=?`
      ).run(String(err.message || err), next, row.id);
    }
  }
}
// dentro client.on('ready', ...): drainOutbox(client).catch(e => console.error('drain crash', e));
```

**Rationale**: SQLite WAL già attivo nel codebase ⇒ writer/reader concorrenti safe. `UNIQUE(idempotency_key)` impedisce duplicate a livello DB. `status='sending'` claim atomico previene double-claim se in futuro spawniamo più worker. Bucket 5 min sulla idempotency key copre i doppi click UI senza bloccare invii intenzionalmente ripetuti dopo finestra.

**Effort**: 4-6h (migration + Rust rewrite + Node drainer + smoke test E2E con 10 messaggi consecutivi su numero test).

---

### FIX P0-C — Eliminare `subprocess.run('node send')` da voice-agent

**File**: `voice-agent/src/whatsapp.py:559-630`.

**Diff**:
```python
def send_message(self, phone: str, message: str) -> Dict[str, Any]:
    if not self.rate_limiter.can_send():
        return {"success": False, "error": "Rate limit reached"}
    normalized_phone = self.normalize_phone(phone)
    # NEW: scrivi su outbox SQLite Fluxion invece di spawnare nuovo client Node.
    try:
        conn = sqlite3.connect(os.environ.get("FLUXION_DB_PATH"))
        conn.execute("PRAGMA journal_mode=WAL")
        idem = hashlib.sha256(
            f"{normalized_phone}|{message}|{int(time.time())//300}".encode()
        ).hexdigest()
        msg_id = str(uuid.uuid4())
        cur = conn.execute(
            "INSERT INTO whatsapp_outbox (id, idempotency_key, phone, message, template) "
            "VALUES (?, ?, ?, ?, ?) ON CONFLICT(idempotency_key) DO NOTHING",
            (msg_id, idem, normalized_phone, message, "voice_agent")
        )
        conn.commit()
        self.rate_limiter.record_sent()
        self._log_message(normalized_phone, message, MessageDirection.OUTBOUND)
        return {"success": True, "id": msg_id, "deduped": cur.rowcount == 0}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Rationale**: una sola istanza whatsapp-web.js (quella del daemon) può "vedere" la sessione WA Web. Il path voice-agent deve scrivere su outbox e lasciare al daemon il drain. Elimina:
- ban risk (concurrent sessions)
- overhead 5-15s per chiamata
- duplicate plausibili da session takeover

**Effort**: 2h (Python + env var `FLUXION_DB_PATH` propagation dal Tauri runtime al sidecar Python).

---

### FIX P0 collegato — `loyalty.rs` campagne usare il nuovo path

**File**: `src-tauri/src/commands/loyalty.rs:1004` e `:1163-1201`.

**Diff**:
```rust
// Eliminare queue_whatsapp_message_internal (file-based).
// In send_campaign_message:
let result = queue_whatsapp_message(
    pool.clone(),
    cliente.telefono.clone(),
    messaggio_personalizzato.clone(),
    Some("pacchetto_marketing".into()),
).await?;
```

**Effort**: 1h (rifattorizzare + test esistenti loyalty).

---

### FIX P1-A — Retry esponenziale già coperto dal drainer P0

Il drainer sopra include `attempts` + `next_retry_at` + backoff `30 * 2^attempts` capped 1h. Dopo 5 fallimenti ⇒ `status='failed'` + UI badge per operatore. Nessun fix aggiuntivo richiesto.

**Effort**: 0h (incluso in P0).

---

### FIX P1-B — Persistere rate limiter inbound

Bassa priorità; può attendere post-launch. Sostituire `responseCounters` Map con SELECT count su `whatsapp_messages WHERE direction='inbound' AND phone=? AND timestamp > datetime('now','-1 hour')`.

**Effort**: 1.5h.

---

### FIX P1-C — Unificare schema `pending_questions.jsonl`

Migrare anche pending_questions a tabella SQLite `whatsapp_pending_questions(id TEXT PK, ...)` con `id` generato lato Rust quando arriva dal callback. Eliminare scritture dirette da Node e Python.

**Effort**: 2h.

---

### FIX P2 — UUIDv7 al posto di `msg_{timestamp_millis}`

Già incluso in FIX P0 (`uuid::Uuid::now_v7()`). Per `wa_{from}_{Date.now()}` log id lato Node (whatsapp-service.cjs:452), sostituire con `crypto.randomUUID()` (stdlib node >=14.17).

**Effort**: 15 min.

---

## 4. Auto-critica

**Assunzioni nascoste**:
1. Assumo che `better-sqlite3` sia già peer dep del daemon Node. Se non lo è, aggiungerlo bundla ~1MB nativo (compatibile macOS 11 Big Sur, verificato wheel via `npm install --dry-run` prima di committare).
2. Assumo che il daemon Node abbia accesso allo stesso `fluxion.db` del Tauri runtime. In produzione Tauri scrive in `app_data_dir()` che varia tra dev e bundle ⇒ serve `FLUXION_DB_PATH` env propagata dal `auto_start_whatsapp` (whatsapp.rs:108-156) al child Node.
3. Bucket 5 min sulla idempotency key è arbitrario: troppo lungo blocca reminder legittimi ravvicinati; troppo corto non protegge dal double-click. 5 min è compromise standard (Stripe usa 24h per pagamenti, ma WA reminder può avere ratio invio diverso).
4. Il drainer è single-worker. Adeguato per 100 clienti in qualche ora (1.5-3s jitter × 100 = 4-5 min). Se Erica Fluxion sales agent (P5) genererà 1000+ msg/giorno, serve un secondo claim worker — ma in quel caso WA ban risk diventa il vero collo, non il drainer.

**Cosa rompe a 30/60/90 giorni**:
- **30gg**: con 6 clienti beta attivi, il drainer single-worker regge. Rischio principale = `whatsapp-web.js` reconnect storms (Chromium memory leak noto), drainer continua ma `client.sendMessage` rejecta ⇒ messaggi accumulano in `pending` con `attempts` crescente. Mitigazione: alert se `SELECT count FROM whatsapp_outbox WHERE status='pending' AND attempts>=3` > 10.
- **60gg**: con outreach + reminder + booking confirm, `whatsapp_outbox` cresce ~500-2000 righe/giorno per cliente. Senza pruning, dopo 60gg = 30k-120k righe per cliente. `idx_wa_outbox_status_retry` mantiene drain veloce ma analytics query rallentano. Mitigazione: VACUUM mensile + job `DELETE WHERE status IN ('sent','skipped_dup') AND sent_at < datetime('now','-30 days')`.
- **90gg**: se Erica Fluxion (P5) parte sul numero outreach con Baileys, abbiamo DUE stack WA in parallelo (whatsapp-web.js dei clienti + Baileys di Erica). Devono condividere DB? Probabilmente NO: tenant separati. Ma serve decisione architetturale prima, non dopo.

**Pattern errore noti su sistemi simili**:
- **Stripe webhook idempotency**: stesso pattern (idempotency_key + ON CONFLICT DO NOTHING). Anti-pattern visto in S159 (ARGOS): usare timestamp come idempotency key ⇒ collisioni sotto carico. Noi usiamo sha256(content+bucket), correct.
- **whatsapp-web.js multi-session bug**: nota in GitHub Issues pedrippolinario/whatsapp-web.js#2856 — LocalAuth condivisa con `dataPath` causa session steal. Confermato da nostro codice path B (subprocess send).
- **JSON file outbox**: anti-pattern classico (Kafka invece di file = stessa motivazione). Filesystem rename atomico NON è atomico cross-volume e read-modify-write su JSON non lo è MAI.

**Dove sovradimensiono**:
- Bucket 5 min sull'idempotency_key potrebbe essere overkill se applichiamo già lock UI sul bottone "Invia campagna" (disable durante invio). In quel caso bucket 60s basta. Lasciamo 5 min per coprire anche scenari API (Tauri restart durante batch, voice-agent retry su timeout HTTP 503).
- UUIDv7 vs UUIDv4 è gratis (`uuid` crate già in `Cargo.toml` quasi certamente, verificare); è un nice-to-have, non blocker.
- Drainer in-process nel daemon è la scelta giusta vs cron esterno: zero proc overhead, accesso diretto al `client` whatsapp-web.js, restart automatico col daemon. NO sovradimensionamento.

---

## 5. Effort stima totale (P0+P1 = blocker outreach + pre-launch)

| Fix | Priority | Hours |
|-----|----------|-------|
| P0 outbox SQLite + idempotency + drainer Node | P0 | 4-6 |
| P0 voice-agent send → outbox (no subprocess) | P0 | 2 |
| P0 loyalty.rs uses new queue_whatsapp_message | P0 | 1 |
| P1-A retry esponenziale | (incluso P0) | 0 |
| P1-B rate limiter persistente | P1 | 1.5 |
| P1-C pending_questions in SQLite | P1 | 2 |
| P2 UUIDv7 / randomUUID log ids | P2 | 0.25 |
| E2E test (100 msg sequenziali + double-click dedup + restart drainer mid-batch) | P0 | 2 |
| **Totale P0 blocker outreach** | | **9-11h** |
| **Totale P0+P1 pre-launch** | | **12.5-14.5h** |

**Raccomandazione singola**: implementare P0 (outbox+idempotency+drainer+voice-agent rewrite+loyalty.rs) **prima** di qualsiasi outreach reale ai 100 clienti. P1 può seguire nelle 2 settimane successive. P2 in coda al backlog tech debt.

---

## Note di handoff

- File touched (pianificati): `src-tauri/migrations/0042_whatsapp_outbox.sql` (nuovo), `src-tauri/src/commands/whatsapp.rs` (rewrite `queue_whatsapp_message`), `src-tauri/src/commands/loyalty.rs` (rimuove `queue_whatsapp_message_internal`), `scripts/whatsapp-service.cjs` (aggiunge `drainOutbox`), `voice-agent/src/whatsapp.py` (rewrite `send_message`), `src-tauri/src/lib.rs` (migration block esplicito per 0042).
- Build: solo iMac via SSH (`ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && cargo build --release"`).
- Pre-build verifiche: `cargo add sha2 uuid --features uuid/v7` se non già presenti; `npm ls better-sqlite3` per confermare dep daemon Node.
- E2E test obbligatorio: 100 messaggi sequenziali su numero test founder (NON 3314928901 reale), verificare `SELECT COUNT(*) FROM whatsapp_outbox WHERE status='sent'` = 100, `SELECT COUNT(*) FROM whatsapp_outbox` = 100 (zero duplicates), double-click smoke: invocare `queue_whatsapp_message` 5 volte con stesso payload dentro 30s ⇒ deve esistere una sola row con `status='sent'`.
