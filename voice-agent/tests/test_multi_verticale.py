"""
FLUXION Voice Agent - Multi-Verticale Integration Tests

Week 2 Day 6-7: Integration Test across 3 verticali

Tests the complete RAG pipeline on:
- Salone (hairdresser)
- Palestra (gym)
- Studio Medico (medical office)

Validates:
- FAQ retrieval accuracy per verticale
- Booking flow per verticale
- Cross-verticale isolation
- Performance consistency

Run with: pytest voice-agent/tests/test_multi_verticale.py -v
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intent_classifier import classify_intent, IntentCategory
from entity_extractor import extract_all
from booking_state_machine import BookingStateMachine, BookingState, StateMachineResult
from faq_manager import FAQManager, FAQConfig, create_faq_manager


# =============================================================================
# TEST DATA PATHS
# =============================================================================

DATA_DIR = Path(__file__).parent.parent / "data"
CONVERSATIONS_FILE = DATA_DIR / "test_conversations.json"

VERTICALE_FAQ_FILES = {
    "salone": DATA_DIR / "faq_salone_test.json",
    "palestra": DATA_DIR / "faq_palestra_test.json",
    "studio_medico": DATA_DIR / "faq_studio_test.json",
}

VERTICALE_SERVICES = {
    "salone": {
        "taglio": ["taglio", "tagliare", "sforbiciata", "spuntatina"],
        "piega": ["piega", "messa in piega", "asciugatura"],
        "colore": ["colore", "tinta", "colorazione"],
        "barba": ["barba", "rasatura"],
        "trattamento": ["trattamento", "cheratina", "maschera"],
    },
    "palestra": {
        "yoga": ["yoga", "meditazione"],
        "pilates": ["pilates"],
        "crossfit": ["crossfit", "functional"],
        "spinning": ["spinning", "bici"],
        "nuoto": ["nuoto", "piscina"],
    },
    "studio_medico": {
        "visita": ["visita", "controllo", "checkup"],
        "ecografia": ["ecografia", "eco"],
        "analisi": ["analisi", "sangue", "prelievo"],
        "vaccino": ["vaccino", "vaccinazione"],
    },
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class VerticaleTestResult:
    """Results for a single verticale test."""
    verticale: str
    faq_tests_passed: int
    faq_tests_total: int
    booking_tests_passed: int
    booking_tests_total: int
    intent_accuracy: float
    avg_latency_ms: float
    errors: List[str] = field(default_factory=list)

    @property
    def faq_accuracy(self) -> float:
        return self.faq_tests_passed / max(1, self.faq_tests_total)

    @property
    def booking_accuracy(self) -> float:
        return self.booking_tests_passed / max(1, self.booking_tests_total)

    @property
    def overall_success(self) -> bool:
        return self.faq_accuracy >= 0.7 and self.booking_accuracy >= 0.7


@dataclass
class IntegrationTestReport:
    """Full integration test report."""
    verticale_results: Dict[str, VerticaleTestResult]
    total_tests: int
    total_passed: int
    total_latency_ms: float
    cross_verticale_isolation: bool

    def to_dict(self) -> Dict:
        return {
            "summary": {
                "total_tests": self.total_tests,
                "total_passed": self.total_passed,
                "pass_rate": self.total_passed / max(1, self.total_tests),
                "avg_latency_ms": self.total_latency_ms / max(1, self.total_tests),
                "cross_verticale_isolation": self.cross_verticale_isolation,
            },
            "verticali": {
                name: {
                    "faq_accuracy": r.faq_accuracy,
                    "booking_accuracy": r.booking_accuracy,
                    "intent_accuracy": r.intent_accuracy,
                    "avg_latency_ms": r.avg_latency_ms,
                    "errors": r.errors,
                }
                for name, r in self.verticale_results.items()
            }
        }


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def load_conversations():
    """Load test conversations from JSON."""
    if CONVERSATIONS_FILE.exists():
        with open(CONVERSATIONS_FILE) as f:
            return json.load(f)
    return {"conversations": []}


@pytest.fixture
def salone_manager():
    """Create FAQ manager for salone."""
    manager = FAQManager()
    if VERTICALE_FAQ_FILES["salone"].exists():
        manager.load_faqs_from_json(str(VERTICALE_FAQ_FILES["salone"]))
    return manager


@pytest.fixture
def palestra_manager():
    """Create FAQ manager for palestra."""
    manager = FAQManager()
    if VERTICALE_FAQ_FILES["palestra"].exists():
        manager.load_faqs_from_json(str(VERTICALE_FAQ_FILES["palestra"]))
    return manager


@pytest.fixture
def studio_manager():
    """Create FAQ manager for studio medico."""
    manager = FAQManager()
    if VERTICALE_FAQ_FILES["studio_medico"].exists():
        manager.load_faqs_from_json(str(VERTICALE_FAQ_FILES["studio_medico"]))
    return manager


@pytest.fixture
def all_managers(salone_manager, palestra_manager, studio_manager):
    """All FAQ managers indexed by verticale."""
    return {
        "salone": salone_manager,
        "palestra": palestra_manager,
        "studio_medico": studio_manager,
    }


@pytest.fixture
def salone_state_machine():
    """Create state machine for salone."""
    return BookingStateMachine(services_config=VERTICALE_SERVICES["salone"])


@pytest.fixture
def palestra_state_machine():
    """Create state machine for palestra."""
    return BookingStateMachine(services_config=VERTICALE_SERVICES["palestra"])


@pytest.fixture
def studio_state_machine():
    """Create state machine for studio medico."""
    return BookingStateMachine(services_config=VERTICALE_SERVICES["studio_medico"])


# =============================================================================
# TEST: SALONE VERTICALE
# =============================================================================

class TestSaloneVerticale:
    """Integration tests for salone (hairdresser) verticale."""

    def test_salone_faq_prices(self, salone_manager):
        """Test salone price FAQ retrieval."""
        test_cases = [
            ("Quanto costa un taglio donna?", "€35"),
            ("Quanto costa il taglio uomo?", "€18"),
            ("Quanto costa il colore?", "€55"),
            ("Quanto costa la barba?", "€12"),
        ]

        passed = 0
        for query, expected in test_cases:
            result = salone_manager.find_answer(query)
            if result and expected in result.answer:
                passed += 1
            else:
                print(f"MISS: '{query}' -> {result.answer if result else 'None'}")

        assert passed >= len(test_cases) * 0.7, f"Price FAQ accuracy {passed}/{len(test_cases)} < 70%"

    def test_salone_faq_hours(self, salone_manager):
        """Test salone hours FAQ retrieval."""
        test_cases = [
            ("A che ora aprite?", "9"),
            ("A che ora chiudete?", "19"),
            ("Siete aperti il lunedì?", "chius"),
        ]

        passed = 0
        for query, expected in test_cases:
            result = salone_manager.find_answer(query)
            if result and expected.lower() in result.answer.lower():
                passed += 1

        assert passed >= len(test_cases) * 0.6, f"Hours FAQ accuracy {passed}/{len(test_cases)} < 60%"

    def test_salone_booking_flow(self, salone_state_machine):
        """Test complete salone booking flow."""
        sm = salone_state_machine

        # Book a haircut
        result = sm.process_message("Vorrei prenotare un taglio")
        assert sm.context.service == "taglio"

        result = sm.process_message("domani")
        assert sm.context.date is not None

        result = sm.process_message("alle 15")
        assert sm.context.time == "15:00"

        result = sm.process_message("sì confermo")
        assert sm.context.state == BookingState.COMPLETED
        assert result.booking is not None

    def test_salone_service_extraction(self):
        """Test salone service extraction."""
        services = VERTICALE_SERVICES["salone"]

        test_cases = [
            ("Vorrei un taglio", "taglio"),
            ("Voglio fare la piega", "piega"),
            ("Mi serve il colore", "colore"),
            ("Barba per favore", "barba"),
        ]

        for text, expected_service in test_cases:
            result = extract_all(text, services)
            assert result.service == expected_service, f"'{text}' -> {result.service} != {expected_service}"


# =============================================================================
# TEST: PALESTRA VERTICALE
# =============================================================================

class TestPalestraVerticale:
    """Integration tests for palestra (gym) verticale."""

    def test_palestra_faq_prices(self, palestra_manager):
        """Test palestra membership FAQ retrieval."""
        test_cases = [
            ("Quanto costa l'abbonamento mensile?", "45"),
            ("Quanto costa l'abbonamento annuale?", "400"),
            ("Quanto costa un singolo corso?", "10"),
        ]

        passed = 0
        for query, expected in test_cases:
            result = palestra_manager.find_answer(query)
            if result and expected in result.answer:
                passed += 1
            else:
                print(f"MISS: '{query}' -> {result.answer if result else 'None'}")

        assert passed >= len(test_cases) * 0.6, f"Palestra price FAQ accuracy {passed}/{len(test_cases)} < 60%"

    def test_palestra_faq_hours(self, palestra_manager):
        """Test palestra hours FAQ retrieval."""
        result = palestra_manager.find_answer("Che orari fate?")
        assert result is not None
        # Should contain hours info
        assert any(char.isdigit() for char in result.answer)

    def test_palestra_faq_services(self, palestra_manager):
        """Test palestra services FAQ retrieval."""
        test_cases = [
            ("Che corsi fate?", ["yoga", "pilates", "crossfit"]),
            ("Avete la piscina?", ["piscina", "25"]),
        ]

        passed = 0
        for query, expected_words in test_cases:
            result = palestra_manager.find_answer(query)
            if result:
                answer_lower = result.answer.lower()
                if any(w.lower() in answer_lower for w in expected_words):
                    passed += 1

        assert passed >= 1, "Palestra services FAQ not working"

    def test_palestra_booking_flow(self, palestra_state_machine):
        """Test palestra class booking flow."""
        sm = palestra_state_machine

        # Book a yoga class
        result = sm.process_message("Vorrei prenotare un corso di yoga")
        assert sm.context.service == "yoga"

        result = sm.process_message("mercoledì")
        assert sm.context.date is not None

        result = sm.process_message("alle 18")
        assert sm.context.time == "18:00"

        result = sm.process_message("confermo")
        assert sm.context.state == BookingState.COMPLETED

    def test_palestra_service_extraction(self):
        """Test palestra service extraction."""
        services = VERTICALE_SERVICES["palestra"]

        test_cases = [
            ("Vorrei fare yoga", "yoga"),
            ("Prenoto spinning", "spinning"),
            ("Corso di pilates", "pilates"),
        ]

        for text, expected_service in test_cases:
            result = extract_all(text, services)
            assert result.service == expected_service, f"'{text}' -> {result.service} != {expected_service}"


# =============================================================================
# TEST: STUDIO MEDICO VERTICALE
# =============================================================================

class TestStudioMedicoVerticale:
    """Integration tests for studio medico (medical office) verticale."""

    def test_studio_faq_prices(self, studio_manager):
        """Test studio medico price FAQ retrieval."""
        test_cases = [
            ("Quanto costa una visita?", "80"),
            ("Quanto costa una visita specialistica?", "120"),
        ]

        passed = 0
        for query, expected in test_cases:
            result = studio_manager.find_answer(query)
            if result and expected in result.answer:
                passed += 1
            else:
                print(f"MISS: '{query}' -> {result.answer if result else 'None'}")

        assert passed >= 1, "Studio price FAQ not working"

    def test_studio_faq_specialists(self, studio_manager):
        """Test studio medico specialist FAQ retrieval."""
        test_cases = [
            ("Avete un dermatologo?", ["dermatologo", "Rossi"]),
            ("Avete un cardiologo?", ["cardiologo", "Bianchi"]),
        ]

        passed = 0
        for query, expected_words in test_cases:
            result = studio_manager.find_answer(query)
            if result:
                answer_lower = result.answer.lower()
                if any(w.lower() in answer_lower for w in expected_words):
                    passed += 1

        assert passed >= 1, "Studio specialist FAQ not working"

    def test_studio_faq_services(self, studio_manager):
        """Test studio medico services FAQ retrieval."""
        test_cases = [
            ("Fate ecografie?", "ecograf"),
            ("Fate le analisi del sangue?", "analis"),
        ]

        passed = 0
        for query, expected in test_cases:
            result = studio_manager.find_answer(query)
            if result and expected.lower() in result.answer.lower():
                passed += 1

        assert passed >= 1, "Studio services FAQ not working"

    def test_studio_booking_flow(self, studio_state_machine):
        """Test studio medico appointment booking flow."""
        sm = studio_state_machine

        # Book a visit
        result = sm.process_message("Vorrei prenotare una visita")
        assert sm.context.service == "visita"

        result = sm.process_message("giovedì")
        assert sm.context.date is not None

        result = sm.process_message("alle 16")
        assert sm.context.time == "16:00"

        result = sm.process_message("sì")
        assert sm.context.state == BookingState.COMPLETED

    def test_studio_service_extraction(self):
        """Test studio medico service extraction."""
        services = VERTICALE_SERVICES["studio_medico"]

        test_cases = [
            ("Vorrei prenotare una visita", "visita"),
            ("Devo fare le analisi", "analisi"),
            ("Prenoto un'ecografia", "ecografia"),
        ]

        for text, expected_service in test_cases:
            result = extract_all(text, services)
            assert result.service == expected_service, f"'{text}' -> {result.service} != {expected_service}"


# =============================================================================
# TEST: CROSS-VERTICALE ISOLATION
# =============================================================================

class TestCrossVerticaleIsolation:
    """Test that verticali don't interfere with each other."""

    def test_salone_doesnt_know_gym_services(self, salone_manager):
        """Salone shouldn't have gym FAQ answers."""
        # These queries should NOT return gym-specific answers
        result = salone_manager.find_answer("Quanto costa l'abbonamento mensile?")
        if result:
            assert "palestra" not in result.answer.lower()
            assert "piscina" not in result.answer.lower()

    def test_palestra_doesnt_know_salon_services(self, palestra_manager):
        """Palestra shouldn't have salon FAQ answers."""
        result = palestra_manager.find_answer("Quanto costa un taglio donna?")
        if result:
            assert "taglio" not in result.answer.lower()
            assert "capelli" not in result.answer.lower()

    def test_studio_doesnt_know_other_services(self, studio_manager):
        """Studio shouldn't have other verticali FAQ answers."""
        result = studio_manager.find_answer("Quanto costa un taglio?")
        if result:
            assert "taglio" not in result.answer.lower()

        result = studio_manager.find_answer("Che corsi fate?")
        if result:
            assert "yoga" not in result.answer.lower()

    def test_service_extraction_isolation(self):
        """Test that service extraction uses correct verticale config."""
        # Salone config shouldn't extract "yoga"
        salone_services = VERTICALE_SERVICES["salone"]
        result = extract_all("Vorrei fare yoga", salone_services)
        assert result.service is None or result.service != "yoga"

        # Palestra config shouldn't extract "taglio"
        palestra_services = VERTICALE_SERVICES["palestra"]
        result = extract_all("Vorrei un taglio", palestra_services)
        assert result.service is None or result.service != "taglio"


