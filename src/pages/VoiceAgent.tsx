// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Agent Page — Sara UI v2
// Waveform hero + booking confirmation modal
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
  Lock,
  Sparkles,
  X,
  Calendar,
  UserCheck,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import { useLicenseStatusEd25519 } from '@/hooks/use-license-ed25519';
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
// Waveform Hero
// ───────────────────────────────────────────────────────────────────

function WaveformHero({
  audioLevel,
  isSpeaking,
  isPlaying,
  isRecording,
  isProcessing,
  isRunning,
}: {
  audioLevel: number;
  isSpeaking: boolean;
  isPlaying: boolean;
  isRecording: boolean;
  isProcessing: boolean;
  isRunning: boolean;
}) {
  const BARS = 48;

  const getBarHeight = (i: number) => {
    const center = BARS / 2;
    const dist = Math.abs(i - center) / center; // 0=center, 1=edge
    const envelope = 1 - dist * 0.6; // bars taper at edges

    if (isProcessing) {
      // Thinking: gentle pulse
      return (Math.sin(Date.now() / 300 + i * 0.4) * 0.5 + 0.5) * 30 * envelope + 4;
    }
    if (isPlaying || (isRecording && isSpeaking)) {
      // Sara speaking or user speaking loud: react to audioLevel
      const noise = Math.sin(Date.now() / 80 + i * 0.7) * 0.3 + 0.7;
      return Math.max(4, audioLevel * 80 * envelope * noise + 6);
    }
    if (isRecording) {
      // Listening: low idle pulse
      return (Math.sin(Date.now() / 600 + i * 0.5) * 0.5 + 0.5) * 12 * envelope + 3;
    }
    // Idle: very subtle breathing
    return (Math.sin(Date.now() / 1200 + i * 0.3) * 0.5 + 0.5) * 8 * envelope + 2;
  };

  const barColor = () => {
    if (isPlaying) return '#2dd4bf'; // teal — Sara speaking
    if (isRecording && isSpeaking) return '#4ade80'; // green — user speaking
    if (isRecording) return '#67e8f9'; // cyan — listening
    if (isProcessing) return '#818cf8'; // indigo — thinking
    return '#0f766e'; // dark teal — idle
  };

  const glowColor = () => {
    if (isPlaying) return 'rgba(45,212,191,0.25)';
    if (isRecording && isSpeaking) return 'rgba(74,222,128,0.2)';
    if (isRecording) return 'rgba(103,232,249,0.15)';
    if (isProcessing) return 'rgba(129,140,248,0.2)';
    return 'rgba(15,118,110,0.1)';
  };

  const [, forceUpdate] = useState(0);
  useEffect(() => {
    const id = setInterval(() => forceUpdate((n) => n + 1), 50);
    return () => clearInterval(id);
  }, []);

  if (!isRunning) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 h-full">
        <div className="w-24 h-24 rounded-full bg-slate-800 border-2 border-slate-700 flex items-center justify-center">
          <Mic className="w-10 h-10 text-slate-600" />
        </div>
        <p className="text-slate-500 text-sm">Avvia Sara per iniziare</p>
      </div>
    );
  }

  return (
    <div
      className="flex flex-col items-center justify-center gap-6 h-full"
      style={{ filter: `drop-shadow(0 0 24px ${glowColor()})` }}
    >
      {/* Waveform bars */}
      <div className="flex items-center gap-[3px] h-24">
        {Array.from({ length: BARS }).map((_, i) => (
          <div
            key={i}
            className="rounded-full transition-none"
            style={{
              width: 3,
              height: `${getBarHeight(i)}px`,
              background: barColor(),
              opacity: 0.85 + Math.abs(i - BARS / 2) / BARS * -0.3,
            }}
          />
        ))}
      </div>

      {/* Center orb with mic */}
      <div
        className="relative w-20 h-20 rounded-full flex items-center justify-center"
        style={{
          background: `radial-gradient(circle, ${barColor()}33 0%, transparent 70%)`,
          border: `1.5px solid ${barColor()}66`,
          boxShadow: `0 0 32px ${glowColor()}, inset 0 0 16px ${glowColor()}`,
        }}
      >
        {isProcessing ? (
          <Loader2 className="w-8 h-8 animate-spin" style={{ color: barColor() }} />
        ) : isPlaying ? (
          <Volume2 className="w-8 h-8 animate-pulse" style={{ color: barColor() }} />
        ) : isRecording && isSpeaking ? (
          <Mic className="w-8 h-8 animate-pulse" style={{ color: barColor() }} />
        ) : isRecording ? (
          <Mic className="w-8 h-8" style={{ color: barColor() }} />
        ) : (
          <Bot className="w-8 h-8" style={{ color: barColor() }} />
        )}
      </div>

      {/* Status label */}
      <p className="text-xs font-medium tracking-widest uppercase" style={{ color: barColor() }}>
        {isProcessing
          ? 'Elaborando...'
          : isPlaying
            ? 'Sara sta parlando'
            : isRecording && isSpeaking
              ? 'Parlando...'
              : isRecording
                ? 'In ascolto...'
                : 'Pronta'}
      </p>
    </div>
  );
}

