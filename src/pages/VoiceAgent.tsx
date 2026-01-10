// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Agent Page
// Chat interface for voice assistant "Paola"
// ═══════════════════════════════════════════════════════════════════

import { useState, useRef, useEffect } from 'react';
import {
  Mic,
  Send,
  Power,
  PowerOff,
  Volume2,
  RefreshCw,
  Loader2,
  Bot,
  User,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import {
  useVoicePipelineStatus,
  useStartVoicePipeline,
  useStopVoicePipeline,
  useVoiceProcessText,
  useVoiceGreet,
  useVoiceResetConversation,
  playAudioFromHex,
  type VoiceResponse,
} from '@/hooks/use-voice-pipeline';

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'error';
  content: string;
  intent?: string;
  timestamp: Date;
  audioHex?: string;
}

// ───────────────────────────────────────────────────────────────────
// Component
// ───────────────────────────────────────────────────────────────────

export function VoiceAgent() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [autoPlay, setAutoPlay] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Hooks
  const { data: status, isLoading: statusLoading } = useVoicePipelineStatus();
  const startPipeline = useStartVoicePipeline();
  const stopPipeline = useStopVoicePipeline();
  const processText = useVoiceProcessText();
  const greet = useVoiceGreet();
  const resetConversation = useVoiceResetConversation();

  const isRunning = status?.running ?? false;
  const isProcessing = processText.isPending || greet.isPending;

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle start pipeline
  const handleStart = async () => {
    try {
      await startPipeline.mutateAsync();
      // Wait for server to be ready, then greet
      setTimeout(async () => {
        try {
          const response = await greet.mutateAsync();
          handleVoiceResponse(response);
        } catch (greetError) {
          const errorMessage: ChatMessage = {
            id: window.crypto.randomUUID(),
            role: 'error',
            content: `Errore nel saluto: ${greetError instanceof Error ? greetError.message : String(greetError)}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        }
      }, 2000);
    } catch (error) {
      console.error('Failed to start pipeline:', error);
      const errorMessage: ChatMessage = {
        id: window.crypto.randomUUID(),
        role: 'error',
        content: `Impossibile avviare Voice Agent: ${error instanceof Error ? error.message : String(error)}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  // Handle stop pipeline
  const handleStop = async () => {
    try {
      await stopPipeline.mutateAsync();
      setMessages([]);
    } catch (error) {
      console.error('Failed to stop pipeline:', error);
    }
  };

  // Handle voice response
  const handleVoiceResponse = async (response: VoiceResponse) => {
    if (response.success && response.response) {
      const message: ChatMessage = {
        id: window.crypto.randomUUID(),
        role: 'assistant',
        content: response.response,
        intent: response.intent ?? undefined,
        timestamp: new Date(),
        audioHex: response.audio_base64 ?? undefined,
      };
      setMessages((prev) => [...prev, message]);

      // Auto-play audio
      if (autoPlay && response.audio_base64) {
        setIsPlaying(true);
        try {
          await playAudioFromHex(response.audio_base64);
        } catch (e) {
          console.error('Audio playback failed:', e);
        }
        setIsPlaying(false);
      }
    }
  };

  // Handle send message
  const handleSend = async () => {
    if (!inputText.trim() || !isRunning || isProcessing) return;

    const userMessage: ChatMessage = {
      id: window.crypto.randomUUID(),
      role: 'user',
      content: inputText.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputText('');

    try {
      const response = await processText.mutateAsync(inputText.trim());
      handleVoiceResponse(response);
    } catch (error) {
      console.error('Failed to process text:', error);
    }
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Play specific message audio
  const handlePlayAudio = async (audioHex: string) => {
    setIsPlaying(true);
    try {
      await playAudioFromHex(audioHex);
    } catch (e) {
      console.error('Audio playback failed:', e);
    }
    setIsPlaying(false);
  };

  // Reset conversation
  const handleReset = async () => {
    try {
      await resetConversation.mutateAsync();
      setMessages([]);
      // Generate new greeting
      const response = await greet.mutateAsync();
      handleVoiceResponse(response);
    } catch (error) {
      console.error('Failed to reset conversation:', error);
    }
  };

  return (
    <div className="h-full flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Voice Agent</h1>
          <p className="text-slate-400">
            Assistente vocale "Paola" per prenotazioni e informazioni
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Status Badge */}
          <Badge
            variant={isRunning ? 'default' : 'secondary'}
            className={cn(
              'gap-1.5',
              isRunning
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-700 text-slate-400'
            )}
          >
            {isRunning ? (
              <>
                <CheckCircle2 className="w-3 h-3" />
                Attivo
              </>
            ) : (
              <>
                <AlertCircle className="w-3 h-3" />
                Inattivo
              </>
            )}
          </Badge>

          {/* Start/Stop Button */}
          {isRunning ? (
            <Button
              data-testid="btn-stop-voice"
              variant="destructive"
              size="sm"
              onClick={handleStop}
              disabled={stopPipeline.isPending}
            >
              {stopPipeline.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <PowerOff className="w-4 h-4 mr-2" />
              )}
              Ferma
            </Button>
          ) : (
            <Button
              data-testid="btn-start-voice"
              variant="default"
              size="sm"
              onClick={handleStart}
              disabled={startPipeline.isPending}
              className="bg-teal-600 hover:bg-teal-700"
            >
              {startPipeline.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
              ) : (
                <Power className="w-4 h-4 mr-2" />
              )}
              Avvia
            </Button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-0">
        {/* Chat Area */}
        <Card className="lg:col-span-3 bg-slate-800/50 border-slate-700 flex flex-col">
          <CardHeader className="border-b border-slate-700 py-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <Bot className="w-5 h-5 text-teal-400" />
                Conversazione
              </CardTitle>
              {isRunning && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleReset}
                  disabled={resetConversation.isPending}
                >
                  <RefreshCw
                    className={cn(
                      'w-4 h-4 mr-2',
                      resetConversation.isPending && 'animate-spin'
                    )}
                  />
                  Reset
                </Button>
              )}
            </div>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-0 min-h-0">
            {/* Messages */}
            <ScrollArea data-testid="voice-transcript" className="flex-1 p-4" ref={scrollRef}>
              {!isRunning ? (
                <div className="h-full flex items-center justify-center text-slate-500">
                  <div className="text-center">
                    <Mic className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Avvia il Voice Agent per iniziare</p>
                    <p className="text-sm mt-1">
                      Clicca "Avvia" in alto a destra
                    </p>
                  </div>
                </div>
              ) : messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-slate-500">
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={cn(
                        'flex gap-3',
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      )}
                    >
                      {message.role === 'assistant' && (
                        <div className="w-8 h-8 rounded-full bg-teal-500/20 flex items-center justify-center flex-shrink-0">
                          <Bot className="w-4 h-4 text-teal-400" />
                        </div>
                      )}
                      {message.role === 'error' && (
                        <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
                          <AlertCircle className="w-4 h-4 text-red-400" />
                        </div>
                      )}
                      <div
                        className={cn(
                          'max-w-[80%] rounded-lg px-4 py-2',
                          message.role === 'user'
                            ? 'bg-teal-600 text-white'
                            : message.role === 'error'
                              ? 'bg-red-900/50 text-red-200 border border-red-700'
                              : 'bg-slate-700 text-slate-100'
                        )}
                      >
                        <p>{message.content}</p>
                        <div className="flex items-center gap-2 mt-1">
                          {message.intent && (
                            <Badge
                              variant="outline"
                              className="text-xs border-slate-600"
                            >
                              {message.intent}
                            </Badge>
                          )}
                          {message.audioHex && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 px-2"
                              onClick={() => handlePlayAudio(message.audioHex!)}
                              disabled={isPlaying}
                            >
                              <Volume2 className="w-3 h-3" />
                            </Button>
                          )}
                          <span className="text-xs text-slate-500">
                            {message.timestamp.toLocaleTimeString('it-IT', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </span>
                        </div>
                      </div>
                      {message.role === 'user' && (
                        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0">
                          <User className="w-4 h-4 text-slate-300" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isProcessing && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-teal-500/20 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-teal-400" />
                      </div>
                      <div className="bg-slate-700 rounded-lg px-4 py-2">
                        <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>

            {/* Input */}
            <div className="border-t border-slate-700 p-4">
              <div className="flex gap-2">
                <Input
                  data-testid="input-voice-text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder={
                    isRunning
                      ? 'Scrivi un messaggio...'
                      : 'Avvia il Voice Agent per iniziare'
                  }
                  disabled={!isRunning || isProcessing}
                  className="bg-slate-700 border-slate-600"
                />
                <Button
                  data-testid="btn-send-voice"
                  onClick={handleSend}
                  disabled={!isRunning || !inputText.trim() || isProcessing}
                  className="bg-teal-600 hover:bg-teal-700"
                >
                  {isProcessing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Status Panel */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader className="border-b border-slate-700 py-3">
            <CardTitle className="text-lg">Stato Sistema</CardTitle>
          </CardHeader>
          <CardContent className="p-4 space-y-4">
            {/* Pipeline Status */}
            <div>
              <label className="text-sm text-slate-400">Voice Pipeline</label>
              <div className="flex items-center gap-2 mt-1">
                <div
                  className={cn(
                    'w-2 h-2 rounded-full',
                    isRunning ? 'bg-emerald-500' : 'bg-slate-600'
                  )}
                />
                <span className="text-sm text-slate-200">
                  {statusLoading
                    ? 'Caricamento...'
                    : isRunning
                      ? 'In esecuzione'
                      : 'Fermo'}
                </span>
              </div>
            </div>

            {/* Port */}
            <div>
              <label className="text-sm text-slate-400">Porta</label>
              <p className="text-sm text-slate-200">{status?.port ?? 3002}</p>
            </div>

            {/* PID */}
            {status?.pid && (
              <div>
                <label className="text-sm text-slate-400">PID</label>
                <p className="text-sm text-slate-200">{status.pid}</p>
              </div>
            )}

            {/* Health */}
            {status?.health && (
              <div>
                <label className="text-sm text-slate-400">Health</label>
                <p className="text-sm text-emerald-400">{status.health.status}</p>
              </div>
            )}

            {/* Auto-play toggle */}
            <div className="pt-4 border-t border-slate-700">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoPlay}
                  onChange={(e) => setAutoPlay(e.target.checked)}
                  className="rounded border-slate-600 bg-slate-700 text-teal-500 focus:ring-teal-500"
                />
                <span className="text-sm text-slate-200">
                  Riproduzione automatica audio
                </span>
              </label>
            </div>

            {/* Info */}
            <div className="pt-4 border-t border-slate-700 text-xs text-slate-500 space-y-1">
              <p>
                <strong>Assistente:</strong> Paola
              </p>
              <p>
                <strong>AI:</strong> FLUXION AI
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
