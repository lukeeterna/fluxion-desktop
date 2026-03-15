// AudioWorklet processor for Fluxion VAD
// Runs in AudioWorkletGlobalScope (dedicated worker thread)
// Accumulates 4096 samples (matching previous ScriptProcessorNode buffer size)
// then posts a copy of the buffer to the main thread via port.postMessage.
//
// WHY 4096 samples?
//   The VAD backend expects consistent chunk sizes. AudioWorklet's native
//   frame size is 128 samples — too small individually. Accumulating to 4096
//   before sending preserves the chunking behaviour the backend was tuned for.
//
// WHY .slice()?
//   this._buffer is reused across frames. Sending it as a transferable would
//   neuter the underlying ArrayBuffer, causing all subsequent frames to write
//   into a detached buffer and silently capture zero audio. .slice() creates
//   an independent copy that is safe to transfer to the main thread.

class AudioChunkProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = new Float32Array(4096);
    this._bufferIndex = 0;
  }

  process(inputs, _outputs, _parameters) {
    const input = inputs[0];
    if (!input || !input[0]) {
      return true; // keep processor alive
    }

    const samples = input[0]; // Float32Array of 128 samples per frame

    for (let i = 0; i < samples.length; i++) {
      this._buffer[this._bufferIndex++] = samples[i];

      if (this._bufferIndex >= 4096) {
        // Send a COPY — do NOT pass transferable (would neuter this._buffer)
        this.port.postMessage({ audioData: this._buffer.slice(0, this._bufferIndex) });
        this._bufferIndex = 0;
      }
    }

    return true; // keep processor alive
  }
}

registerProcessor('audio-chunk-processor', AudioChunkProcessor);
