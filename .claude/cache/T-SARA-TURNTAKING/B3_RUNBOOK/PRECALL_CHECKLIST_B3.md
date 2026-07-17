# PRE-CALL CHECKLIST B3 — finestra live Sara (una pagina, la esegue il FOUNDER)

> Pre-flight CC (#34v, 2026-07-17): deploy allineato MacBook↔iMac (md5 identici),
> NLU attivo = `groq/llama-3.3-70b-versatile` (Cerebras rimosso). `b3_open.sh` killa la
> produzione e rilancia una Sara-go FRESCA dal repo deployato → carica il codice 70B corrente.
> Runbook completo: `.claude/cache/T-SARA-TURNTAKING/B3_RUNBOOK/RUNBOOK_B3.md`.

## 0. Prima di iniziare
- [ ] Sei fisicamente pronto a chiamare **0972536918** dal tuo telefono.
- [ ] Terminale MacBook aperto (i comandi parlano all'iMac via `ssh imac`).
- [ ] Foglio/nota per la scorecard M1..M5.

## 1. Cosa AVVIARE (in ordine)
1. Stato di partenza (deve dire `pjsua2` + reg 200):
   `ssh imac 'bash /tmp/b3/b3_status.sh'`
2. (Consigliato) DRY-RUN senza telefonare: `b3_open.sh` → attendi `CHECKPOINT GO-UP` →
   `b3_status.sh` (deve dire `go`) → `b3_close.sh` → `CHECKPOINT RESTORED`.
3. Finestra reale — apri: `ssh imac 'bash /tmp/b3/b3_open.sh'`
   → **attendi `CHECKPOINT GO-UP`** prima di comporre il numero.

## 2. Cosa OSSERVARE durante la chiamata (M1..M5)
Segna OK / PARZIALE / FAIL + nota. Per ogni turno **annota la latenza percepita** (istantanea / breve / lunga) — NLU 70B.

- **M1 Greeting+disclosure**: Sara saluta, si capisce bene, dice «assistente virtuale».
- **M2 Barge-in**: interrompila mentre parla → deve fermarsi e ascoltarti.
- **M3 Prenotazione**: chiedi un appuntamento → raccoglie nome/servizio/data/ora.
  → **PARZIALE è accettabile** (founder D4): se non completa perfettamente, segna PARZIALE + nota (NON FAIL).
- **M4 Silenzio→reprompt**: stai zitto qualche secondo → deve ri-sollecitarti.
- **M5 Congedo**: saluti e chiudi → **Sara pronuncia il congedo e chiude lei** (riaggancia),
  **BYE ≤2s dalla fine della sua goodbye-TTS** (misura dal termine del SUO saluto, non dalla tua frase).

## 3. Cosa RACCOGLIERE
- [ ] Scorecard M1..M5 compilata (con latenze percepite per turno).
- [ ] WAV chiamata: resta su iMac in
      `.claude/cache/T-SARA-TURNTAKING/calls/` (stereo L=tu, R=Sara) — lo raccoglie CC dopo.
- [ ] Non serve copiare log a mano: `sara_go.log` resta in `/tmp/b3/` su iMac (CC lo estrae).

## 4. Come CHIUDERE (obbligatorio)
1. Riaggancia il telefono.
2. Chiudi: `ssh imac 'bash /tmp/b3/b3_close.sh'` → attendi **`CHECKPOINT RESTORED`**
   (idempotente: rilancia la stessa riga se non lo vedi).
3. Verifica ripristino + **niente orfani**: `ssh imac 'bash /tmp/b3/b3_status.sh'`
   → deve dire `"engine": "pjsua2"` + `"reg_status": 200`, un solo processo su :3002.
4. Se dopo due chiusure non torna `pjsua2` o restano due processi: **fermati e avvisa CC**, non toccare altro.

## Vincoli invarianti
- **Una sola chiamata** (massimo due). Parla come un cliente vero.
- A fine finestra: **pjsua2 ripristinato e verificato** + check orfani.
- La finestra la esegui **tu**; CC raccoglie l'evidenza (WAV/log) nel mandato successivo.