// ───────────────────────────────────────────────────────────────────
// Booking Confirmation Modal
// ───────────────────────────────────────────────────────────────────

function BookingConfirmedModal({
  message,
  onClose,
}: {
  message: ChatMessage;
  onClose: () => void;
}) {
  // Extract service/operator hints from Sara's last message
  const text = message.content;
  const serviceMatch = text.match(/(?:per|servizio[:\s]+|appuntamento[:\s]+)([^\n,\.]{3,30})/i);
  const operatorMatch = text.match(/(?:con|operatore[:\s]+)([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)/);

  return (
    <div className="absolute bottom-4 right-4 z-50 animate-in slide-in-from-bottom-4 fade-in duration-300">
      <Card className="w-72 bg-slate-800 border-slate-600 shadow-2xl">
        <CardHeader className="pb-3 pt-4 px-4 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <CardTitle className="text-sm text-white">Prenotazione Confermata</CardTitle>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </CardHeader>
        <CardContent className="px-4 pb-4 space-y-3">
          {serviceMatch && (
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <Calendar className="w-4 h-4 text-teal-400 flex-shrink-0" />
              <span className="capitalize">{serviceMatch[1].trim()}</span>
            </div>
          )}
          {operatorMatch && (
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <UserCheck className="w-4 h-4 text-teal-400 flex-shrink-0" />
              <span>{operatorMatch[1].trim()}</span>
            </div>
          )}
          <p className="text-xs text-slate-400 bg-slate-900/50 rounded p-2 leading-relaxed">
            {text.length > 120 ? text.slice(0, 120) + '…' : text}
          </p>
          <Button
            size="sm"
            className="w-full bg-teal-600 hover:bg-teal-700 text-white"
            onClick={onClose}
          >
            Ok, grazie
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

// ───────────────────────────────────────────────────────────────────
// Lock Screen (Base tier)
// ───────────────────────────────────────────────────────────────────

function VoiceAgentBloccato({ tier }: { tier: string }) {
  return (
    <div className="h-full flex items-center justify-center p-6">
      <Card className="bg-slate-800 border-slate-700 max-w-md w-full">
        <CardHeader className="flex flex-row items-center gap-3">
          <div className="p-2 bg-amber-500/20 rounded-lg">
            <Lock className="w-6 h-6 text-amber-500" />
          </div>
          <div>
            <CardTitle className="text-white">Voice Agent Non Disponibile</CardTitle>
            <p className="text-sm text-slate-400">Aggiorna la tua licenza per sbloccare</p>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-slate-900 p-4 rounded-lg text-center">
            <p className="text-slate-300 mb-2">
              Il Voice Agent <span className="text-amber-400 font-medium">"Sara"</span> è disponibile
              nei piani <span className="text-teal-400 font-medium">Pro</span> e{' '}
              <span className="text-teal-400 font-medium">Clinic</span>.
            </p>
            <p className="text-slate-500 text-sm">
              Piano attuale: <span className="text-cyan-400">{tier}</span>
            </p>
          </div>
          <div className="flex justify-center">
            <Button className="bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700">
              <Sparkles className="w-4 h-4 mr-2" />
              Aggiorna Licenza
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ───────────────────────────────────────────────────────────────────
// Main Component
// ───────────────────────────────────────────────────────────────────

export function VoiceAgent() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [autoPlay, setAutoPlay] = useState(true);
  const [useVAD, setUseVAD] = useState(true);
  const [isConversationEnded, setIsConversationEnded] = useState(false);
  const [bookingConfirmed, setBookingConfirmed] = useState<ChatMessage | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Hooks
  const { data: licenseStatus, isLoading: isLoadingLicense } = useLicenseStatusEd25519();
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
  const audioLevel = useVAD ? vadRecorder.state.audioLevel : audioRecorder.state.audioLevel;

  // Auto-greet when pipeline is already running but no messages
  useEffect(() => {
    if (isRunning && messages.length === 0 && !greet.isPending && !statusLoading) {
      greet.mutateAsync()
        .then(handleVoiceResponse)
        .catch((err) => {
          addError(`Errore nel saluto: ${err instanceof Error ? err.message : String(err)}`);
        });
    }
  }, [isRunning, statusLoading]);  

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const addError = (content: string) => {
    setMessages((prev) => [...prev, {
      id: window.crypto.randomUUID(),
      role: 'error',
      content,
      timestamp: new Date(),
    }]);
  };

  const handleStart = async () => {
    try {
      await startPipeline.mutateAsync();
      setTimeout(async () => {
        try {
          handleVoiceResponse(await greet.mutateAsync());
        } catch (e) {
          addError(`Errore nel saluto: ${e instanceof Error ? e.message : String(e)}`);
        }
      }, 2000);
    } catch (error) {
      addError(`Impossibile avviare Voice Agent: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const handleStop = async () => {
    try {
      await stopPipeline.mutateAsync();
      setMessages([]);
      setBookingConfirmed(null);
    } catch (error) {
      console.error('Failed to stop pipeline:', error);
    }
  };

  const handleVoiceResponse = async (response: VoiceResponse) => {
    if (!response.success || !response.response) {
      addError(response.error || 'Nessuna risposta dal Voice Agent');
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

    // Booking confirmed modal
    if (response.intent === 'completed' || response.intent === 'confirming') {
      setBookingConfirmed(message);
    }

    if (response.should_exit) {
      setIsConversationEnded(true);
    }

    if (autoPlay && response.audio_base64) {
      setIsPlaying(true);
      try {
        const timeout = new Promise<void>((_, reject) => setTimeout(() => reject(new Error('timeout')), 30000));
        await Promise.race([playAudioFromHex(response.audio_base64), timeout]);
      } catch (e) {
        console.error('Audio playback failed:', e);
      }
      setIsPlaying(false);
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() || !isRunning || isProcessing || isConversationEnded) return;

    const userMessage: ChatMessage = {
      id: window.crypto.randomUUID(),
      role: 'user',
      content: inputText.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputText('');

    try {
      handleVoiceResponse(await processText.mutateAsync(inputText.trim()));
    } catch (error) {
      console.error('Failed to process text:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handlePlayAudio = async (audioHex: string) => {
    setIsPlaying(true);
    try { await playAudioFromHex(audioHex); } catch (e) { console.error(e); }
    setIsPlaying(false);
  };

  const handleReset = async () => {
    try {
      await resetConversation.mutateAsync();
      setMessages([]);
      setIsConversationEnded(false);
      setBookingConfirmed(null);
      handleVoiceResponse(await greet.mutateAsync());
    } catch (error) {
      console.error('Failed to reset:', error);
    }
  };

  const handleMicClick = async () => {
    if (isRecording) {
      const audioHex = useVAD
        ? await vadRecorder.stopListening()
        : await audioRecorder.stopRecording();

      if (audioHex) {
        const placeholder: ChatMessage = {
          id: window.crypto.randomUUID(),
          role: 'user',
          content: useVAD ? '(parlato rilevato...)' : '(registrazione audio...)',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, placeholder]);
        try {
          const response = await processAudio.mutateAsync(audioHex);
          if (response.transcription) {
            setMessages((prev) =>
              prev.map((m) => m.id === placeholder.id ? { ...m, content: response.transcription ?? m.content } : m)
            );
          }
          handleVoiceResponse(response);
        } catch (error) {
          addError(`Errore elaborazione audio: ${error instanceof Error ? error.message : String(error)}`);
        }
      }
    } else {
      if (useVAD) await vadRecorder.startListening();
      else await audioRecorder.startRecording();
    }
  };

  // Feature gate
  if (!isLoadingLicense && licenseStatus?.features.voice_agent === false) {
    return <VoiceAgentBloccato tier={licenseStatus?.tier_display ?? 'Base'} />;
  }

  return (
    <div className="h-full flex flex-col p-6 gap-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          {/* Sara avatar */}
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-400 to-cyan-600 flex items-center justify-center shadow-lg shadow-teal-500/20">
            <span className="text-sm font-bold text-white">S</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Sara</h1>
            <p className="text-xs text-slate-400">Voice Agent · Prenotazioni 24/7</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge
            className={cn(
              'gap-1.5',
              isRunning
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-700 text-slate-400'
            )}
          >
            {isRunning ? (
              <><CheckCircle2 className="w-3 h-3" />Attiva</>
            ) : (
              <><AlertCircle className="w-3 h-3" />Inattiva</>
            )}
          </Badge>
          {isRunning ? (
            <Button variant="destructive" size="sm" onClick={handleStop} disabled={stopPipeline.isPending}>
              {stopPipeline.isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <PowerOff className="w-4 h-4 mr-2" />}
              Ferma
            </Button>
          ) : (
            <Button size="sm" onClick={handleStart} disabled={startPipeline.isPending} className="bg-teal-600 hover:bg-teal-700">
              {startPipeline.isPending ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Power className="w-4 h-4 mr-2" />}
              Avvia
            </Button>
          )}
        </div>
      </div>

      {/* Main layout: left transcript | center waveform */}
      <div className="flex-1 grid grid-cols-5 gap-4 min-h-0">

        {/* LEFT — Transcript */}
        <Card className="col-span-2 bg-slate-800/50 border-slate-700 flex flex-col">
          <CardHeader className="border-b border-slate-700 py-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm flex items-center gap-2">
                <Bot className="w-4 h-4 text-teal-400" />
                Conversazione
              </CardTitle>
              {isRunning && (
                <Button variant="ghost" size="sm" onClick={handleReset} disabled={resetConversation.isPending} className="h-7 px-2 text-xs">
                  <RefreshCw className={cn('w-3 h-3 mr-1', resetConversation.isPending && 'animate-spin')} />
                  Reset
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col p-0 min-h-0">
            <ScrollArea data-testid="voice-transcript" className="flex-1 p-3" ref={scrollRef}>
              {!isRunning ? (
                <div className="h-32 flex items-center justify-center text-slate-600 text-sm text-center px-4">
                  Avvia Sara per iniziare una conversazione
                </div>
              ) : messages.length === 0 ? (
                <div className="h-32 flex items-center justify-center">
                  <Loader2 className="w-6 h-6 animate-spin text-slate-500" />
                </div>
              ) : (
                <div className="space-y-3">
                  {messages.map((message) => (
                    <div key={message.id} className={cn('flex gap-2', message.role === 'user' ? 'justify-end' : 'justify-start')}>
                      {message.role === 'assistant' && (
                        <div className={cn(
                          'w-6 h-6 rounded-full bg-teal-500/20 flex items-center justify-center flex-shrink-0 mt-0.5',
                          isPlaying && 'shadow-[0_0_8px_rgba(20,184,166,0.5)] animate-pulse'
                        )}>
                          <Bot className="w-3 h-3 text-teal-400" />
                        </div>
                      )}
                      {message.role === 'error' && (
                        <div className="w-6 h-6 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <AlertCircle className="w-3 h-3 text-red-400" />
                        </div>
                      )}
                      <div className={cn(
                        'max-w-[85%] rounded-lg px-3 py-1.5 text-sm',
                        message.role === 'user' ? 'bg-teal-600 text-white'
                          : message.role === 'error' ? 'bg-red-900/50 text-red-200 border border-red-700/50'
                            : 'bg-slate-700 text-slate-100'
                      )}>
                        <p className="leading-relaxed">{message.content}</p>
                        <div className="flex items-center gap-1 mt-1">
                          {message.intent && (
                            <Badge variant="outline" className="text-[10px] h-4 border-slate-600 px-1">
                              {message.intent}
                            </Badge>
                          )}
                          {message.audioHex && (
                            <button
                              onClick={() => handlePlayAudio(message.audioHex!)}
                              disabled={isPlaying}
                              className="text-slate-400 hover:text-slate-200 disabled:opacity-50"
                            >
                              <Volume2 className="w-3 h-3" />
                            </button>
                          )}
                          <span className="text-[10px] text-slate-500 ml-auto">
                            {message.timestamp.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      </div>
                      {message.role === 'user' && (
                        <div className="w-6 h-6 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <User className="w-3 h-3 text-slate-300" />
                        </div>
                      )}
                    </div>
                  ))}
                  {isProcessing && (
                    <div className="flex gap-2">
                      <div className="w-6 h-6 rounded-full bg-teal-500/20 flex items-center justify-center">
                        <Bot className="w-3 h-3 text-teal-400" />
                      </div>
                      <div className="bg-slate-700 rounded-lg px-3 py-1.5">
                        <Loader2 className="w-3 h-3 animate-spin text-slate-400" />
                      </div>
                    </div>
                  )}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* CENTER + RIGHT — Waveform hero */}
        <div className="col-span-3 flex flex-col gap-4 min-h-0 relative">
          <Card className="flex-1 bg-slate-900/80 border-slate-700 relative overflow-hidden">
            {/* Background glow */}
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                background: isRunning
                  ? `radial-gradient(ellipse at 50% 50%, ${isPlaying ? 'rgba(45,212,191,0.06)' : isRecording ? 'rgba(103,232,249,0.04)' : 'rgba(15,118,110,0.04)'} 0%, transparent 70%)`
                  : 'none',
              }}
            />
            <CardContent className="h-full p-6 flex flex-col items-center justify-center">
              <WaveformHero
                audioLevel={audioLevel}
                isSpeaking={isSpeaking}
                isPlaying={isPlaying}
                isRecording={isRecording}
                isProcessing={isProcessing}
                isRunning={isRunning}
              />
            </CardContent>

            {/* Booking confirmed modal */}
            {bookingConfirmed && (
              <BookingConfirmedModal
                message={bookingConfirmed}
                onClose={() => setBookingConfirmed(null)}
              />
            )}
          </Card>

          {/* Input bar */}
          <Card className="bg-slate-800/50 border-slate-700 flex-shrink-0">
            <CardContent className="p-3">
              {/* Recording indicator */}
              {isRecording && (
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex items-center gap-[2px] h-4">
                    {[0.6, 1.0, 0.8, 0.95, 0.7].map((f, i) => (
                      <div
                        key={i}
                        className={cn('w-[2px] rounded-full transition-all duration-75', isSpeaking ? 'bg-green-400' : 'bg-teal-400')}
                        style={{ height: `${Math.max(2, audioLevel * f * 16)}px` }}
                      />
                    ))}
                  </div>
                  <span className={cn('text-xs', isSpeaking ? 'text-green-400' : 'text-teal-400')}>
                    {isSpeaking ? 'Parlando...' : 'In ascolto...'}{' '}
                    {useVAD ? vadRecorder.state.duration : audioRecorder.state.duration}s
                  </span>
                  {useVAD && (
                    <div className="flex-1 h-1 bg-slate-700 rounded-full overflow-hidden mx-2">
                      <div
                        className={cn('h-full transition-all duration-100', vadProbability > 0.5 ? 'bg-green-500' : 'bg-yellow-500')}
                        style={{ width: `${Math.max(0, vadProbability) * 100}%` }}
                      />
                    </div>
                  )}
                  <button
                    onClick={() => useVAD ? vadRecorder.cancelListening() : audioRecorder.cancelRecording()}
                    className="text-slate-400 hover:text-slate-200 ml-auto flex items-center gap-1 text-xs"
                  >
                    <Square className="w-3 h-3" /> Annulla
                  </button>
                </div>
              )}
              {(audioRecorder.state.error || vadRecorder.state.error) && (
                <p className="text-xs text-red-400 mb-2">{audioRecorder.state.error || vadRecorder.state.error}</p>
              )}
              {isConversationEnded && (
                <div className="mb-2 flex items-center gap-2 text-xs text-teal-400 bg-teal-500/10 border border-teal-500/30 rounded px-2 py-1.5">
                  <CheckCircle2 className="w-3 h-3 flex-shrink-0" />
                  Conversazione terminata — premi Reset per iniziare una nuova chiamata.
                </div>
              )}
              <div className="flex gap-2 items-center">
                {/* VAD/Auto-play toggles compact */}
                <div className="flex gap-2 text-xs text-slate-500 mr-1">
                  <label className="flex items-center gap-1 cursor-pointer">
                    <input type="checkbox" checked={useVAD} onChange={(e) => setUseVAD(e.target.checked)} disabled={isRecording} className="w-3 h-3 rounded" />
                    VAD
                  </label>
                  <label className="flex items-center gap-1 cursor-pointer">
                    <input type="checkbox" checked={autoPlay} onChange={(e) => setAutoPlay(e.target.checked)} className="w-3 h-3 rounded" />
                    Audio
                  </label>
                </div>

                {/* Mic button */}
                <div className="relative flex items-center justify-center">
                  {isRecording && (
                    <span className={cn('absolute inset-0 rounded-md mic-pulse-ring', isSpeaking ? 'bg-green-500/40' : 'bg-teal-500/40')} />
                  )}
                  <Button
                    data-testid="btn-voice-mic"
                    onClick={handleMicClick}
                    disabled={!isRunning || isProcessing || isConversationEnded}
                    variant={isRecording ? (isSpeaking ? 'default' : 'destructive') : 'outline'}
                    size="sm"
                    className={cn(
                      'relative z-10',
                      isRecording
                        ? isSpeaking ? 'bg-green-600 hover:bg-green-700 border-green-600' : 'bg-teal-600 hover:bg-teal-700 border-teal-600'
                        : 'border-slate-600 hover:bg-slate-700'
                    )}
                  >
                    {(audioRecorder.state.isPreparing || vadRecorder.state.isPreparing) ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </Button>
                </div>

                <Input
                  data-testid="input-voice-text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder={
                    isConversationEnded ? 'Conversazione terminata — premi Reset'
                      : isRecording ? 'Parla ora...'
                        : isRunning ? 'Scrivi o usa il microfono...'
                          : 'Avvia Sara per iniziare'
                  }
                  disabled={!isRunning || isProcessing || isRecording || isConversationEnded}
                  className="bg-slate-700 border-slate-600 text-sm h-9"
                />
                <Button
                  data-testid="btn-send-voice"
                  onClick={handleSend}
                  disabled={!isRunning || !inputText.trim() || isProcessing || isRecording || isConversationEnded}
                  size="sm"
                  className="bg-teal-600 hover:bg-teal-700 h-9"
                >
                  {isProcessing && !isRecording ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
