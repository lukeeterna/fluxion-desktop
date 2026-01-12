"""
Error Recovery Tests - Week 3 Day 3-4

Tests for retry logic, exponential backoff, timeout handling, and circuit breaker.
"""

import asyncio
import pytest
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from error_recovery import (
    # Classes
    ErrorCategory,
    RecoveryAction,
    RetryConfig,
    TimeoutConfig,
    RecoveryResult,
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreaker,
    RecoveryManager,
    TimeoutError,
    # Functions
    get_fallback_response,
    get_escalation_response,
    calculate_delay,
    retry_with_backoff,
    retry_sync_with_backoff,
    with_timeout,
    with_timeout_sync,
    with_recovery,
    get_recovery_manager,
    # Constants
    FALLBACK_RESPONSES,
    DEFAULT_RETRY_CONFIG,
    DEFAULT_TIMEOUT_CONFIG,
)


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture
def retry_config():
    """Fast retry config for testing."""
    return RetryConfig(
        max_retries=3,
        base_delay_ms=10,
        max_delay_ms=100,
        exponential_base=2.0,
        jitter=False
    )


@pytest.fixture
def circuit_breaker():
    """Circuit breaker with low thresholds for testing."""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout_ms=100,
        success_threshold=1
    )
    return CircuitBreaker("test_service", config)


@pytest.fixture
def recovery_manager(retry_config):
    """Recovery manager for testing."""
    return RecoveryManager(retry_config=retry_config)


# ==============================================================================
# Test: Fallback Responses
# ==============================================================================

class TestFallbackResponses:
    """Test fallback response generation."""

    def test_fallback_by_intent(self):
        """Test getting fallback by intent category."""
        response = get_fallback_response(intent="prenotazione")
        assert "problema tecnico" in response or "riprovare" in response

    def test_fallback_by_error_category(self):
        """Test getting fallback by error category."""
        response = get_fallback_response(error_category=ErrorCategory.NETWORK)
        assert "connessione" in response or "riprovare" in response

    def test_fallback_default(self):
        """Test default fallback when no match."""
        response = get_fallback_response()
        assert "problema" in response or "operatore" in response

    def test_fallback_context_substitution(self):
        """Test context variable substitution."""
        response = get_fallback_response(
            intent="info",
            context={"phone": "123456"}
        )
        assert isinstance(response, str)

    def test_escalation_response(self):
        """Test escalation responses."""
        response = get_escalation_response("max_retries")
        assert "operatore" in response

    def test_all_intents_have_fallbacks(self):
        """Test all common intents have fallback responses."""
        intents = ["prenotazione", "info", "conferma", "rifiuto", "cortesia", "operatore"]
        for intent in intents:
            assert intent in FALLBACK_RESPONSES


# ==============================================================================
# Test: Calculate Delay
# ==============================================================================

class TestCalculateDelay:
    """Test exponential backoff delay calculation."""

    def test_first_attempt_delay(self):
        """Test delay for first retry attempt."""
        config = RetryConfig(base_delay_ms=100, jitter=False)
        delay = calculate_delay(0, config)
        assert abs(delay - 0.1) < 0.01  # 100ms = 0.1s

    def test_exponential_growth(self):
        """Test delay increases exponentially."""
        config = RetryConfig(base_delay_ms=100, max_delay_ms=10000, jitter=False)
        delays = [calculate_delay(i, config) for i in range(4)]

        # Each delay should be ~2x previous
        assert delays[1] > delays[0]
        assert delays[2] > delays[1]
        assert delays[3] > delays[2]

    def test_max_delay_cap(self):
        """Test delay is capped at max."""
        config = RetryConfig(base_delay_ms=1000, max_delay_ms=500, jitter=False)
        delay = calculate_delay(10, config)  # Would be huge without cap
        assert delay <= 0.5  # 500ms

    def test_jitter_adds_randomness(self):
        """Test jitter adds randomness to delays."""
        config = RetryConfig(base_delay_ms=100, jitter=True)
        delays = [calculate_delay(0, config) for _ in range(10)]

        # Should have some variance
        assert len(set(delays)) > 1


