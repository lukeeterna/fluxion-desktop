"""
Fluxion Latency Optimizer - Enterprise Voice Agent Performance Kit
==================================================================

Implementazione Best Practice 2026 da Reddit r/LLMDevs:
- Streaming LLM tokens to TTS (no wait for full completion)
- Connection pooling/reuse per Groq/STT/TTS
- Shorter prompts (<2k tokens)
- Model selection dinamico (mixtral-8x7b per semplici, llama-3.3-70b per complessi)

Target P95 Latency: <800ms (dal attuale ~1330ms)

Autore: Fluxion AI Architect
Data: 2026-02-11
"""

import asyncio
import time
import aiohttp
from typing import Dict, Any, Optional, AsyncGenerator, List, Callable
from dataclasses import dataclass, field
from collections import deque
import groq
from groq import Groq, AsyncGroq
import logging

logger = logging.getLogger(__name__)


@dataclass
class LatencyMetrics:
    """Metriche di latenza per un singolo turno."""
    vad_ms: float = 0.0
    stt_ms: float = 0.0
    nlu_ms: float = 0.0
    llm_ms: float = 0.0
    tts_ms: float = 0.0
    total_ms: float = 0.0
    tokens_per_second: float = 0.0
    first_token_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'vad_ms': self.vad_ms,
            'stt_ms': self.stt_ms,
            'nlu_ms': self.nlu_ms,
            'llm_ms': self.llm_ms,
            'tts_ms': self.tts_ms,
            'total_ms': self.total_ms,
            'tokens_per_second': self.tokens_per_second,
            'first_token_ms': self.first_token_ms,
        }


@dataclass
class StreamingChunk:
    """Chunk di testo pronto per TTS."""
    text: str
    is_final: bool = False
    latency_ms: float = 0.0


class FluxionConnectionPool:
    """
    Connection Pool per Groq API e servizi HTTP.
    
    Best Practice 2026:
    - Keep-alive persistent connections
    - Connection reuse per ridurre handshake TLS
    - Timeout ottimizzati per Voice AI
    """
    
    def __init__(
        self,
        groq_api_key: str,
        max_connections: int = 10,
        keep_alive_timeout: float = 30.0
    ):
        self.groq_api_key = groq_api_key
        self.max_connections = max_connections
        self.keep_alive_timeout = keep_alive_timeout
        
        # Groq client con connection pooling
        self._groq_client: Optional[AsyncGroq] = None
        self._groq_sync: Optional[Groq] = None
        
        # aiohttp session per HTTP calls
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        
        # Stats
        self._requests_count = 0
        self._connections_reused = 0
        
    async def initialize(self):
        """Inizializza il connection pool."""
        # TCP connector con keep-alive
        self._connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=5,
            enable_cleanup_closed=True,
            force_close=False,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        # Session con keep-alive headers
        self._session = aiohttp.ClientSession(
            connector=self._connector,
            headers={
                'Connection': 'keep-alive',
                'Keep-Alive': f'timeout={int(self.keep_alive_timeout)}',
            },
            timeout=aiohttp.ClientTimeout(
                total=60,
                connect=10,
                sock_read=30
            )
        )
        
        # Groq client async
        self._groq_client = AsyncGroq(
            api_key=self.groq_api_key,
            timeout=60.0,
        )
        
        # Groq client sync (per fallback)
        self._groq_sync = Groq(api_key=self.groq_api_key)
        
        logger.info(f"[FluxionConnectionPool] Initialized: max_conn={self.max_connections}")
        
    async def close(self):
        """Chiude tutte le connessioni."""
        if self._session:
            await self._session.close()
        if self._connector:
            await self._connector.close()
        logger.info(f"[FluxionConnectionPool] Closed. Requests: {self._requests_count}, Reused: {self._connections_reused}")
        
    @property
    def groq(self) -> AsyncGroq:
        """Restituisce il client Groq async."""
        if not self._groq_client:
            raise RuntimeError("Connection pool not initialized")
        return self._groq_client
        
    @property
    def groq_sync(self) -> Groq:
        """Restituisce il client Groq sync."""
        if not self._groq_sync:
            raise RuntimeError("Connection pool not initialized")
        return self._groq_sync
        
    @property
    def session(self) -> aiohttp.ClientSession:
        """Restituisce la session aiohttp."""
        if not self._session:
            raise RuntimeError("Connection pool not initialized")
        return self._session


