# Prompt ripartenza — generato automaticamente

**Generato**: `2026-06-03T14:33:48Z`
**Sessione**: `1e3a6388-2078-4f9c-b50c-54b1317cf00f`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: committed: c017103
**Last commit**: `c017103 auto-close session 1e3a6388-2078-4f9c-b50c-54b1317cf00f @ 2026-06-03T14:33:48Z`

## Ultimi 5 commit
```
c017103 auto-close session 1e3a6388-2078-4f9c-b50c-54b1317cf00f @ 2026-06-03T14:33:48Z
d6b2314 S333 close: Sara Layer 1 testo VERDE+esteso (50 OK/3 WARN/0 FAIL su 12 verticali). 7 falsi-WARN S332 risolti. Carry S334: fix SIP reg 408->200 + Layer 2 harness audio pjsua2.
4f1685c S333 Step1: Layer 1 test fix+ext — 50 OK/3 WARN/0 FAIL su 12 verticali
8543d97 S332 close: Sara Layer 1 testo VERDE (22 OK/7 WARN/0 FAIL, 0 difetti bloccanti). 7 WARN = falsi negativi del test (registering_phone/disambiguating sono flussi corretti). Carry S333: fix+estensione test Layer 1 + harness audio Layer 2.
c9b25dc S331 close: S332 = Sara live-test confermato da Luke (custom domain demoto a task go-live)
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.md
```

## Ultimo prompt utente (estratto)
```
spegami brevissimamente in cosa consisterà il prossimo turno
```

## Ultimi turni assistant
```
1. **Fix SIP** — la registrazione SIP è caduta (`reg_status:408`, era `200`). Diagnosi + ripristino a `200` (probabile credenziali EHIWEB/vivavox o server irraggiungibile). Prerequisito bloccante.
2. **Layer 2 audio** — il vero gate vendita: harness `sara_audio_harness.py` via pjsua2 che chiama Sara con audio reale (WAV PCM16 8kHz mono), io guido la conversazione via TTS in autonomia. Test golden-path per verticale finché Sara "soddisfa pienamente il cliente" via voce.
Finora abbiamo solo il testo verde; il Layer 2 verifica che STT + voce reggano end-to-end.
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
