# SESSION DIRTY — chiusura senza commit auto

Sessione: `54731d66-8fc2-413e-9c40-1fe8753909b5`  Timestamp: `2026-05-16T19:24:08Z`

Motivo: `git diff --check` fail (whitespace errors o conflict markers).

## Output git diff --check
```
.claude/NEXT_SESSION_PROMPT.md:25: trailing whitespace.
+[{"tool_use_id":"toolu_01SXsHxc2MMbfNtzSW9UXuS6","type":"tool_result","content":"21:  MACRO_CATEGORIE,\n22:  MICRO_CATEGORIE,\n71:  // Step 7: Firma contratto\n113:      if (data.macro_categoria === 'medico' && art9Accepted) {\n136:  // Helper per icona macro categoria\n179:            {step === 1 && (\n184:                  <Label htmlFor=\"nome_attivita\" className=\"text-slate-300\">\n188:                    id=\"nome_attivita\"\n189:                    {...register('nome_attivita')}\n193:   
```

## Status
```
 M .claude/NEXT_SESSION_PROMPT.md
 m tools/VectCutAPI
?? .claude/SESSION_DIRTY.md
```

Risolvi manualmente, poi commit. Sessione successiva legge questo file.
