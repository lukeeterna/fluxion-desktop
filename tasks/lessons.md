# FLUXION — Lessons Learned
> Aggiornare dopo ogni correzione utente o bug ricorrente.
> Formato: data · categoria · errore · fix · regola.

---

## 2026-02-24 — Config / Tauri v2
**Errore:** `windows` e `security` posizionati a livello root in `tauri.conf.json`
**Fix:** Spostati sotto la chiave `app` (breaking change Tauri v2)
**Regola:** In Tauri v2, la struttura è sempre `app.windows[]` e `app.security{}` — non root-level

---

## 2026-02-24 — Build / Cargo
**Errore:** `cargo update` dopo modifica `Cargo.toml` lascia Cargo.lock inconsistente su iMac
**Fix:** Eliminare `Cargo.lock` su iMac dopo ogni aggiornamento `Cargo.toml`, poi rebuild da zero
**Regola:** Non fare solo `cargo update` — delete + rebuild garantisce dipendenze pulite

---

## 2026-02-23 — Networking / Voice Pipeline
**Errore:** `pkill -f 'python main.py'` non termina il processo voice pipeline su iMac
**Fix:** `kill $(lsof -ti:3002)` — il processo usa `Python` con P maiuscola, pkill case-sensitive
**Regola:** Per terminare la pipeline usare sempre `lsof -ti:3002` + `kill`

---

## 2026-02-23 — Networking / URL
**Errore:** Frontend puntava a `localhost:3002` invece di `192.168.1.7:3002` (iMac)
**Fix:** Aggiornato URL in tutti i fetch del frontend
**Regola:** Il voice agent gira su iMac (192.168.1.2 interna, verificare IP attuale). Mai assumere localhost in ambiente dev cross-machine

---

## 2026-02-12 — Testing / Timeout
**Errore:** `voice_process_audio` Rust command andava in timeout dopo 30s (Whisper.cpp ~30s su CPU)
**Fix:** Timeout alzato a 120s (commit 7a26712) come fix temporaneo
**Regola:** Il fix è temporaneo — la vera soluzione è STT più veloce (ggml-tiny o CoreML)
