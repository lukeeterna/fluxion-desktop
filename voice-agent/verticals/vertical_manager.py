"""
Vertical Manager - Gestione configurazioni multi-verticale per Voice Agent
Carica, valida e gestisce le configurazioni specifiche per ogni settore.

Verticali supportati:
- medical: Studi medici, cliniche
- palestra: Palestre, centri fitness
- auto: Officine, carrozzerie
- salone: Saloni di bellezza, parrucchieri
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class VerticalType(Enum):
    """Tipi di verticali supportati"""
    MEDICAL = "medical"
    PALESTRA = "palestra"
    AUTO = "auto"
    SALONE = "salone"


@dataclass
class Intent:
    """Rappresenta un intent con i suoi esempi e slot"""
    id: str
    name: str
    priority: int
    examples: List[str]
    required_slots: List[str]
    optional_slots: List[str]


@dataclass
class Slot:
    """Rappresenta uno slot con tipo e configurazione"""
    name: str
    type: str
    prompt: str
    values: Optional[List[str]] = None
    format: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None


@dataclass
class FAQ:
    """Rappresenta una FAQ con keywords per retrieval"""
    id: str
    keywords: List[str]
    question: str
    answer: str


@dataclass
class VerticalConfig:
    """Configurazione completa di un verticale"""
    vertical_name: str
    display_name: str
    language: str
    description: str
    intents: List[Intent]
    slots: Dict[str, Slot]
    faq: List[FAQ]
    responses: Dict[str, str]
    variables: Dict[str, str]
    triage_rules: List[Dict] = field(default_factory=list)


class VerticalManager:
    """
    Gestore delle configurazioni verticali.
    Carica, valida e fornisce accesso alle configurazioni specifiche per settore.
    """

    def __init__(self, verticals_path: Optional[str] = None):
        """
        Inizializza il manager con il path alle configurazioni.

        Args:
            verticals_path: Path alla directory dei verticali.
                           Default: directory corrente/verticals
        """
        if verticals_path is None:
            verticals_path = Path(__file__).parent
        self.verticals_path = Path(verticals_path)
        self._configs: Dict[str, VerticalConfig] = {}
        self._loaded = False

    def load_all(self) -> Dict[str, VerticalConfig]:
        """Carica tutte le configurazioni verticali disponibili."""
        for vertical_type in VerticalType:
            config_path = self.verticals_path / vertical_type.value / "config.json"
            if config_path.exists():
                self._configs[vertical_type.value] = self._load_config(config_path)
        self._loaded = True
        return self._configs

    def load_vertical(self, vertical_name: str) -> VerticalConfig:
        """
        Carica una singola configurazione verticale.

        Args:
            vertical_name: Nome del verticale (es. "salone", "medical")

        Returns:
            VerticalConfig caricata

        Raises:
            FileNotFoundError: Se la configurazione non esiste
            ValueError: Se il verticale non e' valido
        """
        if vertical_name not in [v.value for v in VerticalType]:
            raise ValueError(f"Verticale non supportato: {vertical_name}")

        config_path = self.verticals_path / vertical_name / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Config non trovata: {config_path}")

        config = self._load_config(config_path)
        self._configs[vertical_name] = config
        return config

    def get_config(self, vertical_name: str) -> Optional[VerticalConfig]:
        """Ottiene una configurazione gia' caricata."""
        if not self._loaded and vertical_name not in self._configs:
            try:
                return self.load_vertical(vertical_name)
            except FileNotFoundError:
                return None
        return self._configs.get(vertical_name)

    def _load_config(self, config_path: Path) -> VerticalConfig:
        """Carica e parsa un file di configurazione JSON."""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Parse intents
        intents = [
            Intent(
                id=i['id'],
                name=i['name'],
                priority=i.get('priority', 3),
                examples=i['examples'],
                required_slots=i.get('required_slots', []),
                optional_slots=i.get('optional_slots', [])
            )
            for i in data.get('intents', [])
        ]

        # Parse slots
        slots = {
            name: Slot(
                name=name,
                type=s['type'],
                prompt=s['prompt'],
                values=s.get('values'),
                format=s.get('format'),
                min=s.get('min'),
                max=s.get('max')
            )
            for name, s in data.get('slots', {}).items()
        }

        # Parse FAQ
        faq = [
            FAQ(
                id=f['id'],
                keywords=f['keywords'],
                question=f['question'],
                answer=f['answer']
            )
            for f in data.get('faq', [])
        ]

        return VerticalConfig(
            vertical_name=data['vertical_name'],
            display_name=data['display_name'],
            language=data['language'],
            description=data['description'],
            intents=intents,
            slots=slots,
            faq=faq,
            responses=data.get('responses', {}),
            variables=data.get('variables', {}),
            triage_rules=data.get('triage_rules', [])
        )

    def get_intent_examples(self, vertical_name: str) -> Dict[str, List[str]]:
        """
        Ottiene tutti gli esempi di intent per un verticale.
        Utile per training NLU.
        """
        config = self.get_config(vertical_name)
        if not config:
            return {}

        return {
            intent.id: intent.examples
            for intent in config.intents
        }

    def get_slot_values(self, vertical_name: str, slot_name: str) -> Optional[List[str]]:
        """Ottiene i valori validi per uno slot categorico."""
        config = self.get_config(vertical_name)
        if not config or slot_name not in config.slots:
            return None

        return config.slots[slot_name].values

    def get_slot_prompt(self, vertical_name: str, slot_name: str) -> Optional[str]:
        """Ottiene il prompt per richiedere uno slot."""
        config = self.get_config(vertical_name)
        if not config or slot_name not in config.slots:
            return None

        return config.slots[slot_name].prompt

    def search_faq(self, vertical_name: str, query: str) -> List[FAQ]:
        """
        Cerca FAQ per keywords.

        Args:
            vertical_name: Nome del verticale
            query: Query di ricerca

        Returns:
            Lista di FAQ che matchano la query
        """
        config = self.get_config(vertical_name)
        if not config:
            return []

        query_lower = query.lower()
        query_words = set(query_lower.split())

        matches = []
        for faq in config.faq:
            # Check keyword overlap
            keyword_set = set(k.lower() for k in faq.keywords)
            if query_words & keyword_set:
                matches.append(faq)
            # Check if any keyword is in query
            elif any(kw.lower() in query_lower for kw in faq.keywords):
                matches.append(faq)

        return matches

    def render_response(
        self,
        vertical_name: str,
        response_key: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Renderizza una risposta template con variabili.

        Args:
            vertical_name: Nome del verticale
            response_key: Chiave della risposta (es. "greeting", "booking_confirm")
            context: Variabili di contesto per il rendering

        Returns:
            Risposta renderizzata con variabili sostituite
        """
        config = self.get_config(vertical_name)
        if not config or response_key not in config.responses:
            return ""

        template = config.responses[response_key]

        # Merge variables from config with context
        variables = {**config.variables}
        if context:
            variables.update(context)

        # Replace {{VARIABLE}} patterns
        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        result = re.sub(r'\{\{(\w+)\}\}', replace_var, template)
        return result

    def render_faq_answer(
        self,
        vertical_name: str,
        faq: FAQ,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Renderizza la risposta di una FAQ con variabili."""
        config = self.get_config(vertical_name)
        if not config:
            return faq.answer

        variables = {**config.variables}
        if context:
            variables.update(context)

        def replace_var(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))

        return re.sub(r'\{\{(\w+)\}\}', replace_var, faq.answer)

    def get_required_slots(self, vertical_name: str, intent_id: str) -> List[str]:
        """Ottiene gli slot obbligatori per un intent."""
        config = self.get_config(vertical_name)
        if not config:
            return []

        for intent in config.intents:
            if intent.id == intent_id:
                return intent.required_slots
        return []

    def get_optional_slots(self, vertical_name: str, intent_id: str) -> List[str]:
        """Ottiene gli slot opzionali per un intent."""
        config = self.get_config(vertical_name)
        if not config:
            return []

        for intent in config.intents:
            if intent.id == intent_id:
                return intent.optional_slots
        return []

    def validate_slot_value(
        self,
        vertical_name: str,
        slot_name: str,
        value: Any
    ) -> bool:
        """
        Valida un valore per uno slot.

        Returns:
            True se il valore e' valido
        """
        config = self.get_config(vertical_name)
        if not config or slot_name not in config.slots:
            return True  # Se slot non definito, accetta qualsiasi valore

        slot = config.slots[slot_name]

        if slot.type == "categorical" and slot.values:
            return str(value).lower() in [v.lower() for v in slot.values]

        if slot.type == "number":
            try:
                num = float(value)
                if slot.min is not None and num < slot.min:
                    return False
                if slot.max is not None and num > slot.max:
                    return False
                return True
            except (ValueError, TypeError):
                return False

        return True  # Per altri tipi, accetta

    def check_triage_urgency(
        self,
        vertical_name: str,
        symptoms: List[str]
    ) -> Optional[Dict]:
        """
        Controlla se i sintomi indicano urgenza (solo per medical).

        Returns:
            Regola di triage se match, None altrimenti
        """
        config = self.get_config(vertical_name)
        if not config or not config.triage_rules:
            return None

        symptoms_lower = [s.lower() for s in symptoms]

        for rule in config.triage_rules:
            rule_symptoms = [s.lower() for s in rule.get('symptoms', [])]
            # Check if any rule symptom matches
            if any(
                any(rs in sym or sym in rs for sym in symptoms_lower)
                for rs in rule_symptoms
            ):
                return rule

        return None

    def list_available_verticals(self) -> List[str]:
        """Lista i verticali disponibili (con config esistente)."""
        available = []
        for vertical_type in VerticalType:
            config_path = self.verticals_path / vertical_type.value / "config.json"
            if config_path.exists():
                available.append(vertical_type.value)
        return available

    def export_training_data(self, vertical_name: str) -> Dict[str, Any]:
        """
        Esporta dati per training NLU in formato standard.

        Returns:
            Dizionario con intents ed entities per training
        """
        config = self.get_config(vertical_name)
        if not config:
            return {}

        training_data = {
            "vertical": vertical_name,
            "language": config.language,
            "intents": [],
            "entities": [],
            "synonyms": []
        }

        # Export intents with examples
        for intent in config.intents:
            training_data["intents"].append({
                "name": intent.id,
                "examples": intent.examples
            })

        # Export slot values as entities
        for slot_name, slot in config.slots.items():
            if slot.values:
                training_data["entities"].append({
                    "name": slot_name,
                    "values": slot.values
                })

        return training_data


