// FLUXION - RAG Chat Component
// Assistente intelligente FLUXION IA

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, AlertCircle, CheckCircle2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useRagAnswer, useTestGroq, useFaqCategories } from '@/hooks/use-rag';
import type { FaqEntry } from '@/types/rag';
import { getConfidenceLabel, FAQ_CATEGORY_LABELS } from '@/types/rag';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  sources?: FaqEntry[];
  confidence?: number;
  model?: string;
}

export function RagChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [category, setCategory] = useState('salone');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: categories } = useFaqCategories();
  const ragAnswer = useRagAnswer();
  const testGroq = useTestGroq();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add system message on mount
  useEffect(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'system',
        content: 'Benvenuto! Sono l\'assistente FLUXION. Seleziona una categoria e fammi una domanda.',
        timestamp: new Date(),
      },
    ]);
  }, []);

  const handleSend = async () => {
    if (!input.trim() || ragAnswer.isPending) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    try {
      const response = await ragAnswer.mutateAsync({
        question: input,
        category,
        businessContext: {
          NOME_ATTIVITA: 'FLUXION Demo',
          TELEFONO: '02 1234567',
          WHATSAPP: '39 333 1234567',
        },
      });

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        confidence: response.confidence,
        model: response.model,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      // Tauri invoke può restituire errori come stringhe o oggetti
      let errorText = 'Errore sconosciuto';
      if (error instanceof Error) {
        errorText = error.message;
      } else if (typeof error === 'string') {
        errorText = error;
      } else if (error && typeof error === 'object' && 'message' in error) {
        errorText = String((error as { message: unknown }).message);
      }

      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'system',
        content: `Errore: ${errorText}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleTestConnection = async () => {
    try {
      const result = await testGroq.mutateAsync();
      setMessages((prev) => [
        ...prev,
        {
          id: `test-${Date.now()}`,
          role: 'system',
          content: `✓ FLUXION IA connesso: ${result}`,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      // Gestisci errori Tauri che possono essere stringhe
      let errorText = 'Errore connessione';
      if (error instanceof Error) {
        errorText = error.message;
      } else if (typeof error === 'string') {
        errorText = error;
      }
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'system',
          content: `Errore connessione: ${errorText}`,
          timestamp: new Date(),
        },
      ]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-cyan-500" />
            FLUXION IA - Assistente
          </CardTitle>
          <div className="flex items-center gap-2">
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Categoria" />
              </SelectTrigger>
              <SelectContent>
                {(categories || ['salone', 'auto']).map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {FAQ_CATEGORY_LABELS[cat as keyof typeof FAQ_CATEGORY_LABELS] || cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="sm"
              onClick={handleTestConnection}
              disabled={testGroq.isPending}
            >
              {testGroq.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                'Test API'
              )}
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col overflow-hidden p-0">
        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {ragAnswer.isPending && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Sto pensando...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Scrivi una domanda..."
              disabled={ragAnswer.isPending}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || ragAnswer.isPending}
            >
              {ragAnswer.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-primary text-primary-foreground'
            : isSystem
            ? 'bg-muted text-muted-foreground'
            : 'bg-cyan-500 text-white'
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Message content */}
      <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : ''}`}>
        <div
          className={`inline-block rounded-lg px-4 py-2 ${
            isUser
              ? 'bg-primary text-primary-foreground'
              : isSystem
              ? 'bg-muted text-muted-foreground'
              : 'bg-card border'
          }`}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>

        {/* Metadata for assistant messages */}
        {message.role === 'assistant' && (
          <div className="mt-2 space-y-2">
            {/* Confidence and model */}
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              {message.confidence !== undefined && (
                <ConfidenceBadge confidence={message.confidence} />
              )}
              {message.model && (
                <Badge variant="outline" className="text-xs">
                  {message.model}
                </Badge>
              )}
            </div>

            {/* Sources */}
            {message.sources && message.sources.length > 0 && (
              <SourcesCard sources={message.sources} />
            )}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-xs text-muted-foreground mt-1">
          {message.timestamp.toLocaleTimeString('it-IT', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </p>
      </div>
    </div>
  );
}

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const { label, color } = getConfidenceLabel(confidence);
  const Icon = color === 'green' ? CheckCircle2 : AlertCircle;

  return (
    <Badge
      variant="outline"
      className={`text-xs ${
        color === 'green'
          ? 'border-green-500 text-green-600'
          : color === 'yellow'
          ? 'border-yellow-500 text-yellow-600'
          : 'border-red-500 text-red-600'
      }`}
    >
      <Icon className="h-3 w-3 mr-1" />
      Confidenza: {label} ({(confidence * 100).toFixed(0)}%)
    </Badge>
  );
}

function SourcesCard({ sources }: { sources: FaqEntry[] }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="text-xs">
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-muted-foreground hover:text-foreground flex items-center gap-1"
      >
        <span>{expanded ? '▼' : '▶'}</span>
        <span>Fonti ({sources.length})</span>
      </button>
      {expanded && (
        <div className="mt-2 space-y-1 pl-4 border-l-2 border-muted">
          {sources.map((source, idx) => (
            <div key={idx} className="text-muted-foreground">
              <span className="font-medium">{source.section}</span>
              {' › '}
              <span>{source.question}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RagChat;
