<!-- VOS-CANONICAL-HANDOFF v1 -->
# HANDOFF [FLUXION] (fonte unica di sessione)

## STATO CORRENTE

### Sessione 2026-06-30 (d) — Proliferazione handoff CHIUSA (VERDE)
- **Cosa**: gitignorati gli effimeri rigenerati dagli hook, sganciati i legacy tracciati (solo untracking, file su disco intatti), allineato `vos-close.sh` perché non li ri-aggiunga. Nessun hook globale toccato, nessun deploy.
- **Commit**: `7faf83c chore(handoff): gitignore effimeri + untrack legacy + vos-close non li ri-aggiunge` + `45e9ade chore(handoff): allarga gitignore a NEXT_SESSION_PROMPT_* underscore + cache, untrack 6 superstiti` (fonte: `git log --oneline -3`). Entrambi su `origin/master` (push OK, bypass branch-rule "CI Pass" via token).
- **[D5] RISOLTO**: 17 legacy `.claude/NEXT_SESSION_PROMPT.*`/`HANDOFF_CURRENT.md`/cache untracked via `git rm --cached` (file fisici verificati presenti, `ls -la`). Done-condition HARD: `git ls-files | grep -iE 'handoff|next_session' | grep -vE '^HANDOFF\.md$|\.py$' | wc -l` = **0** dopo RUN 1 e RUN 2 di `vos-close.sh`; `HANDOFF.md` canonico ancora tracciato (`git ls-files | grep ^HANDOFF\.md$` = 1 riga).
- **[D5-bis] RISOLTO**: i 2 effimeri ora gitignored (`git check-ignore` exit=0); `HANDOFF.md` canonico root NON ignorato (exit=1). Blocco `.gitignore` marker-based `# VOS-HANDOFF-IGNORE` righe ~115-126, glob `NEXT_SESSION_PROMPT.*` + `NEXT_SESSION_PROMPT_*` (underscore) + `cache/NEXT_SESSION_PROMPT*` + `cache/HANDOFF_*`.
- **[D6] confermato chiuso + esteso**: `scripts/vos-close.sh` non solo non apre TextEdit, ma ora NON stub-izza (rimosso loop lossy che riscriveva gli effimeri) e NON fa `git add` dei `.claude/*`; committa SOLO `HANDOFF.md CLAUDE.md scripts/vos-close.sh` (fonte: `git diff` mostrato in sessione; `bash -n` OK; 2 run = no-op).
- **Buco catturato dalla done-condition**: un hook `git add -A` (auto-close PostToolUse) aveva ri-tracciato 6 varianti underscore/cache non coperte dal glob col-punto → risolto allargando `.gitignore` (commit `45e9ade`).

### Discordanze sessione (contratto)
1. **STEP 1** — `check-ignore` plain dava exit=1 sui due effimeri (premessa: exit=0). Causa: git non applica `.gitignore` a file già tracciati; con `--no-index` le regole matchavano. Benigna, risolta dopo STEP 2. Gate STOP (canonico ignorato) NON scattato.
2. **STEP 5** — premessa "le regole date coprono tutti gli effimeri" falsa: 6 varianti `NEXT_SESSION_PROMPT_<suffix>.md` + cache ri-tracciabili. Corretta allargando i glob.

## DISCORDANZE / CONTRADDIZIONI APERTE
1. **[D6-bis] Footgun TextEdit nell'hook globale NON rimosso**: `~/.claude/hooks/session_reports_combine.sh:60` ha ancora `open -a TextEdit "$OUT"` (apre il breadcrumb effimero `HANDOFF_CURRENT.md`). Fuori da questo repo + hook globale condiviso 3 progetti → decisione infra pendente per il giudice/founder, NON azionata (vincolo: non modificare hook globali).
2. **Fonte della proliferazione = hook globali**: `global_session_end.sh` (Stop) scrive `.claude/NEXT_SESSION_PROMPT.md` + auto-commit; `session_reports_combine.sh` (SessionEnd) scrive `.claude/HANDOFF_CURRENT.md`. Ora neutralizzati per il tracking via `.gitignore` (barriera duratura), ma continueranno a rigenerare i file su disco (innocuo: ignorati).

## PROSSIMA DIRETTIVA OPERATIVA
Decisione infra pendente per giudice/founder: se rimuovere il footgun `open -a TextEdit` da `session_reports_combine.sh:60` [D6-bis] — tocca hook GLOBALE condiviso (ARGOS/FLUXION/Guardian), impatto 3 progetti, da valutare prima di agire. Il tracking-side della proliferazione è chiuso e idempotente; nessun altro intervento richiesto su questo repo.

(Carry pre-esistente, se il founder lo riprende: T1a SEO — ripristino working tree `fluxion-seo` in ~/Documents NON /tmp + sezione '3 passi' + quantifica copy #4, prova su pagina live.)
