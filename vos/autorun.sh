#!/usr/bin/env bash
# T-AUTORUN v1 (#34v) — runner headless PLAYBOOK-1
# Ogni STEP = processo CC (`claude -p`) FRESCO. STOP-ON-RED (rosso o >30min).
# Uso:
#   vos/autorun.sh            # catena completa 1->2->3->4 (stop-on-red)
#   vos/autorun.sh 1          # solo STEP 1 (dry-run mandato F4)
#   vos/autorun.sh 2 4        # sottoinsieme di step
set -uo pipefail

# --- risoluzione repo root (indipendente da cwd) -----------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO" || { echo "FATAL: repo non raggiungibile"; exit 2; }

PLAYBOOK="$REPO/vos/PLAYBOOK-1.md"
[ -f "$PLAYBOOK" ] || { echo "FATAL: manca $PLAYBOOK"; exit 2; }

DATE="$(date +%Y%m%d)"
RUNDIR="$REPO/vos/runs/$DATE"
mkdir -p "$RUNDIR"

STEP_TIMEOUT="${STEP_TIMEOUT:-1800}"   # 30 min per step
BUDGET_USD="${BUDGET_USD:-15}"         # repo carica CLAUDE.md+MEMORY.md+rules → input grande
STEP_MODEL="${STEP_MODEL:-sonnet}"     # implementazione = Sonnet (model hierarchy CLAUDE.md); NON Opus
CLAUDE_BIN="${CLAUDE_BIN:-claude}"

# slug per numero step
step_slug() { case "$1" in
  1) echo "1-FIX-OBS";; 2) echo "2-FIX-A";; 3) echo "3-FIX-C";; 4) echo "4-SUITE";;
  *) echo "";; esac; }

# --- regole comuni (verbatim dal PLAYBOOK, anteposte a ogni prompt) ----------
read -r -d '' COMMON_RULES <<'RULES' || true
REGOLE COMUNI (vincolanti, non derogabili):
- porcelain carve-out: l'unico residuo tollerato non-tuo e' "M tools/VectCutAPI". NON toccarlo.
- add SOLO i path esplicitamente dichiarati da questo step. MAI git add -A. (il commit lo fa il runner, non tu)
- niente telefono / niente trunk EHIWEB / niente chiamate reali.
- niente deploy o riavvii su :3002 di produzione. Rig high-port only.
- MAI toccare tools/VectCutAPI, .claude/SARA_STRESS_TEST_PATTERNS.md, cache calls/ in scrittura.
- MAI --dangerously-skip-permissions o equivalenti totali. MAI history rewrite / filter-repo.
- SEGRETI: solo nomi, mai valori.
- report con PROVE (righe di log reali) e "ND" dove il log non arriva. MAI stime.
- niente cat integrali di file grandi.
OUTPUT OBBLIGATORIO: scrivi il report dello step in <STEPDIR>/report.md e CHIUDI SEMPRE lo stdout
con UNA riga esatta, come ULTIMA riga: "VERDETTO: VERDE" oppure "VERDETTO: ROSSO <motivo>".
Il runner decide leggendo l'ULTIMA riga "VERDETTO:"; se manca, lo step e' ROSSO.
RULES

# --- estrai la sezione capitolato di uno step dal PLAYBOOK -------------------
extract_capitolato() {  # $1 = numero step
  awk -v n="$1" '
    $0 ~ "^## STEP " n " " { grab=1 }
    grab && /^---[[:space:]]*$/ { exit }
    grab && $0 ~ "^## STEP " && $0 !~ "^## STEP " n " " && seen { exit }
    grab { print; seen=1 }
  ' "$PLAYBOOK"
}

# --- estrai i path dichiarati (add) dello step ------------------------------
extract_paths() {  # $1 = numero step -> stampa i token path (senza virgole/backtick)
  extract_capitolato "$1" \
    | grep -m1 'PATH consentiti' \
    | sed -E 's/.*\(add\):\*\*//; s/`//g; s/,/ /g' \
    | tr -s ' ' '\n' | sed '/^$/d'
}

# --- watchdog portabile Big Sur (no coreutils `timeout`) --------------------
run_with_timeout() {  # $1=limit_s $2=stdout $3=stderr ; resto = comando
  local limit="$1" out="$2" err="$3"; shift 3
  "$@" >"$out" 2>"$err" &
  local pid=$!
  local waited=0
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$waited" -ge "$limit" ]; then
      kill -TERM "$pid" 2>/dev/null; sleep 3; kill -KILL "$pid" 2>/dev/null
      wait "$pid" 2>/dev/null
      return 124
    fi
    sleep 5; waited=$((waited+5))
  done
  wait "$pid"; return $?
}