# =============================================================================
# TEST: FULL CONVERSATION FLOWS
# =============================================================================

class TestFullConversationFlows:
    """Test complete conversation flows from test_conversations.json."""

    def run_conversation(
        self,
        turns: List[Dict],
        faq_manager: FAQManager,
        state_machine: BookingStateMachine
    ) -> Tuple[int, int, List[str]]:
        """
        Run a conversation and count successes.

        Returns: (passed, total, errors)
        """
        passed = 0
        total = len(turns)
        errors = []

        for turn in turns:
            user_input = turn["user"]
            expected_intent = turn.get("expected_intent", "")

            # Classify intent
            intent_result = classify_intent(user_input)
            actual_intent = intent_result.category.value

            # Check intent
            if expected_intent:
                if actual_intent == expected_intent or expected_intent in actual_intent:
                    passed += 1
                else:
                    errors.append(f"Intent: '{user_input}' -> {actual_intent} != {expected_intent}")

            # Check FAQ response if expected
            expected_response = turn.get("expected_response_contains", [])
            if expected_response:
                faq_result = faq_manager.find_answer(user_input)
                if faq_result:
                    answer_lower = faq_result.answer.lower()
                    if any(exp.lower() in answer_lower for exp in expected_response):
                        pass  # Already counted above
                    else:
                        errors.append(f"FAQ: '{user_input}' -> missing {expected_response}")

            # Process through state machine if booking-related
            if expected_intent in ["prenotazione", "conferma", "cancellazione"]:
                state_machine.process_message(user_input)

        return passed, total, errors

    def test_salone_conversations(self, load_conversations, salone_manager, salone_state_machine):
        """Test salone conversation flows."""
        conversations = load_conversations.get("conversations", [])
        salone_convos = [c for c in conversations if c.get("verticale") == "salone"]

        total_passed = 0
        total_turns = 0
        all_errors = []

        for conv in salone_convos[:5]:  # Test first 5 salone conversations
            salone_state_machine.reset()
            passed, total, errors = self.run_conversation(
                conv["turns"],
                salone_manager,
                salone_state_machine
            )
            total_passed += passed
            total_turns += total
            all_errors.extend(errors)

        accuracy = total_passed / max(1, total_turns)
        print(f"\nSalone conversation accuracy: {accuracy*100:.1f}% ({total_passed}/{total_turns})")
        if all_errors:
            print(f"Errors: {all_errors[:5]}")

        assert accuracy >= 0.6, f"Salone conversation accuracy {accuracy*100:.1f}% < 60%"