# ==============================================================================
# Test: Retry with Backoff (Async)
# ==============================================================================

class TestRetryWithBackoff:
    """Test async retry with exponential backoff."""

    @pytest.mark.asyncio
    async def test_success_on_first_try(self, retry_config):
        """Test successful execution without retry."""
        call_count = 0

        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_with_backoff(success_func, config=retry_config)

        assert result.success is True
        assert result.value == "success"
        assert result.attempts == 1
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_success_after_retries(self, retry_config):
        """Test success after initial failures."""
        call_count = 0

        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary failure")
            return "success"

        result = await retry_with_backoff(fail_then_succeed, config=retry_config)

        assert result.success is True
        assert result.value == "success"
        assert result.attempts == 3

    @pytest.mark.asyncio
    async def test_all_retries_fail(self, retry_config):
        """Test all retries exhausted."""
        call_count = 0

        async def always_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("permanent failure")

        result = await retry_with_backoff(always_fail, config=retry_config)

        assert result.success is False
        assert result.value is None
        assert result.attempts == retry_config.max_retries
        assert "permanent failure" in result.error

    @pytest.mark.asyncio
    async def test_error_handler_called(self, retry_config):
        """Test error handler is called on each failure."""
        errors = []

        def error_handler(error, attempt):
            errors.append((str(error), attempt))

        async def fail_func():
            raise ValueError("test error")

        await retry_with_backoff(
            fail_func,
            config=retry_config,
            error_handler=error_handler
        )

        assert len(errors) == retry_config.max_retries

    @pytest.mark.asyncio
    async def test_supports_sync_functions(self, retry_config):
        """Test retry works with sync functions."""
        def sync_func():
            return "sync result"

        result = await retry_with_backoff(sync_func, config=retry_config)
        assert result.success is True
        assert result.value == "sync result"


# ==============================================================================
# Test: Retry with Backoff (Sync)
# ==============================================================================

class TestRetrySyncWithBackoff:
    """Test sync retry with exponential backoff."""

    def test_success_on_first_try(self, retry_config):
        """Test successful sync execution."""
        def success_func():
            return "success"

        result = retry_sync_with_backoff(success_func, config=retry_config)
        assert result.success is True
        assert result.value == "success"

    def test_retries_on_failure(self, retry_config):
        """Test sync function retries on failure."""
        call_count = 0

        def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("fail")
            return "success"

        result = retry_sync_with_backoff(fail_then_succeed, config=retry_config)
        assert result.success is True
        assert result.attempts == 2


# ==============================================================================
# Test: Timeout Handling
# ==============================================================================

class TestTimeoutHandling:
    """Test timeout functionality."""

    @pytest.mark.asyncio
    async def test_completes_within_timeout(self):
        """Test operation completing within timeout."""
        async def fast_func():
            await asyncio.sleep(0.01)
            return "done"

        result = await with_timeout(fast_func(), timeout_ms=100)
        assert result == "done"

    @pytest.mark.asyncio
    async def test_raises_on_timeout(self):
        """Test timeout error is raised."""
        async def slow_func():
            await asyncio.sleep(10)
            return "never"

        with pytest.raises(TimeoutError) as exc_info:
            await with_timeout(slow_func(), timeout_ms=50, layer="test")

        assert exc_info.value.layer == "test"
        assert exc_info.value.elapsed_ms > 0

    def test_sync_completes_within_timeout(self):
        """Test sync timeout succeeds."""
        def fast_func():
            time.sleep(0.01)
            return "done"

        result = with_timeout_sync(fast_func, timeout_ms=100)
        assert result == "done"

    def test_sync_raises_on_timeout(self):
        """Test sync timeout error is raised."""
        def slow_func():
            time.sleep(10)
            return "never"

        with pytest.raises(TimeoutError):
            with_timeout_sync(slow_func, timeout_ms=50, layer="test")


