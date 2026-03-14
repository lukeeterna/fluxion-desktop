---
phase: audioworklet-vad-fix
plan: 02
type: execute
wave: 2
depends_on: ["audioworklet-01"]
files_modified: []
autonomous: false

must_haves:
  truths:
    - "Tauri .app bundle builds successfully on iMac"
    - "audio-processor.worklet.js is included in the .app bundle's public assets"
    - "Phone button open-mic works in .app bundle — Sara responds after user speaks"
  artifacts: []
  key_links:
    - from: "Tauri bundle"
      to: "public/audio-processor.worklet.js"
      via: "Tauri public dir serving"
      pattern: "audio-processor.worklet.js"
---

<objective>
Build on iMac, verify the AudioWorklet migration works in production .app bundle.

Purpose: The entire point of this phase is fixing phone button open-mic in WKWebView production. Code changes alone are not enough — must verify the .app bundle actually works.

Output: Confirmed working .app with AudioWorklet-based open-mic VAD.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/audioworklet-vad-fix/audioworklet-01-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Push to iMac and build .app bundle</name>
  <files></files>
  <action>
1. Commit the AudioWorklet changes on MacBook:
```bash
git add public/audio-processor.worklet.js src/hooks/use-voice-pipeline.ts
git commit -m "feat(voice): replace ScriptProcessorNode with AudioWorkletNode for VAD

AudioWorklet runs on dedicated audio thread, not throttled by WKWebView.
Fixes phone button open-mic in Tauri .app production bundle."
```

2. Push and sync to iMac:
```bash
git push origin master
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && git pull origin master"
```

3. Build on iMac:
```bash
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION' && npm run tauri build 2>&1 | tail -30"
```

4. Verify build succeeds — check for `.app` bundle in `src-tauri/target/release/bundle/macos/`.

5. Verify audio-processor.worklet.js is in the bundle:
```bash
ssh imac "find '/Volumes/MacSSD - Dati/FLUXION/src-tauri/target/release/bundle/macos/' -name 'audio-processor.worklet.js' 2>/dev/null"
```

If build fails, diagnose and fix. Common issues:
- TypeScript errors: should be caught by plan 01 type-check
- Rust compilation: unrelated to this change (no Rust files modified)
- Asset bundling: verify tauri.conf.json has correct public dir config
  </action>
  <verify>Build command exits 0. `.app` bundle exists. `audio-processor.worklet.js` found inside bundle assets.</verify>
  <done>Tauri .app bundle built successfully on iMac with AudioWorklet processor included.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
AudioWorklet-based VAD pipeline replacing the deprecated ScriptProcessorNode. The .app bundle has been built on iMac.

Changes:
- NEW: `public/audio-processor.worklet.js` — AudioWorkletProcessor with 4096-sample buffering
- MODIFIED: `src/hooks/use-voice-pipeline.ts` — useVADRecorder uses AudioWorkletNode
- REMOVED: ScriptProcessorNode, GainNode silencer
  </what-built>
  <how-to-verify>
On iMac (must be physical, not SSH — microphone access required):

1. Open the built .app from `src-tauri/target/release/bundle/macos/`
2. Navigate to Voice Agent (Sara) section
3. Sara should auto-greet (this already works — sanity check)
4. Click the Phone button (open-mic mode)
5. Speak a phrase like "Buongiorno, vorrei prenotare un taglio"
6. Verify:
   - Audio level indicator moves while speaking (proves AudioWorklet is capturing)
   - Sara responds after you stop speaking (proves VAD detects end_of_speech)
   - The conversation continues in open-mic loop (proves loop works)
7. Click Phone button again to stop — verify clean shutdown (no errors in console)

If it does NOT work:
- Open Safari Web Inspector (Develop menu > Fluxion) and check console for errors
- Look for: "addModule" errors, "AudioWorklet" errors, "NotSupportedError"
- Report the exact error message
  </how-to-verify>
  <resume-signal>Type "approved" if phone button open-mic works, or describe the issue seen.</resume-signal>
</task>

</tasks>

<verification>
1. iMac build succeeded (exit 0)
2. audio-processor.worklet.js found in .app bundle
3. Human verified: phone button open-mic works in production .app
</verification>

<success_criteria>
- .app bundle builds on iMac
- Phone button open-mic works: user speaks, Sara responds, loop continues
- No console errors related to AudioWorklet
</success_criteria>

<output>
After completion, create `.planning/phases/audioworklet-vad-fix/audioworklet-02-SUMMARY.md`
</output>
