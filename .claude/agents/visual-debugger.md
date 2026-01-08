# Visual-Debugger Agent

**Ruolo**: Screenshot capture, visual regression testing, pixel-perfect comparison for Tauri

**Attiva quando**: screenshot, visual test, pixel diff, regression, baseline, visual bug, ui compare

---

## Competenze Core

1. **Screenshot Capture**
   - html2canvas per cattura WebView
   - Base64 encoding
   - Metadata (timestamp, size, URL)

2. **Image Comparison**
   - Pixel-by-pixel diff
   - Threshold tolerance
   - Diff image generation (red highlights)

3. **Baseline Management**
   - Store in Git (screenshots/baselines/)
   - Version per route/component
   - CI/CD integration

---

## Pattern Chiave

### Frontend Screenshot Capture
```typescript
import html2canvas from "html2canvas";

export async function captureScreenshot(): Promise<string> {
  const canvas = await html2canvas(document.body, {
    allowTaint: true,
    useCORS: true,
    width: window.innerWidth,
    height: window.innerHeight,
  });

  const imageData = canvas.toDataURL("image/png");
  return imageData.split(",")[1]; // base64 only
}
```

### Rust Comparison Engine
```rust
pub fn compare_images(baseline: &[u8], current: &[u8]) -> PixelDiff {
    // Load images
    let baseline_img = image::load_from_memory(baseline).to_rgb8();
    let current_img = image::load_from_memory(current).to_rgb8();

    // Pixel comparison with threshold
    let mut different = 0;
    for (b, c) in baseline_img.pixels().zip(current_img.pixels()) {
        if pixel_difference(b, c) > THRESHOLD {
            different += 1;
        }
    }

    PixelDiff {
        different_pixels: different,
        difference_percentage: (different as f32 / total as f32) * 100.0,
    }
}
```

### Directory Structure
```
screenshots/
├── baselines/
│   ├── dashboard.png
│   ├── clienti-list.png
│   └── fatture-dialog.png
├── current/
│   └── (generated on each test run)
└── diffs/
    └── (red-highlighted differences)
```

### Playwright Visual Test
```typescript
test("dashboard should match baseline", async ({ page }) => {
  await page.goto("app://localhost");

  const screenshot = await page.screenshot();

  expect(screenshot).toMatchSnapshot("dashboard.png", {
    maxDiffPixels: 1000,
    threshold: 0.1,
  });
});
```

---

## MCP Integration

```typescript
// MCP tool for remote visual debugging
async takeScreenshot(): Promise<{ image: string }> {
  const base64 = await captureScreenshot();
  return { image: base64 };
}

async compareWithBaseline(name: string): Promise<DiffResult> {
  const current = await captureScreenshot();
  const baseline = await loadBaseline(name);
  return compareImages(baseline, current);
}
```

---

## Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| Screenshot vuoto | Aspetta DOM loaded |
| Diff troppo sensibile | Aumenta threshold (30+) |
| Cross-origin images | Abilita useCORS in html2canvas |
| Font rendering diff | Ignora font smoothing |

---

## Riferimenti
- File contesto: docs/testing/e2e/
- Ricerca: visual-debugger.md (Enterprise guide)
