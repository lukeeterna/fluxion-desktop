# REPORT — B3-RACCOLTA v2 (#34v) — Dossier taratura finestra 17-07-2026

Sessione CC nuova. Consegna: dossier di taratura della chiamata reale + salvage volatili + chiusura finestra B3. **Nessuna modifica a codice** (read-only + commit artefatti).

## 1. Stato finestra — trovato / lasciato
- **Trovato**: `engine:go`, sip reg 200 (0972536918@sip.vivavox.it), 1 processo :3002 (pid 28546). Finestra B3-go ANCORA APERTA.
- **Azione**: `b3_close.sh` (autorizzato GATE-0bis) → CHECKPOINT RESTORED (restore.sh rilancia produzione).
- **Lasciato**: `engine:pjsua2`, reg 200, 1 processo :3002 (pid 31760). ✅ Nessuna anomalia (no doppi processi, 200 dopo un solo close).

## 2. Chiamata analizzata
- Finestra: 21:50:16 → 21:54:30 (~4m14s), engine go, remote RTP 79.98.45.133:12836, PCMA.
- Verticale: `salone` (Salone Demo FLUXION). Caller reale via trunk EHIWEB.
- Esito: booking FALLITO — bloccata in `REGISTERING_PHONE` per ~3.5 min, chiusa da congedo caller.

## 3. Scorecard M1..M5 (ricostruita SOLO dai log)
| Metrica | Esito | Evidenza |
|---|---|---|
| **M1** disclosure «assistente virtuale» nel greeting | **ND** | greeting «…Sono Sar[a]» troncato a 40 char (log:145); stringa «assistente virtuale» NON presente nel testo loggato — impossibile confermare pronuncia |
| **M2** cattura servizio | **FAIL/parziale** | input esatto «taglio e colore per la barba» → PRENOTAZIONE 0.80 (log:208) ma servizio mai confermato; mapping slot→catalogo ND |
| **M3** cattura nome | **FAIL** | «Dbeat» (apertura caller) captato come NOME via euristica S142 bare-name-in-IDLE (log:152-155) → cliente errato registrato |
| **M4** reprompt su silenzio / fuori orario | **parziale/ND** | reprompt presenti; branch fuori-orario (log:1119); timer configurato vs osservato = ND |
| **M5** | **ND** | non identificabile dai log di questa finestra |

## 4. Root-cause pointers (read-only)
1. **Saluto→NOME**: caller apre «Dbeat» → NLU ALTRO conf=0.50 (log:150) → `[S142] Bare name detected in IDLE` (log:152) → `booking_state_machine [S142] Bare name in IDLE → name=Dbeat` (log:153). L'euristica bare-name-in-IDLE accetta qualunque token singolo come nome senza gate di conferma. Codice: `src/orchestrator.py` + `src/booking_state_machine.py` marker `[S142]` (file:riga esatto ND, non aperto).
2. **«colore per la barba» → mapping**: STT esatto «Ciao Sara, vorrei prenotare un taglio e colore per la barba, è possibile?» (log:208). Catalogo salone 8 servizi (log:776) include `taglio_uomo`,`taglio_donna`,`colore`,`barba`. **[IPOTESI]** l'NLU spezza «taglio»→taglio_* e «colore»→`colore` ignorando il qualificatore «barba»; la riga di slot-result esplicita NON è nel log estratto → mapping = **ND**, ipotesi non confermata.
3. **Blocco dettatura telefono**: STT numero collassa ripetutamente — «Groq ha restituito testo vuoto» (log:818,829,845), FasterWhisper fallback timeout 5s (log:821,830,846), infine garbage `ttwchBJfl…` conf=0.00 (log:1157) e numero «444385516126» (12 cifre, non valido, log:1161). Stato bloccato `REGISTERING_PHONE` per tutta la chiamata; `[E6] 3-strike escalation` scatta 4× (log:445,647,869,1007). **[IPOTESI]** RTP inbound degradato/DTMF-vs-voce: rms caller basso su cifre.
4. **«le passo un collega»**: template escalation, trigger = `[E6] 3-strike escalation triggered in registering_phone` (log:445); MA `voip_goengine HANGUP soppresso (FSM-guard): should_exit ma intent non-congedo` (log:455,655,880,1016) → Sara annuncia il collega ma **non chiude**, rientra in reprompt loop. Contraddizione strutturale: annuncia handoff che la guard impedisce.
5. **«comprendo» ripetuto**: NON è filler d'attesa (B1 filler = «Ora verifico…» log:130). È un **prefisso empatico** prepeso ad ogni reprompt di correzione: `Comprendo.`/`Capisco.`/`Mi scusi.`/`Ha ragione.`/`Mi dispiace.` (log:398,451,624,712,874,915,1011…). Scatta ad ogni turno CORREZIONE/ALTRO in REGISTERING_PHONE → percepito come loop di scuse.
6. **M1 disclosure**: greeting pronunciato = variante «Salone Demo FLUXION, buonasera! Sono Sar[a]…» (log:145). Il testo oltre 40 char è troncato dal logger → «assistente virtuale» **non verificabile** = ND (né sì né no).
7. **M4 reprompt su silenzio**: reprompt presenti + branch fuori-orario (log:1119); **timer configurato vs osservato = ND** (parametri endpointing/reprompt non loggati).

