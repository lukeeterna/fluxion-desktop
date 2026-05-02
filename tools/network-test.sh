#!/usr/bin/env bash
# =============================================================================
# FLUXION — Network Connectivity Self-Test (S184 α.4)
# =============================================================================
# Verifica che tutti gli endpoint richiesti da FLUXION siano raggiungibili
# attraverso il firewall/proxy aziendale del cliente PMI.
#
# Esegue probe HTTPS verso ogni servizio in 3 categorie:
#   - CRITICAL : se bloccati l'app NON parte / NON puo aggiornarsi
#   - IMPORTANT: se bloccati l'app funziona ma con feature ridotte
#   - OPTIONAL : Sara voice qualita massima (Edge-TTS) richiede internet
#
# Uso:
#   bash tools/network-test.sh           # report tutti gli endpoint
#   bash tools/network-test.sh --quiet   # solo summary finale
#   bash tools/network-test.sh --json    # output machine-readable
#
# Exit code:
#   0 = tutti i CRITICAL OK (app installabile e funzionante)
#   1 = uno o piu CRITICAL bloccati (whitelist firewall richiesta)
#   2 = solo warning IMPORTANT/OPTIONAL (app funziona, feature ridotte)
#
# Refs:
#   scripts/install/docs/NETWORK-REQUIREMENTS.md (whitelist FQDN PMI)
# =============================================================================

set -u

# ─── Config ─────────────────────────────────────────────────────────────────
CURL_TIMEOUT=5    # secondi per richiesta
USER_AGENT="FLUXION-NetworkTest/1.0 (S184)"

QUIET=0
JSON=0
for arg in "$@"; do
  case "$arg" in
    --quiet) QUIET=1 ;;
    --json)  JSON=1 ;;
    -h|--help)
      sed -n '2,25p' "$0"
      exit 0
      ;;
  esac
done

# ─── Color codes (TTY only) ─────────────────────────────────────────────────
if [[ -t 1 ]] && [[ "$JSON" -eq 0 ]]; then
  C_OK="\033[32m"; C_FAIL="\033[31m"; C_WARN="\033[33m"; C_RESET="\033[0m"
  C_BOLD="\033[1m"; C_DIM="\033[2m"
else
  C_OK=""; C_FAIL=""; C_WARN=""; C_RESET=""; C_BOLD=""; C_DIM=""
fi

# ─── Probe table ────────────────────────────────────────────────────────────
# Format: "category|name|url|expected_http_code|description"
# expected_http_code: 200, 401, or "*" (any 2xx/3xx/4xx is OK — only network failure = FAIL)
PROBES=(
  # CRITICAL (app non funziona/non si aggiorna)
  "CRITICAL|FLUXION License & LLM Proxy|https://fluxion-proxy.gianlucanewtech.workers.dev/health|200|Licenza Ed25519 + NLU Groq/Cerebras"
  "CRITICAL|GitHub Releases (auto-update)|https://api.github.com/repos/lukeeterna/fluxion-desktop/releases/latest|*|Auto-update FLUXION (Tauri updater)"
  "CRITICAL|GitHub Release Assets|https://objects.githubusercontent.com|*|Download MSI/DMG aggiornamenti"

  # IMPORTANT (app funziona ma feature ridotte)
  "IMPORTANT|FLUXION Diagnostic Report|https://fluxion-proxy.gianlucanewtech.workers.dev/api/v1/diagnostic-report|*|Pulsante Send-report supporto"
  "IMPORTANT|Sentry Crash Reporter (DE region)|https://o4511313987170304.ingest.de.sentry.io|*|Crash reporter desktop (privacy-safe)"
  "IMPORTANT|Stripe Checkout (acquisto)|https://api.stripe.com|*|Acquisto licenza dal sito (solo pre-purchase)"
  "IMPORTANT|FLUXION Landing|https://fluxion-landing.pages.dev|*|Sito vetrina + come-installare.html"

  # OPTIONAL (Sara voice qualita massima)
  "OPTIONAL|Edge-TTS Microsoft (Sara IT)|https://speech.platform.bing.com|*|Voce italiana Isabella Neural (qualita 9/10)"
  "OPTIONAL|Groq API direct|https://api.groq.com|*|Fallback diretto LLM (di norma via proxy)"
)