# =============================================================================
# TEST: PERFORMANCE BENCHMARKS
# =============================================================================

class TestPerformanceBenchmarks:
    """Performance benchmarks across all verticali."""

    def test_faq_latency_all_verticali(self, all_managers):
        """Test FAQ latency is consistent across verticali."""
        queries = [
            "Quanto costa?",
            "Che orari fate?",
            "Siete aperti?",
        ]

        for verticale, manager in all_managers.items():
            latencies = []
            for _ in range(50):
                for query in queries:
                    start = time.time()
                    manager.find_answer(query)
                    latencies.append((time.time() - start) * 1000)

            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)

            print(f"\n{verticale} FAQ latency: avg={avg_latency:.2f}ms, max={max_latency:.2f}ms")
            assert avg_latency < 20, f"{verticale} avg latency {avg_latency:.2f}ms > 20ms"

    def test_intent_latency_consistency(self):
        """Test intent classification latency is consistent."""
        queries = [
            "Buongiorno",
            "Vorrei prenotare",
            "Quanto costa?",
            "Grazie",
        ]

        latencies = []
        for _ in range(100):
            for query in queries:
                start = time.time()
                classify_intent(query)
                latencies.append((time.time() - start) * 1000)

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"\nIntent latency: avg={avg_latency:.2f}ms, P95={p95_latency:.2f}ms")
        assert avg_latency < 5, f"Intent avg latency {avg_latency:.2f}ms > 5ms"
        assert p95_latency < 10, f"Intent P95 latency {p95_latency:.2f}ms > 10ms"

    def test_booking_flow_latency(self):
        """Test booking flow latency across verticali."""
        for verticale, services in VERTICALE_SERVICES.items():
            sm = BookingStateMachine(services_config=services)

            start = time.time()
            sm.process_message("Vorrei prenotare")
            sm.process_message("domani")
            sm.process_message("alle 15")
            sm.process_message("sì")
            total_time = (time.time() - start) * 1000

            print(f"\n{verticale} booking flow: {total_time:.2f}ms")
            assert total_time < 50, f"{verticale} booking flow {total_time:.2f}ms > 50ms"