# Singleton instance per uso globale
_manager_instance: Optional[VerticalManager] = None


def get_vertical_manager(verticals_path: Optional[str] = None) -> VerticalManager:
    """Ottiene l'istanza singleton del VerticalManager."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = VerticalManager(verticals_path)
    return _manager_instance


# Convenience functions
def load_vertical(vertical_name: str) -> VerticalConfig:
    """Carica un verticale usando il manager globale."""
    return get_vertical_manager().load_vertical(vertical_name)


def get_faq_answer(vertical_name: str, query: str) -> Optional[str]:
    """Cerca e restituisce la prima risposta FAQ che matcha."""
    manager = get_vertical_manager()
    matches = manager.search_faq(vertical_name, query)
    if matches:
        return manager.render_faq_answer(vertical_name, matches[0])
    return None


def get_greeting(vertical_name: str) -> str:
    """Ottiene il saluto per un verticale."""
    return get_vertical_manager().render_response(vertical_name, "greeting")


def get_slot_prompt_for(vertical_name: str, slot_name: str) -> str:
    """Ottiene il prompt per richiedere uno slot."""
    return get_vertical_manager().get_slot_prompt(vertical_name, slot_name) or f"Mi dice {slot_name}?"


if __name__ == "__main__":
    # Self-test
    print("=" * 60)
    print("VERTICAL MANAGER - SELF TEST")
    print("=" * 60)

    manager = VerticalManager()
    available = manager.list_available_verticals()
    print(f"\nVerticali disponibili: {available}")

    for vertical in available:
        print(f"\n{'='*40}")
        print(f"VERTICALE: {vertical.upper()}")
        print(f"{'='*40}")

        config = manager.load_vertical(vertical)
        print(f"Display name: {config.display_name}")
        print(f"Intents: {len(config.intents)}")
        print(f"FAQ: {len(config.faq)}")
        print(f"Slots: {len(config.slots)}")

        # Test greeting
        greeting = manager.render_response(vertical, "greeting")
        print(f"Greeting: {greeting}")

        # Test FAQ search
        test_queries = {
            "salone": "orari apertura",
            "medical": "specialita",
            "palestra": "abbonamento prezzo",
            "auto": "tagliando costo"
        }

        if vertical in test_queries:
            query = test_queries[vertical]
            faqs = manager.search_faq(vertical, query)
            if faqs:
                answer = manager.render_faq_answer(vertical, faqs[0])
                print(f"FAQ per '{query}': {answer[:80]}...")

        # Test training data export
        training = manager.export_training_data(vertical)
        print(f"Training intents: {len(training.get('intents', []))}")
        print(f"Training entities: {len(training.get('entities', []))}")

    print("\n" + "=" * 60)
    print("SELF TEST COMPLETATO")
    print("=" * 60)