# ─── Probe runner ───────────────────────────────────────────────────────────
declare -i COUNT_CRIT_FAIL=0
declare -i COUNT_IMP_FAIL=0
declare -i COUNT_OPT_FAIL=0
declare -i COUNT_OK=0
RESULTS_JSON=()

probe_one() {
  local category="$1" name="$2" url="$3" expected="$4" desc="$5"
  local elapsed_ms http_code curl_exit curl_out time_s

  # Cross-platform timing via curl -w (BSD date doesn't support %N).
  # Output format: "<http_code>|<time_total_s>"
  curl_out=$(curl -fsS \
    --max-time "$CURL_TIMEOUT" \
    --user-agent "$USER_AGENT" \
    -o /dev/null \
    -w "%{http_code}|%{time_total}" \
    "$url" 2>/dev/null) || curl_exit=$?

  http_code="${curl_out%%|*}"
  time_s="${curl_out##*|}"
  # Convert seconds (e.g. "0.123") to int milliseconds via awk (POSIX)
  if [[ -n "$time_s" ]] && [[ "$time_s" != "$curl_out" ]]; then
    elapsed_ms=$(awk -v t="$time_s" 'BEGIN{printf "%d", t*1000}')
  else
    elapsed_ms=0
  fi

  local status="OK" reason=""
  if [[ -n "${curl_exit:-}" ]] && [[ "${curl_exit}" -ne 0 ]] && [[ -z "$http_code" || "$http_code" == "000" ]]; then
    status="FAIL"
    reason="connessione fallita (curl exit $curl_exit)"
  elif [[ "$expected" != "*" ]] && [[ "$http_code" != "$expected" ]]; then
    if [[ "$http_code" =~ ^[23] ]] || [[ "$http_code" =~ ^4 ]]; then
      # 4xx ancora prova che il path di rete e aperto
      status="OK"
      reason="HTTP $http_code (rete OK, endpoint specifico differisce)"
    else
      status="FAIL"
      reason="HTTP $http_code (atteso $expected)"
    fi
  fi

  if [[ "$status" == "OK" ]]; then
    COUNT_OK+=1
    if [[ "$QUIET" -eq 0 ]] && [[ "$JSON" -eq 0 ]]; then
      printf "  ${C_OK}OK${C_RESET}   [%-9s] %-42s → ${C_DIM}HTTP %s, %dms${C_RESET}\n" \
        "$category" "$name" "${http_code:-?}" "$elapsed_ms"
    fi
  else
    case "$category" in
      CRITICAL)  COUNT_CRIT_FAIL+=1 ;;
      IMPORTANT) COUNT_IMP_FAIL+=1 ;;
      OPTIONAL)  COUNT_OPT_FAIL+=1 ;;
    esac
    if [[ "$JSON" -eq 0 ]]; then
      printf "  ${C_FAIL}FAIL${C_RESET} [%-9s] %-42s → ${C_FAIL}%s${C_RESET}\n" \
        "$category" "$name" "$reason"
      printf "       ${C_DIM}URL: %s${C_RESET}\n" "$url"
      printf "       ${C_DIM}Scopo: %s${C_RESET}\n" "$desc"
    fi
  fi

  RESULTS_JSON+=("{\"category\":\"$category\",\"name\":\"$name\",\"url\":\"$url\",\"http_code\":\"${http_code:-}\",\"elapsed_ms\":$elapsed_ms,\"status\":\"$status\",\"reason\":\"$reason\"}")
}

# ─── Header ─────────────────────────────────────────────────────────────────
if [[ "$JSON" -eq 0 ]] && [[ "$QUIET" -eq 0 ]]; then
  echo ""
  echo "╔═══════════════════════════════════════════════════════════════╗"
  echo "║         FLUXION — Network Connectivity Self-Test              ║"
  echo "║         S184 α.4 — Per IT manager / proxy aziendale           ║"
  echo "╚═══════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Test ${#PROBES[@]} endpoint (timeout ${CURL_TIMEOUT}s/req)..."
  echo ""
fi

# ─── Run probes ─────────────────────────────────────────────────────────────
for probe in "${PROBES[@]}"; do
  IFS='|' read -r cat name url expected desc <<< "$probe"
  probe_one "$cat" "$name" "$url" "$expected" "$desc"
done

