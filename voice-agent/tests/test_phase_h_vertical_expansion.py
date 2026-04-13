"""
Phase H: Vertical Expansion — Test Suite
Tests sub-vertical configs, medical triage, composite cards,
vertical business hours, and analytics vertical tracking.
"""

import json
import os
import sys
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import asdict

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

VERTICALS_DIR = Path(__file__).parent.parent / "verticals"


# =============================================================================
# H1: Sub-vertical individual configs
# =============================================================================

class TestH1SubVerticalConfigs:
    """Test all 6 sub-verticals have complete config files."""

    SUB_VERTICALS = ["barbiere", "beauty", "odontoiatra", "fisioterapia", "gommista", "toelettatura"]
    REQUIRED_FILES = ["config.json", "config.py", "entities.py", "intents.py", "faqs.json"]

    @pytest.mark.parametrize("vertical", SUB_VERTICALS)
    def test_all_required_files_exist(self, vertical):
        """Each sub-vertical has all required files."""
        vdir = VERTICALS_DIR / vertical
        for f in self.REQUIRED_FILES:
            assert (vdir / f).exists(), f"{vertical}/{f} missing"

    @pytest.mark.parametrize("vertical", SUB_VERTICALS)
    def test_config_json_valid(self, vertical):
        """config.json is valid JSON with required keys."""
        config_path = VERTICALS_DIR / vertical / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        assert config["vertical_name"] == vertical
        assert "intents" in config
        assert "slots" in config
        assert "responses" in config
        assert "variables" in config
        assert len(config["intents"]) >= 5, f"{vertical} needs >= 5 intents"

    @pytest.mark.parametrize("vertical", SUB_VERTICALS)
    def test_config_json_has_booking_intent(self, vertical):
        """Every vertical must have a booking intent."""
        config_path = VERTICALS_DIR / vertical / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        intent_names = [i["name"] for i in config["intents"]]
        has_booking = any("book" in n for n in intent_names)
        assert has_booking, f"{vertical} missing booking intent"

    @pytest.mark.parametrize("vertical", SUB_VERTICALS)
    def test_config_json_has_required_slots(self, vertical):
        """Every vertical has date and time slots."""
        config_path = VERTICALS_DIR / vertical / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        slot_names = [s["name"] for s in config["slots"]]
        assert "date" in slot_names, f"{vertical} missing date slot"
        assert "time" in slot_names, f"{vertical} missing time slot"

    @pytest.mark.parametrize("vertical", SUB_VERTICALS)
    def test_config_json_has_variables(self, vertical):
        """Variables dict for template substitution."""
        config_path = VERTICALS_DIR / vertical / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        assert "NOME_ATTIVITA" in config["variables"] or "NOME_STUDIO" in config["variables"]

    @pytest.mark.parametrize("vertical", SUB_VERTICALS)
    def test_faqs_json_valid(self, vertical):
        """faqs.json is valid with keyword arrays."""
        faq_path = VERTICALS_DIR / vertical / "faqs.json"
        with open(faq_path) as f:
            faqs = json.load(f)
        if isinstance(faqs, dict):
            faq_list = faqs.get("faqs", [])
        else:
            faq_list = faqs
        assert len(faq_list) >= 3, f"{vertical} needs >= 3 FAQs"
        for faq in faq_list:
            assert "keywords" in faq, f"{vertical} FAQ missing keywords"
            assert "answer" in faq, f"{vertical} FAQ missing answer"


class TestH1BarbiereEntities:
    """Test barbiere entity extraction."""

    def _get_extractor(self):
        from verticals.barbiere.entities import BarbiereEntityExtractor
        return BarbiereEntityExtractor()

    def test_extract_taglio(self):
        ext = self._get_extractor()
        assert ext.extract_service("vorrei un taglio") == "taglio"

    def test_extract_barba(self):
        ext = self._get_extractor()
        assert ext.extract_service("sistemare la barba") == "barba"

    def test_extract_fade(self):
        ext = self._get_extractor()
        assert ext.extract_service("vorrei un fade") == "fade"

    def test_extract_taglio_barba_combo(self):
        ext = self._get_extractor()
        assert ext.extract_service("taglio e barba completo") == "taglio_barba"

    def test_extract_date_domani(self):
        ext = self._get_extractor()
        expected = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert ext.extract_date("domani") == expected

    def test_extract_time(self):
        ext = self._get_extractor()
        assert ext.extract_time("alle 15:30") == "15:30"

    def test_calculate_duration_taglio(self):
        ext = self._get_extractor()
        assert ext.calculate_duration("taglio") == 30

    def test_calculate_duration_colorazione(self):
        ext = self._get_extractor()
        assert ext.calculate_duration("colorazione") == 60

    def test_create_booking_request(self):
        ext = self._get_extractor()
        req = ext.create_booking_request("Vorrei un taglio domani alle 10:00")
        assert req.service == "taglio"
        assert req.time == "10:00"
        assert req.duration_minutes == 30