# --- esecuzione di un singolo step ------------------------------------------
declare -a RESULTS=()
run_step() {  # $1 = numero step ; ritorna 0=verde 1=rosso
  local n="$1"
  local slug; slug="$(step_slug "$n")"
  [ -n "$slug" ] || { echo "SKIP: step $n sconosciuto"; return 1; }
  local STEPDIR="$RUNDIR/$slug"
  mkdir -p "$STEPDIR"

  local capitolato; capitolato="$(extract_capitolato "$n")"
  local -a paths; while IFS= read -r p; do [ -n "$p" ] && paths+=("$p"); done < <(extract_paths "$n")

  local prompt="${COMMON_RULES//<STEPDIR>/$STEPDIR}

STEP DA ESEGUIRE (capitolato verbatim dal PLAYBOOK-1):
$capitolato

CWD = $REPO . STEPDIR = $STEPDIR ."

  echo "=== [$slug] avvio $(date -u +%FT%TZ) (timeout ${STEP_TIMEOUT}s) ==="
  run_with_timeout "$STEP_TIMEOUT" "$STEPDIR/stdout.log" "$STEPDIR/stderr.log" \
    "$CLAUDE_BIN" -p "$prompt" \
      --model "$STEP_MODEL" \
      --allowedTools "Read Edit Write Bash" \
      --permission-mode default \
      --max-budget-usd "$BUDGET_USD" \
      --no-session-persistence \
      --output-format text
  local rc=$?

  # verdetto: il runner legge l'ULTIMA riga "VERDETTO: ..." stampata dallo step
  local verdict="ROSSO"
  if [ "$rc" -eq 124 ]; then
    verdict="ROSSO timeout>${STEP_TIMEOUT}s"
  else
    local last; last="$(grep '^VERDETTO: ' "$STEPDIR/stdout.log" 2>/dev/null | tail -n1)"
    if [ -z "$last" ]; then
      verdict="ROSSO (nessun verdetto esplicito, rc=$rc)"
    elif printf '%s' "$last" | grep -q '^VERDETTO: VERDE'; then
      verdict="VERDE"
    else
      verdict="${last#VERDETTO: }"   # es. "ROSSO <motivo>"
    fi
  fi
  echo "=== [$slug] verdetto: $verdict ==="

  # commit dei soli path dichiarati + STEPDIR
  local -a addlist=("$STEPDIR")
  for p in "${paths[@]}"; do [ -e "$REPO/$p" ] && addlist+=("$REPO/$p"); done
  git add -- "${addlist[@]}" 2>/dev/null
  # carve-out: non deve MAI entrare VectCutAPI
  git reset -q -- "$REPO/tools/VectCutAPI" 2>/dev/null || true
  local esito_short; esito_short="$(echo "$verdict" | cut -c1-60)"
  if ! git diff --cached --quiet; then
    git commit -q -m "auto($slug/#34v): $esito_short" && git push -q origin master \
      && echo "  commit+push OK" || echo "  WARN commit/push fallito"
  else
    echo "  (nessuna modifica da committare)"
  fi

  local commit_sha; commit_sha="$(git rev-parse --short HEAD)"
  RESULTS+=("$slug|$verdict|$commit_sha")
  [ "$verdict" = "VERDE" ] && return 0 || return 1
}

# --- report finale ----------------------------------------------------------
write_report() {  # $1 = stato_catena
  local report="$RUNDIR/RUN_REPORT.md"
  {
    echo "# RUN_REPORT — T-AUTORUN v1 (#34v) — $DATE"
    echo
    echo "Stato catena: **$1**  ·  generato $(date -u +%FT%TZ)"
    echo
    echo "| Step | Verdetto | Commit |"
    echo "|------|----------|--------|"
    for r in "${RESULTS[@]}"; do
      IFS='|' read -r s v c <<< "$r"; echo "| $s | $v | $c |"
    done
    echo
    echo "## Discordanze"
    echo "- porcelain a fine catena:"
    echo '```'
    git status --porcelain
    echo '```'
    echo "- HEAD: $(git rev-parse --short HEAD) ; origin/master: $(git rev-parse --short origin/master 2>/dev/null || echo ND)"
  } > "$report"
  git add -- "$report"
  git commit -q -m "auto(RUN_REPORT/#34v): $1" && git push -q origin master || true
  echo "RUN_REPORT: $report"
}

# --- main -------------------------------------------------------------------
STEPS=("$@")
[ ${#STEPS[@]} -eq 0 ] && STEPS=(1 2 3 4)

chain_state="COMPLETA"
for n in "${STEPS[@]}"; do
  if ! run_step "$n"; then
    chain_state="STOP-ON-RED@step$n"
    echo ">>> STOP-ON-RED su step $n"
    break
  fi
done

write_report "$chain_state"
[ "$chain_state" = "COMPLETA" ] && exit 0 || exit 1
