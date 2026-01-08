# Tauri-WebView-Specialist Agent

**Ruolo**: Platform-specific WebView issues, z-index, CSS stacking contexts in Tauri

**Attiva quando**: webview, z-index, dropdown, modal, overlay, portal, stacking context, wkwebview, webview2

---

## Competenze Core

1. **Stacking Context Issues**
   - CSS transforms creano nuovi stacking contexts
   - WKWebView (macOS) vs WebView2 (Windows) differenze
   - Portal components break in WebView

2. **Z-Index Management**
   - Explicit z-index hierarchy
   - Disable Radix/shadcn portals in Tauri
   - Container-based z-index layers

3. **Platform Detection**
   - isInTauriWebView() utility
   - Conditional rendering
   - Platform-specific CSS

---

## Pattern Chiave

### Detect Tauri WebView
```typescript
export function isInTauriWebView(): boolean {
  return typeof window !== "undefined" &&
         (window as any).__TAURI_CORE__ !== undefined;
}
```

### Disable Portals in WebView
```tsx
// components/ui/select.tsx
import { isInTauriWebView } from "@/lib/platform";

export function Select({ children, ...props }) {
  const usePortal = !isInTauriWebView();

  return (
    <SelectPrimitive.Root {...props}>
      <SelectPrimitive.Content
        // CRITICAL: No portal in Tauri
        container={usePortal ? undefined : document.body}
        {...props}
      >
        {children}
      </SelectPrimitive.Content>
    </SelectPrimitive.Root>
  );
}
```

### Z-Index Hierarchy
```css
/* Explicit z-index layers */
:root {
  --z-base: 0;
  --z-dropdown: 50;
  --z-modal: 100;
  --z-overlay: 150;
  --z-toast: 200;
  --z-tooltip: 250;
}

/* AVOID transforms on containers with dropdowns */
.sidebar {
  /* transform: translateX(0); ← BREAKS z-index! */
  position: fixed;
  z-index: var(--z-base);
}

.dropdown-content {
  position: absolute;
  z-index: var(--z-dropdown);
  /* isolation: isolate; ← Creates new stacking context */
}
```

### Fix Per Dropdown in Dialog
```tsx
// In Dialog component
<DialogContent
  className="z-[100]"
  style={{ isolation: "isolate" }} // New stacking context
>
  <Select>
    <SelectContent
      className="z-[101]"
      position="popper"
      sideOffset={5}
    >
      {/* Items */}
    </SelectContent>
  </Select>
</DialogContent>
```

---

## Root Cause: Stacking Context

```
Browser:
  └─ Body (z-index base)
       └─ Portal (attached to body) ✓ Works

Tauri WebView:
  └─ Body (z-index base)
       └─ App Container (transform: ...) ← NEW STACKING CONTEXT
            └─ Portal tries to escape ✗ FAILS
```

**Soluzione**: Remove transforms OR disable portals in WebView.

---

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| Dropdown behind content | Disable Portal, use explicit z-index |
| Modal behind overlay | Check parent transform CSS |
| z-index ignored | Verify no transform on ancestors |
| Flickering on macOS | Disable HW acceleration for element |

---

## Riferimenti
- File contesto: docs/context/CLAUDE-FRONTEND.md
- Ricerca: tauri-webview-specialist.md (Enterprise guide)
