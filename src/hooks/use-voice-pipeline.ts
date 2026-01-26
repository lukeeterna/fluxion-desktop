// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Pipeline Hooks
// React hooks for Voice Agent integration
// Supports both Tauri mode (invoke) and Browser mode (HTTP fallback)
// VAD (Voice Activity Detection) for automatic turn detection
// ═══════════════════════════════════════════════════════════════════

import * as React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

// ───────────────────────────────────────────────────────────────────
// Platform Detection & HTTP Fallback
// ───────────────────────────────────────────────────────────────────

const VOICE_PIPELINE_URL = 'http://localhost:3002';
const VAD_CHUNK_INTERVAL_MS = 100; // Send audio chunks every 100ms

function isInTauri(): boolean {
  return typeof window !== 'undefined' &&
    ('__TAURI_INTERNALS__' in window || '__TAURI__' in window);
}

async function httpFallback<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${VOICE_PIPELINE_URL}${endpoint}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

export interface VoicePipelineStatus {
  running: boolean;
  port: number;
  pid: number | null;
  health: {
    status: string;
    service: string;
    version: string;
  } | null;
}

export interface VoiceResponse {
  success: boolean;
  response: string | null;
  transcription: string | null;
  intent: string | null;
  audio_base64: string | null;
  error: string | null;
}

// VAD Types
export interface VADSessionConfig {
  threshold: number;
  silence_ms: number;
  prefix_ms: number;
}

export interface VADChunkResponse {
  success: boolean;
  state: 'IDLE' | 'SPEAKING';
  probability: number;
  event: 'start_of_speech' | 'end_of_speech' | null;
  turn_ready: boolean;
  turn_audio_hex?: string;
  turn_duration_ms?: number;
}

export interface VADRecorderState {
  isListening: boolean;
  isSpeaking: boolean;
  isPreparing: boolean;
  error: string | null;
  probability: number;
  duration: number;
  sessionId: string | null;
}

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const voicePipelineKeys = {
  all: ['voice-pipeline'] as const,
  status: () => [...voicePipelineKeys.all, 'status'] as const,
};

// ───────────────────────────────────────────────────────────────────
// Hooks
// ───────────────────────────────────────────────────────────────────

/**
 * Get voice pipeline status
 */
export function useVoicePipelineStatus() {
  return useQuery({
    queryKey: voicePipelineKeys.status(),
    queryFn: async (): Promise<VoicePipelineStatus> => {
      if (isInTauri()) {
        return await invoke('get_voice_pipeline_status');
      }
      // HTTP fallback for browser mode (E2E tests)
      // Map Python server response to expected TypeScript type
      const data = await httpFallback<{ success: boolean; status: string }>('/status');
      return {
        running: data.status === 'running',
        port: 3002,
        pid: null,
        health: {
          status: data.status,
          service: 'FLUXION Voice Agent',
          version: '2.0.0',
        },
      };
    },
    refetchInterval: 5000, // Poll every 5 seconds
    staleTime: 2000,
  });
}

/**
 * Start voice pipeline
 */
export function useStartVoicePipeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<VoicePipelineStatus> => {
      if (isInTauri()) {
        return await invoke('start_voice_pipeline');
      }
      // HTTP fallback - pipeline is externally managed, just verify it's running
      const data = await httpFallback<{ success: boolean; status: string }>('/status');
      return {
        running: data.status === 'running',
        port: 3002,
        pid: null,
        health: {
          status: data.status,
          service: 'FLUXION Voice Agent',
          version: '2.0.0',
        },
      };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: voicePipelineKeys.status() });
    },
  });
}

/**
 * Stop voice pipeline
 */
export function useStopVoicePipeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<boolean> => {
      if (isInTauri()) {
        return await invoke('stop_voice_pipeline');
      }
      // HTTP fallback - just return true (pipeline managed externally)
      return true;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: voicePipelineKeys.status() });
    },
  });
}

/**
 * Process text through voice pipeline
 */
export function useVoiceProcessText() {
  return useMutation({
    mutationFn: async (text: string): Promise<VoiceResponse> => {
      if (isInTauri()) {
        return await invoke('voice_process_text', { text });
      }
      // HTTP fallback for browser mode - map server response to expected type
      const data = await httpFallback<{
        success: boolean;
        response: string;
        transcription: string;
        intent: string;
        audio_base64: string;
      }>('/process', {
        method: 'POST',
        body: JSON.stringify({ text }),
      });
      return {
        success: data.success,
        response: data.response,
        transcription: data.transcription,
        intent: data.intent,
        audio_base64: data.audio_base64,
        error: null,
      };
    },
  });
}

