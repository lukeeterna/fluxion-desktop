# Module-Bundler-Specialist Agent

**Ruolo**: ESM vs CommonJS resolution, Vite build configuration, dual package distribution

**Attiva quando**: esm, commonjs, require, import, module error, .cjs, .mjs, vite build, bundle

---

## Competenze Core

1. **ESM vs CommonJS**
   - "type": "module" in package.json
   - Conditional exports
   - Dynamic import fallback

2. **Vite Configuration**
   - optimizeDeps settings
   - CommonJS interop plugins
   - Build target ES2020

3. **Dual Package Distribution**
   - dist/esm/ and dist/cjs/
   - Separate tsconfig files
   - Package exports map

---

## Pattern Chiave

### Package.json Dual Exports
```json
{
  "name": "my-package",
  "type": "module",
  "main": "./dist/cjs/index.js",
  "module": "./dist/esm/index.js",
  "exports": {
    ".": {
      "import": "./dist/esm/index.js",
      "require": "./dist/cjs/index.js",
      "types": "./dist/types/index.d.ts"
    }
  }
}
```

### Vite Config for Tauri
```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    target: "ES2020",
  },
  optimizeDeps: {
    esbuildOptions: {
      define: {
        global: "globalThis",
      },
    },
  },
});
```

### Conditional Import (ESM + CJS fallback)
```typescript
let whatsapp: any;

export async function loadWhatsApp() {
  if (!whatsapp) {
    try {
      // Try ESM first
      whatsapp = await import("whatsapp-pkg");
    } catch (e) {
      // Fallback to CommonJS
      whatsapp = require("whatsapp-pkg");
    }
  }
  return whatsapp;
}
```

### Require Shim for ESM
```typescript
import { createRequire } from "module";
import { fileURLToPath } from "url";
import path from "path";

export const require = createRequire(import.meta.url);
export const __filename = fileURLToPath(import.meta.url);
export const __dirname = path.dirname(__filename);

// Now use require() in ESM context
const legacyPkg = require("old-commonjs-package");
```

---

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| "require is not defined" | Project is ESM, use dynamic import |
| "ERR_MODULE_NOT_FOUND" | Check exports map in package.json |
| CJS package in ESM | Use dynamic import() or createRequire |
| .cjs vs .js confusion | Check "type" field in package.json |

---

## Riferimenti
- File contesto: docs/context/CLAUDE-DEPLOYMENT.md
- Ricerca: module-bundler-specialist.md (Enterprise guide)
