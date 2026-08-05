# mandati — Archivio testi integrali dei blocchi emessi dal giudice

Qui vive il testo integrale di ogni blocco emesso e non ancora eseguito.
Una voce di CODA IMPIANTO è eseguibile dal runner solo se qui esiste il file omonimo.
Il founder incolla i blocchi uno per uno: `pbpaste > docs/judge/mandati/<nome>.md`

## Mandati attesi (da CODA IMPIANTO in STATE.md §CODA IMPIANTO)

| Mandato         | Etichetta      | File              | Stato                                                   |
|-----------------|----------------|-------------------|---------------------------------------------------------|
| T-MACCHINA      | CONFIRM_FIRST  | T-MACCHINA.md     | eseguito, chiusura VERDE su master `439c71f8`           |
| T-EXPOSURE      | CONFIRM_FIRST  | T-EXPOSURE.md     | patch post-review sigillata, attende re-review e merge  |
| T-VERIFICA-3K   | CONFIRM_FIRST  | T-VERIFICA-3K.md  | non archiviato                                          |
| T-CI-TRUTH      | SAFE_AUTO      | T-CI-TRUTH.md     | non archiviato                                          |

## Mandati fuori coda (citati nel mandato T-VOS-RUNNER/#45v3)

| Mandato         | Etichetta   | Stato          |
|-----------------|-------------|----------------|
| T-JUDGE-HARDEN  | SAFE_AUTO   | non archiviato |
| T-SATURAZIONE   | SAFE_AUTO   | non archiviato |
| T-CONSEGNA      | SAFE_AUTO   | non archiviato |

## Etichette (PROTOCOLLO §3 / F3)

- `SAFE_AUTO` → il runner può eseguire senza founder
- `CONFIRM_FIRST` → il runner si ferma e chiede al founder prima di eseguire
- `NEVER_AUTO` → non entra mai in un piano automatico (ogni unità che tocchi :3002, telefonia, DB runtime, o history git)
- Mandato senza etichetta = trattato come NEVER_AUTO