/**
 * Generate greeting
 */
export function useVoiceGreet() {
  return useMutation({
    mutationFn: async (): Promise<VoiceResponse> => {
      if (isInTauri()) {
        return await invoke('voice_greet');
      }
      // HTTP fallback for browser mode - map server response to expected type
      const data = await httpFallback<{
        success: boolean;
        response: string;
        audio_base64: string;
        intent: string;
      }>('/greet', { method: 'POST' });
      return {
        success: data.success,
        response: data.response,
        transcription: null,
        intent: data.intent,
        audio_base64: data.audio_base64,
        error: null,
      };
    },
  });
}

/**
 * Text-to-speech only
 */
export function useVoiceSay() {
  return useMutation({
    mutationFn: async (text: string): Promise<VoiceResponse> => {
      if (isInTauri()) {
        return await invoke('voice_say', { text });
      }
      // HTTP fallback for browser mode
      return httpFallback<VoiceResponse>('/say', {
        method: 'POST',
        body: JSON.stringify({ text }),
      });
    },
  });
}

/**
 * Reset conversation
 */
export function useVoiceResetConversation() {
  return useMutation({
    mutationFn: async (): Promise<boolean> => {
      if (isInTauri()) {
        return await invoke('voice_reset_conversation');
      }
      // HTTP fallback for browser mode
      await httpFallback<{ success: boolean }>('/reset', { method: 'POST' });
      return true;
    },
  });
}

/**
 * Process audio through voice pipeline (STT -> NLU -> TTS)
 */
export function useVoiceProcessAudio() {
  return useMutation({
    mutationFn: async (audioHex: string): Promise<VoiceResponse> => {
      if (isInTauri()) {
        return await invoke('voice_process_audio', { audioHex });
      }
      // HTTP fallback for browser mode
      return httpFallback<VoiceResponse>('/process-audio', {
        method: 'POST',
        body: JSON.stringify({ audio_hex: audioHex }),
      });
    },
  });
}

// ───────────────────────────────────────────────────────────────────
// Audio Utilities
// ───────────────────────────────────────────────────────────────────

/**
 * Convert ArrayBuffer to hex string
 */
function arrayBufferToHex(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

/**
 * Convert audio blob to WAV format
 * The Whisper API expects proper WAV files
 */
async function blobToWav(blob: Blob, sampleRate = 16000): Promise<ArrayBuffer> {
  const audioContext = new AudioContext({ sampleRate });
  const arrayBuffer = await blob.arrayBuffer();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

  // Convert to mono if needed
  const numberOfChannels = 1;
  const length = audioBuffer.length;
  const outputBuffer = audioContext.createBuffer(
    numberOfChannels,
    length,
    sampleRate
  );

  // Copy and mix channels to mono
  const outputData = outputBuffer.getChannelData(0);
  const inputData = audioBuffer.getChannelData(0);
  for (let i = 0; i < length; i++) {
    outputData[i] = inputData[i];
  }

  // Encode to WAV
  const wavBuffer = encodeWav(outputBuffer);
  await audioContext.close();
  return wavBuffer;
}

/**
 * Encode AudioBuffer to WAV format
 */
function encodeWav(audioBuffer: AudioBuffer): ArrayBuffer {
  const numChannels = audioBuffer.numberOfChannels;
  const sampleRate = audioBuffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;

  const bytesPerSample = bitDepth / 8;
  const blockAlign = numChannels * bytesPerSample;

  const samples = audioBuffer.getChannelData(0);
  const dataLength = samples.length * bytesPerSample;
  const buffer = new ArrayBuffer(44 + dataLength);
  const view = new DataView(buffer);

  // WAV header
  const writeString = (offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  writeString(0, 'RIFF');
  view.setUint32(4, 36 + dataLength, true);
  writeString(8, 'WAVE');
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true); // fmt chunk size
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);
  writeString(36, 'data');
  view.setUint32(40, dataLength, true);

  // Write audio data
  let offset = 44;
  for (let i = 0; i < samples.length; i++) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    const value = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    view.setInt16(offset, value, true);
    offset += 2;
  }

  return buffer;
}

export interface AudioRecorderState {
  isRecording: boolean;
  isPreparing: boolean;
  error: string | null;
  duration: number;
}