# ==============================================================================
# Test: Circuit Breaker
# ==============================================================================

class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_initial_state_closed(self, circuit_breaker):
        """Test circuit starts in closed state."""
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.can_execute() is True

    def test_opens_after_failures(self, circuit_breaker):
        """Test circuit opens after threshold failures."""
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()

        assert circuit_breaker.state == CircuitState.OPEN
        assert circuit_breaker.can_execute() is False

    def test_success_resets_failure_count(self, circuit_breaker):
        """Test success resets failure counter."""
        circuit_breaker.record_failure()
        circuit_breaker.record_success()
        circuit_breaker.record_failure()

        # Should still be closed (failure count reset)
        assert circuit_breaker.state == CircuitState.CLOSED

    def test_transitions_to_half_open(self, circuit_breaker):
        """Test circuit transitions to half-open after timeout."""
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        assert circuit_breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        time.sleep(0.15)  # 150ms > 100ms recovery timeout

        assert circuit_breaker.state == CircuitState.HALF_OPEN
        assert circuit_breaker.can_execute() is True

    def test_half_open_closes_on_success(self, circuit_breaker):
        """Test half-open closes after success."""
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        time.sleep(0.15)

        assert circuit_breaker.state == CircuitState.HALF_OPEN

        circuit_breaker.record_success()
        assert circuit_breaker.state == CircuitState.CLOSED

    def test_half_open_reopens_on_failure(self, circuit_breaker):
        """Test half-open reopens on failure."""
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        time.sleep(0.15)

        assert circuit_breaker.state == CircuitState.HALF_OPEN

        circuit_breaker.record_failure()
        assert circuit_breaker.state == CircuitState.OPEN

    def test_reset(self, circuit_breaker):
        """Test circuit can be reset."""
        circuit_breaker.record_failure()
        circuit_breaker.record_failure()
        assert circuit_breaker.state == CircuitState.OPEN

        circuit_breaker.reset()
        assert circuit_breaker.state == CircuitState.CLOSED


# ==============================================================================
# Test: Recovery Manager
# ==============================================================================

class TestRecoveryManager:
    """Test the RecoveryManager orchestrator."""

    @pytest.mark.asyncio
    async def test_execute_with_recovery_success(self, recovery_manager):
        """Test successful execution through manager."""
        async def success_func():
            return "result"

        result = await recovery_manager.execute_with_recovery(success_func)
        assert result.success is True
        assert result.value == "result"

    @pytest.mark.asyncio
    async def test_execute_with_circuit_breaker(self, recovery_manager):
        """Test circuit breaker integration."""
        call_count = 0

        async def fail_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        # Exhaust circuit breaker
        for _ in range(10):
            await recovery_manager.execute_with_recovery(
                fail_func, service="test_service"
            )

        breaker = recovery_manager.get_circuit_breaker("test_service")
        assert breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_returns_fallback_on_failure(self, recovery_manager):
        """Test fallback response on failure."""
        async def fail_func():
            raise ValueError("test error")

        result = await recovery_manager.execute_with_recovery(
            fail_func,
            intent="prenotazione"
        )

        assert result.success is False
        assert result.recovery_action == RecoveryAction.FALLBACK

    def test_get_layer_timeout(self, recovery_manager):
        """Test layer timeout retrieval."""
        assert recovery_manager.get_layer_timeout("sentiment") == 100
        assert recovery_manager.get_layer_timeout("groq") == 2000
        assert recovery_manager.get_layer_timeout("unknown") == 1000  # default


# ==============================================================================
# Test: Decorator
# ==============================================================================

