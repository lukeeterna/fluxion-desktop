#!/bin/bash
# Post-write hook per file TypeScript/TSX
# Rilevamento anti-pattern immediato (no tsc completo = troppo lento)
FILE="$1"

[[ "$FILE" != *.ts ]] && [[ "$FILE" != *.tsx ]] && exit 0

WARN=0

# Check: any senza eccezione
if grep -n " any\b" "$FILE" 2>/dev/null | grep -v "// ok-any" | head -3 | grep -q .; then
  echo "⚠️  'any' in $FILE — TypeScript strict violation (usa // ok-any per eccezioni)"
  WARN=1
fi

# Check: @ts-ignore vietato
if grep -n "@ts-ignore" "$FILE" 2>/dev/null | grep -q .; then
  echo "⚠️  '@ts-ignore' in $FILE — vietato da CLAUDE.md"
  WARN=1
fi

# Check: @ts-nocheck vietato
if grep -n "@ts-nocheck" "$FILE" 2>/dev/null | grep -q .; then
  echo "⚠️  '@ts-nocheck' in $FILE — vietato da CLAUDE.md"
  WARN=1
fi

if [[ $WARN -eq 0 ]]; then
  echo "✅ $FILE — TS hook OK"
fi

# Check migration SQL: se il file è una migration, verifica che sia in lib.rs
if [[ "$FILE" == *migrations/*.sql ]]; then
  MIGNAME=$(basename "$FILE" .sql)
  if ! grep -q "$MIGNAME" src-tauri/src/lib.rs 2>/dev/null; then
    echo "⚠️  Migration $MIGNAME NON in src-tauri/src/lib.rs — aggiungila prima del commit!"
  fi
fi
