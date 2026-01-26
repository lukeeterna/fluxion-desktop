// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Agent Page
// Chat interface for voice assistant "Sara"
// ═══════════════════════════════════════════════════════════════════

import { useState, useRef, useEffect } from 'react';
import {
  Mic,
  MicOff,
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
  Square,
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
  useVoiceProcessAudio,
  useVoiceGreet,
  useVoiceResetConversation,
  useAudioRecorder,
  useVADRecorder,
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
  const [useVAD, setUseVAD] = useState(true); // Enable VAD by default
  const scrollRef = useRef<HTMLDivElement>(null);

  // Hooks
  const { data: status, isLoading: statusLoading } = useVoicePipelineStatus();
  const startPipeline = useStartVoicePipeline();
  const stopPipeline = useStopVoicePipeline();
  const processText = useVoiceProcessText();
  const processAudio = useVoiceProcessAudio();
  const greet = useVoiceGreet();
  const resetConversation = useVoiceResetConversation();
  const audioRecorder = useAudioRecorder();
  const vadRecorder = useVADRecorder();

  const isRunning = status?.running ?? false;
  const isProcessing = processText.isPending || processAudio.isPending || greet.isPending;
  const isRecording = useVAD ? vadRecorder.state.isListening : audioRecorder.state.isRecording;
  const isSpeaking = vadRecorder.state.isSpeaking;
  const vadProbability = vadRecorder.state.probability;

  // Debug: log state changes
  useEffect(() => {
    console.log('[VoiceAgent] State:', { isRunning, isProcessing, isPlaying, isRecording,
      useVAD, isSpeaking, vadProbability: vadProbability.toFixed(2),
      greetPending: greet.isPending, textPending: processText.isPending });
  }, [isRunning, isProcessing, isPlaying, isRecording, useVAD, isSpeaking, vadProbability, greet.isPending, processText.isPending]);

  // Auto-greet when pipeline is already running but no messages
  useEffect(() => {
    if (isRunning && messages.length === 0 && !greet.isPending && !statusLoading) {
      console.log('[VoiceAgent] Auto-greeting: pipeline running but no messages');
      greet.mutateAsync()
        .then(handleVoiceResponse)
        .catch((err) => {
          console.error('[VoiceAgent] Auto-greet failed:', err);
          const errorMessage: ChatMessage = {
            id: window.crypto.randomUUID(),
            role: 'error',
            content: `Errore nel saluto: ${err instanceof Error ? err.message : String(err)}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        });
    }
  }, [isRunning, statusLoading]); // Only trigger on initial load

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
    // Handle error responses - always add a message to stop spinner
    if (!response.success || !response.response) {
      const errorContent = response.error || 'Nessuna risposta dal Voice Agent';
      console.error('[VoiceAgent] handleVoiceResponse error:', errorContent);
      const errorMessage: ChatMessage = {
        id: window.crypto.randomUUID(),
        role: 'error',
        content: errorContent,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      return;
    }

    const message: ChatMessage = {
      id: window.crypto.randomUUID(),
      role: 'assistant',
      content: response.response,
      intent: response.intent ?? undefined,
      timestamp: new Date(),
      audioHex: response.audio_base64 ?? undefined,
    };
    setMessages((prev) => [...prev, message]);

    // Auto-play audio with timeout (max 30 seconds)
    if (autoPlay && response.audio_base64) {
      setIsPlaying(true);
      try {
        const timeoutPromise = new Promise<void>((_, reject) =>
          setTimeout(() => reject(new Error('Audio timeout')), 30000)
        );
        await Promise.race([
          playAudioFromHex(response.audio_base64),
          timeoutPromise
        ]);
      } catch (e) {
        console.error('Audio playback failed:', e);
      }
      setIsPlaying(false);
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

  // Handle microphone recording (supports both VAD and manual modes)
  const handleMicClick = async () => {
    console.log('[MicClick] clicked, isRecording:', isRecording, 'useVAD:', useVAD);

    if (isRecording) {
      // Stop recording and process audio
      console.log('[MicClick] stopping recording...');
      const audioHex = useVAD
        ? await vadRecorder.stopListening()
        : await audioRecorder.stopRecording();
      console.log('[MicClick] stopRecording returned, audioHex length:', audioHex?.length ?? 'null');

      if (audioHex) {
        // Add user message placeholder (will show transcription when received)
        const userMessage: ChatMessage = {
          id: window.crypto.randomUUID(),
          role: 'user',
          content: useVAD ? '(VAD: parlato rilevato...)' : '(Registrazione audio...)',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        console.log('[MicClick] added placeholder message, calling processAudio...');

        try {
          const response = await processAudio.mutateAsync(audioHex);
          console.log('[MicClick] processAudio response:', JSON.stringify(response, null, 2));

          // Update user message with transcription
          if (response.transcription) {
            console.log('[MicClick] updating message with transcription:', response.transcription);
            setMessages((prev) =>
              prev.map((m) =>
                m.id === userMessage.id
                  ? { ...m, content: response.transcription ?? m.content }
                  : m
              )
            );
          } else {
            console.log('[MicClick] NO transcription in response');
          }
          handleVoiceResponse(response);
        } catch (error) {
          console.error('[MicClick] processAudio FAILED:', error);
          const errorMessage: ChatMessage = {
            id: window.crypto.randomUUID(),
            role: 'error',
            content: `Errore elaborazione audio: ${error instanceof Error ? error.message : String(error)}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        }
      } else {
        console.log('[MicClick] audioHex is null/empty - no audio captured');
      }
    } else {
      // Start recording
      console.log('[MicClick] starting recording with', useVAD ? 'VAD' : 'manual', 'mode...');
      if (useVAD) {
        await vadRecorder.startListening();
      } else {
        await audioRecorder.startRecording();
      }
      console.log('[MicClick] recording started');
    }
  };

  return (
    <div className="h-full flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Voice Agent</h1>
          <p className="text-slate-400">
            Assistente vocale "Sara" per prenotazioni e informazioni
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
              {/* Recording indicator */}
              {isRecording && (
                <div className="flex items-center gap-2 mb-3">
                  {/* VAD indicator */}
                  {useVAD ? (
                    <>
                      <div className={cn(
                        'w-2 h-2 rounded-full',
                        isSpeaking ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
                      )} />
                      <span className={cn(
                        'text-sm',
                        isSpeaking ? 'text-green-400' : 'text-yellow-400'
                      )}>
                        {isSpeaking ? 'Parlando...' : 'In ascolto...'}
                        {' '}{vadRecorder.state.duration}s
                      </span>
                      {/* VAD probability bar */}
                      <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden mx-2">
                        <div
                          className={cn(
                            'h-full transition-all duration-100',
                            vadProbability > 0.5 ? 'bg-green-500' : 'bg-yellow-500'
                          )}
                          style={{ width: `${Math.max(0, vadProbability) * 100}%` }}
                        />
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                      <span className="text-sm text-red-400">
                        Registrazione in corso... {audioRecorder.state.duration}s
                      </span>
                    </>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => useVAD ? vadRecorder.cancelListening() : audioRecorder.cancelRecording()}
                    className="ml-auto text-slate-400 hover:text-slate-200"
                  >
                    <Square className="w-3 h-3 mr-1" />
                    Annulla
                  </Button>
                </div>
              )}
              {(audioRecorder.state.error || vadRecorder.state.error) && (
                <div className="mb-3 text-sm text-red-400">
                  {audioRecorder.state.error || vadRecorder.state.error}
                </div>
              )}
              <div className="flex gap-2">
                {/* Microphone Button */}
                <Button
                  data-testid="btn-voice-mic"
                  onClick={handleMicClick}
                  disabled={!isRunning || isProcessing}
                  variant={isRecording ? (isSpeaking ? 'default' : 'destructive') : 'outline'}
                  className={cn(
                    isRecording
                      ? isSpeaking
                        ? 'bg-green-600 hover:bg-green-700 border-green-600'
                        : 'bg-yellow-600 hover:bg-yellow-700 border-yellow-600'
                      : 'border-slate-600 hover:bg-slate-700'
                  )}
                >
                  {(audioRecorder.state.isPreparing || vadRecorder.state.isPreparing) ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : isRecording ? (
                    <MicOff className="w-4 h-4" />
                  ) : (
                    <Mic className="w-4 h-4" />
                  )}
                </Button>
                <Input
                  data-testid="input-voice-text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder={
                    isRecording
                      ? 'Parla ora...'
                      : isRunning
                        ? 'Scrivi o usa il microfono...'
                        : 'Avvia il Voice Agent per iniziare'
                  }
                  disabled={!isRunning || isProcessing || isRecording}
                  className="bg-slate-700 border-slate-600"
                />
                <Button
                  data-testid="btn-send-voice"
                  onClick={handleSend}
                  disabled={!isRunning || !inputText.trim() || isProcessing || isRecording}
                  className="bg-teal-600 hover:bg-teal-700"
                >
                  {isProcessing && !isRecording ? (
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

            {/* Microphone Status */}
            <div>
              <label className="text-sm text-slate-400">Microfono</label>
              <div className="flex items-center gap-2 mt-1">
                <div
                  className={cn(
                    'w-2 h-2 rounded-full',
                    isRecording
                      ? isSpeaking ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
                      : 'bg-slate-600'
                  )}
                />
                <span className="text-sm text-slate-200">
                  {isRecording
                    ? useVAD
                      ? isSpeaking
                        ? `Parlando (${vadRecorder.state.duration}s)`
                        : `In ascolto (${vadRecorder.state.duration}s)`
                      : `Registrazione (${audioRecorder.state.duration}s)`
                    : 'Pronto'}
                </span>
              </div>
              {/* VAD probability when active */}
              {isRecording && useVAD && (
                <div className="mt-2">
                  <div className="flex justify-between text-xs text-slate-500">
                    <span>Probabilità voce</span>
                    <span>{(vadProbability * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden mt-1">
                    <div
                      className={cn(
                        'h-full transition-all duration-100',
                        vadProbability > 0.5 ? 'bg-green-500' : vadProbability > 0 ? 'bg-yellow-500' : 'bg-slate-600'
                      )}
                      style={{ width: `${Math.max(0, vadProbability) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Settings toggles */}
            <div className="pt-4 border-t border-slate-700 space-y-3">
              {/* VAD toggle */}
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useVAD}
                  onChange={(e) => setUseVAD(e.target.checked)}
                  disabled={isRecording}
                  className="rounded border-slate-600 bg-slate-700 text-teal-500 focus:ring-teal-500"
                />
                <span className="text-sm text-slate-200">
                  VAD automatico
                </span>
              </label>
              {/* Auto-play toggle */}
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoPlay}
                  onChange={(e) => setAutoPlay(e.target.checked)}
                  className="rounded border-slate-600 bg-slate-700 text-teal-500 focus:ring-teal-500"
                />
                <span className="text-sm text-slate-200">
                  Riproduzione automatica
                </span>
              </label>
            </div>

            {/* Info */}
            <div className="pt-4 border-t border-slate-700 text-xs text-slate-500 space-y-1">
              <p>
                <strong>Assistente:</strong> Sara
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
