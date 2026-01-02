// ═══════════════════════════════════════════════════════════════════
// FLUXION - WhatsApp Templates Hooks
// TanStack Query hooks for WhatsApp template CRUD
// ═══════════════════════════════════════════════════════════════════

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type {
  WhatsAppTemplate,
  CreateWhatsAppTemplateInput,
  UpdateWhatsAppTemplateInput,
  FillTemplateInput,
} from '@/types/whatsapp';

// ───────────────────────────────────────────────────────────────────
// Query Keys
// ───────────────────────────────────────────────────────────────────

export const whatsappKeys = {
  all: ['whatsapp'] as const,
  templates: () => [...whatsappKeys.all, 'templates'] as const,
  templateList: (categoria?: string) =>
    [...whatsappKeys.templates(), { categoria }] as const,
  templateDetails: () => [...whatsappKeys.templates(), 'detail'] as const,
  templateDetail: (id: string) => [...whatsappKeys.templateDetails(), id] as const,
};

// ───────────────────────────────────────────────────────────────────
// Queries
// ───────────────────────────────────────────────────────────────────

/**
 * Get WhatsApp templates, optionally filtered by categoria
 */
export function useWhatsAppTemplates(categoria?: string) {
  return useQuery({
    queryKey: whatsappKeys.templateList(categoria),
    queryFn: () =>
      invoke<WhatsAppTemplate[]>('get_whatsapp_templates', {
        categoria: categoria || null,
      }),
  });
}

/**
 * Get single WhatsApp template by ID
 */
export function useWhatsAppTemplate(id: string) {
  return useQuery({
    queryKey: whatsappKeys.templateDetail(id),
    queryFn: () => invoke<WhatsAppTemplate>('get_whatsapp_template', { id }),
    enabled: !!id,
  });
}

// ───────────────────────────────────────────────────────────────────
// Mutations
// ───────────────────────────────────────────────────────────────────

/**
 * Create new WhatsApp template
 */
export function useCreateWhatsAppTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: CreateWhatsAppTemplateInput) =>
      invoke<WhatsAppTemplate>('create_whatsapp_template', { input }),
    onSuccess: () => {
      // Invalidate all template lists
      queryClient.invalidateQueries({ queryKey: whatsappKeys.templates() });
    },
  });
}

/**
 * Update existing WhatsApp template
 */
export function useUpdateWhatsAppTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: UpdateWhatsAppTemplateInput }) =>
      invoke<WhatsAppTemplate>('update_whatsapp_template', { id, input }),
    onSuccess: (data) => {
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: whatsappKeys.templates() });
      // Invalidate specific detail
      queryClient.invalidateQueries({ queryKey: whatsappKeys.templateDetail(data.id) });
    },
  });
}

/**
 * Delete WhatsApp template (soft delete)
 */
export function useDeleteWhatsAppTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => invoke<void>('delete_whatsapp_template', { id }),
    onSuccess: () => {
      // Invalidate all template queries
      queryClient.invalidateQueries({ queryKey: whatsappKeys.templates() });
    },
  });
}

/**
 * Fill WhatsApp template with variables and track usage
 */
export function useFillWhatsAppTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: FillTemplateInput) =>
      invoke<string>('fill_whatsapp_template', { input }),
    onSuccess: (_, variables) => {
      // Invalidate specific template to refresh uso_count and ultimo_uso
      queryClient.invalidateQueries({
        queryKey: whatsappKeys.templateDetail(variables.template_id),
      });
      // Invalidate lists to refresh usage stats
      queryClient.invalidateQueries({ queryKey: whatsappKeys.templates() });
    },
  });
}
