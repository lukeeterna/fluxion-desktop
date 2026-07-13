# VOS AUDIT — ACCEPT-EDITS REACTIVATION (2026-07-13)

Mandato: AUDIT-ACCEPTEDITS (taglia XS, read-only). Nessun edit a config/hook/settings.
Sessione: e33af056 (used_pct=36% dal json proprio). git HEAD al lancio: 7562a62b.

---

## A1 — TABELLA SORGENTI MODE (grep mode-key)

| File | Esiste | defaultMode / acceptEdits / bypassPermissions / autoApprove |
|------|--------|--------------------------------------------------------------|
| `~/.claude/settings.json` | sì | nessun match mode-key |
| `~/.claude/settings.local.json` | sì | nessun match mode-key |
| `~/.claude.json` | sì | **riga 639: `"tengu_quill_harbor": "acceptEdits"`** (unica occorrenza di "acceptEdits" nell'intero file, count=1) |
| `.claude/settings.json` (repo) | sì | nessun match mode-key; ha blocco `permissions` (:125 allow/:150 deny) — SENZA `defaultMode` |
| `.claude/settings.local.json` (repo) | sì | nessun match mode-key; ha blocco `permissions` (:2 allow) — SENZA `defaultMode` |

Contesto riga 639 (redatto): è dentro un blocco contiguo di flag `tengu_*`
(`tengu_cobalt_heron`, `tengu_silk_almanac`, `tengu_windows_credman`, `tengu_soft_slate_nudge`…)
= cache locale di feature-gate lato-server, NON una chiave di permesso impostata dall'utente.

**Nessun `permissions.defaultMode` in NESSUN file settings.**

## A2 — HOOK / PLUGIN SCAN

Hook registrati:
- `~/.claude/settings.json`: SessionStart / UserPromptSubmit / PreToolUse / PostToolUse (blacklist pip + root-rm protection). PreToolUse emette SOLO `permissionDecision: "deny"`. Nessun `allow`/`approve`.
- `.claude/settings.json` (repo): SessionStart `gsd-check-update.js`, statusline `gsd-statusline.cjs`, + UserPromptSubmit/PostToolUse/PreToolUse.
- `.claude/settings.local.json:904` (repo): 2° blocco hooks → SessionStart `session-start.sh`, UserPromptSubmit(voice/pipeline/Sara) `check-services.sh`.

Plugin: `~/.claude/plugins/` = blocklist.json + known_marketplaces.json + marketplaces (nessun plugin che tocca il modo). `~/.claude.json:238 "plugins": []`.

Grep `acceptEdits|approve|permissionDecision.*allow|defaultMode|setMode|bypassPermissions`:
- script hook (`.claude/hooks/`, `~/.claude/hooks/`): SOLO `global_violation_gate.py:13` che **legge** `permission_mode` come campo di input (commento) — non lo setta.
- comandi hook inline nei settings JSON: **nessun** allow/approve/acceptEdits.
- file gsd (agents/hooks/commands): **nessun** match.

**Nessun hook/plugin, statico o inline, attiva acceptEdits o auto-approva Edit/Write a runtime.**

## A3 — VERDETTO (una riga)

**(iii) NESSUNA evidenza statica** impone acceptEdits: zero `permissions.defaultMode`, zero hook/plugin che setta il modo. L'unico artefatto statico che contiene letteralmente "acceptEdits" è `~/.claude.json:639 tengu_quill_harbor` — **valore di feature-gate in cache lato-server, non config utente**. → Indiziato = **meccanismo di sessione/UI del client** (stato di modo ricordato dal runtime, o il gate `tengu_quill_harbor` che influenza il modo di default). La decisione la dà l'**osservazione live del founder**: *quando* si riaccende (al boot / alla 1ª richiesta di edit / dopo comando gsd) è il reperto mancante — nessuna config lo forza in modo deterministico.

## A4 — PROPOSTA DI FIX (solo testuale — esecuzione = founder)

Non c'è una riga di config "colpevole" da rimuovere (non esiste `defaultMode`). Due leve, in ordine:

1. **Rendere il modo di boot DETERMINISTICO** (neutralizza sia la memoria di sessione sia il gate):
   - File: `~/.claude/settings.json` → aggiungere dentro `permissions`:
     `"defaultMode": "default"` (o `"plan"` se vuoi partire sempre in sola-lettura).
   - Rischio: basso — forza SOLO il modo di avvio; non tocca le allow/deny esistenti.
   - Rollback: rimuovere la chiave `defaultMode`.
   - Nota: se dopo questo il modo si riaccende ancora → conferma che è il runtime UI del client, non la config → il reperto "quando" resta l'unica via.

2. **Sonda diagnostica sul gate** (facoltativa, non distruttiva):
   - `~/.claude.json:639 tengu_quill_harbor: "acceptEdits"` → è cache di gate; il client può riscriverla al prossimo refresh. Cambiarla a mano NON è affidabile (verrebbe sovrascritta) → NON raccomandato come fix, solo come osservazione.

**Fix raccomandato = #1** (defaultMode esplicito). Decisione ed esecuzione: founder.

---

VERDETTO | (iii) nessuna config statica forza acceptEdits; unico indiziato statico `~/.claude.json:639 tengu_quill_harbor="acceptEdits"` (gate cache) → meccanismo di sessione, osservazione live decide.
EVIDENZE | `~/.claude.json:639`; nessun `defaultMode` nei 5 settings; PreToolUse solo `deny`; `global_violation_gate.py:13` legge-non-setta.
PROPOSTA | aggiungere `"defaultMode":"default"` in `~/.claude/settings.json` permissions (rischio basso, rollback = rimuovi chiave).
CONTEXT % | 36% (json e33af056).