export interface UseAudioRecorderReturn {
  state: AudioRecorderState;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<string | null>;
  cancelRecording: () => void;
}

/**
 * Hook for recording audio from microphone
 * Returns audio as hex string for Whisper STT
 */
export function useAudioRecorder(): UseAudioRecorderReturn {
  const mediaRecorderRef = React.useRef<MediaRecorder | null>(null);
  const chunksRef = React.useRef<Blob[]>([]);
  const timerRef = React.useRef<NodeJS.Timeout | null>(null);
  const mimeTypeRef = React.useRef<string>('');

  const [state, setState] = React.useState<AudioRecorderState>({
    isRecording: false,
    isPreparing: false,
    error: null,
    duration: 0,
  });

  const startRecording = React.useCallback(async () => {
    console.log('[AudioRecorder] startRecording called');
    try {
      setState({ isRecording: false, isPreparing: true, error: null, duration: 0 });
      chunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      // Detect supported audio format (Safari/WKWebView doesn't support webm)
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/mp4',
        'audio/aac',
        '', // Empty = browser default
      ];

      let selectedMimeType = '';
      for (const mimeType of mimeTypes) {
        if (mimeType === '' || MediaRecorder.isTypeSupported(mimeType)) {
          selectedMimeType = mimeType;
          break;
        }
      }

      const recorderOptions: { mimeType?: string } = {};
      if (selectedMimeType) {
        recorderOptions.mimeType = selectedMimeType;
      }
      mimeTypeRef.current = selectedMimeType;

      const mediaRecorder = new MediaRecorder(stream, recorderOptions);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.start(100); // Collect data every 100ms
      mediaRecorderRef.current = mediaRecorder;
      console.log('[AudioRecorder] MediaRecorder started, state =', mediaRecorder.state);

      // Start duration timer
      const startTime = Date.now();
      timerRef.current = setInterval(() => {
        setState((s) => ({
          ...s,
          duration: Math.floor((Date.now() - startTime) / 1000),
        }));
      }, 100);

      setState({ isRecording: true, isPreparing: false, error: null, duration: 0 });
      console.log('[AudioRecorder] isRecording set to true');
    } catch (err) {
      setState((s) => ({
        ...s,
        isPreparing: false,
        error:
          err instanceof Error ? err.message : 'Failed to access microphone',
      }));
    }
  }, []);

  const stopRecording = React.useCallback(async (): Promise<string | null> => {
    // Stop timer immediately
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    const mediaRecorder = mediaRecorderRef.current;

    // No recorder or not in recording state - cleanup and return
    if (!mediaRecorder || mediaRecorder.state === 'inactive') {
      console.log('[AudioRecorder] stopRecording: no active recorder, cleaning up');
      mediaRecorderRef.current = null;
      chunksRef.current = [];
      setState({ isRecording: false, isPreparing: false, error: null, duration: 0 });
      return null;
    }

    console.log('[AudioRecorder] stopRecording: state =', mediaRecorder.state);

    return new Promise((resolve) => {
      const handleStop = async () => {
        console.log('[AudioRecorder] onstop fired');

        // Stop all tracks
        mediaRecorder.stream.getTracks().forEach((track) => track.stop());

        // Clear ref
        mediaRecorderRef.current = null;

        // Convert to WAV and hex
        try {
          const blobType = mimeTypeRef.current || 'audio/webm';
          const blob = new Blob(chunksRef.current, { type: blobType });
          const wavBuffer = await blobToWav(blob);
          const hexString = arrayBufferToHex(wavBuffer);

          chunksRef.current = [];
          setState({ isRecording: false, isPreparing: false, error: null, duration: 0 });
          resolve(hexString);
        } catch (err) {
          console.error('[AudioRecorder] encode error:', err);
          chunksRef.current = [];
          setState({
            isRecording: false,
            isPreparing: false,
            error: err instanceof Error ? err.message : 'Failed to encode audio',
            duration: 0,
          });
          resolve(null);
        }
      };

      // Set handler and stop
      mediaRecorder.onstop = handleStop;
      mediaRecorder.stop();
    });
  }, []);

  const cancelRecording = React.useCallback(() => {
    console.log('[AudioRecorder] cancelRecording called');
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (mediaRecorderRef.current) {
      const recorder = mediaRecorderRef.current;
      recorder.stream.getTracks().forEach((track) => track.stop());
      // Only stop if still recording/paused
      if (recorder.state !== 'inactive') {
        recorder.onstop = null; // Prevent handler from running
        recorder.stop();
      }
      mediaRecorderRef.current = null;
    }
    chunksRef.current = [];
    setState({ isRecording: false, isPreparing: false, error: null, duration: 0 });
  }, []);

  return { state, startRecording, stopRecording, cancelRecording };
}

