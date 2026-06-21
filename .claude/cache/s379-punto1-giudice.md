# Prompt per GIUDICE (Claude AI) — validare/contestare la chiusura del "Punto 1" (fingerprint licenza FLUXION)

> Copia tutto questo blocco in una chat Claude.ai nuova. Rispondi come revisore tecnico indipendente.

## Tuo ruolo
Sei un revisore tecnico indipendente. Non ti fidare delle conclusioni: valuta SOLO il metodo e l'evidenza. Output finale: **CONFERMO** o **CONTESTO** la chiusura, con motivazione tecnica e (se contesti) l'esperimento minimo che mancherebbe per chiudere davvero.

## Contesto prodotto
FLUXION è un gestionale desktop (Tauri + Rust + SQLite) venduto €497 una-tantum, licenza Ed25519 hardware-locked. Su Windows reale, su una macchina che ha **pagato davvero** (charge Stripe LIVE, host `AlessiaManuel`, email `manueldx2014`), si temeva un bug "Punto 1": all'avvio l'app potrebbe ri-chiedere l'attivazione della licenza (re-prompt) se il fingerprint hardware calcolato a runtime non combacia con quello salvato all'attivazione → ramo `HARDWARE_MISMATCH`. Sarebbe un blocker di fiducia: il cliente pagante vedrebbe "licenza non attiva / registrata su un altro Mac".

## Codice rilevante (fonte reale, verificato)
Funzione che genera il fingerprint (`src-tauri/src/commands/license_ed25519.rs:285`):
```rust
pub fn generate_fingerprint() -> String {
    let mut sys = System::new_all();
    sys.refresh_all();
    let hostname     = sys.host_name().unwrap_or("unknown");
    let cpu_brand    = sys.cpus().first().map(|c| c.brand()).unwrap_or("unknown");
    let total_memory = sys.total_memory();      // sysinfo 0.29.11 → byte
    let system_name  = sys.name().unwrap_or("unknown");
    let src = format!("{}:{}:{}:{}", hostname, cpu_brand, total_memory, system_name);
    // SHA-256(src), poi hex dei primi 16 byte
}
```
Ramo che produce il re-prompt (`:543-559`): se la licenza è attivata (tier != Trial) e `fp_salvato != fingerprint_runtime` → stato licenza invalido / `HARDWARE_MISMATCH`.

## Cosa è stato fatto per chiudere il Punto 1 (metodo S378 — da validare)
Via SSH read-only sulla macchina pagante (app accesa, DB letto con FileShare.ReadWrite):
1. **Letto il fingerprint SALVATO** dal DB reale (`license_cache` id=1, `C:\Users\gianluca\AppData\Roaming\com.fluxion.desktop\fluxion.db`):
   `343865fe7623b3063a50941e55e68e29` (status=active, tier=base, machine_id vuoto, email manueldx2014).
2. **Ricostruito il fingerprint RUNTIME** prendendo i valori hardware LIVE correnti della stessa macchina:
   `AlessiaManuel : Intel(R) Core(TM) i5-4210U CPU @ 1.70GHz : 8516689920 : Windows`
   → SHA-256 → primi 16 byte → `343865fe7623b3063a50941e55e68e29`.
3. **Confronto: identici (==)**. Conclusione tratta: `fp == fingerprint` → niente `HARDWARE_MISMATCH` → `is_valid=true, is_activated=true` → il re-prompt NON è causato dal fingerprint. Si è definito questo "prova per costruzione" (gli input hardware stabili letti ora riproducono l'hash salvato), non deduzione statica del codice.

## Le domande per te (giudice)
1. **Il metodo è sound?** "Prova per costruzione in UN istante" (ricostruisco l'hash dai valori live e combacia con quello salvato) è sufficiente a concludere che il fingerprint è **temporalmente stabile** e non produrrà re-prompt a un avvio futuro? O dimostra solo che in quell'istante coincide?
2. **Punti di instabilità degli input.** Valuta uno per uno se possono cambiare tra l'attivazione e un avvio futuro, sulla stessa macchina fisica, causando un hash diverso:
   - `host_name()` (rinomina PC da parte dell'utente?)
   - `cpu.brand()` (stringa stabile?)
   - `total_memory()` byte (può variare? es. memoria riservata firmware, aggiornamenti BIOS, reporting sysinfo non deterministico?)
   - `sys.name()` ("Windows" stabile? cambia tra major update?)
3. **Drift di versione libreria.** Se in una build FUTURA di FLUXION cambia la versione di `sysinfo` (es. unità di `total_memory` da byte a KB, o `name()` che restituisce "Windows 11" invece di "Windows"), l'hash cambia su un binario aggiornato → re-prompt su clienti già attivati. È un rischio reale? Va mitigato ora (es. fingerprint versionato / migrazione)?
4. **Verdetto.** Dato tutto sopra: il Punto 1 è **chiuso** (nessun bug fingerprint, eventuale re-prompt passato = build vecchia) oppure resta un **rischio residuo** che richiede un esperimento aggiuntivo? Se sì, qual è l'esperimento minimo (falsificabile, €0) che lo chiuderebbe — es. reboot della macchina + ri-lettura, o simulazione del bump di `sysinfo`?

Rispondi conciso ma completo. Niente diplomazia: conferma con dati o contesta con dati.
