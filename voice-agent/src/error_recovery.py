"""
Error Recovery & Retry Logic Module.

Week 3 Day 3-4: VOICE-AGENT-RAG.md implementation
Provides retry with exponential backoff, fallback responses, and timeout handling.
"""

import asyncio
import functools
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

T = TypeVar('T')


class ErrorCategory(Enum):
    """Categories of errors for appropriate handling."""
    NETWORK = "network"           # Connection issues, timeouts
    SERVICE = "service"           # API errors, rate limits
    VALIDATION = "validation"     # Invalid input/output
    TIMEOUT = "timeout"           # Operation took too long
    UNKNOWN = "unknown"           # Unexpected errors


class RecoveryAction(Enum):
    """Actions to take when error occurs."""
    RETRY = "retry"               # Retry the operation
    FALLBACK = "fallback"         # Use fallback response
    ESCALATE = "escalate"         # Escalate to operator
    ABORT = "abort"               # Stop processing


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay_ms: int = 100
    max_delay_ms: int = 2000
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class TimeoutConfig:
    """Timeout configuration per layer."""
    layer_0_sentiment_ms: int = 100      # Sentiment analysis
    layer_1_exact_ms: int = 50           # Exact match
    layer_2_intent_ms: int = 100         # Intent classification
    layer_3_faq_ms: int = 500            # FAQ retrieval
    layer_4_groq_ms: int = 2000          # Groq LLM fallback
    total_max_ms: int = 3000             # Total pipeline timeout


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""
    success: bool
    value: Any
    attempts: int
    total_time_ms: float
    error: Optional[str]
    recovery_action: RecoveryAction


# Default configurations
DEFAULT_RETRY_CONFIG = RetryConfig()
DEFAULT_TIMEOUT_CONFIG = TimeoutConfig()


# =============================================================================
# Fallback Responses (Italian)
# =============================================================================

FALLBACK_RESPONSES: Dict[str, str] = {
    # By intent category
    "prenotazione": "Mi dispiace, ho avuto un problema tecnico. Può riprovare a dirmi quando vorrebbe prenotare?",
    "info": "Mi dispiace, non riesco a trovare l'informazione in questo momento. Può riprovare o contattarci al telefono?",
    "conferma": "Mi scusi, non ho capito bene. Può ripetere se conferma o meno?",
    "rifiuto": "D'accordo. C'è qualcos'altro che posso fare per lei?",
    "cortesia": "Prego, sono a sua disposizione.",
    "operatore": "La passo subito a un operatore. Un momento di pazienza...",
    "waitlist": "Mi dispiace, ho avuto un problema con la lista d'attesa. Può riprovare?",

    # By error type
    "network": "Mi dispiace, ho avuto un problema di connessione. Può riprovare tra qualche secondo?",
    "timeout": "Mi scusi, ci sta mettendo più tempo del previsto. Può riprovare?",
    "service": "Mi dispiace, il servizio non è disponibile in questo momento. Può riprovare tra poco?",
    "validation": "Mi scusi, non ho capito bene. Può ripetere per favore?",

    # Generic fallback
    "default": "Mi dispiace, ho avuto un problema. Può riprovare o preferisce parlare con un operatore?",
}

# Escalation responses when multiple retries fail
ESCALATION_RESPONSES: Dict[str, str] = {
    "max_retries": "Mi dispiace, sto avendo difficoltà tecniche. La metto in contatto con un operatore.",
    "timeout": "Mi scusi per l'attesa. La passo a un operatore che potrà aiutarla meglio.",
    "critical": "Mi dispiace per il disagio. Un operatore sarà con lei tra poco.",
}


