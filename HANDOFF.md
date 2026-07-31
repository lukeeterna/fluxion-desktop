[FLUXION] HANDOFF — 2026-07-31 sessione 3830a8ae

## STATO CORRENTE
T-STRESS-VERTICALI (#34v) COMPLETATO — VERDETTO ROSSO.
Tutti gli artefatti committati e pushati su origin/master (d7b8ba96).

## COMMIT SESSIONE
- a60e4f19 — script Sol verbatim `vos/runs/20260731/stress_verticali.py`
- fd32bc12 — scorecard `vos/runs/20260731/stress_verticali.md` + `docs/judge/STATE.md`
- d7b8ba96 — report sessione + prompt Sol v2 in `.claude/cache/`

## RISULTATI STRESS TEST
6/6 verticali FAIL. Root cause:
1. Booking universale — FSM resta in `waiting_date`, `booking_created` mai osservata
2. Catalogo 4/6 — Sara risponde FAQ invece di listare servizi
3. Cross-contamination fisioterapia→auto ("Siamo l'Officina Demo FLUXION")
4. Latenza p95 > 9000ms su fisioterapia/palestra/estetica

Verticale più pronto: **Parrucchiere / Barbiere**

## PROSSIMA DIRETTIVA OPERATIVA
Incollare `.claude/cache/PROMPT_SOL_STRESS_VERTICALI_v2.md` a Sol (GPT/esterno) e attendere
script v2. Poi eseguirlo su iMac contro :3002 e produrre nuova scorecard.
Prima però: decidere se fixare i FAIL strutturali su Sara (booking FSM, catalogo RAG,
cross-contamination KB) o procedere con Parrucchiere come verticale pilota.

## DISCORDANZE APERTE
- HANDOFF.md non esisteva → creato ora
- vos_check.sh gate (d): HANDOFF assente era OK durante sessione, ora presente per prossima