class TestH1BarbiereIntents:
    """Test barbiere intent classification."""

    def _get_classifier(self):
        from verticals.barbiere.intents import BarbiereIntentClassifier, IntentType
        return BarbiereIntentClassifier(), IntentType

    def test_prenotazione(self):
        cls, IT = self._get_classifier()
        result = cls.classify("Vorrei prenotare un taglio")
        assert result.type == IT.PRENOTAZIONE

    def test_prezzi(self):
        cls, IT = self._get_classifier()
        result = cls.classify("Quanto costa un fade?")
        assert result.type == IT.PREZZI

    def test_orari(self):
        cls, IT = self._get_classifier()
        result = cls.classify("A che ora aprite?")
        assert result.type == IT.ORARI

    def test_saluto(self):
        cls, IT = self._get_classifier()
        result = cls.classify("Buongiorno")
        assert result.type == IT.SALUTO

    def test_fallback_low_confidence(self):
        cls, IT = self._get_classifier()
        result = cls.classify("xyz random text")
        assert result.type == IT.FALLBACK


class TestH1BeautyEntities:
    """Test beauty center entity extraction."""

    def _get_extractor(self):
        from verticals.beauty.entities import BeautyEntityExtractor
        return BeautyEntityExtractor()

    def test_extract_pulizia_viso(self):
        ext = self._get_extractor()
        assert ext.extract_service("vorrei una pulizia del viso") == "pulizia_viso"

    def test_extract_ceretta(self):
        ext = self._get_extractor()
        assert ext.extract_service("devo fare la ceretta") == "ceretta"

    def test_extract_massaggio(self):
        ext = self._get_extractor()
        assert ext.extract_service("voglio un massaggio rilassante") == "massaggio"

    def test_extract_epilazione_laser(self):
        ext = self._get_extractor()
        assert ext.extract_service("epilazione laser diodo") == "epilazione_laser"

    def test_duration_pulizia_viso(self):
        ext = self._get_extractor()
        assert ext.calculate_duration("pulizia_viso") == 60


class TestH1OdontoiatraEntities:
    """Test dental entity extraction."""

    def _get_extractor(self):
        from verticals.odontoiatra.entities import OdontoiatraEntityExtractor
        return OdontoiatraEntityExtractor()

    def test_extract_igiene(self):
        ext = self._get_extractor()
        assert ext.extract_service("pulizia dei denti") == "igiene"

    def test_extract_otturazione(self):
        ext = self._get_extractor()
        assert ext.extract_service("ho una carie da curare") == "otturazione"

    def test_extract_impianto(self):
        ext = self._get_extractor()
        assert ext.extract_service("informazioni sugli impianti") == "impianto"

    def test_urgency_critica(self):
        ext = self._get_extractor()
        assert ext.extract_urgency("non respiro, emergenza") == "critica"

    def test_urgency_alta(self):
        ext = self._get_extractor()
        assert ext.extract_urgency("ho un dolore forte al dente") == "alta"

    def test_urgency_media(self):
        ext = self._get_extractor()
        assert ext.extract_urgency("ho un po' di fastidio") == "media"


class TestH1FisioterapiaEntities:
    """Test physiotherapy entity extraction."""

    def _get_extractor(self):
        from verticals.fisioterapia.entities import FisioterapiaEntityExtractor
        return FisioterapiaEntityExtractor()

    def test_extract_tecarterapia(self):
        ext = self._get_extractor()
        assert ext.extract_service("ho bisogno di tecarterapia") == "tecarterapia"

    def test_extract_onde_urto(self):
        ext = self._get_extractor()
        assert ext.extract_service("terapia con onde d'urto") == "onde_urto"

    def test_extract_posturale(self):
        ext = self._get_extractor()
        assert ext.extract_service("ginnastica posturale") == "posturale"

    def test_urgency_alta(self):
        ext = self._get_extractor()
        assert ext.extract_urgency("colpo della strega, non riesco a muovermi") == "alta"


