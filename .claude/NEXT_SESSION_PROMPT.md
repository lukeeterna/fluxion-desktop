# Prompt ripartenza — generato automaticamente

**Generato**: `2026-05-20T16:23:28Z`
**Sessione**: `d850783d-0aa1-488b-88f4-73544bbce99c`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `ac4b03c docs(S271): close VERDE — refactor internal_* + 4 cargo test PASS + handoff S272 BUG-FATT-7 prevention`

## Ultimi 5 commit
```
ac4b03c docs(S271): close VERDE — refactor internal_* + 4 cargo test PASS + handoff S272 BUG-FATT-7 prevention
bc098b3 fix(S271): test common helper applica migrations stile prod (error swallow)
e0321bf refactor(S271): extract internal_* fatture functions + integration tests BUG-FATT-3/4/6
bcf75db auto-close session f3915fec-a3b9-4c73-a737-89c2427086e1 @ 2026-05-20T15:10:21Z
fe541df docs(S270): close VERDE + BUG-FATT-7 hotfix runtime + MCP cli-printing-press reference
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.manual.md
```

## Ultimo prompt utente (estratto)
```
      .claude/rules/context-budget-gate.md.  
```

## Ultimi turni assistant
```
- **Cargo test FAIL** → CLOSE VERDE-CON-ASTERISCO, fix in S273 con stack trace preciso (no re-design)
Il fallback A che proponi salverebbe context ma sprecherebbe il lavoro già scritto e correttamente landed. Cargo test è ~10s su iMac, output piccolo (PASS/FAIL + linee fallite). Costo context minimo.
**Procedo?** (sì/no — se sì: rsync + cargo test, max 3 turni a chiusura)
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
