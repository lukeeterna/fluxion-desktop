#!/usr/bin/env bash
# vos_plan.sh — Piano runner VOS: legge CODA IMPIANTO, filtra SAFE_AUTO con file archiviato.
# Non esegue nulla. Scrive vos/plan/<timestamp>.md con elenco ordinato + sha256.
# Tetto: 3 unità per piano.
#
# PROTOCOLLO §27: il runner automatizza l'esecuzione, mai l'autorizzazione.
# PROTOCOLLO §25: controlla vos/STOP prima di ogni passo.

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel)"
MANDATI_DIR="$REPO_ROOT/docs/judge/mandati"
STATE_FILE="$REPO_ROOT/docs/judge/STATE.md"
PLAN_DIR="$REPO_ROOT/vos/plan"
STOP_FILE="$REPO_ROOT/vos/STOP"
MAX_UNITS=3

# — Kill switch (PROTOCOLLO 25) —
if [ -f "$STOP_FILE" ]; then
  echo "STOP: $STOP_FILE esiste. Runner bloccato." >&2
  exit 1
fi

# — Verifica prerequisiti —
if [ ! -f "$STATE_FILE" ]; then
  echo "ERRORE: STATE.md non trovato: $STATE_FILE" >&2
  exit 1
fi

if [ ! -d "$MANDATI_DIR" ]; then
  echo "ERRORE: directory mandati non trovata: $MANDATI_DIR" >&2
  exit 1
fi

# — Leggi HEAD attuale —
CURRENT_HEAD=$(git -C "$REPO_ROOT" rev-parse --short HEAD)

# — Estrai CODA IMPIANTO da STATE.md —
# Formato atteso: "N. T-NOME (corsia CORSIA) — descrizione"
CODA_SECTION=$(awk '/^## CODA IMPIANTO/,/^---/' "$STATE_FILE" | grep -E '^[0-9]+\. ')

if [ -z "$CODA_SECTION" ]; then
  echo "PIANO: coda impianto vuota. Nessuna unità eseguibile." | tee /dev/stderr
  # Scrivi piano vuoto
  TS=$(date -u +"%Y%m%dT%H%M%SZ")
  PLAN_FILE="$PLAN_DIR/${TS}.md"
  mkdir -p "$PLAN_DIR"
  {
    echo "# Piano VOS — $TS"
    echo ""
    echo "Generato da: vos_plan.sh"
    echo "HEAD: $CURRENT_HEAD"
    echo "Coda impianto: VUOTA"
    echo ""
    echo "## Unità pianificate"
    echo ""
    echo "(nessuna)"
    echo ""
    echo "---"
    echo "sha256: $(echo "PIANO_VUOTO_$TS" | shasum -a 256 | awk '{print $1}')"
  } > "$PLAN_FILE"
  echo "Piano scritto: $PLAN_FILE"
  exit 0
fi

# — Per ogni voce di coda, controlla mandato archiviato e etichetta SAFE_AUTO —
count=0
selected_units=()
selected_corsie=()
selected_etichette=()
selected_descrizioni=()
selected_basi=()

while IFS= read -r line; do
  # Estrai nome unità e corsia: "N. T-NOME (corsia CORSIA) — ..."
  NOME=$(echo "$line" | sed -E 's/^[0-9]+\. ([A-Z0-9_-]+[v0-9]*).*/\1/')
  CORSIA=$(echo "$line" | sed -E 's/.*\(corsia ([A-Z]+)\).*/\1/')
  DESCR=$(echo "$line" | sed -E 's/^[0-9]+\. [^—]+— //')

  # Pulizia nome (rimuovi suffissi tipo " v2")
  NOME_FILE=$(echo "$line" | sed -E 's/^[0-9]+\. (T-[A-Z0-9_-]+).*/\1/')

  MANDATO_FILE="$MANDATI_DIR/${NOME_FILE}.md"

  # Controlla se il file mandato esiste
  if [ ! -f "$MANDATO_FILE" ]; then
    echo "SKIP $NOME_FILE: file mandato non archiviato ($MANDATO_FILE)" >&2
    continue
  fi

  # Controlla etichetta in prima riga
  ETICHETTA=$(head -1 "$MANDATO_FILE" | sed -E 's/^ETICHETTA: //')

  if [ "$ETICHETTA" != "SAFE_AUTO" ]; then
    echo "SKIP $NOME_FILE: etichetta=$ETICHETTA (non SAFE_AUTO)" >&2
    continue
  fi

  # Leggi base attesa dal file mandato (cerca riga "Base attesa: XXXXXXX" o "GATE-0.*=")
  BASE_ATTESA=$(grep -i "base attesa\|GATE-0" "$MANDATO_FILE" | grep -oE '[0-9a-f]{7,40}' | head -1 || echo "N/A")

  selected_units+=("$NOME_FILE")
  selected_corsie+=("$CORSIA")
  selected_etichette+=("SAFE_AUTO")
  selected_descrizioni+=("$DESCR")
  selected_basi+=("$BASE_ATTESA")

  count=$((count + 1))
  if [ "$count" -ge "$MAX_UNITS" ]; then
    echo "Tetto $MAX_UNITS unità raggiunto." >&2
    break
  fi
done <<< "$CODA_SECTION"

# — Scrivi il piano —
TS=$(date -u +"%Y%m%dT%H%M%SZ")
PLAN_FILE="$PLAN_DIR/${TS}.md"
mkdir -p "$PLAN_DIR"

{
  echo "# Piano VOS — $TS"
  echo ""
  echo "Generato da: vos_plan.sh"
  echo "HEAD al momento della pianificazione: $CURRENT_HEAD"
  echo "Unità selezionate: $count (tetto: $MAX_UNITS)"
  echo ""
  echo "## Unità pianificate"
  echo ""

  if [ "${#selected_units[@]}" -eq 0 ]; then
    echo "(nessuna — nessuna unità SAFE_AUTO con file archiviato trovata)"
  else
    for i in "${!selected_units[@]}"; do
      idx=$((i + 1))
      echo "### $idx. ${selected_units[$i]}"
      echo "- **Corsia**: ${selected_corsie[$i]}"
      echo "- **Etichetta**: ${selected_etichette[$i]}"
      echo "- **Base attesa**: ${selected_basi[$i]}"
      echo "- **Descrizione**: ${selected_descrizioni[$i]}"
      echo "- **Mandato**: docs/judge/mandati/${selected_units[$i]}.md"
      echo "- **Path che scriverebbero**: (vedere mandato per dettaglio)"
      echo "- **CHIAVE**: ${selected_units[$i]}@${selected_basi[$i]}"
      echo ""
    done
  fi

  echo "---"
  # sha256 del contenuto del piano (esclusa questa riga stessa)
  PLAN_BODY="PIANO_${TS}_UNITS_${count}_HEAD_${CURRENT_HEAD}"
  echo "sha256: $(printf '%s' "$PLAN_BODY" | shasum -a 256 | awk '{print $1}')"
} > "$PLAN_FILE"

echo "Piano scritto: $PLAN_FILE"
echo "Unità incluse: $count"
cat "$PLAN_FILE"