# =============================================================================
# TEST: INTEGRATION REPORT
# =============================================================================

class TestIntegrationReport:
    """Generate integration test report."""

    def test_generate_report(self, all_managers, load_conversations):
        """Generate and validate integration test report."""
        report_data = {
            "verticali": {},
            "summary": {
                "total_faq_tests": 0,
                "total_faq_passed": 0,
                "total_booking_tests": 0,
                "total_booking_passed": 0,
            }
        }

        # Test each verticale
        for verticale, manager in all_managers.items():
            faq_passed = 0
            faq_total = 5

            # Basic FAQ tests
            if verticale == "salone":
                test_queries = [
                    ("Quanto costa un taglio?", ["€", "35", "18"]),
                    ("A che ora aprite?", ["9"]),
                    ("Siete aperti il lunedì?", ["chius", "lunedì"]),
                    ("C'è parcheggio?", ["parcheggio"]),
                    ("Accettate Satispay?", ["Satispay"]),
                ]
            elif verticale == "palestra":
                test_queries = [
                    ("Quanto costa l'abbonamento?", ["€", "45", "400"]),
                    ("Che orari fate?", ["aperi", "6", "22"]),
                    ("Avete la piscina?", ["piscina"]),
                    ("Posso fare una prova?", ["prova", "gratuit"]),
                    ("C'è parcheggio?", ["parcheggio"]),
                ]
            else:  # studio_medico
                test_queries = [
                    ("Quanto costa una visita?", ["€", "80"]),
                    ("Avete un dermatologo?", ["dermatologo"]),
                    ("Fate ecografie?", ["ecograf"]),
                    ("Devo prenotare?", ["prenotazion"]),
                    ("Come posso pagare?", ["carta", "contant"]),
                ]

            faq_total = len(test_queries)
            for query, expected in test_queries:
                result = manager.find_answer(query)
                if result:
                    answer_lower = result.answer.lower()
                    if any(exp.lower() in answer_lower for exp in expected):
                        faq_passed += 1

            report_data["verticali"][verticale] = {
                "faq_accuracy": faq_passed / faq_total,
                "faq_passed": faq_passed,
                "faq_total": faq_total,
            }
            report_data["summary"]["total_faq_tests"] += faq_total
            report_data["summary"]["total_faq_passed"] += faq_passed

        # Print report
        print("\n" + "=" * 60)
        print("INTEGRATION TEST REPORT - Week 2 Day 6-7")
        print("=" * 60)

        for verticale, data in report_data["verticali"].items():
            accuracy = data["faq_accuracy"] * 100
            print(f"\n{verticale.upper()}:")
            print(f"  FAQ Accuracy: {accuracy:.1f}% ({data['faq_passed']}/{data['faq_total']})")

        total_acc = report_data["summary"]["total_faq_passed"] / report_data["summary"]["total_faq_tests"]
        print(f"\n{'=' * 60}")
        print(f"OVERALL FAQ ACCURACY: {total_acc*100:.1f}%")
        print("=" * 60)

        # Assert overall accuracy
        assert total_acc >= 0.6, f"Overall FAQ accuracy {total_acc*100:.1f}% < 60%"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
