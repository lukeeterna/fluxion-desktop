// ═══════════════════════════════════════════════════════════════════
// FLUXION - Pending Questions (FAQ Learning System)
// Mostra domande senza risposta e permette di salvare come FAQ
// ═══════════════════════════════════════════════════════════════════

import { useState, type FC } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  MessageCircleQuestion,
  Save,
  Trash2,
  CheckCircle,
  Clock,
  User,
  Phone,
  BookOpen,
  Sparkles,
  AlertCircle,
} from 'lucide-react'

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface PendingQuestion {
  id: string
  question: string
  fromPhone: string
  fromName: string
  category: string
  timestamp: string
  status: 'pending' | 'answered' | 'saved_as_faq'
  operatorResponse: string | null
  responseTimestamp: string | null
}

// ───────────────────────────────────────────────────────────────────
// Hooks
// ───────────────────────────────────────────────────────────────────

function usePendingQuestions() {
  return useQuery({
    queryKey: ['pending-questions'],
    queryFn: () => invoke<PendingQuestion[]>('get_pending_questions'),
    refetchInterval: 10000, // Poll every 10 seconds
  })
}

function useSaveCustomFaq() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (params: { question: string; answer: string; section?: string }) =>
      invoke('save_custom_faq', params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-questions'] })
      queryClient.invalidateQueries({ queryKey: ['custom-faqs'] })
    },
  })
}

function useUpdatePendingQuestionStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (params: { questionId: string; newStatus: string }) =>
      invoke('update_pending_question_status', params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-questions'] })
    },
  })
}

function useDeletePendingQuestion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (questionId: string) =>
      invoke('delete_pending_question', { questionId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-questions'] })
    },
  })
}

// ───────────────────────────────────────────────────────────────────
// Question Card Component
// ───────────────────────────────────────────────────────────────────

interface QuestionCardProps {
  question: PendingQuestion
  onSaveFaq: (question: string, answer: string) => Promise<void>
  onDelete: (id: string) => void
  onUpdateStatus: (id: string, status: string) => void
}

