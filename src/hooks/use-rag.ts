// FLUXION - RAG Hooks
// TanStack Query hooks for FLUXION IA (Retrieval Augmented Generation)

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoke } from '@tauri-apps/api/core';
import type { FaqEntry, RagResponse, BusinessContext, FaqCategory } from '@/types/rag';

// ============================================================================
// Query Keys
// ============================================================================

export const ragKeys = {
  all: ['rag'] as const,
  categories: () => [...ragKeys.all, 'categories'] as const,
  faqs: (category: string) => [...ragKeys.all, 'faqs', category] as const,
  connection: () => [...ragKeys.all, 'connection'] as const,
};

// ============================================================================
// Queries
// ============================================================================

/**
 * List available FAQ categories
 */
export function useFaqCategories() {
  return useQuery({
    queryKey: ragKeys.categories(),
    queryFn: async (): Promise<string[]> => {
      return invoke('list_faq_categories');
    },
    staleTime: Infinity, // Categories don't change often
  });
}

/**
 * Load FAQs for a specific category
 */
export function useFaqs(category: FaqCategory | string) {
  return useQuery({
    queryKey: ragKeys.faqs(category),
    queryFn: async (): Promise<FaqEntry[]> => {
      return invoke('load_faqs', { category });
    },
    enabled: !!category,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Test Groq API connection
 */
export function useTestGroqConnection() {
  return useQuery({
    queryKey: ragKeys.connection(),
    queryFn: async (): Promise<string> => {
      return invoke('test_groq_connection');
    },
    enabled: false, // Only run manually
    retry: false,
  });
}

// ============================================================================
// Mutations
// ============================================================================

/**
 * RAG answer mutation - ask a question and get AI-powered response
 */
export function useRagAnswer() {
  return useMutation({
    mutationFn: async (params: {
      question: string;
      category: FaqCategory | string;
      businessContext?: BusinessContext;
    }): Promise<RagResponse> => {
      return invoke('rag_answer', {
        question: params.question,
        category: params.category,
        businessContext: params.businessContext,
      });
    },
  });
}

/**
 * Quick FAQ search - retrieval only, no LLM
 */
export function useQuickFaqSearch() {
  return useMutation({
    mutationFn: async (params: {
      question: string;
      category: FaqCategory | string;
    }): Promise<FaqEntry[]> => {
      return invoke('quick_faq_search', {
        question: params.question,
        category: params.category,
      });
    },
  });
}

/**
 * Test Groq connection mutation
 */
export function useTestGroq() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<string> => {
      return invoke('test_groq_connection');
    },
    onSuccess: (data) => {
      queryClient.setQueryData(ragKeys.connection(), data);
    },
  });
}

// ============================================================================
// Convenience Hooks
// ============================================================================

/**
 * Combined hook for RAG chat interface
 */
export function useRagChat(category: FaqCategory | string, businessContext?: BusinessContext) {
  const ragAnswer = useRagAnswer();
  const quickSearch = useQuickFaqSearch();

  const askQuestion = async (question: string, useFullRag = true) => {
    if (useFullRag) {
      return ragAnswer.mutateAsync({
        question,
        category,
        businessContext,
      });
    } else {
      const faqs = await quickSearch.mutateAsync({ question, category });
      // Return first FAQ answer if found
      if (faqs.length > 0) {
        return {
          answer: faqs[0].answer,
          sources: faqs,
          confidence: 1.0,
          model: 'keyword-match',
        } as RagResponse;
      }
      throw new Error('Nessun risultato trovato');
    }
  };

  return {
    askQuestion,
    isLoading: ragAnswer.isPending || quickSearch.isPending,
    error: ragAnswer.error || quickSearch.error,
    lastResponse: ragAnswer.data,
  };
}
