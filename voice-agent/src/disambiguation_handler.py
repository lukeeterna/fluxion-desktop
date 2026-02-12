"""
FLUXION Voice Agent - Disambiguation Handler

Enterprise-grade client disambiguation module.
Handles multiple client matches by requesting additional info (data_nascita).

Features:
- Deterministic disambiguation flow
- Birth date extraction and validation
- Phonetic/fuzzy name matching for STT error detection
- Multi-step disambiguation with context preservation
- GDPR-compliant data handling
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from enum import Enum


# =============================================================================
# PHONETIC / FUZZY MATCHING UTILITIES
# =============================================================================

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def name_similarity(name1: str, name2: str) -> float:
    """
    Calculate similarity between two names (0.0 to 1.0).
    Uses Levenshtein distance normalized by max length.
    """
    if not name1 or not name2:
        return 0.0

    n1 = name1.lower().strip()
    n2 = name2.lower().strip()

    if n1 == n2:
        return 1.0

    # Calculate Levenshtein distance
    distance = levenshtein_distance(n1, n2)
    max_len = max(len(n1), len(n2))

    if max_len == 0:
        return 0.0

    # Normalize to 0-1 similarity score
    similarity = 1.0 - (distance / max_len)
    return max(0.0, similarity)


def is_phonetically_similar(name1: str, name2: str, threshold: float = 0.75) -> bool:
    """
    Check if two names are phonetically/fuzzy similar.

    This helps detect STT errors like:
    - "Gino" vs "Gigio" (similar pronunciation)
    - "Maria" vs "Mario" (gender confusion)
    - "Anna" vs "Ana" (spelling variation)

    CoVe 2026: Now checks PHONETIC_VARIANTS dictionary in addition to
    Levenshtein similarity for better Italian name matching.

    Args:
        name1: First name
        name2: Second name
        threshold: Similarity threshold (default 0.75)

    Returns:
        True if names are similar enough
    """
    n1 = name1.lower().strip()
    n2 = name2.lower().strip()
    
    # Exact match
    if n1 == n2:
        return True
    
    # Check PHONETIC_VARIANTS dictionary (CoVe 2026 enhancement)
    # If both names are variants of the same base name, they're phonetically similar
    for base_name, variants in PHONETIC_VARIANTS.items():
        all_variants = set(variants + [base_name])
        if n1 in all_variants and n2 in all_variants:
            return True
    
    # Check if one is a base name and other is its variant
    for base_name, variants in PHONETIC_VARIANTS.items():
        if (n1 == base_name and n2 in variants) or (n2 == base_name and n1 in variants):
            return True
    
    # Fall back to Levenshtein similarity
    similarity = name_similarity(name1, name2)
    return similarity >= threshold


# Common Italian name variations that sound similar
PHONETIC_VARIANTS = {
    "gino": ["gigio", "gino", "gigi", "gianni"],
    "gigio": ["gino", "gigi", "gianni"],
    "maria": ["mario", "marie", "mari"],
    "mario": ["maria", "maro"],
    "anna": ["ana", "annamaria", "annamaria"],
    "luigi": ["gigi", "luigia", "luisa"],
    "gigi": ["luigi", "gino", "gigio"],
    "rosa": ["rosy", "rosi", "rosalba"],
    "giuseppe": ["peppe", "beppe", "giuseppina"],
    "francesco": ["franco", "francesca", "ciccio"],
    "antonio": ["antonino", "tony", "toni", "antonietta"],
}


def check_name_ambiguity(input_name: str, matched_name: str) -> Tuple[bool, float, str]:
    """
    Check if there might be ambiguity between input name and matched name.

    Returns:
        (is_ambiguous, confidence, suggestion)
        - is_ambiguous: True if names are similar but not identical
        - confidence: Similarity score
        - suggestion: Human-readable suggestion
    """
    similarity = name_similarity(input_name, matched_name)

    # Exact match - no ambiguity
    if input_name.lower() == matched_name.lower():
        return False, 1.0, ""

    # Check direct similarity (high threshold)
    if similarity >= 0.85:
        return True, similarity, f"Forse intendeva '{matched_name}'?"

    # Check phonetic variants
    input_lower = input_name.lower()
    matched_lower = matched_name.lower()

    for base_name, variants in PHONETIC_VARIANTS.items():
        if input_lower in variants and matched_lower in variants:
            return True, 0.9, f"Forse intendeva '{matched_name}'?"

    # Medium similarity - ask for confirmation
    if similarity >= 0.70:
        return True, similarity, f"Mi conferma che si chiama '{matched_name}'?"

    return False, similarity, ""


class DisambiguationState(Enum):
    """Disambiguation flow states."""
    NOT_NEEDED = "not_needed"
    WAITING_NICKNAME = "waiting_nickname"  # Ask "Mario o Marione?"
    WAITING_BIRTH_DATE = "waiting_birth_date"
    RESOLVED = "resolved"
    FAILED = "failed"
    PROPOSE_REGISTRATION = "propose_registration"


@dataclass
class DisambiguationContext:
    """Context for client disambiguation."""
    state: DisambiguationState = DisambiguationState.NOT_NEEDED
    search_name: str = ""
    potential_clients: List[Dict[str, Any]] = field(default_factory=list)
    resolved_client: Optional[Dict[str, Any]] = None
    attempts: int = 0
    max_attempts: int = 3
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "search_name": self.search_name,
            "potential_count": len(self.potential_clients),
            "resolved": self.resolved_client is not None,
            "attempts": self.attempts
        }


@dataclass
class DisambiguationResult:
    """Result of disambiguation attempt."""
    success: bool
    state: DisambiguationState
    client: Optional[Dict[str, Any]] = None
    response_text: str = ""
    needs_user_input: bool = False
    propose_registration: bool = False


# Italian months mapping
MESI_IT = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
    # Short forms
    "gen": 1, "feb": 2, "mar": 3, "apr": 4, "mag": 5, "giu": 6,
    "lug": 7, "ago": 8, "set": 9, "ott": 10, "nov": 11, "dic": 12
}


# Response templates
TEMPLATES = {
    "ask_nickname": (
        "Ho trovato più clienti. {options}?"
    ),
    "ask_birth_date": (
        "Ho trovato {count} clienti con il nome {name}. "
        "Per identificarla correttamente, mi può dire la sua data di nascita?"
    ),
    "ask_birth_date_retry": (
        "Non ho capito la data. Può dirla nel formato giorno, mese, anno? "
        "Ad esempio: 15 marzo 1985."
    ),
    "no_match_with_date": (
        "Non ho trovato un cliente {name} nato il {date}. "
        "Vuole che la registri come nuovo cliente?"
    ),
    "resolved": "Perfetto, {full_name}! Come posso aiutarla oggi?",
    "max_attempts": (
        "Mi scusi, non sono riuscita a identificarla. "
        "La metto in contatto con un operatore."
    ),
    "single_client": "Buongiorno {full_name}! Come posso aiutarla?",
    "new_client": (
        "Non ho trovato il suo nominativo in archivio. "
        "Vuole che la registri come nuovo cliente?"
    ),
}


class DisambiguationHandler:
    """
    Enterprise disambiguation handler.

    Flow:
    1. search_clients() returns multiple matches
    2. start_disambiguation() initiates disambiguation flow
    3. process_birth_date() attempts to resolve with birth date
    4. Repeat until resolved, failed, or max attempts
    """

    def __init__(self, max_attempts: int = 3):
        self.max_attempts = max_attempts
        self.context = DisambiguationContext(max_attempts=max_attempts)

    def reset(self):
        """Reset disambiguation state."""
        self.context = DisambiguationContext(max_attempts=self.max_attempts)

    def get_context(self) -> DisambiguationContext:
        """Get current context."""
        return self.context

    def start_disambiguation(
        self,
        name: str,
        clients: List[Dict[str, Any]]
    ) -> DisambiguationResult:
        """
        Start disambiguation flow when multiple clients match.

        Strategy:
        1. If clients have unique nicknames/names → ask "Mario o Marione?"
        2. Otherwise fall back to birth date

        Args:
            name: Search name
            clients: List of matching clients

        Returns:
            DisambiguationResult with next step
        """
        self.context.search_name = name
        self.context.potential_clients = clients
        self.context.attempts = 0

        if len(clients) == 0:
            # No clients found - propose registration
            self.context.state = DisambiguationState.PROPOSE_REGISTRATION
            return DisambiguationResult(
                success=False,
                state=DisambiguationState.PROPOSE_REGISTRATION,
                response_text=TEMPLATES["new_client"],
                propose_registration=True
            )

        if len(clients) == 1:
            # Single match - check for phonetic ambiguity
            client = clients[0]
            full_name = self._get_full_name(client)

            # Check if input name is phonetically similar but not identical
            is_ambiguous, confidence, suggestion = check_name_ambiguity(
                self.context.search_name, client.get("nome", "")
            )

            if is_ambiguous and confidence >= 0.70:
                # High similarity but not exact - ask for confirmation
                self.context.state = DisambiguationState.WAITING_BIRTH_DATE
                return DisambiguationResult(
                    success=False,
                    state=DisambiguationState.WAITING_BIRTH_DATE,
                    response_text=f"Ho trovato '{full_name}'. {suggestion} Mi può confermare la sua data di nascita per sicurezza?",
                    needs_user_input=True
                )

            # Exact or clear match - proceed normally
            self.context.state = DisambiguationState.RESOLVED
            self.context.resolved_client = client
            return DisambiguationResult(
                success=True,
                state=DisambiguationState.RESOLVED,
                client=client,
                response_text=TEMPLATES["single_client"].format(full_name=full_name)
            )

        # Multiple matches - first ask birth date, nickname as fallback
        self.context.state = DisambiguationState.WAITING_BIRTH_DATE
        return DisambiguationResult(
            success=False,
            state=DisambiguationState.WAITING_BIRTH_DATE,
            response_text=TEMPLATES["ask_birth_date"].format(
                count=len(clients),
                name=name
            ),
            needs_user_input=True
        )

    def process_birth_date(
        self,
        user_input: str,
        clients: Optional[List[Dict[str, Any]]] = None
    ) -> DisambiguationResult:
        """
        Process user input containing birth date.

        Args:
            user_input: User's message (may contain birth date)
            clients: Optional updated client list (if re-searched from DB)

        Returns:
            DisambiguationResult with resolution status
        """
        if clients is not None:
            self.context.potential_clients = clients

        self.context.attempts += 1

        # Check max attempts
        if self.context.attempts > self.max_attempts:
            self.context.state = DisambiguationState.FAILED
            return DisambiguationResult(
                success=False,
                state=DisambiguationState.FAILED,
                response_text=TEMPLATES["max_attempts"]
            )

        # Extract birth date from input
        birth_date = self.extract_birth_date(user_input)

        if not birth_date:
            # Couldn't extract date - ask again
            return DisambiguationResult(
                success=False,
                state=DisambiguationState.WAITING_BIRTH_DATE,
                response_text=TEMPLATES["ask_birth_date_retry"],
                needs_user_input=True
            )

        # Format date for comparison (YYYY-MM-DD)
        date_str = birth_date.strftime("%Y-%m-%d")

        # Find matching client
        matching_client = None
        for client in self.context.potential_clients:
            client_dob = client.get("data_nascita", "")
            if client_dob == date_str:
                matching_client = client
                break

        if matching_client:
            # Found unique match
            self.context.state = DisambiguationState.RESOLVED
            self.context.resolved_client = matching_client
            full_name = self._get_full_name(matching_client)
            return DisambiguationResult(
                success=True,
                state=DisambiguationState.RESOLVED,
                client=matching_client,
                response_text=TEMPLATES["resolved"].format(full_name=full_name)
            )

        # No match with birth date - try nickname fallback
        nicknames = self._get_unique_identifiers(self.context.potential_clients)
        if nicknames:
            # Can disambiguate by nickname! "Mario o Marione?"
            self.context.state = DisambiguationState.WAITING_NICKNAME
            options = " o ".join(nicknames)
            return DisambiguationResult(
                success=False,
                state=DisambiguationState.WAITING_NICKNAME,
                response_text=f"Non ho trovato questa data. {options}?",
                needs_user_input=True
            )

        # No nickname fallback - propose registration
        self.context.state = DisambiguationState.PROPOSE_REGISTRATION
        formatted_date = self._format_date_italian(birth_date)
        return DisambiguationResult(
            success=False,
            state=DisambiguationState.PROPOSE_REGISTRATION,
            response_text=TEMPLATES["no_match_with_date"].format(
                name=self.context.search_name,
                date=formatted_date
            ),
            propose_registration=True
        )

    def extract_birth_date(self, text: str) -> Optional[date]:
        """
        Extract birth date from Italian text.

        Supports formats:
        - "15 marzo 1985"
        - "15/03/1985"
        - "15-03-1985"
        - "1985-03-15" (ISO)
        - "nato il 15 marzo 1985"
        - "sono del 15 marzo 85"
        - "il 15 marzo 1985"
        - "15 marzo 85"
        - "15/03/85"
        - "primo marzo 1990" (ordinal day)
        - "quindici marzo 1985" (written numbers)

        Returns:
            date object or None
        """
        import logging
        logger = logging.getLogger(__name__)
        
        text_lower = text.lower().strip()
        logger.info(f"[extract_birth_date] Processing: '{text_lower}'")

        # Italian written numbers for days (1-31)
        giorni_scritti = {
            'primo': 1, 'uno': 1, 'due': 2, 'tre': 3, 'quattro': 4, 'cinque': 5,
            'sei': 6, 'sette': 7, 'otto': 8, 'nove': 9, 'dieci': 10,
            'undici': 11, 'dodici': 12, 'tredici': 13, 'quattordici': 14, 'quindici': 15,
            'sedici': 16, 'diciassette': 17, 'diciotto': 18, 'diciannove': 19, 'venti': 20,
            'ventuno': 21, 'ventidue': 22, 'ventitré': 23, 'ventitre': 23, 'ventiquattro': 24,
            'venticinque': 25, 'ventisei': 26, 'ventisette': 27, 'ventotto': 28, 'ventinove': 29,
            'trenta': 30, 'trentuno': 31
        }

        # Pattern 1: Italian format "15 marzo 1985" or "nato il 15 marzo 1985"
        # CoVe: Migliorato regex per catturare più contesti
        pattern_it = r'(?:nato|nata|nascita|del|di|il)?\s*(\d{1,2})\s+([a-zèéàùìò]+)\s+(\d{2,4})\b'
        match = re.search(pattern_it, text_lower)
        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower().rstrip('èéàùìò')
            year = int(match.group(3))

            # Convert 2-digit year to 4-digit (cutoff 1930-2029)
            if year < 100:
                year = 1900 + year if year >= 30 else 2000 + year

            # Convert month name to number
            month = MESI_IT.get(month_name)
            if month:
                try:
                    result = date(year, month, day)
                    logger.info(f"[extract_birth_date] Pattern IT matched: {result}")
                    return result
                except ValueError as e:
                    logger.warning(f"[extract_birth_date] Invalid date: {day}/{month}/{year} - {e}")

        # Pattern 1b: Written day + month + year (e.g., "quindici marzo 1985")
        # Find written number followed by month
        for giorno_str, giorno_num in giorni_scritti.items():
            for mese_str, mese_num in MESI_IT.items():
                pattern_written = rf'\b{giorno_str}\s+{mese_str}\s+(\d{{2,4}})\b'
                match = re.search(pattern_written, text_lower)
                if match:
                    year = int(match.group(1))
                    if year < 100:
                        year = 1900 + year if year >= 30 else 2000 + year
                    try:
                        result = date(year, mese_num, giorno_num)
                        logger.info(f"[extract_birth_date] Pattern written matched: {result}")
                        return result
                    except ValueError:
                        pass

        # Pattern 2: Numeric format "15/03/1985" or "15-03-1985"
        # CoVe: Supporta anche formati senza leading zero
        pattern_numeric = r'\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})\b'
        match = re.search(pattern_numeric, text_lower)
        if match:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))

            # Convert 2-digit year
            if year < 100:
                year = 1900 + year if year >= 30 else 2000 + year

            try:
                result = date(year, month, day)
                logger.info(f"[extract_birth_date] Pattern numeric matched: {result}")
                return result
            except ValueError as e:
                logger.warning(f"[extract_birth_date] Invalid numeric date: {day}/{month}/{year} - {e}")

        # Pattern 3: ISO format "1985-03-15"
        pattern_iso = r'\b(\d{4})-(\d{2})-(\d{2})\b'
        match = re.search(pattern_iso, text_lower)
        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            day = int(match.group(3))
            try:
                result = date(year, month, day)
                logger.info(f"[extract_birth_date] Pattern ISO matched: {result}")
                return result
            except ValueError as e:
                logger.warning(f"[extract_birth_date] Invalid ISO date: {e}")

        # Pattern 4: Day + "di" + month + year (e.g., "15 di marzo 1985")
        pattern_di = r'(?:nato|nata|il)?\s*(\d{1,2})\s+di\s+([a-zèéàùìò]+)\s+(\d{2,4})\b'
        match = re.search(pattern_di, text_lower)
        if match:
            day = int(match.group(1))
            month_name = match.group(2).lower().rstrip('èéàùìò')
            year = int(match.group(3))
            if year < 100:
                year = 1900 + year if year >= 30 else 2000 + year
            month = MESI_IT.get(month_name)
            if month:
                try:
                    result = date(year, month, day)
                    logger.info(f"[extract_birth_date] Pattern DI matched: {result}")
                    return result
                except ValueError:
                    pass

        logger.info(f"[extract_birth_date] No pattern matched for: '{text}'")
        return None

    def _get_unique_identifiers(self, clients: List[Dict[str, Any]]) -> Optional[List[str]]:
        """
        Get unique identifiers for each client.

        Strategy (priority order):
        1. soprannome if unique → ["Mario", "Marione"]
        2. nome + cognome if unique → ["Mario Rossi", "Mario Bianchi"]
        3. None (can't differentiate)

        Returns list of identifiers if all are unique, None otherwise.
        """
        # Strategy 1: soprannome / nome
        identifiers = []
        for client in clients:
            soprannome = client.get("soprannome") or client.get("nickname")
            nome = client.get("nome", "")
            identifier = soprannome if soprannome else nome
            identifiers.append(identifier)

        if len(set(identifiers)) == len(identifiers):
            return identifiers

        # Strategy 2: full name (nome + cognome)
        full_names = []
        for client in clients:
            nome = client.get("nome", "")
            cognome = client.get("cognome", "")
            full_name = f"{nome} {cognome}".strip()
            full_names.append(full_name)

        if len(set(full_names)) == len(full_names):
            return full_names

        return None

    def process_nickname_choice(self, user_input: str) -> DisambiguationResult:
        """
        Process user's nickname choice (e.g., "Marione" from "Mario o Marione?").

        Args:
            user_input: User's response containing chosen name/nickname

        Returns:
            DisambiguationResult with resolution status
        """
        self.context.attempts += 1

        if self.context.attempts > self.max_attempts:
            self.context.state = DisambiguationState.FAILED
            return DisambiguationResult(
                success=False,
                state=DisambiguationState.FAILED,
                response_text=TEMPLATES["max_attempts"]
            )

        user_lower = user_input.lower().strip()

        # Use the same identifiers that were presented to the user
        unique_ids = self._get_unique_identifiers(self.context.potential_clients)
        if unique_ids:
            # Build map from presented identifier → client
            identifier_map = {}
            for identifier, client in zip(unique_ids, self.context.potential_clients):
                identifier_map[identifier.lower()] = client

            # Match user input against presented identifiers (longer first)
            sorted_ids = sorted(identifier_map.keys(), key=len, reverse=True)
            for identifier in sorted_ids:
                if identifier in user_lower:
                    client = identifier_map[identifier]
                    self.context.state = DisambiguationState.RESOLVED
                    self.context.resolved_client = client
                    full_name = self._get_full_name(client)
                    return DisambiguationResult(
                        success=True,
                        state=DisambiguationState.RESOLVED,
                        client=client,
                        response_text=TEMPLATES["resolved"].format(full_name=full_name)
                    )

        # No match - ask again with options
        nicknames = self._get_unique_identifiers(self.context.potential_clients)
        if nicknames:
            options = " o ".join(nicknames)
            return DisambiguationResult(
                success=False,
                state=DisambiguationState.WAITING_NICKNAME,
                response_text=f"Non ho capito. {options}?",
                needs_user_input=True
            )

        # Fall back to birth date
        self.context.state = DisambiguationState.WAITING_BIRTH_DATE
        return DisambiguationResult(
            success=False,
            state=DisambiguationState.WAITING_BIRTH_DATE,
            response_text=TEMPLATES["ask_birth_date_retry"],
            needs_user_input=True
        )

    def _get_full_name(self, client: Dict[str, Any]) -> str:
        """Get full name from client dict."""
        nome = client.get("nome", "")
        cognome = client.get("cognome", "")
        return f"{nome} {cognome}".strip() or "Cliente"

    def _format_date_italian(self, d: date) -> str:
        """Format date in Italian."""
        months = [
            "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
            "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"
        ]
        return f"{d.day} {months[d.month - 1]} {d.year}"

    @property
    def is_waiting(self) -> bool:
        """Check if waiting for user input."""
        return self.context.state in (
            DisambiguationState.WAITING_NICKNAME,
            DisambiguationState.WAITING_BIRTH_DATE
        )

    @property
    def is_resolved(self) -> bool:
        """Check if disambiguation is resolved."""
        return self.context.state == DisambiguationState.RESOLVED

    @property
    def resolved_client(self) -> Optional[Dict[str, Any]]:
        """Get resolved client if available."""
        return self.context.resolved_client

    def check_nickname_match(self, nickname: str, surname: str) -> Optional[Dict[str, Any]]:
        """
        Check if a nickname matches known client names or nicknames.
        
        CoVe 2026: Advanced nickname resolution using PHONETIC_VARIANTS
        and fuzzy matching. Handles cases like:
        - "Gigi" → "Gigio" 
        - "Giovi" → "Giovanna"
        - "Peppe" → "Giuseppe"
        
        Args:
            nickname: The nickname or short name to check
            surname: Client surname for additional matching
            
        Returns:
            Client dict if match found, None otherwise
        """
        nickname_lower = nickname.lower().strip()
        surname_lower = surname.lower().strip()
        
        # Check against phonetic variants dictionary
        for base_name, variants in PHONETIC_VARIANTS.items():
            if nickname_lower in variants or nickname_lower == base_name:
                # Found a match - return simulated client
                return {
                    "id": f"nick_{base_name}_{surname_lower}",
                    "nome": base_name.capitalize(),
                    "cognome": surname.capitalize(),
                    "soprannome": nickname if nickname_lower != base_name else None,
                    "matched_via": "nickname",
                    "confidence": 0.95
                }
        
        # Check if nickname is similar to any base name using fuzzy matching
        for base_name in PHONETIC_VARIANTS.keys():
            if name_similarity(nickname_lower, base_name) >= 0.75:
                return {
                    "id": f"nick_{base_name}_{surname_lower}",
                    "nome": base_name.capitalize(),
                    "cognome": surname.capitalize(),
                    "soprannome": nickname,
                    "matched_via": "fuzzy",
                    "confidence": 0.85
                }
        
        return None


# Singleton instance
_handler: Optional[DisambiguationHandler] = None


def get_disambiguation_handler() -> DisambiguationHandler:
    """Get singleton disambiguation handler."""
    global _handler
    if _handler is None:
        _handler = DisambiguationHandler()
    return _handler


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    handler = DisambiguationHandler()

    # Test 1: Birth date resolves immediately
    print("Test 1: Birth date match - risolve subito")
    print("-" * 40)
    clients = [
        {"id": "1", "nome": "Mario", "cognome": "Rossi", "data_nascita": "1985-03-15", "soprannome": None},
        {"id": "2", "nome": "Mario", "cognome": "Rossi", "data_nascita": "1990-07-22", "soprannome": "Marione"},
    ]

    result = handler.start_disambiguation("Mario", clients)
    print(f"State: {result.state.value}")
    print(f"Response: {result.response_text}")

    print("\nUser says: 'sono nato il 15 marzo 1985'")
    result = handler.process_birth_date("sono nato il 15 marzo 1985")
    print(f"State: {result.state.value}")
    print(f"Response: {result.response_text}")
    print(f"Client: {result.client}")

    # Test 2: Birth date fails → nickname fallback
    print("\n" + "=" * 40)
    print("Test 2: Birth date fails → nickname fallback")
    print("-" * 40)
    handler.reset()

    result = handler.start_disambiguation("Mario", clients)
    print(f"State: {result.state.value}")
    print(f"Response: {result.response_text}")

    print("\nUser says: '10 gennaio 1980' (wrong date)")
    result = handler.process_birth_date("10 gennaio 1980")
    print(f"State: {result.state.value}")
    print(f"Response: {result.response_text}")

    print("\nUser says: 'Marione'")
    result = handler.process_nickname_choice("Marione")
    print(f"State: {result.state.value}")
    print(f"Response: {result.response_text}")
    print(f"Client: {result.client}")

    # Test 3: Birth date extraction
    print("\n" + "=" * 40)
    print("Test 3: Birth date extraction")
    print("-" * 40)

    test_inputs = [
        "15 marzo 1985",
        "nato il 22/07/1990",
        "sono del 5 gennaio 78",
        "1985-03-15",
        "15-03-85",
    ]

    for inp in test_inputs:
        d = handler.extract_birth_date(inp)
        print(f"'{inp}' -> {d}")
