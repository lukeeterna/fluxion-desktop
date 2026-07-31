# Prompt per Sol — Stress test Sara verticali (v2)

## Contesto progetto
FLUXION è un gestionale desktop per PMI italiane con un voice agent AI chiamato Sara
(Python, porta 3002, iMac 192.168.1.2). Sara gestisce prenotazioni, FAQ e catalogo servizi
per diversi tipi di attività: parrucchieri, officine auto, dentisti, fisioterapisti, palestre, centri estetici.

## Scopo dello script che devi costruire
Certificare il comportamento di Sara su 6 verticali PMI italiani eseguendo una batteria
di test contro il server live `:3002`. Lo script deve:

1. Testare ogni verticale in modo isolato (switch verticale via API, reset sessione tra i test)
2. Misurare 5 dimensioni per verticale:
   - **Booking**: Sara riesce a completare una prenotazione (da "voglio prenotare" a conferma finale)?
   - **FAQ**: Sara risponde correttamente a domande frequenti sul servizio?
   - **Guardrail**: Sara rifiuta richieste di servizi non pertinenti al verticale?
   - **Catalogo**: Sara sa elencare i servizi offerti dalla struttura?
   - **Argomentazioni**: Sara sa valorizzare il servizio quando l'utente ha dubbi?
3. Misurare latenza p95 per verticale (soglia OK = 5000ms)
4. Produrre una scorecard Markdown con OK/WARN/FAIL per ogni dimensione + lista FAIL con evidenza verbatim
5. Fare cleanup dei dati fixture inseriti nel DB durante il test
6. Identificare il "verticale più pronto" per il lancio

## Endpoint disponibili (eseguire su iMac via SSH o in locale sul server)
```
GET  http://127.0.0.1:3002/health
POST http://127.0.0.1:3002/api/voice/process        # body: {"text": "..."}
POST http://127.0.0.1:3002/api/voice/set-vertical   # body: {"vertical": "salone"}
POST http://127.0.0.1:3002/api/voice/reset
GET  http://127.0.0.1:3002/api/voice/voip/status
```

## Verticali da testare (6)
| Nome test    | API vertical   |
|-------------|----------------|
| Parrucchiere | salone         |
| Officina     | auto           |
| Dentista     | odontoiatra    |
| Fisioterapia | fisioterapia   |
| Palestra     | palestra       |
| Estetica     | beauty         |

## Asset riusabile già in repo
`voice-agent/tests/e2e/test_sara_stress_per_verticale.py` (14/05/2026)
Contiene un dict `VERTICALS` con `booking_conversations`, `faq`, `guardrail_wrong_service`
per i verticali: salone, auto, medical, palestra, beauty.
Puoi importarlo come modulo o estrarne le conversazioni — è collaudato su :3002.

## DB verticali
`voice-agent/data/vertical_dbs/<vertical>.db` — SQLite, tabella `servizi(nome, ...)`.
Puoi leggerli per costruire query catalogo realistiche.

## Vincoli
- Script va eseguito su iMac (non MacBook — :3002 bound 127.0.0.1)
- Seed fixture nel DB dei clienti con tag identificabile per cleanup sicuro
- Cleanup garantito anche in caso di errore (finally block)
- Ripristino verticale al termine (`salone` = default demo)
- Budget tempo: max 20 min totali, max 3 min per verticale
- Output MD in `vos/runs/20260731/stress_verticali_v2.md`

## FAIL già noti dalla run precedente (v1, 2026-07-31)
Per il tuo riferimento — non è richiesto che li risolvi, ma saperlo ti aiuta a costruire test più robusti:
- Booking mai completato (FSM resta in `waiting_date`) — possibile causa: nome cliente fittizio non in DB demo
- Catalogo non servito su 4/6 verticali — Sara risponde FAQ generica invece di listare servizi
- Cross-contamination fisioterapia→auto (risponde "Siamo l'Officina Demo FLUXION" a "Chi siete?")
- Latenza p95 > 9000ms su fisioterapia, palestra, estetica

Script v1 in repo: `vos/runs/20260731/stress_verticali.py`
Report v1 in repo: `vos/runs/20260731/stress_verticali.md`

## Output atteso (formato scorecard)
```markdown
# Stress Verticali Sara — [DATA]

## Verticale: Parrucchiere (api=salone)
| Dimensione  | Esito | Dettaglio |
|------------|-------|-----------|
| Booking    | FAIL  | ... |
| FAQ        | OK    | ... |
...
p95 latenza: Xms

## FAIL — Evidenza verbatim
...

## Verticale più pronto: [NOME]
```

Costruisci lo script come ritieni opportuno — sei libero di strutturarlo diversamente dalla v1.
L'unico vincolo è che produca la scorecard sopra e faccia cleanup dei fixture.
