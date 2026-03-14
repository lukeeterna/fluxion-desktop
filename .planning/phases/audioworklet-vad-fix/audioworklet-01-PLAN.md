---
phase: audioworklet-vad-fix
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - public/audio-processor.worklet.js
  - src/hooks/use-voice-pipeline.ts
autonomous: true

must_haves:
  truths:
    - "AudioWorkletProcessor receives microphone audio in a dedicated worker thread"
    - "Audio chunks are buffered as Int16Array and sent to VAD backend every 100ms"
    - "Audio level visualization updates from worklet data"
    - "All cleanup paths (stopListening, cancelListening, useEffect unmount) disconnect AudioWorkletNode"
    - "No ScriptProcessorNode, no GainNode silencer, no setInterval for chunk sending remain"
  artifacts:
    - path: "public/audio-processor.worklet.js"
      provides: "AudioWorkletProcessor subclass for PCM audio capture"
      contains: "registerProcessor"
    - path: "src/hooks/use-voice-pipeline.ts"
      provides: "useVADRecorder hook with AudioWorkletNode instead of ScriptProcessorNode"
      contains: "AudioWorkletNode"
  key_links:
    - from: "src/hooks/use-voice-pipeline.ts"
      to: "public/audio-processor.worklet.js"
      via: "audioContext.audioWorklet.addModule"
      pattern: "addModule.*audio-processor\\.worklet\\.js"
    - from: "public/audio-processor.worklet.js"
      to: "src/hooks/use-voice-pipeline.ts"
      via: "port.postMessage -> port.onmessage"
      pattern: "port\\.postMessage|port\\.onmessage"
---

<objective>
Create the AudioWorklet processor file and migrate useVADRecorder from ScriptProcessorNode to AudioWorkletNode.

Purpose: ScriptProcessorNode is deprecated and its onaudioprocess callback does not fire in WKWebView production (Tauri .app bundle). AudioWorkletNode runs on a dedicated audio thread that WKWebView does not throttle, fixing the phone button open-mic.

Output: Working AudioWorklet-based audio capture pipeline that passes `npm run type-check`.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@src/hooks/use-voice-pipeline.ts
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create AudioWorklet processor file</name>
  <files>public/audio-processor.worklet.js</files>
  <action>
Create `public/audio-processor.worklet.js` with an AudioWorkletProcessor subclass.

Requirements:
- Class name: `AudioChunkProcessor`
- Register as: `'audio-chunk-processor'`
- In `process(inputs, outputs, parameters)`:
  - Get `inputs[0][0]` (first input, first channel = Float32Array of 128 samples)
  - Guard: if no input data, return true
  - Accumulate samples into an internal buffer (Float32Array)
  - When buffer reaches 4096 samples (to match previous ScriptProcessorNode buffer size for VAD chunk compatibility), post a message with the buffer via `this.port.postMessage({ audioData: buffer })` and reset the internal buffer
  - Always `return true` to keep processor alive
- Constructor: call `super()`, initialize `this._buffer = new Float32Array(4096)` and `this._bufferIndex = 0`
- The 4096 sample accumulation is critical: VAD backend expects chunks of consistent size. AudioWorklet's native 128-sample frames are too small individually.
- This is a plain JS file (not TypeScript) because AudioWorklet modules are loaded via URL, not bundled.

Do NOT use transferable (buffer transfer) — the buffer is reused internally, so send a copy.
  </action>
  <verify>File exists at `public/audio-processor.worklet.js`. Contains `registerProcessor('audio-chunk-processor', AudioChunkProcessor)`. Contains `process(inputs` method. Contains `this.port.postMessage`.</verify>
  <done>AudioWorklet processor file created with 4096-sample buffering and postMessage output.</done>
</task>

<task type="auto">
  <name>Task 2: Migrate useVADRecorder to AudioWorkletNode</name>
  <files>src/hooks/use-voice-pipeline.ts</files>
  <action>
Modify `src/hooks/use-voice-pipeline.ts` to replace ScriptProcessorNode with AudioWorkletNode. All changes are within the `useVADRecorder` function (lines ~647-1139).

**A. Update processorRef type (line 650):**
Replace:
```typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const processorRef = React.useRef<any>(null); // ScriptProcessorNode
```
With:
```typescript
const processorRef = React.useRef<AudioWorkletNode | null>(null);
```
Remove the eslint-disable comment — no longer needed since AudioWorkletNode is a proper type.

