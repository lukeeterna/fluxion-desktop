# TURNS — chiamata reale 2026-07-17 (engine go, remote 79.98.45.133:12836)

> Una riga per turno. Colonne come da mandato. ND dove il log non arriva.
> `lat_turno` = campo `latency=…ms` di `turno reale loggato in conversation_turns` (voip_goengine) —
> **NON** è la latenza percepita fine-utterance→audio (quella richiede timestamp end-utterance non loggati → ND).
> `TTS_total` = campo `total=…ms` della riga EdgeTTSEngine (sintesi, non playout).
> Persistenza DB `conversation_turns`: **ND** — nessun .db voice-agent contiene la tabella; HTTP Bridge offline (log:810).

| n | t_fine≈ | STT_esatto (caller) | conf | NLU intent (ms, modello) | FSM stato_pre→post / handler | strike | risposta Sara (troncata) | TTS_total | lat_turno ms | note |
|---|---------|---------------------|------|--------------------------|------------------------------|--------|--------------------------|-----------|--------------|------|
| G | 21:50:16 | — (greeting) | — | — | IDLE | 0 | «Salone Demo FLUXION, buonasera! Sono Sar…» | 597ms | — | disclosure «assistente virtuale» ND |
| 1 | 21:50:18 | `Dbeat` | 0.50 | ALTRO 351ms groq-70b | IDLE→(new client) / S142 bare-name | 0 | «Non trovo Dbeat tra i nostri clienti. Mi…» | 804ms | 559.9 | nome errato registrato (RC#1) |
| 2 | 21:50:34 | `Ciao Sara, vorrei prenotare un taglio e colore per la barba, è possibile?` | 0.80 | PRENOTAZIONE 365ms groq-70b | →booking / prenotazione | 0 | «Capisco. Chiaro. Grazie Dbeat Ciao Sara,…» | ND | ND | servizio non confermato (RC#2) |
| 3 | 21:51:31 | ND (STT non loggato) | ND | ALTRO 467ms | REGISTERING_PHONE | ND | «Ha ragione. Mi ripete il numero di telef…» | 816ms | ND | reprompt numero |
| 4 | 21:51:41 | ND | ND | ALTRO 344ms | REGISTERING_PHONE | ND | «Mi dispiace. Mi ripete il numero di tele…» | 716ms | ND | reprompt |
| 5 | 21:51:42 | `E' IL MIO NOME` | ND | CORREZIONE 294ms | REGISTERING_PHONE correction / GroqNLU correzione_nome | 3 | «Comprendo. La passo subito a un collega.» | 1783ms | ND | E6 3-strike; HANGUP soppresso (RC#4) |
| 6 | 21:51:46 | ND | ND | ALTRO 252ms | REGISTERING_PHONE | ND | «Mi scusi. Mi ripete il numero di telefon…» | 812ms | ND | reprompt |
| 7 | 21:52:30 | `Le comunico il numero che non risponde più.` | 0.80 | ALTRO 411ms | REGISTERING_PHONE correction | ND | «Capisco. Mi ripete il numero di telefono…» | 646ms | ND | reprompt |
| 8 | 21:52:37 | `Si è bloccata lì, mi ha richiesto il numero, gliel'ho ripornito.` | 0.80 | ALTRO 328ms | REGISTERING_PHONE | 3 | «Ha ragione. Certo. La passo subito a un…» | 1326ms | ND | E6 3-strike; HANGUP soppresso |
| 9 | 21:52:42 | `Ma è ferma di non risponde più. Sara ci sei?` | ND | ESCALATION 220ms | REGISTERING_PHONE correction | ND | «Comprendo. Mi ripete il numero di telefo…» | 954ms | ND | |
| 10 | 21:53:03 | ND | ND | ESCALATION 222ms | REGISTERING_PHONE | 3 | «Mi scusi. La passo subito a un collega. » | 2063ms | 251.7 | E6 3-strike; HANGUP soppresso |
| 11 | 21:53:12 | ND | ND | CORTESIA 223ms | REGISTERING_PHONE | ND | «Ha ragione. Perfetto, mi dica il numero …» | 586ms | ND | |
| 12 | 21:53:35 | ND | ND | CORTESIA 389ms | REGISTERING_PHONE | 3 | «Mi dispiace. La passo subito a un colleg…» | 1006ms | ND | E6 3-strike; HANGUP soppresso |
| 13 | 21:54:00 | ND | ND | PRENOTAZIONE 393ms | REGISTERING_PHONE | ND | (nessun TTS immediato) | — | ND | |
| 14 | 21:54:06 | ND | ND | ESCALATION 241ms | REGISTERING_PHONE / [WA-ESC] | ND | «Al momento siamo fuori dall'orario di ap…» | 1560ms | ND | WA non disp.→ tel letto (1113); fuori orario (M4?) |
| 15 | 21:54:18 | `ttwchBJfl…4LM3GQ` (garbage) | 0.00 | regex fallback | REGISTERING_PHONE | ND | «Mi scusi. Certo. Ho capito 444385516126,…» | 899ms | 444.9 | STT collassato; num 12 cifre non valido; BARGE-IN |
| 16 | 21:54:23 | `Occhiunando a dire comprendo, intercalare lievemente fuori posto.` | 0.50 | ALTRO 477ms | REGISTERING_PHONE | ND | «Capisco. Per confermare, il numero è 444…» | 1495ms | 531.1 | BARGE-IN |
| 17 | 21:54:29 | `Grazie, arrivederci.` | 0.90 | CORTESIA 274ms | →exit / S142 standalone goodbye | ND | «Ha ragione. Prego. Arrivederci, buona gi…» | 842ms | 276.6 | exit=True, fine chiamata |

## Latenze (turno reale, campo latency= voip_goengine)
Valori loggati: 559.9 · 251.7 · 444.9 · 531.1 · 276.6 ms (n=5 su 17 turni; resto ND)
- min = 251.7ms · med = 444.9ms · max = 559.9ms
- **Scomposizione fine-utt→audio out**: ND (manca timestamp fine-utterance nel log)

## Latenze TTS sintesi (total= EdgeTTSEngine, turni in-call)
range 586 → 2063ms; TTFB range 366 → 817ms (in-call). Warm-up 21:49 escluso.
