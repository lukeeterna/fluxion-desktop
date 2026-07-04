# REPORT — T-SARA-PYRTP-SPIKE (2026-07-04)

> Report di sessione. L'inventario dello stack è in `STACK_SARA.md` (deliverable A) e NON è
> duplicato qui. Questo report copre esecuzione, discordanze e verdetto dello spike (B).

## ESITO SINTETICO
- **(A) Inventario stack Sara** → FATTO. `STACK_SARA.md` committato (`2135f72`).
- **(B) Spike pyVoIP** → NON eseguito (stop pianificato per GESTIONE CONTEXT del mandato).
  Nessun verdetto VERDE/ROSSO sullo spike: rimandato a sessione fresca con margine.

## COSA È STATO FATTO (read-only, baseline mai toccata)
1. FASE 0.1 — `/api/voice/voip/status` = `registered:true, reg_status:200`, engine pjsua2;
   `/health` v2.1.0. PID Sara = 54563, cmd `python3 main.py --port 3002`, cwd
   `/Volumes/MacSSD - Dati/fluxion/voice-agent`. Piano restore annotato in STACK_SARA.md.
2. FASE 0.2 — SIP locale su 5080 (env `VOIP_LOCAL_PORT` unset→default, voip_pjsua2.py:193),
   forwardato dal router. Nessun range RTP statico: RTP effimero via ICE/STUN (:952-954) →
   ritorno audio per **latching simmetrico** del provider. Decide la strategia dello spike:
   bind RTP + **TX beep-first** per aprire il binding NAT e far latchare il ritorno.
3. FASE 0-BIS — inventario completo (7 punti schema) → STACK_SARA.md.

## DISCORDANZE (vince il disco)
- **STT**: health runtime riporta `GroqSTT`, ma stt.py/requirements dichiarano `faster-whisper`
  primary + Groq fallback (stt.py:4-7). Runtime attivo = Groq cloud.
- **local_port**: dataclass field default 5090 (voip_pjsua2.py:176) vs valore operativo env
  default 5080 (:193). Operativo = 5080 → premessa del mandato confermata.
- **budget hook**: hook VOS ha riportato 65→79% dopo poche tool-call = falso-positivo RAW noto
  (REGOLA #27/S351). Stop deciso per l'ordine ESPLICITO del mandato sul context, non per l'hook.

## STATO LASCIATO
- Sara UP PID 54563, `reg_status:200`, DB non toccato. Tutto read-only → nessun restore
  necessario (baseline intatta). `.venv-spike` NON creato, nessun pip install eseguito.

## NEXT (sessione fresca)
- FASE 0-TER: pyVoIP ultima stabile 1.6.x su PyPI (verificare deps = zero binarie).
- FASE 1: `voice-agent/.venv-spike` (gitignore) + `voice-agent/tools/pyrtp_spike.py`
  (REGISTER sip.vivavox.it da .env, bind SIP 5080, RTP coerente, answer→beep 2s→loop eco,
  log rms/byte RX + cattura WAV, guardia alarm, hangup 120s). yes/no NATIVO founder prima di
  fermare Sara (kill PID 54563) per liberare account+porta.
- FASE 2-3: test live founder (chiama 0972536918, beep+eco, ~20s) → verdetto VERDE/ROSSO.
