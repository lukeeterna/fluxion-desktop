// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Pipeline Hooks
// React hooks for Voice Agent integration
// ═══════════════════════════════════════════════════════════════════

import * as React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';

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
      return await invoke('get_voice_pipeline_status');
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
      return await invoke('start_voice_pipeline');
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
      return await invoke('stop_voice_pipeline');
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
      return await invoke('voice_process_text', { text });
    },
  });
}

/**
 * Generate greeting
 */
export function useVoiceGreet() {
  return useMutation({
    mutationFn: async (): Promise<VoiceResponse> => {
      return await invoke('voice_greet');
    },
  });
}

/**
 * Text-to-speech only
 */
export function useVoiceSay() {
  return useMutation({
    mutationFn: async (text: string): Promise<VoiceResponse> => {
      return await invoke('voice_say', { text });
    },
  });
}

/**
 * Reset conversation
 */
export function useVoiceResetConversation() {
  return useMutation({
    mutationFn: async (): Promise<boolean> => {
      return await invoke('voice_reset_conversation');
    },
  });
}

/**
 * Process audio through voice pipeline (STT -> NLU -> TTS)
 */
export function useVoiceProcessAudio() {
  return useMutation({
    mutationFn: async (audioHex: string): Promise<VoiceResponse> => {
      return await invoke('voice_process_audio', { audioHex });
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
    try {
      setState((s) => ({ ...s, isPreparing: true, error: null }));
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

      // Start duration timer
      const startTime = Date.now();
      timerRef.current = setInterval(() => {
        setState((s) => ({
          ...s,
          duration: Math.floor((Date.now() - startTime) / 1000),
        }));
      }, 100);

      setState((s) => ({ ...s, isRecording: true, isPreparing: false }));
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
    return new Promise((resolve) => {
      if (!mediaRecorderRef.current) {
        resolve(null);
        return;
      }

      const mediaRecorder = mediaRecorderRef.current;

      mediaRecorder.onstop = async () => {
        // Stop timer
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }

        // Stop all tracks
        mediaRecorder.stream.getTracks().forEach((track) => track.stop());

        // Convert to WAV and hex
        try {
          const blobType = mimeTypeRef.current || 'audio/webm';
          const blob = new Blob(chunksRef.current, { type: blobType });
          const wavBuffer = await blobToWav(blob);
          const hexString = arrayBufferToHex(wavBuffer);

          setState((s) => ({ ...s, isRecording: false, duration: 0 }));
          resolve(hexString);
        } catch (err) {
          setState((s) => ({
            ...s,
            isRecording: false,
            error: err instanceof Error ? err.message : 'Failed to encode audio',
          }));
          resolve(null);
        }
      };

      mediaRecorder.stop();
    });
  }, []);

  const cancelRecording = React.useCallback(() => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
      mediaRecorderRef.current = null;
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    chunksRef.current = [];
    setState({ isRecording: false, isPreparing: false, error: null, duration: 0 });
  }, []);

  return { state, startRecording, stopRecording, cancelRecording };
}

/**
 * Play audio from hex string
 */
export async function playAudioFromHex(hexString: string): Promise<void> {
  // Convert hex to bytes
  const bytes = new Uint8Array(
    hexString.match(/.{1,2}/g)?.map((byte) => parseInt(byte, 16)) || []
  );

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
