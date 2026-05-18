# Prompt ripartenza — generato automaticamente

**Generato**: `2026-05-18T09:22:43Z`
**Sessione**: `fbeafe7e-a033-426e-9f52-12483419f4ed`
**Repo**: `/Volumes/MontereyT7/FLUXION` (branch `master`)
**Commit auto**: commit-failed
**Last commit**: `b2082c6 docs(S261): close VERDE-CON-ASTERISCO — S260 P4 code+tests+audit shipped, live verify pending GUI launch`

## Ultimi 5 commit
```
b2082c6 docs(S261): close VERDE-CON-ASTERISCO — S260 P4 code+tests+audit shipped, live verify pending GUI launch
caf2dd9 feat(S260 P4): encryption impostazioni_fatturazione PII — 8 cols (REGOLA #8)
7c8ac00 docs(S259): close VERDE — P3.a UX toast cross-entity + P3.b audit next target
93a0073 fix(S259 P3.a): toast.error su mutation catch — 4 pages, 10 sites (REGOLA #11)
b437c43 docs(S258): close VERDE-CON-ASTERISCO — S257 P2 suppliers PII LIVE VERIFY 6/6 PASS
```

## File modificati nell'ultimo commit
```
M	.claude/NEXT_SESSION_PROMPT.manual.md
```

## Ultimo prompt utente (estratto)
```
[{"tool_use_id":"toolu_01FFoc5sfG3DbdsaHQ5maV1t","type":"tool_result","content":"842b0b61ab437e565ac6c76e99b851db\n1122304 18 Mag 11:09","is_error":false}]
```

## Ultimi turni assistant
```
3. **STEP 5+6 (idempotency)**: quando riapri l'app (cmd-Q poi `cargo tauri dev` di nuovo) tieni il log e cercami `🔐 PII migration (impostazioni_fatturazione): already applied`
4. **STEP 8 (XML SDI)**: emetti una fattura test → controlla che l'XML output contenga `<Denominazione>Automation Business</Denominazione>` e `<IdCodice>02159940762</IdCodice>` in plaintext
Dimmi cosa vedi per ognuno (o "tutto ok" se 4/4 PASS) e chiudo VERDE.
```

## Come riprendere

1. Apri Claude Code da `/Volumes/MontereyT7/FLUXION`
2. Leggi questo file (auto-loaded? dipende da config progetto)
3. Continua dal punto indicato negli ultimi turni assistant sopra

Se `SESSION_DIRTY.md` esiste in questa stessa cartella, risolvi PRIMA i conflitti.