class TestWithRecoveryDecorator:
    """Test the @with_recovery decorator."""

    @pytest.mark.asyncio
    async def test_async_decorator_success(self):
        """Test async decorator on successful function."""
        @with_recovery(fallback_value="fallback")
        async def success_func():
            return "success"

        result = await success_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_async_decorator_fallback(self):
        """Test async decorator returns fallback on failure."""
        config = RetryConfig(max_retries=2, base_delay_ms=1)

        @with_recovery(config=config, fallback_value="fallback")
        async def fail_func():
            raise ValueError("fail")

        result = await fail_func()
        assert result == "fallback"

    def test_sync_decorator_success(self):
        """Test sync decorator on successful function."""
        @with_recovery(fallback_value="fallback")
        def success_func():
            return "success"

        result = success_func()
        assert result == "success"

    def test_sync_decorator_fallback(self):
        """Test sync decorator returns fallback on failure."""
        config = RetryConfig(max_retries=2, base_delay_ms=1)

        @with_recovery(config=config, fallback_value="fallback")
        def fail_func():
            raise ValueError("fail")

        result = fail_func()
        assert result == "fallback"


# ==============================================================================
# Test: Timeout Config
# ==============================================================================

class TestTimeoutConfig:
    """Test timeout configuration."""

    def test_default_config(self):
        """Test default timeout values."""
        config = DEFAULT_TIMEOUT_CONFIG

        assert config.layer_0_sentiment_ms == 100
        assert config.layer_1_exact_ms == 50
        assert config.layer_2_intent_ms == 100
        assert config.layer_3_faq_ms == 500
        assert config.layer_4_groq_ms == 2000
        assert config.total_max_ms == 3000

    def test_custom_config(self):
        """Test custom timeout configuration."""
        config = TimeoutConfig(
            layer_4_groq_ms=1000,
            total_max_ms=2000
        )

        assert config.layer_4_groq_ms == 1000
        assert config.total_max_ms == 2000


# ==============================================================================
# Test: Recovery Result
# ==============================================================================

class TestRecoveryResult:
    """Test RecoveryResult dataclass."""

    def test_success_result(self):
        """Test successful result structure."""
        result = RecoveryResult(
            success=True,
            value="data",
            attempts=1,
            total_time_ms=50.0,
            error=None,
            recovery_action=RecoveryAction.RETRY
        )

        assert result.success is True
        assert result.value == "data"
        assert result.error is None

    def test_failure_result(self):
        """Test failure result structure."""
        result = RecoveryResult(
            success=False,
            value=None,
            attempts=3,
            total_time_ms=500.0,
            error="Connection failed",
            recovery_action=RecoveryAction.FALLBACK
        )

        assert result.success is False
        assert "Connection" in result.error
        assert result.recovery_action == RecoveryAction.FALLBACK


# ==============================================================================
# Test: Performance
# ==============================================================================

class TestPerformance:
    """Test performance requirements."""

    @pytest.mark.asyncio
    async def test_retry_overhead(self, retry_config):
        """Test retry mechanism has minimal overhead on success."""
        async def instant_func():
            return True

        start = time.perf_counter()
        for _ in range(100):
            await retry_with_backoff(instant_func, config=retry_config)
        elapsed = time.perf_counter() - start

        avg_ms = (elapsed / 100) * 1000
        assert avg_ms < 1, f"Average overhead {avg_ms:.2f}ms exceeds 1ms"

    def test_circuit_breaker_check_speed(self, circuit_breaker):
        """Test circuit breaker check is fast."""
        start = time.perf_counter()
        for _ in range(1000):
            circuit_breaker.can_execute()
        elapsed = time.perf_counter() - start

        avg_us = (elapsed / 1000) * 1_000_000
        assert avg_us < 100, f"Average check {avg_us:.2f}us exceeds 100us"


# ==============================================================================
# Test: Global Instance
# ==============================================================================

class TestGlobalInstance:
    """Test global recovery manager instance."""

    def test_singleton_pattern(self):
        """Test get_recovery_manager returns singleton."""
        manager1 = get_recovery_manager()
        manager2 = get_recovery_manager()
        assert manager1 is manager2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