class FluxionStreamingLLM:
    """
    Streaming LLM Handler - Stream tokens to TTS senza aspettare completion.
    
    Best Practice 2026:
    - Non aspettare LLM completion, stream tokens immediatamente
    - Buffering intelligente: yield su punteggiatura o buffer size
    - Parallel TTS: inizia sintesi vocale mentre LLM ancora genera
    
    Target: Ridurre Time-To-First-Audio (TTFA) del 40-50%
    """
    
    def __init__(
        self,
        connection_pool: FluxionConnectionPool,
        min_chunk_size: int = 30,
        max_chunk_size: int = 100,
        sentence_delimiters: List[str] = None
    ):
        self.pool = connection_pool
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.sentence_delimiters = sentence_delimiters or ['.', '!', '?', ';', ':', '\n']
        
        # Model selection strategy
        self.fast_model = "mixtral-8x7b-32768"  # Per turni semplici
        self.accurate_model = "llama-3.3-70b-versatile"  # Per complessi
        
    def _should_yield(self, buffer: str) -> bool:
        """Decide se fare yield del buffer corrente."""
        if len(buffer) >= self.max_chunk_size:
            return True
        if len(buffer) >= self.min_chunk_size:
            # Check per delimitatori di frase
            if any(d in buffer for d in self.sentence_delimiters):
                return True
            # Check per parole di transizione
            transition_words = [' e ', ' ma ', ' però ', ' quindi ', ' allora ']
            if any(w in buffer.lower() for w in transition_words):
                return True
        return False
        
    async def stream_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        use_fast_model: bool = False,
        max_tokens: int = 150,
        temperature: float = 0.3
    ) -> AsyncGenerator[StreamingChunk, None]:
        """
        Stream LLM response in TTS-ready chunks.
        
        Args:
            prompt: Il prompt per l'LLM
            context: Contesto conversazione
            use_fast_model: Usa mixtral-8x7b per latenza minore
            max_tokens: Max tokens da generare
            temperature: Temperatura sampling
            
        Yields:
            StreamingChunk: Chunk pronto per TTS
        """
        start_time = time.perf_counter()
        model = self.fast_model if use_fast_model else self.accurate_model
        
        # Ottimizzazione prompt: tronca se troppo lungo
        if len(prompt) > 4000:  # ~2000 tokens
            prompt = self._truncate_prompt(prompt, max_chars=3500)
            logger.warning(f"[FluxionStreamingLLM] Prompt troncato a 3500 chars")
        
        buffer = ""
        first_token_time = None
        total_tokens = 0
        
        try:
            stream = await self.pool.groq.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(context)},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            
            async for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                
                if first_token_time is None and delta:
                    first_token_time = time.perf_counter() - start_time
                
                buffer += delta
                total_tokens += len(delta.split()) if delta else 0
                
                # Yield su condizioni
                if self._should_yield(buffer):
                    # Trova il punto migliore per spezzare
                    split_point = self._find_split_point(buffer)
                    if split_point > 0:
                        to_yield = buffer[:split_point].strip()
                        buffer = buffer[split_point:].strip()
                        
                        if to_yield:
                            yield StreamingChunk(
                                text=to_yield,
                                is_final=False,
                                latency_ms=(time.perf_counter() - start_time) * 1000
                            )
            
            # Yield finale
            if buffer.strip():
                yield StreamingChunk(
                    text=buffer.strip(),
                    is_final=True,
                    latency_ms=(time.perf_counter() - start_time) * 1000
                )
                
            # Log metrics
            total_time = time.perf_counter() - start_time
            tps = total_tokens / total_time if total_time > 0 else 0
            logger.info(
                f"[FluxionStreamingLLM] Stream completo: "
                f"tokens={total_tokens}, time={total_time:.2f}s, "
                f"tps={tps:.1f}, first_token={first_token_time*1000:.1f}ms"
            )
            
        except Exception as e:
            logger.error(f"[FluxionStreamingLLM] Errore streaming: {e}")
            # Fallback: ritorna risposta completa
            try:
                response = await self.pool.groq.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt(context)},
                        {"role": "user", "content": prompt}
                    ],
                    stream=False,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                text = response.choices[0].message.content
                yield StreamingChunk(
                    text=text,
                    is_final=True,
                    latency_ms=(time.perf_counter() - start_time) * 1000
                )
            except Exception as e2:
                logger.error(f"[FluxionStreamingLLM] Fallback fallito: {e2}")
                raise
                
    def _find_split_point(self, text: str) -> int:
        """Trova il miglior punto per spezzare il testo."""
        # Cerca delimitatori
        for delim in ['. ', '! ', '? ', '; ', ': ', '\n']:
            idx = text.rfind(delim, 0, self.max_chunk_size)
            if idx > self.min_chunk_size:
                return idx + len(delim)
        
        # Cerca spazi
        if len(text) > self.max_chunk_size:
            idx = text.rfind(' ', self.min_chunk_size, self.max_chunk_size)
            if idx > 0:
                return idx + 1
        
        return len(text)
        
    def _truncate_prompt(self, prompt: str, max_chars: int) -> str:
        """Tronca il prompt mantenendo contesto importante."""
        # Mantieni le prime 500 chars (istruzioni) e ultime 2500 (contesto recente)
        if len(prompt) <= max_chars:
            return prompt
        
        prefix = prompt[:500]
        suffix = prompt[-(max_chars - 500):]
        return prefix + "\n... [contesto troncato per brevità] ...\n" + suffix
        
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Genera system prompt ottimizzato."""
        base = """Sei Sara, assistente vocale di Fluxion. 
