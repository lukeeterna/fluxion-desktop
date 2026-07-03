
# REPORT ESECUZIONE — T-SARA-B-prep (armare la chiamata live)
**Data**: 2026-07-03 · **Host esecuzione**: iMac (`gianlucadistasi console`, loggato ore 18:39) · **Verdetto finale: CHIAMA ORA — SÌ**

Report della sequenza dal momento «imac loggato» in poi. Tutti gli output sono reali (SSH su iMac).

---

## 0. Contesto pre-login (sintesi)
Con l'iMac alla schermata di login (`/dev/console` owner = root, `who` vuoto) il bridge :3001 NON era avviabile:
il bridge vive solo dentro l'app Tauri GUI e richiede una sessione Aqua. Verdetto provvisorio = NO, bloccato su login founder.
Il founder ha eseguito il login → sbloccato.

---

## 1. Verifica sessione GUI (premessa azione 1)
```
who | grep console      → gianlucadistasi console  Jul 3 18:39
stat /dev/console owner  → gianlucadistasi
lsof -i :3001 LISTEN     → FREE-3001
```
Premessa «sessione desktop attiva» = VERA. Proceduto.

## 2. ROOT CAUSE — perché la release app non basta
Sorgente `src-tauri/src/lib.rs:906`:
```rust
#[cfg(debug_assertions)]      // il bridge esiste SOLO in build DEBUG
{
    ... http_bridge::start_http_bridge(app_handle) ...
}
```
Primo tentativo: `open Fluxion.app` (build **release** in `target/release/bundle/macos/`).
Esito: processo vivo (pid 56928) MA `:3001` = STILL-FREE, `health_http=000`.
→ La release NON contiene il codice del bridge (compilato fuori con `cfg(debug_assertions)`).
DISCORDANZA azione 1: `premessa: avvia l'app | fatto: la release non serve il bridge | correzione: serve build DEBUG = npm run tauri dev`.
(Coerente con `.claude/hooks/check-services.sh` che indica proprio `npm run tauri dev`.)

## 3. Avvio bridge corretto (build DEBUG)
```
kill 56928                                   → killed-stray-release (cleanup istanza release lanciata da me)
cd "/Volumes/MacSSD - Dati/fluxion"
nohup npm run tauri dev > "/Volumes/MacSSD - Dati/fluxion/tauri-dev.log" 2>&1 &   (pid 57375)
```
Poll :3001 → **BRIDGE-UP after 8s** (build debug cachata, nessuna ricompilazione lunga).
```
lsof -i :3001 LISTEN → tauri-app 57494 gianlucadistasi ... TCP 127.0.0.1:3001 (LISTEN)
curl :3001/health    → {"service":"FLUXION HTTP Bridge","status":"ok","timestamp":"2026-07-03T18:47:33+02:00"}  (200)
```
Coda log tauri-dev.log:
```
✅ Migrations completed
ℹ️  GDPR encryption deferred (CRUD will retry on first sensitive call): Keychain read failed: User interaction is not allowed.
💾 Auto-backup: backup già aggiornato
🟢 WhatsApp service started (PID: 57552)
🚀 Application ready
🌉 HTTP Bridge started on http://127.0.0.1:3001
```
**Azione 1 = COMPLETA.**

## 4. Write-path (azione 2) — stesso path di Sara
DB reale individuato via `lsof -p 57494`:
`/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db` (WAL: presenti -wal/-shm).

Contratto handler `http_bridge.rs:1004`: `id` = uuid generato; `servizio` risolto con `LIKE` su tabella `servizi`
(nessun match → default `srv-default`); insert in `appuntamenti` con FK su `cliente_id`, `servizio_id`.

**Tentativo 1** (servizio fittizio `test-sarab`):
```
resp = {"error":"... (code: 787) FOREIGN KEY constraint failed","success":false}
```
Causa: `servizio="test-sarab"` non matcha → `servizio_id="srv-default"` inesistente → FK viola. (cliente_id era valido.)

**Tentativo 2** (servizio REALE `Tagliando`, come farebbe Sara in chiamata):
```
POST :3001/api/appuntamenti/create
  body: {"cliente_id":"1b8b2c34d370437ea4746101f91b0657","servizio":"Tagliando","data":"2099-01-01","ora":"09:00"}
resp: {"id":"8754b668-7d98-48a6-9485-7d4ca711c614","success":true,
       "message":"Appuntamento creato per 2099-01-01 alle 09:00"}
```
**VERIFY in DB**:
```
8754b668-7d98-48a6-9485-7d4ca711c614 | cliente 1b8b2c34… | servizio_id 27dff1ef… |
2099-01-01T09:00:00 | confermato | fonte_prenotazione=voice
```
**CLEANUP**:
```
DELETE FROM appuntamenti WHERE data_ora_inizio LIKE '2099-01-01%';
PRAGMA wal_checkpoint(TRUNCATE);   → 0|0|0 (ok)
remaining_test_rows = 0
```
**Write-path FUNZIONA: SÌ** (prova E2E su DB reale, riga creata e poi rimossa senza residui).

## 5. Log marker + metrics (azione 3)
```
marker → /tmp/voice-pipeline.log :
  ===== T-SARA-B MARKER 2026-07-03T16:49:33Z armed founder-live-calls 0972536918 =====
curl :3002/api/metrics/latency → 200
curl :3002/health              → 200 (verificato in fase precedente)
```
NB: il log per-turno è su `/tmp/voice-pipeline.log` (basicConfig→stderr, redirect da start command documentato) — effimero (sopravvive fino al reboot).

## 6. CAVEAT non bloccante (per la sessione di analisi)
Log bridge: `GDPR encryption deferred — Keychain read failed: User interaction is not allowed`.
- L'insert appuntamento NON tocca PII → provato OK.
- La ricerca/creazione **cliente NUOVO** in chiamata reale decifra PII → richiede keychain.
- Ora che la GUI è loggata dovrebbe fare retry-success, **ma non verificato in questo task**.
- Raccomandazione: nelle 5 chiamate includere almeno uno scenario **cliente nuovo** per esercitare quel ramo;
  il marker nei log lo catturerà per l'analisi.

## 7. Stato lasciato attivo (per le chiamate)
- `:3001` bridge UP (pid tauri-app 57494; dev server `npm run tauri dev` pid 57375, log `/Volumes/MacSSD - Dati/fluxion/tauri-dev.log`).
- `:3002` voice pipeline UP.
- Entrambi i servizi verdi (conferma hook: `✅ HTTP Bridge 3001 ATTIVO / ✅ Voice Pipeline 3002 ATTIVO`).
- Stack SIP NDEBUG dal commit `dd5ade9`.

---

# VERDETTO: CHIAMA ORA — SÌ
**Numero**: **0972536918**
Bridge write-path provato E2E, voice pipeline up, metrics + marker log posizionati.
Il founder esegue le 5 chiamate. Analisi log = task separato in sessione nuova (HANDOFF.md NON toccato in questa sessione, come da istruzione).
