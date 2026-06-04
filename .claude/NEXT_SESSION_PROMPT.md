# Prompt ripartenza — generato automaticamente

**Generato**: `2026-06-04T11:14:27Z`
**Sessione**: `c3c98f94-55ac-4ade-b90a-2b3560545abe`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: DIRTY (vedi /Volumes/MontereyT7/FLUXION/.claude/SESSION_DIRTY.md)
**Last commit**: `2996915 S337 close: pjsip downgrade 2.15.1 FATTO ma ipotesi root cause FALSIFICATA. Sara crasha identico su INVITE loopback — 2.15.1 ha la STESSA op-queue async di 2.16-dev. Bug STRUTTURALE version-independent (port-add da thread onCallMediaState, group-lock unset su _pjsua2_thread). REGOLA #1c: 2 cicli falliti (S336 fix Python, S337 downgrade) → S338 = decisione architetturale (opt1 libRegisterThread / opt2 Asterisk ARI), NO 3° fix autonomo.`

## Ultimi 5 commit
```
2996915 S337 close: pjsip downgrade 2.15.1 FATTO ma ipotesi root cause FALSIFICATA. Sara crasha identico su INVITE loopback — 2.15.1 ha la STESSA op-queue async di 2.16-dev. Bug STRUTTURALE version-independent (port-add da thread onCallMediaState, group-lock unset su _pjsua2_thread). REGOLA #1c: 2 cicli falliti (S336 fix Python, S337 downgrade) → S338 = decisione architetturale (opt1 libRegisterThread / opt2 Asterisk ARI), NO 3° fix autonomo.
b85eae7 S336 close: Sara Layer 2 ROOT CAUSE = pjsip 2.16-dev op-queue group-lock bug. INVITE diretto OK, ma crash conference-port commit NON Python-fixable. NEXT = downgrade pjsip 2.15.1 (runbook S244 B1).
196b491 S335: Sara Layer 2 harness scaffold + FINDING sblocco INVITE diretto (bypassa EHIWEB)
e85bc50 S334 close: SIP 403 = registrazione incagliata lato EHIWEB (evidenza OPTIONS qualify). Mail supporto inviata. STATO = WAIT risposta EHIWEB.
5d3327a S334: root cause SIP 403 = binding residuo desync lato EHIWEB (evidenza OPTIONS qualify). Ammo escalation.
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.manual.md
M	.claude/NEXT_SESSION_PROMPT.md
M	.claude/SESSION_DIRTY.md
M	.claude/agent-memory/voice-engineer/project_sip_loopback_crash_pjsip216.md
```

## Ultimo prompt utente (estratto)
```
VOS COSA DICE QUANDO INCONTRI PROBLEMI DI QUESTO TIPO ?
```

## Ultimi turni assistant
```
## La domanda che VOS mi obbliga a farti
Anti-avvitamento + zero-cost: prima di scegliere *come* far funzionare pjsua2, VOS chiede se **pjsua2 è la strada giusta**. 3 sessioni su un bug di threading della conference bridge sono il segnale. Asterisk ARI (Sara = solo cervello, media/SIP esterni) **elimina la classe di bug**, non la aggira.
**Vuoi che scriva ora il prompt per il giudice esterno** (root cause corretta + le 2 opzioni + dati), così S338 parte da un verdetto e non da un terzo tentativo alla cieca? È un'azione da CLOSING (un file, ~5 min), compatibile col budget context al 69%.
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
