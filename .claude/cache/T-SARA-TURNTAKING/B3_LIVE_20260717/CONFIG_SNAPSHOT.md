# CONFIG_SNAPSHOT — chiamata reale 2026-07-17 (engine go, capture window B3)

> Fonte: `sara_go.log` (righe citate). Ogni valore con provenienza. ND = non nel log.

## Runtime che ha governato la chiamata
- **Engine VoIP**: `go` (VOICE_ENGINE=go + SARA_TEST_CAPTURE=1) — b3_open.sh:60; remote RTP `79.98.45.133:12836`, payloadType=8 (PCMA) — sara_go.log:137
- **SIP**: username 0972536918 @ sip.vivavox.it, reg_status 200 — GATE-0bis status endpoint

## Modelli
| Componente | Valore | Fonte |
|---|---|---|
| STT primary | GroqSTT cloud (~200ms) | sara_go.log:757,764 |
| STT fallback | FasterWhisper tiny, compute=int8, timeout 5s | sara_go.log:819,821,822,823 |
| NLU | groq/llama-3.3-70b-versatile (PRIMARY) | sara_go.log:150,208 |
| TTS | EdgeTTSEngine voice `it-IT-IsabellaNeural`, converter afconvert, quality mode (9.0/10) + TTSCache | sara_go.log:2,3,765 |
| VAD | webrtcvad=True, onnxruntime=True (ten_vad_integration) | sara_go.log:1 |
| Name corrector | jellyfish phonetic fast-path attivo | sara_go.log:5 |

## Verticale attivo: `salone`
- GUIDED Dialog Engine init vertical=salone — sara_go.log:761
- FAQ caricate: 18/25 (10 skip per var non risolte) — sara_go.log:786,787
- Var non risolte: PREZZO_COLORE_COMPLETO, PREZZO_BALAYAGE, PREZZO_TAGLIO_BAMBINO, DURATA_TRATTAMENTI, LISTA_OPERATORI, NUM_POSTI_PARCHEGGIO, PREZZO_GIFT_CARD_MIN, PREZZO_LISCIATURA, PREZZO_MASCHERA, SCONTO_PASSAPAROLA — sara_go.log:786

## CATALOGO SERVIZI COMPLETO (verticale salone) — 8 servizi da DB
Fonte: `[F19] Loaded 8 services from DB` — sara_go.log:776, 804
1. `taglio_uomo`
2. `taglio_donna`
3. `piega`
4. `colore`
5. `meches`
6. `barba`
7. `trattamento_cheratina`
8. `extension`

> Nota: il log espone gli **id** dei servizi, NON la mappa id→nome-display→categoria né i prezzi
> (prezzi = variabili non risolte). Mappa completa nome→id/categoria = **ND** nel log
> (risiede in config verticale/DB non estratta in questa finestra S).

## Barge-in / endpointing (dai marker RTP)
- Barge-in RX: soglia `thr=500` su rms, `floor` dinamico, pre=17 frame — sara_go.log:BARGE-IN (es. riga con `rms=2875 thr=500`)
- RX-MARK stato LISTENING/SPEAKING con sustain — sara_go.log:[RX-MARK]
- **Timer reprompt su silenzio (ms)**: ND — non loggato
- **Parametri VAD endpointing (ms)**: ND — non loggati (solo backend disponibili)

## Escalation / strike
- Meccanismo: `[E6] 3-strike escalation triggered in registering_phone` — sara_go.log:445,647,869,1007
- HANGUP guard: `HANGUP soppresso (FSM-guard): should_exit ma intent non-congedo` — sara_go.log:455,655,880,1016
- **Soglia strike numerica esplicita**: 3 (nome regola E6) — ND il file:riga di config

## Voce TTS
`it-IT-IsabellaNeural` (femminile, Edge-TTS quality) — sara_go.log:2