def get_fallback_response(
    intent: Optional[str] = None,
    error_category: Optional[ErrorCategory] = None,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Get appropriate fallback response based on context.

    Args:
        intent: Current intent category
        error_category: Type of error that occurred
        context: Additional context (e.g., phone number, business name)

    Returns:
        Fallback response string
    """
    # Try intent-specific response first
    if intent and intent.lower() in FALLBACK_RESPONSES:
        response = FALLBACK_RESPONSES[intent.lower()]
    # Try error-specific response
    elif error_category and error_category.value in FALLBACK_RESPONSES:
        response = FALLBACK_RESPONSES[error_category.value]
    else:
        response = FALLBACK_RESPONSES["default"]

    # Substitute context variables if provided
    if context:
        for key, value in context.items():
            response = response.replace(f"{{{key}}}", str(value))

    return response


def get_escalation_response(reason: str = "max_retries") -> str:
    """Get escalation message when recovery fails."""
    return ESCALATION_RESPONSES.get(reason, ESCALATION_RESPONSES["max_retries"])


# =============================================================================
# Retry Logic with Exponential Backoff
# =============================================================================

def calculate_delay(
    attempt: int,
    config: RetryConfig = DEFAULT_RETRY_CONFIG
) -> float:
    """
    Calculate delay for retry attempt using exponential backoff.

    Args:
        attempt: Current attempt number (0-indexed)
        config: Retry configuration

    Returns:
        Delay in seconds
    """
    import random

    # Exponential backoff
    delay_ms = config.base_delay_ms * (config.exponential_base ** attempt)

    # Cap at max delay
    delay_ms = min(delay_ms, config.max_delay_ms)

    # Add jitter (±25% randomization)
    if config.jitter:
        jitter_range = delay_ms * 0.25
        delay_ms += random.uniform(-jitter_range, jitter_range)

    return max(0, delay_ms / 1000)  # Convert to seconds


async def retry_with_backoff(
    func: Callable[..., T],
    *args,
    config: RetryConfig = DEFAULT_RETRY_CONFIG,
    error_handler: Optional[Callable[[Exception, int], None]] = None,
    **kwargs
) -> RecoveryResult:
    """
    Execute function with retry and exponential backoff.

    Args:
        func: Async function to execute
        *args: Function arguments
        config: Retry configuration
        error_handler: Optional callback for error logging
        **kwargs: Function keyword arguments

    Returns:
        RecoveryResult with success status and value or error
    """
    start_time = time.perf_counter()
    last_error = None

    for attempt in range(config.max_retries):
        try:
            # Handle both sync and async functions
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return RecoveryResult(
                success=True,
                value=result,
                attempts=attempt + 1,
                total_time_ms=elapsed_ms,
                error=None,
                recovery_action=RecoveryAction.RETRY if attempt > 0 else RecoveryAction.RETRY
            )

        except Exception as e:
            last_error = e
            if error_handler:
                error_handler(e, attempt)

            # Don't delay on last attempt
            if attempt < config.max_retries - 1:
                delay = calculate_delay(attempt, config)
                await asyncio.sleep(delay)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return RecoveryResult(
        success=False,
        value=None,
        attempts=config.max_retries,
        total_time_ms=elapsed_ms,
        error=str(last_error),
        recovery_action=RecoveryAction.FALLBACK
    )


def retry_sync_with_backoff(
    func: Callable[..., T],
    *args,
    config: RetryConfig = DEFAULT_RETRY_CONFIG,
    **kwargs
) -> RecoveryResult:
    """
    Synchronous version of retry with backoff.

    Args:
        func: Sync function to execute
        *args: Function arguments
        config: Retry configuration
        **kwargs: Function keyword arguments

    Returns:
        RecoveryResult with success status and value or error
    """
    start_time = time.perf_counter()
    last_error = None

    for attempt in range(config.max_retries):
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return RecoveryResult(
                success=True,
                value=result,
                attempts=attempt + 1,
                total_time_ms=elapsed_ms,
                error=None,
                recovery_action=RecoveryAction.RETRY if attempt > 0 else RecoveryAction.RETRY
            )

        except Exception as e:
            last_error = e

            # Don't delay on last attempt
            if attempt < config.max_retries - 1:
                delay = calculate_delay(attempt, config)
                time.sleep(delay)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return RecoveryResult(
        success=False,
        value=None,
        attempts=config.max_retries,
        total_time_ms=elapsed_ms,
        error=str(last_error),
        recovery_action=RecoveryAction.FALLBACK
    )


# =============================================================================
# Timeout Handling
# =============================================================================

class TimeoutError(Exception):
    """Custom timeout error with context."""
    def __init__(self, message: str, elapsed_ms: float, layer: Optional[str] = None):
        super().__init__(message)
        self.elapsed_ms = elapsed_ms
        self.layer = layer


async def with_timeout(
    coro,
    timeout_ms: float,
    layer: Optional[str] = None
) -> Any:
    """
    Execute coroutine with timeout.

    Args:
        coro: Coroutine to execute
        timeout_ms: Timeout in milliseconds
        layer: Optional layer name for error context

    Returns:
        Coroutine result

    Raises:
        TimeoutError: If operation exceeds timeout
    """
    start_time = time.perf_counter()

    try:
        result = await asyncio.wait_for(coro, timeout=timeout_ms / 1000)
        return result
    except asyncio.TimeoutError:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        raise TimeoutError(
            f"Operation timed out after {elapsed_ms:.0f}ms (limit: {timeout_ms}ms)",
            elapsed_ms=elapsed_ms,
            layer=layer
        )


def with_timeout_sync(
    func: Callable[..., T],
    timeout_ms: float,
    *args,
    layer: Optional[str] = None,
    **kwargs
) -> T:
    """
    Execute sync function with timeout using threading.

    Args:
        func: Function to execute
        timeout_ms: Timeout in milliseconds
        *args: Function arguments
        layer: Optional layer name for error context
        **kwargs: Function keyword arguments

    Returns:
        Function result

    Raises:
        TimeoutError: If operation exceeds timeout
    """
    import concurrent.futures

    start_time = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            result = future.result(timeout=timeout_ms / 1000)
            return result
        except concurrent.futures.TimeoutError:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            raise TimeoutError(
                f"Operation timed out after {elapsed_ms:.0f}ms (limit: {timeout_ms}ms)",
                elapsed_ms=elapsed_ms,
                layer=layer
            )


# =============================================================================
# Circuit Breaker Pattern
# =============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject calls
    HALF_OPEN = "half_open" # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5      # Failures before opening
    recovery_timeout_ms: int = 30000  # Time before half-open
    success_threshold: int = 2      # Successes to close


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.

    Usage:
        breaker = CircuitBreaker("groq_api")

        if breaker.can_execute():
            try:
                result = await call_groq(...)
                breaker.record_success()
            except Exception:
                breaker.record_failure()
    """

    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        self._check_recovery()
        return self._state

    def _check_recovery(self):
        """Check if circuit should transition to half-open."""
        if self._state == CircuitState.OPEN and self._last_failure_time:
            elapsed_ms = (time.time() - self._last_failure_time) * 1000
            if elapsed_ms >= self.config.recovery_timeout_ms:
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        state = self.state
        return state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    def record_success(self):
        """Record successful execution."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0

        self._failure_count = 0

    def record_failure(self):
        """Record failed execution."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN

        elif self._failure_count >= self.config.failure_threshold:
            self._state = CircuitState.OPEN

    def reset(self):
        """Reset circuit to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None


# =============================================================================
# Decorator for Error Handling
# =============================================================================

def with_recovery(
    config: RetryConfig = DEFAULT_RETRY_CONFIG,
    fallback_value: Any = None,
    fallback_func: Optional[Callable] = None
):
    """
    Decorator for automatic error recovery.

    Usage:
        @with_recovery(config=RetryConfig(max_retries=3), fallback_value="default")
        async def my_function():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            result = await retry_with_backoff(func, *args, config=config, **kwargs)

            if result.success:
                return result.value
            elif fallback_func:
                return fallback_func(*args, **kwargs)
            else:
                return fallback_value

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            result = retry_sync_with_backoff(func, *args, config=config, **kwargs)

            if result.success:
                return result.value
            elif fallback_func:
                return fallback_func(*args, **kwargs)
            else:
                return fallback_value

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# =============================================================================
# Recovery Manager (Orchestrates all recovery mechanisms)
# =============================================================================

class RecoveryManager:
    """
    Centralized manager for error recovery in the voice pipeline.

    Features:
    - Retry with exponential backoff
    - Timeout handling per layer
    - Circuit breakers for external services
    - Fallback response generation
    """

    def __init__(
        self,
        retry_config: RetryConfig = None,
        timeout_config: TimeoutConfig = None
    ):
        self.retry_config = retry_config or DEFAULT_RETRY_CONFIG
        self.timeout_config = timeout_config or DEFAULT_TIMEOUT_CONFIG

        # Circuit breakers for external services
        self._circuit_breakers: Dict[str, CircuitBreaker] = {
            "groq": CircuitBreaker("groq_api"),
            "http_bridge": CircuitBreaker("http_bridge"),
            "tts": CircuitBreaker("tts_service"),
        }

    def get_circuit_breaker(self, service: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service not in self._circuit_breakers:
            self._circuit_breakers[service] = CircuitBreaker(service)
        return self._circuit_breakers[service]

    async def execute_with_recovery(
        self,
        func: Callable,
        *args,
        service: Optional[str] = None,
        timeout_ms: Optional[float] = None,
        intent: Optional[str] = None,
        **kwargs
    ) -> RecoveryResult:
        """
        Execute function with full recovery support.

        Args:
            func: Function to execute
            *args: Function arguments
            service: Service name for circuit breaker
            timeout_ms: Override timeout
            intent: Intent for fallback response
            **kwargs: Function keyword arguments

        Returns:
            RecoveryResult with success/failure info
        """
        # Check circuit breaker
        if service:
            breaker = self.get_circuit_breaker(service)
            if not breaker.can_execute():
                return RecoveryResult(
                    success=False,
                    value=get_fallback_response(intent, ErrorCategory.SERVICE),
                    attempts=0,
                    total_time_ms=0,
                    error="Circuit breaker open",
                    recovery_action=RecoveryAction.FALLBACK
                )

        # Execute with retry
        start_time = time.perf_counter()

        try:
            result = await retry_with_backoff(
                func, *args,
                config=self.retry_config,
                **kwargs
            )

            # Update circuit breaker
            if service:
                if result.success:
                    breaker.record_success()
                else:
                    breaker.record_failure()

            return result

        except TimeoutError as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            if service:
                self.get_circuit_breaker(service).record_failure()

            return RecoveryResult(
                success=False,
                value=get_fallback_response(intent, ErrorCategory.TIMEOUT),
                attempts=1,
                total_time_ms=elapsed_ms,
                error=str(e),
                recovery_action=RecoveryAction.FALLBACK
            )

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            if service:
                self.get_circuit_breaker(service).record_failure()

            return RecoveryResult(
                success=False,
                value=get_fallback_response(intent, ErrorCategory.UNKNOWN),
                attempts=1,
                total_time_ms=elapsed_ms,
                error=str(e),
                recovery_action=RecoveryAction.FALLBACK
            )

    def get_layer_timeout(self, layer: str) -> float:
        """Get timeout for a specific layer."""
        timeout_map = {
            "sentiment": self.timeout_config.layer_0_sentiment_ms,
            "exact_match": self.timeout_config.layer_1_exact_ms,
            "intent": self.timeout_config.layer_2_intent_ms,
            "faq": self.timeout_config.layer_3_faq_ms,
            "groq": self.timeout_config.layer_4_groq_ms,
        }
        return timeout_map.get(layer, 1000)  # Default 1 second


# Global recovery manager instance
_default_manager: Optional[RecoveryManager] = None


def get_recovery_manager() -> RecoveryManager:
    """Get or create default RecoveryManager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = RecoveryManager()
    return _default_manager