# ─── Local services (informational only) ─────────────────────────────────────
if [[ "$JSON" -eq 0 ]] && [[ "$QUIET" -eq 0 ]]; then
  echo ""
  echo "${C_BOLD}Servizi locali (informativi):${C_RESET}"
  if curl -fsS -m 1 http://127.0.0.1:3001/health -o /dev/null 2>/dev/null; then
    printf "  ${C_OK}OK${C_RESET}   HTTP Bridge Tauri (porta 3001) attivo\n"
  else
    printf "  ${C_DIM}--   HTTP Bridge Tauri (porta 3001) non attivo (normale se app chiusa)${C_RESET}\n"
  fi
  if curl -fsS -m 1 http://127.0.0.1:3002/health -o /dev/null 2>/dev/null; then
    printf "  ${C_OK}OK${C_RESET}   Voice Pipeline Sara (porta 3002) attivo\n"
  else
    printf "  ${C_DIM}--   Voice Pipeline Sara (porta 3002) non attivo (normale se Sara non avviata)${C_RESET}\n"
  fi
fi

# ─── Final summary ──────────────────────────────────────────────────────────
EXIT_CODE=0
if (( COUNT_CRIT_FAIL > 0 )); then
  EXIT_CODE=1
elif (( COUNT_IMP_FAIL > 0 )) || (( COUNT_OPT_FAIL > 0 )); then
  EXIT_CODE=2
fi

if [[ "$JSON" -eq 1 ]]; then
  # JSON output for CI / programmatic consumers
  printf '{"results":['
  printf '%s' "$(IFS=,; echo "${RESULTS_JSON[*]}")"
  printf '],"summary":{"ok":%d,"critical_fail":%d,"important_fail":%d,"optional_fail":%d,"exit_code":%d}}\n' \
    "$COUNT_OK" "$COUNT_CRIT_FAIL" "$COUNT_IMP_FAIL" "$COUNT_OPT_FAIL" "$EXIT_CODE"
else
  echo ""
  echo "════════════════════════════════════════════════════════════════"
  echo "${C_BOLD}Riepilogo:${C_RESET}"
  printf "  %s%d/%d OK%s    %sCRITICAL fail: %d%s    %sIMPORTANT fail: %d%s    %sOPTIONAL fail: %d%s\n" \
    "$C_OK" "$COUNT_OK" "${#PROBES[@]}" "$C_RESET" \
    "$([[ $COUNT_CRIT_FAIL -gt 0 ]] && echo "$C_FAIL" || echo "")" "$COUNT_CRIT_FAIL" "$C_RESET" \
    "$([[ $COUNT_IMP_FAIL -gt 0 ]] && echo "$C_WARN" || echo "")" "$COUNT_IMP_FAIL" "$C_RESET" \
    "$([[ $COUNT_OPT_FAIL -gt 0 ]] && echo "$C_WARN" || echo "")" "$COUNT_OPT_FAIL" "$C_RESET"
  echo ""

  case "$EXIT_CODE" in
    0)
      printf "  ${C_OK}${C_BOLD}✓ Tutti gli endpoint critici raggiungibili.${C_RESET}\n"
      printf "  FLUXION puo' essere installato e aggiornato senza problemi.\n"
      ;;
    1)
      printf "  ${C_FAIL}${C_BOLD}✗ Endpoint CRITICI bloccati dal firewall.${C_RESET}\n"
      printf "  FLUXION ${C_BOLD}NON funzionera'${C_RESET} senza whitelist degli endpoint sopra.\n"
      printf "  Inoltrare la lista all'IT manager: ${C_BOLD}scripts/install/docs/NETWORK-REQUIREMENTS.md${C_RESET}\n"
      ;;
    2)
      printf "  ${C_WARN}${C_BOLD}⚠ Endpoint CRITICI OK, ma alcuni IMPORTANT/OPTIONAL bloccati.${C_RESET}\n"
      printf "  FLUXION funzionera' con feature ridotte.\n"
      printf "  Vedi: ${C_BOLD}scripts/install/docs/NETWORK-REQUIREMENTS.md${C_RESET}\n"
      ;;
  esac
  echo ""
  printf "  Supporto: ${C_BOLD}fluxion.gestionale@gmail.com${C_RESET}\n"
  echo "════════════════════════════════════════════════════════════════"
  echo ""
fi

exit "$EXIT_CODE"