class TestH1GommistaEntities:
    """Test tire center entity extraction."""

    def _get_extractor(self):
        from verticals.gommista.entities import GommistaEntityExtractor
        return GommistaEntityExtractor()

    def test_extract_cambio_gomme(self):
        ext = self._get_extractor()
        assert ext.extract_service("devo cambiare le gomme invernali") == "cambio_gomme"

    def test_extract_convergenza(self):
        ext = self._get_extractor()
        assert ext.extract_service("fare la convergenza") == "convergenza"

    def test_extract_foratura(self):
        ext = self._get_extractor()
        assert ext.extract_service("ho una gomma forata") == "foratura"

    def test_extract_targa(self):
        ext = self._get_extractor()
        assert ext.extract_targa("la mia auto è AB123CD") == "AB123CD"

    def test_extract_misura_pneumatici(self):
        ext = self._get_extractor()
        assert ext.extract_misura("mi servono 205/55 R16") == "205/55 R16"


class TestH1ToelettaturaEntities:
    """Test pet grooming entity extraction."""

    def _get_extractor(self):
        from verticals.toelettatura.entities import ToelettaturaEntityExtractor
        return ToelettaturaEntityExtractor()

    def test_extract_bagno(self):
        ext = self._get_extractor()
        assert ext.extract_service("vorrei fare il bagno al cane") == "bagno"

    def test_extract_tosatura(self):
        ext = self._get_extractor()
        assert ext.extract_service("devo far tosare il cane") == "tosatura"

    def test_extract_pet_type_cane(self):
        ext = self._get_extractor()
        assert ext.extract_pet_type("ho un cane labrador") == "cane"

    def test_extract_pet_type_gatto(self):
        ext = self._get_extractor()
        assert ext.extract_pet_type("il mio gatto persiano") == "gatto"

    def test_extract_pet_size_grande(self):
        ext = self._get_extractor()
        assert ext.extract_pet_size("è un labrador grande") == "grande"

    def test_duration_adjusts_by_size(self):
        ext = self._get_extractor()
        base = ext.calculate_duration("bagno", "medio")
        large = ext.calculate_duration("bagno", "grande")
        small = ext.calculate_duration("bagno", "piccolo")
        assert large > base > small


# =============================================================================
# H2: Expanded medical triage rules
# =============================================================================

class TestH2MedicalTriageExpanded:
    """Test expanded medical triage rules."""

    def _load_triage_rules(self):
        config_path = VERTICALS_DIR / "medical" / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        return config["triage_rules"]

    def test_triage_rules_count(self):
        rules = self._load_triage_rules()
        assert len(rules) >= 5, f"Expected >= 5 triage rules, got {len(rules)}"

    def test_emergency_rules_exist(self):
        rules = self._load_triage_rules()
        emergency = [r for r in rules if r["urgency"] == "emergency"]
        assert len(emergency) >= 2, "Need at least 2 emergency rules"

    def test_urgent_rules_exist(self):
        rules = self._load_triage_rules()
        urgent = [r for r in rules if r["urgency"] == "urgent"]
        assert len(urgent) >= 2, "Need at least 2 urgent rules"

    def test_normal_rules_exist(self):
        rules = self._load_triage_rules()
        normal = [r for r in rules if r["urgency"] == "normal"]
        assert len(normal) >= 1, "Need at least 1 normal rule"

    def test_emergency_mentions_118(self):
        rules = self._load_triage_rules()
        emergency = [r for r in rules if r["urgency"] == "emergency"]
        for rule in emergency:
            assert "118" in rule["response"] or "pronto soccorso" in rule["response"].lower()

    def test_dental_trauma_covered(self):
        rules = self._load_triage_rules()
        dental_symptoms = []
        for rule in rules:
            dental_symptoms.extend(rule["symptoms"])
        assert any("dente" in s for s in dental_symptoms), "Dental trauma not covered"

    def test_odontoiatra_triage_rules(self):
        config_path = VERTICALS_DIR / "odontoiatra" / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        rules = config.get("triage_rules", [])
        assert len(rules) >= 3, f"Odontoiatra needs >= 3 triage rules, got {len(rules)}"

    def test_fisioterapia_triage_rules(self):
        config_path = VERTICALS_DIR / "fisioterapia" / "config.json"
        with open(config_path) as f:
            config = json.load(f)
        rules = config.get("triage_rules", [])
        assert len(rules) >= 3, f"Fisioterapia needs >= 3 triage rules, got {len(rules)}"


