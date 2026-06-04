# Verdetto giudice esterno (Claude.ai) — S337 → S338

> Risposta al prompt `.claude/cache/agents/s337/claude-ai-prompt-s337.md`. Incollata da Luke 2026-06-04.

## VERDETTO SECCO
**Opzione 1 — fix threading.** MA NON la variante già falsificata (deferral manuale nel drainer). Il meccanismo corretto è la marshaling **integrata** di pjsua2:
- `uaConfig.threadCnt = 0`
- `uaConfig.mainThreadOnly = true`
- `libCreate()` e `libHandleEvents()` eseguiti sullo **STESSO** thread.

**NON Asterisk. NON abbandonare il loopback.** Costo stimato reale: ~1h se la diagnosi è corretta (cambio di 2 campi config + garanzia thread-affinity).

## META-DOMANDA (risposta per prima) — intuizione giusta sui sintomi, conclusione sbagliata
Il loopback È più ostile della produzione e la chiamata reale ha funzionato — ma "quindi abbandona il loopback" è errato. Il fix NON è lavoro buttato su un harness artificiale: è il modo **documentato e corretto** di far girare pjsua2 sotto Python, e indurisce anche la produzione.
Doc PJSIP esplicita: con linguaggi high-level (Python) va disabilitato il worker thread interno (`threadCnt=0`), perché Python non gradisce essere chiamato da un thread esterno (worker PJSIP). La chiamata provider "funzionava" per **fortuna di timing**, non per correttezza: una race che si manifesta solo in loopback è un bug **reale latente in produzione**. "Funziona perché la latenza di rete nasconde la corsa" = bomba a orologeria, non certificato di sanità.
→ Il loopback è lo strumento di regressione, non un test da abbandonare. Risolverlo serve a entrambi.

## PERCHÉ LA DIAGNOSI S337 È SBAGLIATA (version-independent ≠ irreducibile)
"version-independent" è corretto; "→ irreducibile" no. È version-independent perché il meccanismo difettoso è lo stesso in 2.15.1 e 2.16 — e quel meccanismo ha un **fix documentato**.
Root cause vera = ticket fondativo pjsua2 **#1519**: su Python solo i thread creati da Python possono chiamare Python; problema col callback chiamato da un worker thread. Il worker SIP si può disabilitare, ma **altri worker thread — es. il sound/media device — NON si possono disabilitare**. Soluzione = framework che posta il job al "main thread" durante `libHandleEvents()`.
Traduzione del crash:
1. `threadCnt=0` spegne il worker SIP, **non** il thread media/sound device (resta vivo).
2. Quel media-thread esegue `onCallMediaState` e/o l'op conferenza → setta owner del group-lock su sé stesso.
3. `_pjsua2_thread` (che chiama `libHandleEvents`) fa l'unset → owner mismatch → `grp_lock_unset_owner_thread` abort.
4. `possibly re-registering existing thread` = prova che un thread non-tuo (media-thread) entra in pjlib.
In loopback su 127.0.0.1 il media negozia istantaneamente → dispatch sempre sul media-thread → crash deterministico. Col provider la sequenza è diluita → race a volte chiusa.

## IL FIX ESATTO (API reale)
Framework di marshaling = flag **`mainThreadOnly`** (campo `UaConfig`). Doc PJSUA2: con flag non-zero, tutti i callback da thread ≠ main thread vengono **postati al main thread** ed eseguiti da `Endpoint::libHandleEvents()`. Funziona SOLO se `threadCnt==0` e `libHandleEvents()` gira sul main thread (default = thread che ha chiamato `Endpoint::libCreate()`).
Da verificare/applicare in `voip_pjsua2.py`:
1. `epConfig.uaConfig.threadCnt = 0` — verifica sia davvero 0. Se >0 = doppio modello threading (antipattern).
2. `epConfig.uaConfig.mainThreadOnly = true` — quasi certamente il **campo mancante**.
3. **Thread-affinity** (punto che si rompe più spesso): `ep.libCreate()` e il loop `ep.libHandleEvents()` DEVONO girare sullo stesso identico thread (`_pjsua2_thread`). Se `libCreate()` è sul main Python e `libHandleEvents()` su un thread separato → `mainThreadOnly` posta i job al thread di libCreate ma li esegue un altro → flag senza effetto. Sposta `libCreate()` dentro `_pjsua2_thread`, oppure rendi `_pjsua2_thread` il creatore dell'Endpoint.

