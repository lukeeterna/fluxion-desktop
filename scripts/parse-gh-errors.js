#!/usr/bin/env node

const annotations = process.argv[2] || '';

const errors = {
  typescript: [],
  rust: [],
  missing_deps: [],
  unused_vars: []
};

// Parse annotations
annotations.split('\n').forEach(line => {
  if (line.includes("'import type'") || line.includes("cannot be used as a value")) {
    const match = line.match(/\[(.*?):.*?#L(\d+)\]/);
    if (match) {
      errors.typescript.push({
        file: match[1],
        line: match[2]
      });
    }
  }
  
  if (line.includes('Cannot find module')) {
    const match = line.match(/Cannot find module '([^']+)'/);
    if (match) errors.missing_deps.push(match[1]);
  }
  
  if (line.includes('is declared but never used')) {
    const match = line.match(/'([^']+)' is declared but never used/);
    if (match) errors.unused_vars.push(match[1]);
  }
  
  if (line.includes('formatting') || line.includes('cargo fmt')) {
    errors.rust.push('formatting_required');
  }
});

// Generate fix commands
console.log(`
# 🔧 FIX AUTOMATICO ERRORI CI/CD

${errors.rust.length > 0 ? `
## 1️⃣ FIX RUST FORMATTING
\`\`\`bash
cd src-tauri && cargo fmt && cd .. && git add src-tauri/
\`\`\`
` : ''}

${errors.typescript.length > 0 ? `
## 2️⃣ FIX TYPESCRIPT IMPORTS
Nei seguenti file, cambia "import type" in "import" SOLO per schema Zod:
${errors.typescript.map(e => `- ${e.file}:${e.line}`).join('\n')}

\`\`\`bash
npm run fix:imports
\`\`\`
` : ''}

${errors.missing_deps.length > 0 ? `
## 3️⃣ INSTALLA DIPENDENZE
\`\`\`bash
${errors.missing_deps.map(dep => `npm install ${dep}`).join('\n')}
\`\`\`
` : ''}

${errors.unused_vars.length > 0 ? `
## 4️⃣ RIMUOVI VARIABILI NON USATE
Rimuovi: ${errors.unused_vars.join(', ')}
` : ''}

## ✅ COMMIT FINALE
\`\`\`bash
git add .
git commit -m "fix: resolve CI/CD errors"
git push
\`\`\`
`);