const QuestionCard: FC<QuestionCardProps> = ({
  question,
  onSaveFaq,
  onDelete,
  onUpdateStatus,
}) => {
  const [editedAnswer, setEditedAnswer] = useState(question.operatorResponse || '')
  const [isSaving, setIsSaving] = useState(false)

  const handleSaveFaq = async () => {
    if (!editedAnswer.trim()) return
    setIsSaving(true)
    try {
      await onSaveFaq(question.question, editedAnswer)
      onUpdateStatus(question.id, 'saved_as_faq')
    } finally {
      setIsSaving(false)
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const statusColors = {
    pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
    answered: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    saved_as_faq: 'bg-green-500/20 text-green-400 border-green-500/30',
  }

  const statusLabels = {
    pending: 'In attesa',
    answered: 'Risposto',
    saved_as_faq: 'Salvato come FAQ',
  }

  return (
    <div className={`p-4 rounded-lg border ${statusColors[question.status]} bg-slate-900`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded text-xs ${statusColors[question.status]}`}>
            {question.status === 'pending' && <Clock className="inline h-3 w-3 mr-1" />}
            {question.status === 'answered' && <CheckCircle className="inline h-3 w-3 mr-1" />}
            {question.status === 'saved_as_faq' && <BookOpen className="inline h-3 w-3 mr-1" />}
            {statusLabels[question.status]}
          </span>
          <span className="text-xs text-slate-500">{formatTime(question.timestamp)}</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onDelete(question.id)}
          className="h-8 w-8 p-0 text-slate-500 hover:text-red-400"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>

      {/* Contact Info */}
      <div className="flex items-center gap-4 mb-3 text-sm text-slate-400">
        <span className="flex items-center gap-1">
          <User className="h-3 w-3" />
          {question.fromName}
        </span>
        <span className="flex items-center gap-1">
          <Phone className="h-3 w-3" />
          +{question.fromPhone}
        </span>
      </div>

      {/* Question */}
      <div className="mb-4">
        <Label className="text-xs text-slate-500 uppercase mb-1 block">Domanda</Label>
        <p className="text-white bg-slate-800 p-3 rounded-lg">
          {question.question}
        </p>
      </div>

      {/* Answer (editable if not saved yet) */}
      {question.status !== 'saved_as_faq' && (
        <div className="mb-4">
          <Label className="text-xs text-slate-500 uppercase mb-1 block">
            {question.operatorResponse ? 'Risposta operatore (modifica se necessario)' : 'Scrivi risposta'}
          </Label>
          <Textarea
            value={editedAnswer}
            onChange={(e) => setEditedAnswer(e.target.value)}
            placeholder="Scrivi la risposta che verrà salvata come FAQ..."
            className="bg-slate-800 border-slate-700 text-white min-h-[80px]"
          />
        </div>
      )}

      {/* Saved Answer (read-only) */}
      {question.status === 'saved_as_faq' && question.operatorResponse && (
        <div className="mb-4">
          <Label className="text-xs text-slate-500 uppercase mb-1 block">Risposta salvata</Label>
          <p className="text-green-400 bg-green-500/10 p-3 rounded-lg border border-green-500/30">
            {question.operatorResponse}
          </p>
        </div>
      )}

      {/* Actions */}
      {question.status !== 'saved_as_faq' && (
        <div className="flex justify-end gap-2">
          <Button
            onClick={handleSaveFaq}
            disabled={!editedAnswer.trim() || isSaving}
            className="bg-green-600 hover:bg-green-500"
          >
            {isSaving ? (
              <>
                <Clock className="h-4 w-4 mr-2 animate-spin" />
                Salvataggio...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Salva come FAQ
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  )
}

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

export const PendingQuestions: FC = () => {
  const { data: questions, isLoading } = usePendingQuestions()
  const saveFaq = useSaveCustomFaq()
  const updateStatus = useUpdatePendingQuestionStatus()
  const deleteQuestion = useDeletePendingQuestion()

  const handleSaveFaq = async (question: string, answer: string) => {
    await saveFaq.mutateAsync({ question, answer })
  }

  const handleDelete = (id: string) => {
    if (window.confirm('Eliminare questa domanda?')) {
      deleteQuestion.mutate(id)
    }
  }

  const handleUpdateStatus = (id: string, status: string) => {
    updateStatus.mutate({ questionId: id, newStatus: status })
  }

  // Filter questions by status
  const pendingQuestions = questions?.filter(q => q.status === 'pending') || []
  const answeredQuestions = questions?.filter(q => q.status === 'answered') || []
  const savedQuestions = questions?.filter(q => q.status === 'saved_as_faq') || []

  const totalPending = pendingQuestions.length + answeredQuestions.length

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <MessageCircleQuestion className="h-6 w-6 text-yellow-400" />
            </div>
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                Domande in Attesa
                {totalPending > 0 && (
                  <span className="bg-yellow-500 text-black text-xs font-bold px-2 py-0.5 rounded-full">
                    {totalPending}
                  </span>
                )}
              </CardTitle>
              <CardDescription>
                Domande a cui il bot non ha saputo rispondere
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Sparkles className="h-4 w-4 text-cyan-400" />
            <span>Salva per insegnare al bot</span>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {isLoading ? (
          <div className="text-center py-8 text-slate-500">
            <Clock className="h-8 w-8 mx-auto mb-2 animate-spin" />
            <p>Caricamento...</p>
          </div>
        ) : !questions?.length ? (
          <div className="text-center py-8 text-slate-500">
            <CheckCircle className="h-10 w-10 mx-auto mb-2 text-green-500/50" />
            <p>Nessuna domanda in attesa!</p>
            <p className="text-sm mt-1">Il bot sta rispondendo a tutte le domande.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Pending & Answered Questions */}
            {(pendingQuestions.length > 0 || answeredQuestions.length > 0) && (
              <div>
                <h3 className="text-sm font-semibold text-yellow-400 mb-3 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Da Salvare ({totalPending})
                </h3>
                <div className="space-y-4">
                  {[...answeredQuestions, ...pendingQuestions].map((q) => (
                    <QuestionCard
                      key={q.id}
                      question={q}
                      onSaveFaq={handleSaveFaq}
                      onDelete={handleDelete}
                      onUpdateStatus={handleUpdateStatus}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Saved Questions (collapsed by default) */}
            {savedQuestions.length > 0 && (
              <details className="group">
                <summary className="cursor-pointer text-sm font-semibold text-green-400 mb-3 flex items-center gap-2">
                  <BookOpen className="h-4 w-4" />
                  Salvate come FAQ ({savedQuestions.length})
                  <span className="text-xs text-slate-500">(clicca per espandere)</span>
                </summary>
                <div className="space-y-4 mt-3">
                  {savedQuestions.map((q) => (
                    <QuestionCard
                      key={q.id}
                      question={q}
                      onSaveFaq={handleSaveFaq}
                      onDelete={handleDelete}
                      onUpdateStatus={handleUpdateStatus}
                    />
                  ))}
                </div>
              </details>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