**B. Add a startTimeRef** to track duration (since we're removing setInterval):
After line 663 (`const waitForTurnRef = ...`), add:
```typescript
const startTimeRef = React.useRef<number>(0);
```

**C. Replace audio capture setup in startListening (lines 825-865):**
Replace the entire block from `// Use ScriptProcessorNode` through `}, VAD_CHUNK_INTERVAL_MS);` with:

```typescript
      // AudioWorklet: dedicated audio thread, not throttled by WKWebView
      await audioContext.audioWorklet.addModule('/audio-processor.worklet.js');
      const workletNode = new AudioWorkletNode(audioContext, 'audio-chunk-processor');
      processorRef.current = workletNode;

      workletNode.port.onmessage = (event: MessageEvent<{ audioData: Float32Array }>) => {
        const float32 = event.data.audioData;
        const pcmData = floatTo16BitPCM(float32);
        audioBufferRef.current.push(pcmData);
        allAudioRef.current.push(pcmData.slice());

        // Calculate RMS audio level for visualization
        let sum = 0;
        for (let i = 0; i < float32.length; i++) {
          sum += float32[i] * float32[i];
        }
        const rms = Math.sqrt(sum / float32.length);
        audioLevelRef.current = Math.min(1, rms * 5);
      };

      source.connect(workletNode);
      // AudioWorkletNode does NOT need connection to destination — no GainNode silencer needed

      // Start sending buffered chunks to VAD backend at regular intervals
      const startTime = Date.now();
      startTimeRef.current = startTime;
      chunkIntervalRef.current = setInterval(() => {
        processAudioBuffer();
        if (isMountedRef.current) {
          setState(s => ({
            ...s,
            duration: Math.floor((Date.now() - startTime) / 1000),
            audioLevel: audioLevelRef.current,
          }));
        }
      }, VAD_CHUNK_INTERVAL_MS);
```

IMPORTANT: We KEEP the setInterval for `processAudioBuffer()` because the VAD backend expects chunks sent at 100ms intervals via HTTP POST. The worklet collects raw PCM; the interval sends accumulated buffers to the backend. The worklet replaces ScriptProcessorNode's onaudioprocess (audio capture), NOT the chunk-sending interval.

**D. Remove the GainNode silencer lines (lines 846-852):**
These lines are replaced by the simpler `source.connect(workletNode)` above. The old code was:
```typescript
const silencer = audioContext.createGain();
silencer.gain.value = 0;
source.connect(processor);
processor.connect(silencer);
silencer.connect(audioContext.destination);
```
This entire block is gone in the new code above.

**E. Update cleanup in stopListening (lines 908-910):**
The existing code already does:
```typescript
if (processorRef.current) {
  processorRef.current.disconnect();
  processorRef.current = null;
}
```
This works identically for AudioWorkletNode — `.disconnect()` is inherited from AudioNode. Also close the worklet port for clean shutdown. Replace with:
```typescript
if (processorRef.current) {
  processorRef.current.port.close();
  processorRef.current.disconnect();
  processorRef.current = null;
}
```

**F. Update cleanup in cancelListening (lines 1062-1064):**
Same pattern — add `port.close()` before `disconnect()`:
```typescript
if (processorRef.current) {
  processorRef.current.port.close();
  processorRef.current.disconnect();
  processorRef.current = null;
}
```

**G. Update cleanup in useEffect unmount (lines 1114-1116):**
Same pattern — add `port.close()` before `disconnect()`:
```typescript
if (processorRef.current) {
  processorRef.current.port.close();
  processorRef.current.disconnect();
  processorRef.current = null;
}
```

**H. Verify no remaining ScriptProcessorNode references:**
Search the file for `ScriptProcessor`, `createScriptProcessor`, `onaudioprocess`, `createGain` (in useVADRecorder scope only — createGain may exist elsewhere). Remove any remaining references or comments about ScriptProcessorNode.

**I. Verify `chunkIntervalRef` is still used:**
Confirm that `chunkIntervalRef` is still declared, set in startListening, and cleared in stopListening/cancelListening/useEffect cleanup. It is still needed for processAudioBuffer interval.

**What NOT to change:**
- Do NOT touch floatTo16BitPCM, int16ToHex, processAudioBuffer, sendVADChunk — these are unchanged
- Do NOT touch the streamRef (MediaStream) handling — unchanged
- Do NOT touch waitForTurn, notifyTtsSpeaking — unchanged
- Do NOT touch anything outside useVADRecorder function
- Do NOT remove VAD_CHUNK_INTERVAL_MS constant — it's still used
  </action>
  <verify>Run `npm run type-check` from `/Volumes/MontereyT7/FLUXION/` — must produce 0 errors. Grep for `ScriptProcessor` in use-voice-pipeline.ts — must return 0 matches. Grep for `AudioWorkletNode` — must return matches. Grep for `createGain` within useVADRecorder — must return 0 matches (may still exist in other functions).</verify>
  <done>useVADRecorder uses AudioWorkletNode. processorRef typed as AudioWorkletNode | null. All 3 cleanup paths close port and disconnect. No ScriptProcessorNode references remain. type-check passes with 0 errors.</done>
</task>

</tasks>

<verification>
1. `npm run type-check` passes with 0 errors
2. `grep -c 'ScriptProcessor' src/hooks/use-voice-pipeline.ts` returns 0
3. `grep -c 'AudioWorkletNode' src/hooks/use-voice-pipeline.ts` returns 2+ matches
4. `grep -c 'addModule' src/hooks/use-voice-pipeline.ts` returns 1 match
5. `grep -c 'registerProcessor' public/audio-processor.worklet.js` returns 1 match
6. `grep -c 'createGain' src/hooks/use-voice-pipeline.ts` — check that none are in useVADRecorder scope
</verification>

<success_criteria>
- public/audio-processor.worklet.js exists with AudioWorkletProcessor subclass
- use-voice-pipeline.ts uses AudioWorkletNode instead of ScriptProcessorNode
- GainNode silencer removed from useVADRecorder
- All 3 cleanup paths (stop, cancel, unmount) call port.close() + disconnect()
- processorRef typed as AudioWorkletNode | null (no `any`)
- npm run type-check passes with 0 errors
</success_criteria>

<output>
After completion, create `.planning/phases/audioworklet-vad-fix/audioworklet-01-SUMMARY.md`
</output>
