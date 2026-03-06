// ═══════════════════════════════════════════════════════════════════
// FLUXION - Media Hooks (F06 Sprint A)
// TanStack Query hooks per gestione foto/video schede cliente
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  MediaRecord,
  SaveMediaImageInput,
  SaveMediaVideoInput,
  MediaConsentInfo,
  MediaCategoria,
} from '../types/media';

// ─────────────────────────────────────────────────────────────────────
// QUERY KEYS
// ─────────────────────────────────────────────────────────────────────

export const mediaKeys = {
  all: ['media'] as const,
  cliente: (clienteId: number, tipo?: string, categoria?: MediaCategoria) =>
    [...mediaKeys.all, 'cliente', clienteId, tipo, categoria] as const,
};

// ─────────────────────────────────────────────────────────────────────
// QUERY: lista media cliente
// ─────────────────────────────────────────────────────────────────────

export function useClienteMedia(
  clienteId: number,
  tipo?: string,
  categoria?: MediaCategoria,
) {
  return useQuery({
    queryKey: mediaKeys.cliente(clienteId, tipo, categoria),
    queryFn: async (): Promise<MediaRecord[]> => {
      return invoke('get_cliente_media', {
        clienteId,
        tipo: tipo ?? null,
        categoria: categoria ?? null,
      });
    },
    enabled: clienteId > 0,
  });
}

// ─────────────────────────────────────────────────────────────────────
// MUTATION: save image
// ─────────────────────────────────────────────────────────────────────

export function useSaveMediaImage(clienteId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: SaveMediaImageInput): Promise<MediaRecord> => {
      return invoke('save_media_image', { input });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mediaKeys.cliente(clienteId) });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// MUTATION: save video
// ─────────────────────────────────────────────────────────────────────

export function useSaveMediaVideo(clienteId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: SaveMediaVideoInput): Promise<MediaRecord> => {
      return invoke('save_media_video', { input });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mediaKeys.cliente(clienteId) });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// MUTATION: delete media
// ─────────────────────────────────────────────────────────────────────

export function useDeleteMedia(clienteId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (mediaId: number): Promise<void> => {
      return invoke('delete_media', { mediaId });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mediaKeys.cliente(clienteId) });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// MUTATION: update consent
// ─────────────────────────────────────────────────────────────────────

export function useUpdateMediaConsent() {
  return useMutation({
    mutationFn: async (input: MediaConsentInfo & { clienteId: number }): Promise<void> => {
      return invoke('update_media_consent', {
        input: {
          cliente_id: input.clienteId,
          consenso_interno: input.consenso_interno,
          consenso_social: input.consenso_social,
          consenso_clinico: input.consenso_clinico,
        },
      });
    },
  });
}

// ─────────────────────────────────────────────────────────────────────
// UTILITY: read file as base64 data URL
// ─────────────────────────────────────────────────────────────────────

export async function readMediaAsDataUrl(relativePath: string, mimeType = 'image/jpeg'): Promise<string> {
  const b64: string = await invoke('read_media_file', { relativePath });
  return `data:${mimeType};base64,${b64}`;
}
