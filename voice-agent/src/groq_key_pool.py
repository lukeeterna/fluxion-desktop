"""
Groq Key Pool - Fluxion F03 Latency Optimizer
=============================================
Round-robin rotation across up to 3 Groq free-tier API keys.
Triples effective rate limit - rotates on 429 errors.

Python 3.9 compatible.
Thread safety: single-thread asyncio event loop (GIL safe).
Note: self._index += 1 is safe in asyncio single-thread event loop - no await
      point separates read and write, so no coroutine interleaving is possible.

Usage:
    pool = GroqKeyPool()
    key = pool.current_key()
    # on 429 error:
    key = pool.rotate()

Env vars: GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3
"""
import os
from typing import List


class GroqKeyPool:
    """Round-robin Groq API key pool for rate limit resilience."""

    def __init__(self):
        self._keys: List[str] = []
        self._index: int = 0
        # Load from env: GROQ_API_KEY, GROQ_API_KEY_2, GROQ_API_KEY_3
        for suffix in ["", "_2", "_3"]:
            key = os.environ.get("GROQ_API_KEY" + suffix)
            if key and key.strip():
                self._keys.append(key.strip())
        if not self._keys:
            raise ValueError(
                "At least one GROQ_API_KEY must be set in environment. "
                "Optional: GROQ_API_KEY_2, GROQ_API_KEY_3 for rate limit pooling."
            )

    def current_key(self) -> str:
        """Return the current active key (does not advance index)."""
        return self._keys[self._index % len(self._keys)]

    def rotate(self) -> str:
        """Advance to next key and return it. Call on 429 rate limit error."""
        self._index += 1
        return self.current_key()

    @property
    def size(self) -> int:
        """Number of keys in the pool."""
        return len(self._keys)

    def __repr__(self) -> str:
        return "GroqKeyPool(size={}, current_index={})".format(
            self.size, self._index % self.size
        )