// ───────────────────────────────────────────────────────────────────
// VAD Audio Recorder
// ───────────────────────────────────────────────────────────────────

export interface UseVADRecorderReturn {
  state: VADRecorderState;
  startListening: () => Promise<void>;
  stopListening: () => Promise<string | null>;
  cancelListening: () => void;
}

/**
 * Hook for VAD-enabled audio recording
 * Automatically detects when user stops speaking
 */
export function useVADRecorder(): UseVADRecorderReturn {
  const audioContextRef = React.useRef<AudioContext | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const processorRef = React.useRef<any>(null); // ScriptProcessorNode
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const streamRef = React.useRef<any>(null); // MediaStream
  const sessionIdRef = React.useRef<string | null>(null);
  const chunkIntervalRef = React.useRef<NodeJS.Timeout | null>(null);
  const audioBufferRef = React.useRef<Int16Array[]>([]);
  const turnAudioRef = React.useRef<string | null>(null);
  const resolveStopRef = React.useRef<((value: string | null) => void) | null>(null);

  const [state, setState] = React.useState<VADRecorderState>({
    isListening: false,
    isSpeaking: false,
    isPreparing: false,
    error: null,
    probability: 0,
    duration: 0,
    sessionId: null,
  });

  // Start VAD session on backend
  const startVADSession = React.useCallback(async (): Promise<string> => {
    const response = await fetch(`${VOICE_PIPELINE_URL}/api/voice/vad/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    const data = await response.json();
    if (!data.success) throw new Error(data.error || 'Failed to start VAD session');
    return data.session_id;
  }, []);

  // Send audio chunk to VAD
  const sendVADChunk = React.useCallback(async (audioHex: string): Promise<VADChunkResponse> => {
    if (!sessionIdRef.current) throw new Error('No VAD session');

    const response = await fetch(`${VOICE_PIPELINE_URL}/api/voice/vad/chunk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionIdRef.current,
        audio_hex: audioHex,
      }),
    });
    return response.json();
  }, []);

  // Stop VAD session
  const stopVADSession = React.useCallback(async () => {
    if (!sessionIdRef.current) return;

    try {
      await fetch(`${VOICE_PIPELINE_URL}/api/voice/vad/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionIdRef.current }),
      });
    } catch (e) {
      console.warn('[VAD] Failed to stop session:', e);
    }
    sessionIdRef.current = null;
  }, []);

  // Convert Float32Array to Int16Array (PCM)
  const floatTo16BitPCM = (float32Array: Float32Array): Int16Array => {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
  };

  // Convert Int16Array to hex string
  const int16ToHex = (int16Array: Int16Array): string => {
    const bytes = new Uint8Array(int16Array.buffer);
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
  };

  // Process collected audio and send to VAD
  const processAudioBuffer = React.useCallback(async () => {
    if (audioBufferRef.current.length === 0) return;

    // Concatenate all buffered chunks
    const totalLength = audioBufferRef.current.reduce((acc, arr) => acc + arr.length, 0);
    const combined = new Int16Array(totalLength);
    let offset = 0;
    for (const chunk of audioBufferRef.current) {
      combined.set(chunk, offset);
      offset += chunk.length;
    }
    audioBufferRef.current = [];

    // Send to VAD
    const audioHex = int16ToHex(combined);
    try {
      const result = await sendVADChunk(audioHex);

      setState(s => ({
        ...s,
        isSpeaking: result.state === 'SPEAKING',
        probability: result.probability,
      }));

      // Check for turn completion
      if (result.turn_ready && result.turn_audio_hex) {
        console.log('[VAD] Turn complete:', result.turn_duration_ms, 'ms');
        turnAudioRef.current = result.turn_audio_hex;

        // Auto-stop when turn is complete
        if (resolveStopRef.current) {
          resolveStopRef.current(result.turn_audio_hex);
          resolveStopRef.current = null;
        }
      }

      // Log events
      if (result.event) {
        console.log('[VAD] Event:', result.event);
      }
    } catch (e) {
      console.error('[VAD] Chunk error:', e);
    }
  }, [sendVADChunk]);

  const startListening = React.useCallback(async () => {
    console.log('[VAD] startListening called');
    try {
      setState(s => ({ ...s, isPreparing: true, error: null }));
      audioBufferRef.current = [];
      turnAudioRef.current = null;

      // Start VAD session on backend
      const sessionId = await startVADSession();
      sessionIdRef.current = sessionId;
      console.log('[VAD] Session started:', sessionId);

      // Get microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      streamRef.current = stream;

      // Create audio context for processing
      const audioContext = new AudioContext({ sampleRate: 16000 });
      audioContextRef.current = audioContext;

      const source = audioContext.createMediaStreamSource(stream);

      // Use ScriptProcessorNode to get raw audio data
      // Note: This is deprecated but more widely supported than AudioWorklet
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        const pcmData = floatTo16BitPCM(inputData);
        audioBufferRef.current.push(pcmData);
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      // Start sending chunks to VAD
      const startTime = Date.now();
      chunkIntervalRef.current = setInterval(() => {
        processAudioBuffer();
        setState(s => ({
          ...s,
          duration: Math.floor((Date.now() - startTime) / 1000),
        }));
      }, VAD_CHUNK_INTERVAL_MS);

      setState({
        isListening: true,
        isSpeaking: false,
        isPreparing: false,
        error: null,
        probability: 0,
        duration: 0,
        sessionId,
      });

      console.log('[VAD] Listening started');
    } catch (err) {
      console.error('[VAD] Start error:', err);
      setState(s => ({
        ...s,
        isPreparing: false,
        error: err instanceof Error ? err.message : 'Failed to start VAD',
      }));
      await stopVADSession();
    }
  }, [startVADSession, processAudioBuffer, stopVADSession]);

  const stopListening = React.useCallback(async (): Promise<string | null> => {
    console.log('[VAD] stopListening called');

    // Stop chunk sending
    if (chunkIntervalRef.current) {
      clearInterval(chunkIntervalRef.current);
      chunkIntervalRef.current = null;
    }

    // Process any remaining audio
    await processAudioBuffer();

    // Stop audio processing
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (audioContextRef.current) {
      await audioContextRef.current.close();
      audioContextRef.current = null;
    }

    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track: { stop: () => void }) => track.stop());
      streamRef.current = null;
    }

    // Stop VAD session
    await stopVADSession();

    // Get the turn audio if available
    const turnAudio = turnAudioRef.current;
    turnAudioRef.current = null;
    audioBufferRef.current = [];

    setState({
      isListening: false,
      isSpeaking: false,
      isPreparing: false,
      error: null,
      probability: 0,
      duration: 0,
      sessionId: null,
    });

    // If we have turn audio from VAD, return it
    // Otherwise, we need to convert buffered audio to WAV
    if (turnAudio) {
      console.log('[VAD] Returning turn audio:', turnAudio.length, 'hex chars');
      return turnAudio;
    }

    console.log('[VAD] No turn audio captured');
    return null;
  }, [processAudioBuffer, stopVADSession]);

  const cancelListening = React.useCallback(() => {
    console.log('[VAD] cancelListening called');

    if (chunkIntervalRef.current) {
      clearInterval(chunkIntervalRef.current);
      chunkIntervalRef.current = null;
    }

    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track: { stop: () => void }) => track.stop());
      streamRef.current = null;
    }

    stopVADSession();

    turnAudioRef.current = null;
    audioBufferRef.current = [];
    resolveStopRef.current = null;

    setState({
      isListening: false,
      isSpeaking: false,
      isPreparing: false,
      error: null,
      probability: 0,
      duration: 0,
      sessionId: null,
    });
  }, [stopVADSession]);

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      cancelListening();
    };
  }, [cancelListening]);

  return { state, startListening, stopListening, cancelListening };
}

/**
 * Play audio from hex string (optimized for large audio)
 */
export async function playAudioFromHex(hexString: string): Promise<void> {
  // Optimized hex to bytes conversion (no regex, ~10x faster)
  const len = hexString.length / 2;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = parseInt(hexString.substring(i * 2, i * 2 + 2), 16);
  }

  // Create blob and audio element
  const blob = new window.Blob([bytes], { type: 'audio/wav' });
  const url = window.URL.createObjectURL(blob);

  return new Promise((resolve, reject) => {
    const audio = new window.Audio(url);
    audio.onended = () => {
      window.URL.revokeObjectURL(url);
      resolve();
    };
    audio.onerror = (e) => {
      window.URL.revokeObjectURL(url);
      reject(e);
    };
    audio.play().catch(reject);
  });
}
