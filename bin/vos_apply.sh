#!/usr/bin/env bash
# vos_apply.sh — Esecutore VOS. Argomento: path di un piano prodotto da vos_plan.sh.
# Non ri-deriva niente: esegue il piano ricevuto, in quell'ordine.
#
# PROTOCOLLO §27: il runner automatizza l'esecuzione, mai l'autorizzazione.
# PROTOCOLLO §25: controlla vos/STOP prima di ogni passo.
# PROTOCOLLO F6:  verifica CHIAVE in LEDGER.md prima di ogni unità.
#
# IMPORTANTE: in T-VOS-RUNNER/#45v3 questo script è CREATO MA NON ESEGUITO.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
STOP_FILE="$REPO_ROOT/vos/STOP"
LEDGER_FILE="$REPO_ROOT/docs/judge/LEDGER.md"
PLAN_FILE="${1:-}"

# — Argomento obbligatorio —
if [ -z "$PLAN_FILE" ]; then
  echo "Uso: $0 <path-piano>" >&2
  echo "     Il piano deve essere prodotto da vos_plan.sh" >&2
  exit 1
fi

if [ ! -f "$PLAN_FILE" ]; then
  echo "ERRORE: piano non trovato: $PLAN_FILE" >&2
  exit 1
fi

# — Kill switch (PROTOCOLLO 25) — controllo PRE-AVVIO —
if [ -f "$STOP_FILE" ]; then
  echo "STOP: $STOP_FILE esiste. Esecuzione bloccata." >&2
  exit 1
fi

echo "=== vos_apply.sh: avvio esecuzione piano ==="
echo "Piano: $PLAN_FILE"

# — Verifica sha256 del piano —
DECLARED_SHA=$(grep '^sha256: ' "$PLAN_FILE" | awk '{print $2}')
if [ -z "$DECLARED_SHA" ]; then
  echo "ERRORE: nessun sha256 nel piano." >&2
  exit 1
fi

# Calcola sha256 del corpo del piano (riga PIANO_...)
PLAN_BODY=$(grep '^sha256: ' "$PLAN_FILE" | sed 's/^sha256: //')
COMPUTED_SHA=$(printf '%s' "$(grep '^sha256: ' "$PLAN_FILE" | awk '{print $2}')" | shasum -a 256 | awk '{print $1}' || echo "")
# Nota: la verifica sha256 è sul CORPO derivato, non sul file intero (vedi vos_plan.sh)
# Per verifica robusta: confronta DECLARED_SHA con sha256 della body string nel piano
PLAN_TIMESTAMP=$(grep '^# Piano VOS — ' "$PLAN_FILE" | awk '{print $NF}')
PLAN_UNITS=$(grep '^Unità selezionate: ' "$PLAN_FILE" | grep -oE '[0-9]+' | head -1)
PLAN_HEAD=$(grep '^HEAD al momento della pianificazione: ' "$PLAN_FILE" | awk '{print $NF}')

RECOMPUTED_BODY="PIANO_${PLAN_TIMESTAMP}_UNITS_${PLAN_UNITS}_HEAD_${PLAN_HEAD}"
RECOMPUTED_SHA=$(printf '%s' "$RECOMPUTED_BODY" | shasum -a 256 | awk '{print $1}')

if [ "$DECLARED_SHA" != "$RECOMPUTED_SHA" ]; then
  echo "ERRORE: sha256 del piano non coincide." >&2
  echo "  Dichiarato: $DECLARED_SHA" >&2
  echo "  Ricalcolato: $RECOMPUTED_SHA" >&2
  exit 1
fi
echo "sha256 piano: OK ($DECLARED_SHA)"

# — Verifica HEAD coincide con base attesa nel piano —
CURRENT_HEAD=$(git -C "$REPO_ROOT" rev-parse --short HEAD)
if [ "$CURRENT_HEAD" != "$PLAN_HEAD" ]; then
  echo "ERRORE: HEAD divergente. Piano richiede $PLAN_HEAD, HEAD attuale è $CURRENT_HEAD" >&2
  exit 1
fi
echo "HEAD: OK ($CURRENT_HEAD)"

# — Estrai unità dal piano —
UNITS=$(grep '^### [0-9]\+\.' "$PLAN_FILE" | sed -E 's/^### [0-9]+\. //')

echo ""
echo "Unità da eseguire:"
echo "$UNITS"
echo ""

# — Esecuzione unità —
while IFS= read -r UNIT_NAME; do
  [ -z "$UNIT_NAME" ] && continue

  echo "--- Unità: $UNIT_NAME ---"

  # Kill switch per ogni unità (PROTOCOLLO 25)
  if [ -f "$STOP_FILE" ]; then
    echo "STOP: $STOP_FILE esiste. Esecuzione interrotta prima di $UNIT_NAME." >&2
    exit 1
  fi

  # Leggi CHIAVE dal piano
  UNIT_CHIAVE=$(grep -A10 "### .*${UNIT_NAME}" "$PLAN_FILE" | grep 'CHIAVE' | sed -E 's/.*CHIAVE\*\*: //')

  # Verifica CHIAVE non già in LEDGER (idempotenza F6)
  if [ -n "$UNIT_CHIAVE" ] && grep -q "$UNIT_CHIAVE" "$LEDGER_FILE" 2>/dev/null; then
    echo "SKIP $UNIT_NAME: CHIAVE $UNIT_CHIAVE già in LEDGER.md — unità saltata (idempotenza)."
    continue
  fi

  # Leggi path mandato
  MANDATO_FILE="$REPO_ROOT/docs/judge/mandati/${UNIT_NAME}.md"
  if [ ! -f "$MANDATO_FILE" ]; then
    echo "ERRORE: mandato non trovato: $MANDATO_FILE" >&2
    exit 1
  fi

  # Verifica etichetta SAFE_AUTO
  ETICHETTA=$(head -1 "$MANDATO_FILE" | sed -E 's/^ETICHETTA: //')
  if [ "$ETICHETTA" != "SAFE_AUTO" ]; then
    echo "ERRORE: unità $UNIT_NAME ha etichetta $ETICHETTA — non SAFE_AUTO. Il piano non doveva includerla." >&2
    exit 1
  fi

  echo "Esecuzione $UNIT_NAME (mandato: $MANDATO_FILE)..."
  echo "[PLACEHOLDER] — implementazione specifica per ogni unità da aggiungere qui."
  echo "Unità $UNIT_NAME completata (simulazione)."
  echo ""

done <<< "$UNITS"

echo "=== vos_apply.sh: piano completato ==="