Nota `libRegisterThread()`: serve ma da solo NON basta (utente .NET con stesso assert ha confermato che non risolve). Evita "calling pjlib from unknown thread" ma NON l'owner-mismatch del group-lock → serve affinità single-thread + marshaling.

## Q2 (crash su `Add port 1`, porta interna di `answer()`) — prova A FAVORE
Il deferral S243/S335 falliva perché spostava solo le op Python; la porta interna di pjsip in `answer()` resta fuori controllo. `mainThreadOnly` opera più in basso: marshalizza ANCHE i callback interni di pjsip. Ecco perché il deferral non poteva funzionare e questo sì. S335 che sposta il crash su `Add port 1` diceva esattamente: il problema non è QUALE op, è su QUALE thread gira qualsiasi op.

## ASTERISK/ARI (Opzione 2) — NO, e non ora
- Rischio Big Sur reale (già muro libc++/ICU su questa macchina; build Asterisk da sorgente su Big Sur no-AVX2 = secondo rabbit-hole). "Costo zero" sul software, non sul tempo.
- Non serve il gate: il gate è "validare Sara", non riscrivere il transport.
- 4-8h ottimistiche → con debug build Big Sur diventano 2-3 giorni.
→ Parcheggia come F2/F3, riconsidera solo se pjsua2 resta cronicamente instabile DOPO il fix config.

## TRADE-OFF 30/60/90gg
- **30gg**: Opz.1 sblocca loopback subito + regressione autonoma su Sara senza dipendere dal 403. ~1h, rischio minimo.
- **60gg**: a 403 sbloccato, validi con chiamata reale + loopback come rete di sicurezza per ogni modifica FSM/RAG. Doppia copertura. Nessun nuovo daemon su hardware fragile.
- **90gg**: se loopback resta stabile → era config, non architettura, Asterisk archiviato a €0. Se emergono nuovi crash threading anche con `mainThreadOnly` → solo allora ARI giustificato da evidenza, non da paura.

## AUTORIZZAZIONE RISPETTO A VINCOLO #1c (ciclo bounded, hard cap 2h)
Questo è il 3° ciclo → serve criterio di falsificazione netto, non terzo tentativo aperto.
- **Cosa fare**: applica i 3 punti (threadCnt=0, mainThreadOnly=true, affinità libCreate/libHandleEvents stesso thread). PRIMA di modificare, ispeziona la config attuale e registra i 3 valori in questo file: probabile che la sola lettura dica subito quale dei tre è violato.
- **Criterio di STOP netto (binario)**: se con `threadCnt=0` + `mainThreadOnly=true` + libCreate/libHandleEvents provatamente sullo stesso thread il loopback continua ad abortire su `grp_lock_unset_owner_thread` → diagnosi config FALSIFICATA → fermati, sposta il gate su "validazione con chiamata reale post-403", parcheggia il loopback, e NON aprire un 4° ciclo né toccare Asterisk senza nuovo verdetto esterno.
Singolo ciclo, esito binario verificabile → compatibile con lo spirito #1c.

## FONTI CITATE DAL GIUDICE (da verificare in S338 prima di applicare)
- Doc PJSIP threadCnt=0 per linguaggi high-level (Python)
- pjsua2 issue #1519 (worker thread / sound device non disabilitabile / marshaling main thread)
- Doc PJSUA2 `UaConfig.mainThreadOnly`
- Thread Narkive (.NET, libRegisterThread non risolve da solo l'assert)
