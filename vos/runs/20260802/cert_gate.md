# T-CERT-GATE/#47 — Referto allineamento runtime
> Data: 2026-08-02 | Corsia: MACCHINA | Commit base: c143dd99

---

## GATE-0
- HEAD MacBook: c143dd99 = origin/master ✅
- vos_check.sh: 7/7 PASS (rimosso NEXT_SESSION_PROMPT.md stale da sessione precedente) ✅

## F1 — Allineamento iMac
- HEAD PRIMA: 2c25742d
- HEAD DOPO: c143dd99 (= origin/master)
- Operazione: git stash push (booking_state_machine.py + vos/runs/20260731/stress_verticali_v2*.md) → git merge --ff-only origin/master
- booking_state_machine.py nello stash: IDENTICO a master (diff vuoto) → modifiche già contenute in master, stash lasciato senza riapplicare
- vos/runs/20260731 nello stash: differiscono da master (diff non vuoto) → lasciato nello stash
- Carve-out (src-tauri/fluxion.db*): non modificati dai commit in pull, rimasti intatti

## F2 — Tabella SHA256

| File | SHA256 iMac | SHA256 MacBook/master | Match |
|------|------------|----------------------|-------|
| voice-agent/src/booking_state_machine.py | d64a3934c265c7472da26874db9a59b7b32166997077a75d3262ab4951995afd | d64a3934c265c7472da26874db9a59b7b32166997077a75d3262ab4951995afd | ✅ |
| voice-agent/src/orchestrator.py | 1a632b3204f943c1125c0a9fcd9acfedfcd08e3f618f25dc42b90fdddb0ba7a0 | 1a632b3204f943c1125c0a9fcd9acfedfcd08e3f618f25dc42b90fdddb0ba7a0 | ✅ |
| voice-agent/src/escalation_manager.py | ac8b0a5134df28eb89754dc3da2ed6698b68a1664a85184f6849198de9ca3266 | ac8b0a5134df28eb89754dc3da2ed6698b68a1664a85184f6849198de9ca3266 | ✅ |
| voice-agent/src/voip_goengine.py | cbcf00d5109d31515a89f5d51c319fc229fb6449175bcd328379ab1889a857c8 | cbcf00d5109d31515a89f5d51c319fc229fb6449175bcd328379ab1889a857c8 | ✅ |

Tutti e 4 i file coincidono per SHA256. Nessuna differenza.

## F3 — Gate permanente
- `bin/vos_check.sh`: aggiunto controllo g) che raggiunge iMac via SSH se :3002 è up e verifica HEAD==origin/master + voice-agent/ pulito; fallisce con "runtime non verificabile" se SSH irraggiungibile o :3002 down
- `docs/judge/PROTOCOLLO.md`: aggiunta regola 30 — "Nessuna misura e nessuna certificazione è valida se il repo della macchina runtime non coincide con origin/master. L'età del processo non basta."

## F4 — Riavvio :3002
- Processo PID 3057 (avviato 18:14 su codice 2c25742d) terminato
- Nuovo processo PID 41118 avviato con VOICE_ENGINE=go SARA_TEST_CAPTURE=1
- Verifica ps: PID=41118, VOICE_ENGINE=go, SARA_TEST_CAPTURE=1 ✅
- Log: `GoEngine start: registered=True reg_status=200` ✅
- /health: `{"status": "ok", "service": "FLUXION Voice Agent Enterprise"}` ✅

## F5 — CERT-21-COPIONE.md
- Rimosso il blocco bash con ssh, utente (gianlucadistasi) e percorso chiave (~/.ssh/id_ed25519)
- Sostituito con: "Raccolta: la esegue CC nell'unità T-CERT-RACCOLTA subito dopo la chiamata."

## F6 — Residui DB
- COUNT_PRIMA: 0 record con id c57e6ade o 9636bbc7 in src-tauri/fluxion.db (15 tot) e voice-agent/fluxion.db (0 appuntamenti)
- COUNT_DOPO: invariato (già assenti — nessuna DELETE necessaria)
- Perché T-VOS-RUNNER li dichiarò inesistenti: erano genuinamente assenti al momento del controllo. Il booking 9636bbc7 fu creato da T-BOOKING-FIX2 nel DB voice-agent attivo (salone.db); c57e6ade era un residuo di stress test. Entrambi erano stati rimossi (o non persistiti sul DB corrente) prima che T-VOS-RUNNER girasse. STATE.md di T-CERT-PREP li elencava da referti storici senza riverificare il DB live — questo era il falso: non T-VOS-RUNNER.

---

PRONTI A CHIAMARE: SI