Rispondi in modo naturale e conciso per la conversazione vocale.
Usa frasi corte e dirette."""
        
        if context.get('verticale'):
            base += f"\nContesto: {context['verticale']}"
        if context.get('cliente'):
            base += f"\nCliente: {context['cliente']}"
            
        return base


class FluxionLatencyOptimizer:
    """
    Ottimizzatore di latenza principale - Coordina tutte le ottimizzazioni.
    
    Features:
    - Connection pooling
    - Streaming LLM
    - Model selection dinamica
    - Prompt compression
    - Metrics tracking
    """
    
    def __init__(self, groq_api_key: str):
        self.api_key = groq_api_key
        self.pool = FluxionConnectionPool(groq_api_key)
        self.streaming = None  # Inizializzato in setup()
        
        # Metrics tracking
        self._metrics_history: deque = deque(maxlen=1000)
        self._current_metrics: Optional[LatencyMetrics] = None
        
    async def setup(self):
        """Setup iniziale dell'optimizer."""
        await self.pool.initialize()
        self.streaming = FluxionStreamingLLM(self.pool)
        logger.info("[FluxionLatencyOptimizer] Setup completo")
        
    async def shutdown(self):
        """Cleanup."""
        await self.pool.close()
        logger.info("[FluxionLatencyOptimizer] Shutdown completo")
        
    def start_tracking(self) -> LatencyMetrics:
        """Inizia tracking latenza per un nuovo turno."""
        self._current_metrics = LatencyMetrics()
        return self._current_metrics
        
    def record_metric(self, component: str, ms: float):
        """Registra metrica per componente."""
        if self._current_metrics:
            setattr(self._current_metrics, f"{component}_ms", ms)
            
    def end_tracking(self) -> LatencyMetrics:
        """Finisce tracking e salva metriche."""
        if self._current_metrics:
            self._current_metrics.total_ms = (
                self._current_metrics.vad_ms +
                self._current_metrics.stt_ms +
                self._current_metrics.nlu_ms +
                self._current_metrics.llm_ms +
                self._current_metrics.tts_ms
            )
            self._metrics_history.append(self._current_metrics)
            return self._current_metrics
        return LatencyMetrics()
        
    def get_stats(self, window: int = 100) -> Dict[str, Any]:
        """Restituisce statistiche latenza."""
        recent = list(self._metrics_history)[-window:]
        if not recent:
            return {}
            
        totals = [m.total_ms for m in recent]
        llm_times = [m.llm_ms for m in recent]
        
        return {
            'avg_total_ms': sum(totals) / len(totals),
            'p95_total_ms': sorted(totals)[int(len(totals) * 0.95)],
            'p99_total_ms': sorted(totals)[int(len(totals) * 0.99)],
            'avg_llm_ms': sum(llm_times) / len(llm_times),
            'min_total_ms': min(totals),
            'max_total_ms': max(totals),
            'samples': len(recent),
        }
        
    async def optimize_llm_call(
        self,
        prompt: str,
        context: Dict[str, Any],
        complexity: str = "auto"  # "simple", "complex", "auto"
    ) -> AsyncGenerator[StreamingChunk, None]:
        """
        Chiama LLM con ottimizzazioni automatiche.
        
        Args:
            prompt: Prompt per LLM
            context: Contesto conversazione
            complexity: "simple" usa modello veloce, "complex" usa accurato, "auto" decide
        """
        use_fast = complexity == "simple"
        if complexity == "auto":
            # Euristiche per determinare complessità
            use_fast = self._is_simple_query(prompt, context)
            
        async for chunk in self.streaming.stream_response(
            prompt=prompt,
            context=context,
            use_fast_model=use_fast
        ):
            yield chunk
            
    def _is_simple_query(self, prompt: str, context: Dict) -> bool:
        """Determina se una query è semplice (usa modello veloce)."""
        # Query semplici: conferme, rifiuti, info base
        simple_patterns = [
            'sì', 'no', 'va bene', 'confermo', 'cancella',
            'orari', 'prezzi', 'dove siete', 'grazie'
        ]
        prompt_lower = prompt.lower()
        
        if any(p in prompt_lower for p in simple_patterns):
            return True
            
        # Se il contesto ha già tutti i dati, è semplice
        if context.get('state') in ['confirming', 'waiting_time']:
            return True
            
        return False


