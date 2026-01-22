// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Pipeline Hooks
// React hooks for Voice Agent integration
// Supports both Tauri mode (invoke) and Browser mode (HTTP fallback)
// ═══════════════════════════════════════════════════════════════════

import * as React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

// ───────────────────────────────────────────────────────────────────
// Platform Detection & HTTP Fallback
// ───────────────────────────────────────────────────────────────────

const VOICE_PIPELINE_URL = 'http://localhost:3002';

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
