"""
Test Suite for Guided Dialog Engine
FLUXION Voice Agent "Sara"

Run with: pytest tests/test_guided_dialog.py -v
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from guided_dialog import (
    GuidedDialogEngine,
    ItalianFuzzyMatcher,
    DialogState,
    DialogContext,
    VerticalConfigLoader,
    SLOT_TO_STATE,
)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def temp_db():
    """Create temporary SQLite database with test data."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clienti (
            id INTEGER PRIMARY KEY,
            nome TEXT, cognome TEXT,
            telefono TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servizi (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            prezzo REAL,
            attivo BOOLEAN DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operatori (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            cognome TEXT,
            attivo BOOLEAN DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appuntamenti (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER,
            servizio_id INTEGER,
            operatore_id INTEGER,
            data DATE,
            ora_inizio TIME,
            stato TEXT DEFAULT 'confermato',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert test data
    cursor.execute("INSERT INTO servizi (nome, prezzo) VALUES ('Taglio uomo', 20)")
    cursor.execute("INSERT INTO servizi (nome, prezzo) VALUES ('Taglio donna', 30)")
    cursor.execute("INSERT INTO servizi (nome, prezzo) VALUES ('Piega', 15)")
    cursor.execute("INSERT INTO servizi (nome, prezzo) VALUES ('Colore', 50)")
    cursor.execute("INSERT INTO operatori (nome, cognome) VALUES ('Marco', 'Rossi')")
    cursor.execute("INSERT INTO operatori (nome, cognome) VALUES ('Giulia', 'Bianchi')")
    cursor.execute("INSERT INTO operatori (nome, cognome) VALUES ('Luca', 'Verdi')")
    cursor.execute("INSERT INTO clienti (nome, cognome, telefono) VALUES ('Mario', 'Cliente', '3331234567')")

    conn.commit()
    conn.close()

    yield path

    # Cleanup
    os.unlink(path)


@pytest.fixture
def engine(temp_db):
    """Create GuidedDialogEngine instance."""
    return GuidedDialogEngine(
        vertical_id="salone",
        db_path=temp_db
    )


# ============================================================
# TEST: ItalianFuzzyMatcher
# ============================================================

class TestItalianFuzzyMatcher:
    """Test fuzzy matching italiano."""

    def test_ordinali_numeri(self):
        """Test numeri ordinali."""
        assert ItalianFuzzyMatcher.match_ordinal("1") == 0
        assert ItalianFuzzyMatcher.match_ordinal("2") == 1
        assert ItalianFuzzyMatcher.match_ordinal("3") == 2
        assert ItalianFuzzyMatcher.match_ordinal("10") == 9

    def test_ordinali_parole(self):
        """Test ordinali in parole."""
        assert ItalianFuzzyMatcher.match_ordinal("uno") == 0
        assert ItalianFuzzyMatcher.match_ordinal("due") == 1
        assert ItalianFuzzyMatcher.match_ordinal("tre") == 2
        assert ItalianFuzzyMatcher.match_ordinal("primo") == 0
        assert ItalianFuzzyMatcher.match_ordinal("secondo") == 1

    def test_ordinali_articoli(self):
        """Test ordinali con articoli."""
        assert ItalianFuzzyMatcher.match_ordinal("il primo") == 0
        assert ItalianFuzzyMatcher.match_ordinal("la prima") == 0
        assert ItalianFuzzyMatcher.match_ordinal("il secondo") == 1
        assert ItalianFuzzyMatcher.match_ordinal("la seconda") == 1

    def test_conferma_si(self):
        """Test conferma positiva."""
        assert ItalianFuzzyMatcher.is_conferma_si("si")
        assert ItalianFuzzyMatcher.is_conferma_si("si!")
        assert ItalianFuzzyMatcher.is_conferma_si("va bene")
        assert ItalianFuzzyMatcher.is_conferma_si("ok")
        assert ItalianFuzzyMatcher.is_conferma_si("perfetto")
        assert ItalianFuzzyMatcher.is_conferma_si("confermo")
        assert not ItalianFuzzyMatcher.is_conferma_si("no")

    def test_conferma_no(self):
        """Test conferma negativa."""
        assert ItalianFuzzyMatcher.is_conferma_no("no")
        assert ItalianFuzzyMatcher.is_conferma_no("annulla")
        assert ItalianFuzzyMatcher.is_conferma_no("cancella")
        assert not ItalianFuzzyMatcher.is_conferma_no("si")

    def test_nuovo_cliente(self):
        """Test riconoscimento nuovo cliente."""
        assert ItalianFuzzyMatcher.is_nuovo_cliente("e la prima volta")
        assert ItalianFuzzyMatcher.is_nuovo_cliente("non sono mai stato")
        assert ItalianFuzzyMatcher.is_nuovo_cliente("sono nuovo")
        assert ItalianFuzzyMatcher.is_nuovo_cliente("mai stato da voi")
        assert not ItalianFuzzyMatcher.is_nuovo_cliente("vorrei un taglio")

    def test_operatore_default(self):
        """Test operatore default."""
        assert ItalianFuzzyMatcher.is_operatore_default("chiunque")
        assert ItalianFuzzyMatcher.is_operatore_default("chi c'e")
        assert ItalianFuzzyMatcher.is_operatore_default("chi e disponibile")
        assert ItalianFuzzyMatcher.is_operatore_default("fate voi")
        assert not ItalianFuzzyMatcher.is_operatore_default("Marco")

    def test_date_oggi(self):
        """Test data oggi."""
        result = ItalianFuzzyMatcher.extract_date("oggi")
        expected = datetime.now().strftime("%Y-%m-%d")
        assert result == expected

    def test_date_domani(self):
        """Test data domani."""
        result = ItalianFuzzyMatcher.extract_date("domani")
        expected = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert result == expected

    def test_date_dopodomani(self):
        """Test data dopodomani."""
        result = ItalianFuzzyMatcher.extract_date("dopodomani")
        expected = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        assert result == expected

    def test_date_giorno_settimana(self):
        """Test data giorno della settimana."""
        result = ItalianFuzzyMatcher.extract_date("lunedi")
        assert result is not None
        # Deve essere un lunedi futuro
        date_obj = datetime.strptime(result, "%Y-%m-%d")
        assert date_obj.weekday() == 0  # Monday
        assert date_obj > datetime.now()

    def test_time_mattina(self):
        """Test ora mattina."""
        result = ItalianFuzzyMatcher.extract_time("mattina")
        assert result == "09:00"

    def test_time_pomeriggio(self):
        """Test ora pomeriggio."""
        result = ItalianFuzzyMatcher.extract_time("pomeriggio")
        assert result == "14:00"

    def test_time_esplicito(self):
        """Test ora esplicita."""
        assert ItalianFuzzyMatcher.extract_time("10:30") == "10:30"
        assert ItalianFuzzyMatcher.extract_time("alle 15") == "15:00"
        assert ItalianFuzzyMatcher.extract_time("le 9") == "09:00"

    def test_normalize(self):
        """Test normalizzazione testo."""
        assert ItalianFuzzyMatcher.normalize("Si!") == "si"
        assert ItalianFuzzyMatcher.normalize("Domani?") == "domani"
        assert ItalianFuzzyMatcher.normalize("  Spazi   multipli  ") == "spazi multipli"

    def test_sinonimi_servizi(self):
        """Test match servizi con sinonimi."""
        services = ["Taglio uomo", "Taglio donna", "Piega", "Colore"]

        assert ItalianFuzzyMatcher.match_servizio_sinonimo("taglio", services) in ["Taglio uomo", "Taglio donna"]
        assert ItalianFuzzyMatcher.match_servizio_sinonimo("piega", services) == "Piega"
        assert ItalianFuzzyMatcher.match_servizio_sinonimo("tinta", services) == "Colore"
        assert ItalianFuzzyMatcher.match_servizio_sinonimo("xyz", services) is None


# ============================================================
# TEST: GuidedDialogEngine
# ============================================================

class TestGuidedDialogEngine:
    """Test core dialog engine."""

    def test_start_dialog_nuovo_cliente(self, engine):
        """Test start dialogo nuovo cliente."""
        greeting, context = engine.start_dialog(user_phone=None)

        assert context.state in [DialogState.COLLECTING_SERVIZIO, DialogState.GREETING]
        assert context.vertical_id == "salone"
        assert len(greeting) > 0
        assert "Sara" in greeting or "Buongiorno" in greeting

    def test_start_dialog_cliente_noto(self, engine, temp_db):
        """Test start dialogo cliente noto."""
        greeting, context = engine.start_dialog(user_phone="3331234567")

        assert context.db_client_id is not None
        assert "cliente_nome" in context.slot_values
        assert context.slot_values["cliente_nome"] == "Mario Cliente"

    def test_validate_slot_servizio_ordinale(self, engine):
        """Test validazione slot servizio con ordinale."""
        engine.start_dialog()

        is_valid, value = engine._validate_slot("servizio", "1")
        assert is_valid
        # Services are sorted alphabetically: Colore, Piega, Taglio donna, Taglio uomo
        assert value == "Colore"  # First service alphabetically

    def test_validate_slot_servizio_nome(self, engine):
        """Test validazione slot servizio con nome."""
        engine.start_dialog()

        is_valid, value = engine._validate_slot("servizio", "piega")
        assert is_valid
        assert value == "Piega"

    def test_validate_slot_operatore_nome(self, engine):
        """Test validazione slot operatore con nome."""
        engine.start_dialog()

        is_valid, value = engine._validate_slot("operatore", "Marco")
        assert is_valid
        assert "Marco" in value

    def test_validate_slot_operatore_default(self, engine):
        """Test validazione slot operatore default."""
        engine.start_dialog()

        is_valid, value = engine._validate_slot("operatore", "chiunque")
        assert is_valid
        assert value == "primo disponibile"

    def test_validate_slot_data_domani(self, engine):
        """Test validazione slot data."""
        engine.start_dialog()

        is_valid, value = engine._validate_slot("data", "domani")
        assert is_valid
        assert value is not None

    def test_validate_slot_ora_mattina(self, engine):
        """Test validazione slot ora."""
        engine.start_dialog()

        is_valid, value = engine._validate_slot("ora", "mattina")
        assert is_valid
        assert value == "09:00"

    def test_validate_slot_cliente_nome(self, engine):
        """Test validazione slot nome cliente."""
        engine.start_dialog()

        is_valid, value = engine._validate_slot("cliente_nome", "Mario Rossi")
        assert is_valid
        assert value == "Mario Rossi"

    def test_validate_slot_cliente_tel(self, engine):
        """Test validazione slot telefono."""
        engine.start_dialog()

        is_valid, value = engine._validate_slot("cliente_tel", "333 1234567")
        assert is_valid
        assert value == "3331234567"

    def test_fallback_counter_increment(self, engine):
        """Test incremento fallback counter."""
        engine.start_dialog()

        # Prima risposta invalida
        response, state = engine.process_user_input("xyz123")
        assert engine.context.fallback_count.get("servizio", 0) == 1
        assert state == DialogState.FALLBACK_1

        # Seconda risposta invalida
        response, state = engine.process_user_input("abc456")
        assert engine.context.fallback_count.get("servizio", 0) == 2
        assert state == DialogState.FALLBACK_2

    def test_escalation_max_fallback(self, engine):
        """Test escalation dopo 3 fallback."""
        engine.start_dialog()
        engine.context.fallback_count["servizio"] = 2

        response, state = engine.process_user_input("xyz")
        assert state == DialogState.FALLBACK_3_ESCALATION

    def test_faq_inline_prezzo(self, engine):
        """Test FAQ inline per prezzi."""
        engine.start_dialog()

        response, state = engine.process_user_input("quanto costa un taglio?")
        assert "20" in response or "euro" in response.lower()

    def test_conversazione_completa(self, engine):
        """Test conversazione completa end-to-end."""
        greeting, context = engine.start_dialog()

        # Servizio
        response, state = engine.process_user_input("1")  # Taglio uomo
        assert "Taglio uomo" in response or "perfetto" in response.lower()

        # Operatore
        response, state = engine.process_user_input("1")  # Marco
        assert "Marco" in response or "ottimo" in response.lower()

        # Data
        response, state = engine.process_user_input("domani")
        assert "domani" in response.lower() or "trovato" in response.lower()

        # Ora
        response, state = engine.process_user_input("mattina")
        assert "09:00" in response or "perfetto" in response.lower()

        # Nome (se non cliente noto)
        if state != DialogState.CONFIRMING:
            response, state = engine.process_user_input("Test User")

        # Telefono (se richiesto)
        if state != DialogState.CONFIRMING:
            response, state = engine.process_user_input("3339876543")

        # Dovrebbe essere in conferma
        assert state == DialogState.CONFIRMING

        # Conferma
        response, state = engine.process_user_input("si")
        assert state == DialogState.SUCCESS


# ============================================================
# TEST: Integrazione
# ============================================================

class TestIntegration:
    """Test di integrazione end-to-end."""

    def test_conversazione_ambigua_con_fallback(self, engine):
        """Test conversazione con input ambiguo -> fallback."""
        engine.start_dialog()

        # Input ambiguo
        response1, state1 = engine.process_user_input("boh non so")
        assert "capir" in response1.lower() or "trattamento" in response1.lower() or "aiutarla" in response1.lower() or "servizio" in response1.lower()

        # Ancora ambiguo
        response2, state2 = engine.process_user_input("mah")
        assert "1)" in response2 or "2)" in response2  # Opzioni numerate

    def test_conversazione_off_topic(self, engine):
        """Test redirect da domanda off-topic."""
        engine.start_dialog()

        # FAQ sui prezzi
        response, _ = engine.process_user_input("quali sono i prezzi?")
        assert "euro" in response.lower() or "prezzo" in response.lower()

    def test_cliente_noto_salta_dati(self, engine, temp_db):
        """Test che cliente noto salta raccolta nome/telefono."""
        greeting, context = engine.start_dialog(user_phone="3331234567")

        # Verifica che nome e telefono siano gia popolati
        assert "cliente_nome" in context.slot_values
        assert "cliente_tel" in context.slot_values

        # Servizio
        response, state = engine.process_user_input("1")
        # Operatore
        response, state = engine.process_user_input("chiunque")
        # Data
        response, state = engine.process_user_input("domani")
        # Ora
        response, state = engine.process_user_input("10")

        # Dovrebbe andare diretto a conferma (no nome/tel)
        assert state == DialogState.CONFIRMING


# ============================================================
# TEST: VerticalConfigLoader
# ============================================================

class TestVerticalConfigLoader:
    """Test config loader."""

    def test_load_salone_config(self):
        """Test caricamento config salone."""
        loader = VerticalConfigLoader("salone")

        assert loader.config["vertical_id"] == "salone"
        assert "prompts" in loader.config
        assert "slots_order" in loader.config

    def test_load_default_config(self):
        """Test fallback a config default."""
        loader = VerticalConfigLoader("non_esistente")

        assert "prompts" in loader.config
        assert "slots_order" in loader.config

    def test_get_prompt(self):
        """Test get prompt con placeholder."""
        loader = VerticalConfigLoader("salone")

        prompt = loader.get_prompt("greeting_cliente_noto", nome_cliente="Mario")
        assert "Mario" in prompt

    def test_get_services(self, temp_db):
        """Test get services da DB."""
        loader = VerticalConfigLoader("salone")

        services = loader.get_services(temp_db)
        assert len(services) >= 1
        assert "nome" in services[0]

    def test_get_operatori(self, temp_db):
        """Test get operatori da DB."""
        loader = VerticalConfigLoader("salone")

        operatori = loader.get_operatori(temp_db)
        assert len(operatori) >= 1
        assert "nome" in operatori[0]


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