# Singleton globale
_optimizer: Optional[FluxionLatencyOptimizer] = None


async def get_optimizer(api_key: Optional[str] = None) -> FluxionLatencyOptimizer:
    """Restituisce singleton optimizer."""
    global _optimizer
    if _optimizer is None:
        if api_key is None:
            import os
            api_key = os.getenv('GROQ_API_KEY')
        _optimizer = FluxionLatencyOptimizer(api_key)
        await _optimizer.setup()
    return _optimizer


async def shutdown_optimizer():
    """Shutdown globale."""
    global _optimizer
    if _optimizer:
        await _optimizer.shutdown()
        _optimizer = None


# =============================================================================
# TEST
# =============================================================================

async def test_latency_optimizer():
    """Test dell'optimizer."""
    import os
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("[TEST] GROQ_API_KEY non impostata, salto test")
        return
        
    print("[TEST] Inizializzazione FluxionLatencyOptimizer...")
    opt = await get_optimizer(api_key)
    
    print("[TEST] Test streaming LLM...")
    context = {'verticale': 'salone', 'cliente': 'Mario Rossi'}
    
    start = time.perf_counter()
    chunks = []
    async for chunk in opt.optimize_llm_call(
        "Saluta il cliente e chiedi che servizio desidera",
        context,
        complexity="simple"
    ):
        chunks.append(chunk.text)
        print(f"  Chunk ({chunk.latency_ms:.1f}ms): {chunk.text[:50]}...")
        
    total_time = (time.perf_counter() - start) * 1000
    full_response = " ".join(chunks)
    
    print(f"\n[TEST] Risultato:")
    print(f"  - Chunk ricevuti: {len(chunks)}")
    print(f"  - Tempo totale: {total_time:.1f}ms")
    print(f"  - Risposta: {full_response[:100]}...")
    
    # Stats
    stats = opt.get_stats()
    print(f"\n[TEST] Stats: {stats}")
    
    await shutdown_optimizer()
    print("[TEST] Completato!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_latency_optimizer())