## 5. Sintesi latenze
- Turno reale (`latency=` voip_goengine, n=5): 559.9 / 251.7 / 444.9 / 531.1 / 276.6 ms → **min 251.7 · med 444.9 · max 559.9**.
- TTS sintesi in-call (`total=`): range 586→2063ms; TTFB 366→817ms.
- **Scomposizione fine-utterance→audio out (latenza percepita)**: ND — timestamp di fine-utterance non loggato.

## 6. Salvage volatili (regola founder 17/07 — durabilità dichiarata)
Tutti gli artefatti volatili (`/tmp/b3` iMac, cancellabile al reboot) copiati in **repo committato** (classe: durabile/versionata):
- Scripts → `.claude/cache/T-SARA-TURNTAKING/B3_RUNBOOK/scripts/` (b3_open/close/status.sh, restore.sh, RUNBOOK_B3.md)
- `sara_go.log` (224KB, chiamata) → `B3_LIVE_20260717/`
- `sara_restore.tail2000.log` (tail -2000 del restore log) → `B3_LIVE_20260717/`
- **Writer sara_restore.log**: processo Sara produzione (`main.py --port 3002`, pjsua2, pid 31760) via `restore.sh:11` `nohup … > /tmp/b3/sara_restore.log 2>&1`. NON launchd/watchdog. `restore.sh` **tronca** ad ogni restore. Attivo da restore 22:18 di stasera.

## 7. MANIFEST artefatti
```
.claude/cache/T-SARA-TURNTAKING/
├── REPORT_B3-RACCOLTA_20260717.md            (questo file)
├── B3_RUNBOOK/scripts/
│   ├── b3_open.sh  b3_close.sh  b3_status.sh  restore.sh  RUNBOOK_B3.md
└── B3_LIVE_20260717/
    ├── sara_go.log                           (224KB, chiamata reale go)
    ├── sara_restore.tail2000.log             (tail -2000 restore log)
    ├── TURNS.md                              (17 turni + latenze)
    ├── TRANSCRIPT.md                         (dialogo caller/Sara)
    ├── CONFIG_SNAPSHOT.md                    (runtime + catalogo servizi)
    └── TEMPLATES_FIRED.md                    (testi pronunciati, troncati a 40ch)
```

## 8. Discordanze
1. **sara_restore.log ≠ 13,8MB**: il mandato lo dà a 13,8MB; il file reale è **39KB** (39319B @22:11), cresciuto a ~55KB durante restore attivo. Spiegazione: `restore.sh` usa `>` (tronca) ad ogni restore → il 13,8MB era di un restore precedente longevo, azzerato al restore 22:18. `tail -2000` = intero file corrente.
2. **WAV chiamata ASSENTE**: nonostante `SARA_TEST_CAPTURE=1` (b3_open.sh:60), nessun `.wav` post-21:00 in `/tmp/b3` né in `voice-agent/.claude/cache`. → **REGOLA #32 NON soddisfatta** in questa finestra (chiamata senza WAV per il giudice). Metadati WAV = NONE.
3. **conversation_turns non persistito**: il log dice «turno reale loggato in conversation_turns» ma nessun `.db` voice-agent contiene la tabella; HTTP Bridge offline (log:810). Dati turno autorevoli DB = ND (ricostruiti dal log).
4. **Catalogo servizi**: log espone solo id (8), non mappa nome→id→categoria né prezzi (var non risolte). Mappa completa = ND.

## 9. Context
- Json sessione corrente (`6fdbb8f1`, source transcript): **used_pct 9,6%**.
- Hook VOS (vos_state) in-run: **~54%**. Divergenza nota (MEMORY: % VOS RAW gonfiate vs reale). Valore autorevole = json 9,6%; operativamente ho lavorato sotto la soglia di chiusura VOS 60%.

## 10. Taglia
Consegna S completa per le parti estraibili dai log. **Mancano (fuori portata log/taglia)**: latenza percepita fine-utt→audio (no timestamp), WAV (non catturato), mappa servizi nome→id, file:riga codice dei template e delle euristiche S142/E6, testo template integrale >40 char. Chiusura pulita.
