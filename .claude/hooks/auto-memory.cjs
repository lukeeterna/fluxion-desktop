#!/usr/bin/env node
/**
 * FLUXION Auto Memory — PostToolUse Hook
 *
 * Rileva git commit o task completati e inietta reminder CoVe 2026 FASE 5
 * per aggiornare automaticamente MEMORY.md + HANDOFF.md.
 *
 * Riceve via stdin: { tool_name, tool_input, tool_response }
 * Output → iniettato come system-reminder per Claude
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Leggi input dal tool via stdin
let rawInput = '';
process.stdin.on('data', chunk => { rawInput += chunk; });

process.stdin.on('end', () => {
  try {
    const data = JSON.parse(rawInput);
    const toolName = data.tool_name || data.tool || '';
    const toolInput = data.tool_input || data.input || {};
    const toolOutput = data.tool_response || data.output || {};

    // Solo hook su Bash tool
    if (toolName !== 'Bash') {
      process.exit(0);
    }

    const command = (toolInput.command || '').toLowerCase();
    const outputText = (toolOutput.output || toolOutput.stdout || '').toLowerCase();

    // ────────────────────────────────────────────────────────────
    // TRIGGER 1: git commit riuscito
    // ────────────────────────────────────────────────────────────
    const isGitCommit = /git\s+commit/.test(command);
    // Commit riuscito: nessun errore nell'output E il comando era git commit
    const noError = !/error|fatal|nothing\s+to\s+commit|hook\s+failed/.test(outputText);

    if (isGitCommit && noError) {
      // Estrai hash commit dall'output (formato: [master abc1234] o [abc1234])
      const rawOutput = toolOutput.output || toolOutput.stdout || '';
      const hashMatch = rawOutput.match(/\[(?:master|main)?\s*([a-f0-9]{6,12})\]/) ||
                        rawOutput.match(/\b([a-f0-9]{7,12})\b/);
      const commitHash = hashMatch ? hashMatch[1] : 'latest';

      writeMemoryMarker('git_commit', commitHash);
      printReminder('GIT COMMIT', [
        `Commit ${commitHash} rilevato.`,
        'CoVe 2026 FASE 5 richiede aggiornamento MEMORY.md + HANDOFF.md.',
        'Aggiorna ora o alla fine del task corrente.',
      ]);
      process.exit(0);
    }

    // ────────────────────────────────────────────────────────────
    // TRIGGER 2: pytest/test suite completata su voice-agent
    // ────────────────────────────────────────────────────────────
    const isPytest = /pytest/.test(command);
    const allPassed = /passed/.test(outputText) && !/failed|error/.test(outputText);

    if (isPytest && allPassed) {
      writeMemoryMarker('pytest_pass', new Date().toISOString());
      printReminder('TEST PASS', [
        'Test suite voice-agent PASS.',
        'Aggiorna MEMORY.md voce "Voice pipeline: ✅ N/N test".',
      ]);
      process.exit(0);
    }

    // ────────────────────────────────────────────────────────────
    // TRIGGER 3: npm run type-check OK
    // ────────────────────────────────────────────────────────────
    const isTypeCheck = /type.check/.test(command);
    const typeCheckOk = /0\s+error/.test(outputText) || outputText.trim() === '';

    if (isTypeCheck && typeCheckOk) {
      printReminder('TYPE-CHECK OK', [
        'TypeScript check 0 errori.',
        'Ricorda: CoVe 2026 FASE 4 completata → procedi con FASE 5 (deploy + memory).',
      ]);
      process.exit(0);
    }

    process.exit(0);

  } catch (_e) {
    // Parsing fallito → non bloccare
    process.exit(0);
  }
});

/**
 * Scrive un marker nel cache per tracciare eventi di sessione.
 */
function writeMemoryMarker(event, value) {
  try {
    const cacheDir = path.join(os.homedir(), '.claude', 'cache');
    const markerFile = path.join(cacheDir, 'fluxion-memory-marker.json');

    if (!fs.existsSync(cacheDir)) {
      fs.mkdirSync(cacheDir, { recursive: true });
    }

    let markers = {};
    if (fs.existsSync(markerFile)) {
      markers = JSON.parse(fs.readFileSync(markerFile, 'utf8'));
    }

    markers[event] = value;
    markers._lastUpdate = new Date().toISOString();
    markers._needsMemoryUpdate = true;

    fs.writeFileSync(markerFile, JSON.stringify(markers, null, 2));
  } catch (_e) {
    // Silenzioso — non bloccare mai
  }
}

/**
 * Stampa il reminder che Claude vedrà come system-reminder.
 */
function printReminder(trigger, lines) {
  console.log(`\n⚡ AUTO-MEMORY [${trigger}] — CoVe 2026 FASE 5`);
  lines.forEach(l => console.log(`   ${l}`));
  console.log(`   → Aggiorna: HANDOFF.md + MEMORY.md`);
  console.log(`   → File: /Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/\n`);
}
