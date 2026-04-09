#!/bin/bash
# Aspetta che il batch corrente finisca, poi rilancia con glow
cd /Volumes/MontereyT7/FLUXION/video-factory

echo "Aspetto fine batch corrente..."
while pgrep -f "assemble_all.py" > /dev/null 2>&1; do
  sleep 10
done

echo "Batch precedente finito. Lancio versione con glow testo..."
python3 assemble_all.py all > /tmp/fluxion_assembly_glow.log 2>&1

echo "FATTO. Log in /tmp/fluxion_assembly_glow.log"
echo "Report:"
tail -20 /tmp/fluxion_assembly_glow.log
