"""
FLUXION Voice Agent - Backchannel Engine

Injects natural acknowledgment phrases to make Sara feel human.

Backchannels are short utterances ("Capisco", "Certo", "Ok") that signal
active listening. They're injected BEFORE the main response in certain contexts.

Different from MICRO_REACTIONS in booking_state_machine.py:
  - MICRO_REACTIONS = emotional warmth tied to FSM transitions (e.g. "Ottima scelta!")
  - Backchannels = conversational acknowledgment independent of FSM ("Capisco", "Ok")
"""

import random

# Backchannel phrase pools by conversational context.
# Each pool must have >= 2 phrases for variety.
BACKCHANNELS = {
    "info_provided": ["Ok", "Perfetto", "Benissimo", "Capito"],
    "confirmed": ["Ottimo", "Benissimo", "Perfetto", "Grande"],
    "long_input": ["Capisco", "Certo", "Ho capito", "Chiaro"],
    "correction": ["Ah ok", "Capisco", "Nessun problema"],
}

# FSM states where user is providing slot info
_INFO_STATES = frozenset({
    "waiting_name", "waiting_surname", "waiting_date", "waiting_time",
    "waiting_service", "waiting_phone", "waiting_email",
})

# FSM states where user is confirming something
_CONFIRM_STATES = frozenset({
    "confirming", "asking_close_confirmation",
})

# Minimum turns between consecutive backchannels
_COOLDOWN_TURNS = 3

# Minimum user input length (chars) to count as "long input"
_LONG_INPUT_THRESHOLD = 60


class BackchannelEngine:
    """Decides WHEN and WHAT backchannel to inject before Sara's main response."""

    def __init__(self):
        self._turn_counter = 0
        self._last_backchannel_turn = -_COOLDOWN_TURNS - 1  # allow first

    def should_backchannel(
        self,
        user_input: str,
        intent: str,
        fsm_state: str,
        sentiment: str = "neutral",
        is_first_turn: bool = False,
    ) -> bool:
        """Decide if a backchannel should be injected before the main response."""
        # NEVER on greeting / first turn
        if is_first_turn or self._turn_counter == 0:
            return False

        # NEVER when user is frustrated
        if sentiment in ("negative", "frustrated", "angry"):
            return False

        # Cooldown: max 1 backchannel per N turns
        if (self._turn_counter - self._last_backchannel_turn) < _COOLDOWN_TURNS:
            return False

        # Check if context warrants a backchannel
        fsm_lower = fsm_state.lower() if fsm_state else ""

        if fsm_lower in _INFO_STATES:
            return True
        if fsm_lower in _CONFIRM_STATES:
            return True
        if len(user_input) >= _LONG_INPUT_THRESHOLD:
            return True

        return False

    def get_backchannel(self, context: str = "info_provided", response: str = "") -> str:
        """
        Get a random backchannel phrase for the given context.

        Args:
            context: One of the BACKCHANNELS keys.
            response: The main response text -- avoids duplicating its first word.
        """
        pool = BACKCHANNELS.get(context, BACKCHANNELS["info_provided"])
        if not pool:
            return ""

        # Avoid duplicating the first word of the main response
        response_start = response.split()[0].rstrip(",.!") if response else ""
        filtered = [p for p in pool if p.split()[0].rstrip(",.!") != response_start]
        chosen_pool = filtered if filtered else pool

        choice = random.choice(chosen_pool)
        self._last_backchannel_turn = self._turn_counter
        return choice

    def classify_context(self, fsm_state: str, user_input: str) -> str:
        """Determine the backchannel context category from FSM state and input."""
        fsm_lower = fsm_state.lower() if fsm_state else ""

        if fsm_lower in _CONFIRM_STATES:
            return "confirmed"
        if fsm_lower in _INFO_STATES:
            return "info_provided"
        if len(user_input) >= _LONG_INPUT_THRESHOLD:
            return "long_input"
        return "info_provided"

    def tick(self):
        """Increment turn counter. Call after each process() turn."""
        self._turn_counter += 1

    def reset(self):
        """Reset for new session."""
        self._turn_counter = 0
        self._last_backchannel_turn = -_COOLDOWN_TURNS - 1
