# FLUXION — Report Sessione + Next Prompt — 2026-06-11 (sera)

================================================================
## PARTE 1 — REPORT DELLA SESSIONE
================================================================

### Obiettivo di partenza
Chiudere **VERITÀ #2a** = attivazione licenza REALE su Windows (gate revenue Pila-1):
pre-piazzare il file licenza via SSH → 1 tocco founder (Carica File → Attiva) →
verifica 3-punti via SSH.

### Cosa è stato fatto (verificato)
1. **PC Windows vivo**: `ssh fluxion-win` OK, `tauri-app.exe` 19MB in `%LOCALAPPDATA%\Fluxion`.
2. **File licenza pre-piazzato**: `fluxion-license-base.json` su `C:\Users\gianluca\Desktop\`,
   byte-identico a REAL_PAYLOAD/REAL_SIG S291 (`license_ed25519_v1.rs:129-131`). Verificato.
3. **Baseline anti-falso-verde catturata**: `license_cache` = 0 righe PRIMA dell'attivazione.

### IMPREVISTO — il wizard di setup non completava ("non si avvia")
Il founder ha disinstallato/reinstallato, rifatto il wizard (Salone bella Ida, tel 3807769822,
CF, mail distasiida@gmail.com), accettato termini, cliccato "Avvia FLUXION" → app non parte.

**Diagnosi (verificata sul DB live Windows)**:
- Processo vivo, WebView2 v149 OK, migrazioni complete, MA `impostazioni` = solo default,
  `gdpr_consents`=0, operatori=0, clienti=0 → **dati wizard MAI salvati**.
- WAL ultima scrittura subito dopo il launch (prima della fine wizard) → `onSubmit` non ha
  mai scritto sul DB.

**ROOT CAUSE (confermata dal founder)**: validazione **P.IVA** (`types/setup.ts:15`,
`partita_iva.length(11)`). P.IVA non di 11 cifre → `handleSubmit` blocca `onSubmit` → 0 scritture.
L'errore COMPARIVA inline sul campo P.IVA, ma il founder non l'ha visto perché non era sotto gli
occhi al momento del click "Avvia FLUXION".

**Risolto**: corretta la P.IVA (11 cifre) → wizard completato → app aperta.

### 2° IMPREVISTO — modal di rete al primo avvio
Messaggio "PC connesso a internet ma server FLUXION non risponde / DNS irraggiungibile, Piper".
**NON è un blocco**: è `FirstRunNetworkModal`, informativo. Proxy verificato VIVO da Mac
(`fluxion-app.com/health` → HTTP 200 in 0,2s). Transitorio al boot. App funziona al 100%
offline; Sara usa voce locale Piper finché la rete non si stabilizza.

### Insight critico per la VENDITA (founder)
Un "cliente medio-basso che non lo sa" si pianterebbe negli stessi 2 punti:
- **P.IVA**: errore inline non basta, va mostrato un riepilogo prominente al click del pulsante.
- **Modal DNS/Piper**: testo allarmante per un non-tecnico, va reso rassicurante.
→ Entrambi = **fix UX obbligatori PRIMA di vendere**.

### STATO FINALE
- 🟢 App FLUXION gira su Windows reale, wizard completato, dashboard accessibile.
- 🟢 **VERITÀ #2a = CHIUSA, gate revenue Pila-1 sbloccato**. Founder ha caricato il .json e attivato.
  Verifica 3-punti via SSH tutta VERDE:
  - (1) `license_cache` id=1: `status=active`, `tier=base`, `email=fluxion.gestionale@gmail.com`,
    **firma = REALE match** (`ToiIWbu…qAA==`, byte-identica Worker S291, NON placeholder).
  - (2) gating deterministico `tier=base` → `fatturazione_pa=true` + `voice_agent=false`
    (`license_ed25519.rs:136-225`).
  - (3) firma reale persistita = `verify_strict` passato (`save_license` gira solo su verify valido).
  - Nota non-bloccante: `license_history`=0 righe (attivazione non logga lo storico) → follow-up.
- 📝 2 fix UX pre-vendita registrati (wizard error summary + testo modal rete).

================================================================
## PARTE 2 — NEXT PROMPT (prossima sessione)
================================================================

### TASK A — VERITÀ #2a ✅ GIÀ CHIUSA (2026-06-11). Vedi STATO FINALE sopra. Nessuna azione.
Eventuale follow-up minore: investigare perché l'attivazione NON scrive in `license_history`
(`event_type='activated'`) — non-bloccante, `license_cache` è la verità del gate.

### TASK B (priorità 1 ora) — fix UX pre-vendita (build iMac + reinstall founder)
1. `src/components/setup/SetupWizard.tsx`: `handleSubmit(onSubmit, onInvalid)`; in `onInvalid`
   mostrare **riepilogo prominente accanto a "Avvia FLUXION"** di tutto ciò che manca/è da
   correggere (map `formState.errors` → lista leggibile) + scroll/jump al primo campo invalido +
   allo step che lo contiene. Aggiungere `toast.error(String(error))` nel `catch` (riga 123-125).
2. `src/components/FirstRunNetworkModal.tsx:52`: riscrivere testo meno allarmante per non-tecnici.
3. Build su iMac → reinstall founder fisico → test: P.IVA errata di proposito → il riepilogo
   deve essere visibile e bloccare con messaggio chiaro.

### DOPO VERITÀ #2a (milestone Pila-1, WIP=1)
Restano 2 gate per essere vendibili: **(c) charge E2E €1** + **(d) magazzino su 1 verticale**.
Pila-2 (code signing EV, hardening, GDPR e2e) CONGELATA fino al 1° CLOSED_WON.

### REGOLE OPERATIVE
- SSH→Windows: PowerShell non cmd. `ssh fluxion-win 'powershell -NoProfile -Command "..."'`.
- Macchina cliente: nessun refactor extra, prova per step, STOP+report su fail.
- Carry dettagliato tecnico completo in: `.claude/NEXT_SESSION_PROMPT.manual.md`.
