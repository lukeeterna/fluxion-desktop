// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Pipeline Hooks
// React hooks for Voice Agent integration
// ═══════════════════════════════════════════════════════════════════

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

// ───────────────────────────────────────────────────────────────────
// Audio Utilities
// ───────────────────────────────────────────────────────────────────

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
