"""
Vertical Integration Module - Bridge between VerticalManager and Orchestrator

This module provides integration between the new vertical configuration system
and the existing orchestrator, enabling:
- Vertical-specific greetings and responses
- Intent classification using vertical configs
- Slot validation based on vertical definitions
- FAQ retrieval from vertical configs
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Add verticals directory to path
_verticals_path = Path(__file__).parent.parent / "verticals"
if str(_verticals_path) not in sys.path:
    sys.path.insert(0, str(_verticals_path))

try:
    from vertical_manager import (
        VerticalManager,
        VerticalConfig,
        Intent,
        Slot,
        FAQ,
        VerticalType,
        get_vertical_manager
    )
    HAS_VERTICAL_MANAGER = True
except ImportError as e:
    print(f"[VERTICAL] VerticalManager not available: {e}")
    HAS_VERTICAL_MANAGER = False


class VerticalIntentMatch(Enum):
    """Result of intent matching against vertical config."""
    EXACT = "exact"      # Exact match with examples
    FUZZY = "fuzzy"      # Partial/fuzzy match
    NONE = "none"        # No match found


@dataclass
class IntentMatchResult:
    """Result of intent matching."""
    intent_id: str
    confidence: float
    match_type: VerticalIntentMatch
    required_slots: List[str]
    optional_slots: List[str]


@dataclass
class FAQMatchResult:
    """Result of FAQ matching."""
    faq_id: str
    question: str
    answer: str
    confidence: float


class VerticalIntegration:
    """
    Integration layer between VerticalManager and VoiceOrchestrator.

    Provides:
    - Vertical detection based on business category
    - Intent matching using vertical configurations
    - Slot prompts and validation
    - FAQ retrieval
    - Response rendering with variables
    """

    def __init__(self, vertical_name: Optional[str] = None):
        """
        Initialize vertical integration.

        Args:
            vertical_name: Optional vertical name to load immediately
        """
        self.manager: Optional[VerticalManager] = None
        self.current_vertical: Optional[str] = None
        self.config: Optional[VerticalConfig] = None
        self._intent_cache: Dict[str, IntentMatchResult] = {}

        if HAS_VERTICAL_MANAGER:
            verticals_path = Path(__file__).parent.parent / "verticals"
            self.manager = VerticalManager(verticals_path)

            if vertical_name:
                self.set_vertical(vertical_name)

    def is_available(self) -> bool:
        """Check if vertical manager is available."""
        return HAS_VERTICAL_MANAGER and self.manager is not None

    def get_available_verticals(self) -> List[str]:
        """Get list of available verticals."""
        if not self.is_available():
            return []
        return self.manager.list_available_verticals()

    def set_vertical(self, vertical_name: str) -> bool:
        """
        Set the current vertical.

        Args:
            vertical_name: Name of vertical (salone, medical, etc.)

        Returns:
            True if vertical was loaded successfully
        """
        if not self.is_available():
            return False

        try:
            self.config = self.manager.load_vertical(vertical_name)
            self.current_vertical = vertical_name
            self._intent_cache.clear()  # Clear cache for new vertical
            return True
        except Exception as e:
            print(f"[VERTICAL] Failed to load vertical {vertical_name}: {e}")
            return False

    def detect_vertical_from_category(self, category: str) -> str:
        """
        Map business category to vertical name.

        Args:
            category: Business category from setup (e.g., "parrucchiere")

        Returns:
            Vertical name (salone, medical, etc.)
        """
        # Category mapping
        category_map = {
            # Salone
            "parrucchiere": "salone",
            "barbiere": "salone",
            "estetista": "salone",
            "salone": "salone",
            "beauty": "salone",
            "bellezza": "salone",

            # Medical
            "medico": "medical",
            "dottore": "medical",
            "clinica": "medical",
            "ambulatorio": "medical",
            "studio_medico": "medical",
            "dentista": "medical",
            "fisioterapista": "medical",

            # Restaurant
            "ristorante": "restaurant",
            "pizzeria": "restaurant",
            "trattoria": "restaurant",
            "bar": "restaurant",
            "caffe": "restaurant",
            "pasticceria": "restaurant",

            # Palestra
            "palestra": "palestra",
            "fitness": "palestra",
            "gym": "palestra",
            "crossfit": "palestra",
            "yoga": "palestra",
            "pilates": "palestra",

            # Auto
            "officina": "auto",
            "carrozzeria": "auto",
            "autolavaggio": "auto",
            "meccanico": "auto",
            "gommista": "auto",
            "elettrauto": "auto",
        }

        category_lower = category.lower().replace(" ", "_")
        return category_map.get(category_lower, "salone")  # Default to salone

    # =========================================================================
    # GREETING & RESPONSES
    # =========================================================================

    def get_greeting(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get vertical-specific greeting.

        Args:
            context: Optional context variables (business_name, etc.)

        Returns:
            Rendered greeting string
        """
        if not self.config:
            return "Buongiorno, come posso aiutarla?"

        return self.manager.render_response(
            self.current_vertical,
            "greeting",
            context
        )

    def get_response(
        self,
        response_key: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get a response template rendered with context.

        Args:
            response_key: Key of response (greeting, booking_confirm, etc.)
            context: Variables to substitute

        Returns:
            Rendered response string
        """
        if not self.config:
            return ""

        return self.manager.render_response(
            self.current_vertical,
            response_key,
            context
        )

    def get_fallback_response(self) -> str:
        """Get the fallback response for unrecognized input."""
        return self.get_response("fallback") or "Mi scusi, non ho capito. Puo' ripetere?"

    # =========================================================================
    # INTENT MATCHING
    # =========================================================================

    def match_intent(self, user_input: str) -> Optional[IntentMatchResult]:
        """
        Match user input against vertical intents.

        Uses fuzzy matching against intent examples.

        Args:
            user_input: User's text input

        Returns:
            IntentMatchResult if match found, None otherwise
        """
        if not self.config:
            return None

        user_lower = user_input.lower().strip()

        # Check cache first
        if user_lower in self._intent_cache:
            return self._intent_cache[user_lower]

        best_match: Optional[IntentMatchResult] = None
        best_score = 0.0

        for intent in self.config.intents:
            for example in intent.examples:
                example_lower = example.lower()

                # Exact match
                if user_lower == example_lower:
                    result = IntentMatchResult(
                        intent_id=intent.id,
                        confidence=1.0,
                        match_type=VerticalIntentMatch.EXACT,
                        required_slots=intent.required_slots,
                        optional_slots=intent.optional_slots
                    )
                    self._intent_cache[user_lower] = result
                    return result

                # Fuzzy match (simple word overlap)
                score = self._fuzzy_score(user_lower, example_lower)
                if score > best_score and score >= 0.5:
                    best_score = score
                    best_match = IntentMatchResult(
                        intent_id=intent.id,
                        confidence=score,
                        match_type=VerticalIntentMatch.FUZZY,
                        required_slots=intent.required_slots,
                        optional_slots=intent.optional_slots
                    )

        if best_match:
            self._intent_cache[user_lower] = best_match

        return best_match

    def _fuzzy_score(self, text1: str, text2: str) -> float:
        """Calculate simple word overlap score between two texts."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        overlap = words1 & words2
        return len(overlap) / max(len(words1), len(words2))

    def get_intent_examples(self) -> Dict[str, List[str]]:
        """Get all intent examples for training/matching."""
        if not self.config:
            return {}
        return self.manager.get_intent_examples(self.current_vertical)

    # =========================================================================
    # SLOT MANAGEMENT
    # =========================================================================

    def get_slot_prompt(self, slot_name: str) -> str:
        """
        Get the prompt for requesting a slot value.

        Args:
            slot_name: Name of slot (date, time, service, etc.)

        Returns:
            Prompt string to ask user for slot value
        """
        if not self.config:
            return f"Mi puo' dire {slot_name}?"

        return self.manager.get_slot_prompt(
            self.current_vertical,
            slot_name
        ) or f"Mi puo' dire {slot_name}?"

    def get_slot_values(self, slot_name: str) -> Optional[List[str]]:
        """
        Get valid values for a categorical slot.

        Args:
            slot_name: Name of slot

        Returns:
            List of valid values, or None if not categorical
        """
        if not self.config:
            return None
        return self.manager.get_slot_values(self.current_vertical, slot_name)

    def validate_slot(self, slot_name: str, value: Any) -> bool:
        """
        Validate a slot value against vertical configuration.

        Args:
            slot_name: Name of slot
            value: Value to validate

        Returns:
            True if valid
        """
        if not self.config:
            return True
        return self.manager.validate_slot_value(
            self.current_vertical,
            slot_name,
            value
        )

    def get_required_slots(self, intent_id: str) -> List[str]:
        """Get required slots for an intent."""
        if not self.config:
            return []
        return self.manager.get_required_slots(self.current_vertical, intent_id)

    def get_optional_slots(self, intent_id: str) -> List[str]:
        """Get optional slots for an intent."""
        if not self.config:
            return []
        return self.manager.get_optional_slots(self.current_vertical, intent_id)

    # =========================================================================
    # FAQ RETRIEVAL
    # =========================================================================

    def search_faq(self, query: str) -> List[FAQMatchResult]:
        """
        Search FAQs using keyword matching.

        Args:
            query: User's question

        Returns:
            List of matching FAQs with rendered answers
        """
        if not self.config:
            return []

        matches = self.manager.search_faq(self.current_vertical, query)

        results = []
        for faq in matches:
            rendered_answer = self.manager.render_faq_answer(
                self.current_vertical,
                faq
            )
            results.append(FAQMatchResult(
                faq_id=faq.id,
                question=faq.question,
                answer=rendered_answer,
                confidence=0.8  # Default confidence for keyword match
            ))

        return results

    def get_faq_answer(self, query: str) -> Optional[str]:
        """
        Get the best FAQ answer for a query.

        Args:
            query: User's question

        Returns:
            Best matching answer, or None if no match
        """
        matches = self.search_faq(query)
        if matches:
            return matches[0].answer
        return None

    # =========================================================================
    # TRIAGE (Medical only)
    # =========================================================================

    def check_triage(self, symptoms: List[str]) -> Optional[Dict]:
        """
        Check symptoms for medical urgency (medical vertical only).

        Args:
            symptoms: List of reported symptoms

        Returns:
            Triage rule if urgent, None otherwise
        """
        if not self.config or self.current_vertical != "medical":
            return None
        return self.manager.check_triage_urgency(self.current_vertical, symptoms)

    # =========================================================================
    # TRAINING DATA EXPORT
    # =========================================================================

    def export_training_data(self) -> Dict[str, Any]:
        """
        Export training data for NLU model.

        Returns:
            Dictionary with intents, entities, and examples
        """
        if not self.config:
            return {}
        return self.manager.export_training_data(self.current_vertical)

    # =========================================================================
    # VARIABLE MANAGEMENT
    # =========================================================================

    def get_variable(self, var_name: str) -> Optional[str]:
        """Get a configured variable value."""
        if not self.config:
            return None
        return self.config.variables.get(var_name)

    def set_variable(self, var_name: str, value: str) -> None:
        """Set a variable value (runtime override)."""
        if self.config:
            self.config.variables[var_name] = value

    def update_variables(self, updates: Dict[str, str]) -> None:
        """Update multiple variables at once."""
        if self.config:
            self.config.variables.update(updates)


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_integration_instance: Optional[VerticalIntegration] = None


def get_vertical_integration(vertical_name: Optional[str] = None) -> VerticalIntegration:
    """
    Get the singleton VerticalIntegration instance.

    Args:
        vertical_name: Optional vertical to initialize with

    Returns:
        VerticalIntegration instance
    """
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = VerticalIntegration(vertical_name)
    elif vertical_name and vertical_name != _integration_instance.current_vertical:
        _integration_instance.set_vertical(vertical_name)
    return _integration_instance


# =============================================================================
# SELF-TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("VERTICAL INTEGRATION - SELF TEST")
    print("=" * 60)

    # Test initialization
    integration = VerticalIntegration()
    print(f"\nAvailable: {integration.is_available()}")
    print(f"Verticals: {integration.get_available_verticals()}")

    # Test each vertical
    for vertical in integration.get_available_verticals():
        print(f"\n{'='*40}")
        print(f"TESTING: {vertical.upper()}")
        print(f"{'='*40}")

        integration.set_vertical(vertical)

        # Test greeting
        greeting = integration.get_greeting({"NOME_SALONE": "Test Salon"})
        print(f"Greeting: {greeting}")

        # Test intent matching
        test_inputs = {
            "salone": "vorrei un taglio",
            "medical": "vorrei prenotare una visita",
            "restaurant": "tavolo per due stasera",
            "palestra": "corso di yoga domani",
            "auto": "devo fare il tagliando"
        }

        if vertical in test_inputs:
            result = integration.match_intent(test_inputs[vertical])
            if result:
                print(f"Intent match: {result.intent_id} (conf: {result.confidence:.2f})")
                print(f"Required slots: {result.required_slots}")

        # Test FAQ
        faq_queries = {
            "salone": "orari",
            "medical": "specialita",
            "restaurant": "menu",
            "palestra": "abbonamento",
            "auto": "tagliando"
        }

        if vertical in faq_queries:
            answer = integration.get_faq_answer(faq_queries[vertical])
            if answer:
                print(f"FAQ answer: {answer[:60]}...")

        # Test slot prompt
        slot = "date" if vertical != "salone" else "service"
        prompt = integration.get_slot_prompt(slot)
        print(f"Slot prompt ({slot}): {prompt}")

    print("\n" + "=" * 60)
    print("SELF TEST COMPLETED")
    print("=" * 60)
