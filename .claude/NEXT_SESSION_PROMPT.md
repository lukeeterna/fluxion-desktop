# Prompt ripartenza — generato automaticamente

**Generato**: `2026-05-12T15:19:20Z`
**Sessione**: `a773dc04-6b3b-495e-a212-8ac795d167ce`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `fdd6827 feat(S205): fix 4 P0 bugs PSTN stress test + WhatsApp auto-start`

## Ultimi 5 commit
```
fdd6827 feat(S205): fix 4 P0 bugs PSTN stress test + WhatsApp auto-start
5814d96 feat(S204): modo autonomo test RUNBOOK-P1 VoIP — MVP smoke validato
3a05068 docs(S203): RUNBOOK-P1 riscritto per flusso VoIP reale Ehiweb SIP
0dd07ad docs(S202): HANDOFF aggiornato — onboarding Ehiweb VoIP chiuso
1a6cb51 feat(S202): onboarding Ehiweb VoIP cliente — guida + CTA + doc CTO
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.md
M	.claude/session_state.md
M	voice-agent/main.py
M	voice-agent/src/_INDEX.md
M	voice-agent/src/booking_state_machine.py
M	voice-agent/src/name_corrector.py
M	voice-agent/src/orchestrator.py
```

## Ultimo prompt utente (estratto)
```
[{"tool_use_id":"toolu_018di8J5vpYtpgEhtKuC2XkN","type":"tool_result","content":"2-// Claude Code Statusline - GSD Edition\n3:// Shows: model | current task | directory | context usage\n4-\n5-const fs = require('fs');\n6-const path = require('path');\n--\n--\n18-    const session = data.session_id || '';\n19:    const remaining = data.context_window?.remaining_percentage;\n20-\n--\n20-\n21:    // Context Budget Gate bridge (Layer 3): /tmp/claude-ctx-{session_id}.json\n22:    // Written by .claud
```

## Ultimi turni assistant
```
REGOLA #7 hard: /context come ground truth, MAI statusline custom finché non fissata.
```
Apri sessione nuova, parti da qui.
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