# =============================================================================
# H3: Vertical-aware analytics (verification only)
# =============================================================================

class TestH3VerticalAnalytics:
    """Verify vertical_id tracking in analytics."""

    def test_conversation_session_has_verticale_id(self):
        from src.analytics import ConversationSession
        session = ConversationSession()
        assert hasattr(session, 'verticale_id')
        assert session.verticale_id == ""

    def test_analytics_start_session_accepts_verticale_id(self):
        from src.analytics import FluxionAnalytics
        analytics = FluxionAnalytics(db_path=":memory:")
        session_id = analytics.start_session(verticale_id="barbiere")
        assert session_id is not None

    def test_analytics_get_metrics_filters_by_vertical(self):
        from src.analytics import FluxionAnalytics
        analytics = FluxionAnalytics(db_path=":memory:")
        # Should not raise when filtering by vertical
        metrics = analytics.get_metrics(verticale_id="salone", days=7)
        assert metrics is not None


# =============================================================================
# H4: Cross-vertical composite customer cards
# =============================================================================

class TestH4CompositeCustomerCards:
    """Test CompositeCustomerCard functionality."""

    def test_create_composite(self):
        from src.vertical_schemas import CustomerCardFactory
        composite = CustomerCardFactory.create_composite(
            customer_id="test-001",
            verticals=["odontoiatra", "fisioterapia"]
        )
        assert composite.customer_id == "test-001"
        assert len(composite.get_verticals()) == 2
        assert composite.has_vertical("odontoiatra")
        assert composite.has_vertical("fisioterapia")

    def test_composite_get_card(self):
        from src.vertical_schemas import CustomerCardFactory, SchedaOdontoiatrica
        composite = CustomerCardFactory.create_composite(
            customer_id="test-002",
            verticals=["odontoiatra"]
        )
        card = composite.get_card("odontoiatra")
        assert isinstance(card, SchedaOdontoiatrica)

    def test_composite_with_profile(self):
        from src.vertical_schemas import CustomerCardFactory, CustomerProfile, CustomerTier
        profile = CustomerProfile(
            customer_id="test-003", phone="3331234567",
            name="Mario", surname="Rossi",
            tier=CustomerTier.GOLD, allergies=["lattice"]
        )
        composite = CustomerCardFactory.create_composite(
            customer_id="test-003",
            verticals=["beauty", "odontoiatra"],
            profile=profile
        )
        assert composite.profile.name == "Mario"
        assert "lattice" in composite.get_all_allergies()

    def test_composite_aggregate_allergies(self):
        from src.vertical_schemas import (
            CompositeCustomerCard, SchedaOdontoiatrica, SchedaEstetica,
            CustomerProfile, CustomerTier
        )
        profile = CustomerProfile(
            customer_id="test-004", phone="333", name="Anna", surname="Bianchi",
            allergies=["penicillina"]
        )
        composite = CompositeCustomerCard(
            customer_id="test-004", profile=profile,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        dental = SchedaOdontoiatrica(customer_id="test-004", created_at=datetime.now().isoformat())
        dental.allergia_lattice = True
        dental.allergia_anestesia = True
        composite.add_card("odontoiatra", dental)

        beauty = SchedaEstetica(customer_id="test-004", created_at=datetime.now().isoformat())
        beauty.allergie_prodotti = ["henné"]
        composite.add_card("beauty", beauty)

        all_allergies = composite.get_all_allergies()
        assert "penicillina" in all_allergies
        assert "lattice" in all_allergies
        assert "anestesia locale" in all_allergies
        assert "henné" in all_allergies

    def test_composite_medical_warnings(self):
        from src.vertical_schemas import CompositeCustomerCard, AnamnesiBase
        composite = CompositeCustomerCard(
            customer_id="test-005",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        anamnesi = AnamnesiBase(
            customer_id="test-005",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        anamnesi.patologie_croniche = ["diabete", "ipertensione"]
        composite.add_card("medical", anamnesi)
        warnings = composite.get_medical_warnings()
        assert len(warnings) >= 1
        assert "diabete" in warnings[0]

    def test_composite_to_dict(self):
        from src.vertical_schemas import CustomerCardFactory
        composite = CustomerCardFactory.create_composite(
            customer_id="test-006",
            verticals=["barbiere", "beauty"]
        )
        d = composite.to_dict()
        assert d["customer_id"] == "test-006"
        assert "barbiere" in d["verticals"]
        assert "beauty" in d["verticals"]
        assert "cards" in d

    def test_factory_sub_vertical_mapping(self):
        from src.vertical_schemas import CustomerCardFactory, SchedaParrucchiere, SchedaVeicolo, SchedaEstetica
        assert isinstance(CustomerCardFactory.create_card("barbiere", "x"), SchedaParrucchiere)
        assert isinstance(CustomerCardFactory.create_card("gommista", "x"), SchedaVeicolo)
        assert isinstance(CustomerCardFactory.create_card("beauty", "x"), SchedaEstetica)


# =============================================================================
# H5: Vertical business hours in availability checker
# =============================================================================

class TestH5VerticalBusinessHours:
    """Test per-vertical business hours configuration."""

    def _get_config(self, vertical):
        from src.availability_checker import AvailabilityConfig
        return AvailabilityConfig.for_vertical(vertical)

    def test_palestra_early_opening(self):
        config = self._get_config("palestra")
        assert config.opening_time == "06:00"
        assert config.closing_time == "22:00"

    def test_palestra_no_lunch_break(self):
        config = self._get_config("palestra")
        assert config.lunch_start == ""

    def test_medical_standard_hours(self):
        config = self._get_config("medical")
        assert config.opening_time == "08:30"
        assert 5 not in config.working_days  # No Saturday for medical
        assert 6 not in config.working_days  # No Sunday

    def test_salone_closed_monday(self):
        config = self._get_config("salone")
        assert 1 not in config.working_days  # Monday not in working days

    def test_barbiere_closed_monday(self):
        config = self._get_config("barbiere")
        assert 1 not in config.working_days

    def test_auto_early_opening(self):
        config = self._get_config("auto")
        assert config.opening_time == "08:00"

    def test_gommista_service_durations(self):
        config = self._get_config("gommista")
        assert "cambio_gomme" in config.service_durations
        assert config.service_durations["cambio_gomme"] == 45

    def test_odontoiatra_has_saturday(self):
        config = self._get_config("odontoiatra")
        assert 6 in config.working_days  # Saturday

    def test_fisioterapia_early_start(self):
        config = self._get_config("fisioterapia")
        assert config.opening_time == "08:30"

    def test_toelettatura_hours(self):
        config = self._get_config("toelettatura")
        assert config.opening_time == "09:00"
        assert "bagno" in config.service_durations

    def test_beauty_service_durations(self):
        config = self._get_config("beauty")
        assert "pulizia_viso" in config.service_durations
        assert config.service_durations["pulizia_viso"] == 60

    def test_unknown_vertical_returns_default(self):
        config = self._get_config("unknown_vertical")
        assert config.opening_time == "09:00"  # default
        assert config.closing_time == "19:00"

    def test_all_verticals_have_configs(self):
        """Every registered vertical has a business hours config."""
        verticals = ["salone", "barbiere", "beauty", "medical", "odontoiatra",
                      "fisioterapia", "palestra", "auto", "gommista", "toelettatura"]
        for v in verticals:
            config = self._get_config(v)
            assert config.opening_time != "", f"{v} has empty opening_time"
            assert len(config.working_days) >= 4, f"{v} has too few working days"


# =============================================================================
# Integration: vertical manager recognizes new sub-verticals
# =============================================================================

class TestVerticalManagerIntegration:
    """Test that vertical_manager.py recognizes the new sub-verticals."""

    def test_vertical_type_enum_has_sub_verticals(self):
        from verticals.vertical_manager import VerticalType
        sub_verticals = ["barbiere", "beauty", "odontoiatra", "fisioterapia", "gommista", "toelettatura"]
        for sv in sub_verticals:
            assert any(vt.value == sv for vt in VerticalType), f"{sv} not in VerticalType enum"

    def test_config_json_loadable_for_all(self):
        """All sub-verticals have loadable config.json."""
        from verticals.vertical_manager import VerticalType
        sub_verticals = ["barbiere", "beauty", "odontoiatra", "fisioterapia", "gommista", "toelettatura"]
        for sv in sub_verticals:
            config_path = VERTICALS_DIR / sv / "config.json"
            with open(config_path) as f:
                config = json.load(f)
            assert config["vertical_name"] == sv


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-q"])
