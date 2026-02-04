"""
FLUXION Voice Agent - Service & Operator Resolver
Collega le entità estratte dai regex agli ID del database
"""

from typing import Optional, Dict, List, Tuple, Any
from difflib import SequenceMatcher
import re


class FuzzyMatcher:
    """Matching fuzzy tra testo estratto e candidati DB"""
    
    @staticmethod
    def find_best_match(query: str, candidates: List[Dict], threshold: float = 0.6) -> Tuple[Optional[Dict], float]:
        """
        Trova il miglior match fuzzy.
        
        Args:
            query: Testo estratto dall'utente (es: "taglio", "Giovanna")
            candidates: Lista dict con 'name', 'aliases', 'id'
            threshold: Soglia minima di similarità (0-1)
        
        Returns:
            (candidato_migliore, score)
        """
        query_lower = query.lower().strip()
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            scores = []
            
            # Match su nome principale
            name_score = SequenceMatcher(None, query_lower, candidate["name"].lower()).ratio()
            scores.append(name_score)
            
            # Match su alias
            for alias in candidate.get("aliases", []):
                alias_score = SequenceMatcher(None, query_lower, alias.lower()).ratio()
                scores.append(alias_score)
                
                # Check substring per alias corti
                if len(query_lower) >= 3 and query_lower in alias.lower():
                    scores.append(0.95)
                if len(alias) >= 3 and alias.lower() in query_lower:
                    scores.append(0.9)
            
            # Check substring sul nome
            if len(query_lower) >= 3 and query_lower in candidate["name"].lower():
                scores.append(0.9)
            
            candidate_best = max(scores)
            if candidate_best > best_score:
                best_score = candidate_best
                best_match = candidate
        
        if best_score >= threshold:
            return best_match, best_score
        return None, best_score


class ServiceResolver:
    """Resolver per servizi da database"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.matcher = FuzzyMatcher()
        self.cache = {}  # Cache per business_id
    
    def resolve(
        self,
        extracted_text: str,
        business_id: str,
        category_hint: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        Risolve testo servizio in ID database.
        
        Returns:
            (success, service_data, message)
        """
        if not extracted_text:
            return False, None, "Nessun servizio specificato"
        
        # Carica servizi dal DB (con cache)
        services = self._get_services_for_business(business_id)
        
        if not services:
            return False, None, "Nessun servizio trovato per questa attività"
        
        # Se c'è hint categoria, filtra
        if category_hint:
            services = [s for s in services if s.get("category") == category_hint]
        
        # Fuzzy match
        match, score = self.matcher.find_best_match(extracted_text, services, threshold=0.6)
        
        if match:
            return True, {
                "id": match["id"],
                "name": match["name"],
                "duration": match.get("duration_minutes", 30),
                "price": match.get("price"),
                "category": match.get("category"),
                "requires_operator": match.get("requires_operator", False),
                "match_confidence": score
            }, f"Servizio trovato: {match['name']}"
        
        # Nessun match trovato
        available = ", ".join([s["name"] for s in services[:5]])
        return False, None, f"Servizio non riconosciuto. Disponibili: {available}"
    
    def get_suggestions(self, partial_text: str, business_id: str, limit: int = 3) -> List[Dict]:
        """Restituisce suggerimenti per autocompletamento"""
        services = self._get_services_for_business(business_id)
        
        scores = []
        for service in services:
            score = SequenceMatcher(None, partial_text.lower(), service["name"].lower()).ratio()
            scores.append((service, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return [{"id": s["id"], "name": s["name"]} for s, _ in scores[:limit]]
    
    def _get_services_for_business(self, business_id: str) -> List[Dict]:
        """Carica servizi con cache"""
        cache_key = f"services_{business_id}"
        
        if cache_key not in self.cache:
            services = self.db.get_services_by_business(business_id)
            # Formatta per fuzzy matcher
            formatted = []
            for s in services:
                formatted.append({
                    "id": s["id"],
                    "name": s["name"],
                    "aliases": s.get("aliases", []),
                    "duration_minutes": s.get("duration_minutes", 30),
                    "price": s.get("price"),
                    "category": s.get("category"),
                    "requires_operator": s.get("requires_operator", False)
                })
            self.cache[cache_key] = formatted
        
        return self.cache[cache_key]
    
    def clear_cache(self, business_id: Optional[str] = None):
        """Pulisce cache servizi"""
        if business_id:
            self.cache.pop(f"services_{business_id}", None)
        else:
            self.cache.clear()


class OperatorResolver:
    """Resolver per operatori da database"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.matcher = FuzzyMatcher()
    
    def resolve(
        self,
        extracted_name: str,
        business_id: str,
        service_id: Optional[str] = None,
        date: Optional[str] = None,
        time: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict], str]:
        """
        Risolve nome operatore in ID database.
        
        Args:
            extracted_name: Nome estratto dal testo (es: "Giovanna")
            business_id: ID attività
            service_id: Opzionale - filtra per operatori che fanno quel servizio
            date: Opzionale - per verificare disponibilità
            time: Opzionale - per verificare disponibilità
        
        Returns:
            (success, operator_data, message)
        """
        if not extracted_name:
            return False, None, "Nessun operatore specificato"
        
        # Carica operatori
        operators = self._get_operators_for_business(business_id, service_id)
        
        if not operators:
            return False, None, "Nessun operatore trovato"
        
        # Fuzzy match sul nome
        match, score = self.matcher.find_best_match(extracted_name, operators, threshold=0.7)
        
        if match:
            # Verifica disponibilità se data/ora specificati
            if date and time:
                available = self._check_operator_availability(match["id"], date, time)
                if not available:
                    return False, {
                        "id": match["id"],
                        "name": match["name"]
                    }, f"{match['name']} non è disponibile alle {time}"
            
            return True, {
                "id": match["id"],
                "name": match["name"],
                "gender": match.get("gender", "F"),
                "specialties": match.get("specialties", []),
                "match_confidence": score
            }, f"Operatore trovato: {match['name']}"
        
        # Nessun match
        available_names = ", ".join([o["name"] for o in operators[:5]])
        return False, None, f"Operatore non trovato. Disponibili: {available_names}"
    
    def get_available_operators(
        self,
        business_id: str,
        date: str,
        time: str,
        service_id: Optional[str] = None
    ) -> List[Dict]:
        """Restituisce operatori disponibili per slot"""
        operators = self._get_operators_for_business(business_id, service_id)
        available = []
        
        for op in operators:
            if self._check_operator_availability(op["id"], date, time):
                available.append({
                    "id": op["id"],
                    "name": op["name"],
                    "gender": op.get("gender", "F")
                })
        
        return available
    
    def get_preferred_or_available(
        self,
        customer_id: str,
        business_id: str,
        date: str,
        time: str,
        service_id: Optional[str] = None
    ) -> Tuple[Optional[Dict], List[Dict]]:
        """
        Restituisce operatore preferito del cliente se disponibile,
        altrimenti lista alternative.
        """
        # Recupera preferenza cliente
        customer = self.db.get_customer(customer_id)
        preferred_id = customer.get("preferred_operator_id") if customer else None
        
        preferred = None
        if preferred_id:
            # Verifica disponibilità
            if self._check_operator_availability(preferred_id, date, time):
                op = self.db.get_operator(preferred_id)
                preferred = {
                    "id": op["id"],
                    "name": op["name"],
                    "is_preferred": True
                }
        
        # Recupera tutti gli altri disponibili
        all_available = self.get_available_operators(business_id, date, time, service_id)
        
        # Escludi preferito se già preso
        alternatives = [a for a in all_available if a["id"] != preferred_id]
        
        return preferred, alternatives
    
    def _get_operators_for_business(
        self,
        business_id: str,
        service_id: Optional[str] = None
    ) -> List[Dict]:
        """Carica operatori attivi per business"""
        operators = self.db.get_operators_by_business(business_id, active_only=True)
        
        # Se servizio specificato, filtra
        if service_id:
            operators = [
                op for op in operators
                if service_id in op.get("services", []) or not op.get("services")
            ]
        
        # Formatta per matcher
        return [{
            "id": op["id"],
            "name": op["name"],
            "aliases": op.get("nicknames", []),
            "gender": op.get("gender", "F"),
            "specialties": op.get("specialties", [])
        } for op in operators]
    
    def _check_operator_availability(self, operator_id: str, date: str, time: str) -> bool:
        """Verifica se operatore è libero"""
        # Recupera booking esistenti
        bookings = self.db.get_operator_bookings(operator_id, date)
        
        # Verifica sovrapposizione
        for b in bookings:
            if b["time"] == time:
                return False
        
        # Verifica orari lavoro
        schedule = self.db.get_operator_schedule(operator_id, date)
        if schedule:
            return schedule["open"] <= time <= schedule["close"]
        
        return True


class EntityResolverPipeline:
    """Pipeline completa: testo → entità → ID database"""
    
    def __init__(self, db_connection):
        self.service_resolver = ServiceResolver(db_connection)
        self.operator_resolver = OperatorResolver(db_connection)
        self.db = db_connection
    
    def resolve_booking_entities(
        self,
        service_text: Optional[str],
        operator_text: Optional[str],
        business_id: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Risolve tutte le entità per una prenotazione.
        
        Returns:
            {
                "service": {"resolved": bool, "data": {...}, "error": str},
                "operator": {"resolved": bool, "data": {...}, "error": str},
                "suggestions": {...}
            }
        """
        result = {
            "service": {"resolved": False, "data": None, "error": None},
            "operator": {"resolved": False, "data": None, "error": None},
            "suggestions": {}
        }
        
        # Risolvi servizio
        if service_text:
            success, data, msg = self.service_resolver.resolve(
                service_text, 
                business_id,
                category_hint=context.get("category") if context else None
            )
            result["service"]["resolved"] = success
            result["service"]["data"] = data
            result["service"]["error"] = None if success else msg
            
            if not success:
                # Suggerimenti
                result["suggestions"]["services"] = self.service_resolver.get_suggestions(
                    service_text, business_id
                )
        
        # Risolvi operatore
        if operator_text:
            success, data, msg = self.operator_resolver.resolve(
                operator_text,
                business_id,
                service_id=result["service"]["data"]["id"] if result["service"]["data"] else None
            )
            result["operator"]["resolved"] = success
            result["operator"]["data"] = data
            result["operator"]["error"] = None if success else msg
        
        return result


# =============================================================================
# ESEMPI D'USO
# =============================================================================

"""
# Esempio flusso completo:

1. Utente dice: "Vorrei prenotare con Giovanna per un taglio"

2. Regex estrae:
   - intent: PRENOTAZIONE
   - service_text: "taglio"
   - operator_text: "Giovanna"

3. ServiceResolver:
   - Input: "taglio"
   - DB: [{id: "srv1", name: "Taglio Donna", aliases: ["taglio", "sforbiciata"]}]
   - Match: 95% similarità
   - Output: {id: "srv1", name: "Taglio Donna", duration: 30}

4. OperatorResolver:
   - Input: "Giovanna"
   - DB: [{id: "op1", name: "Giovanna Bianchi", nicknames: ["Giovanna"]}]
   - Match: 100% similarità
   - Verifica disponibilità: OK
   - Output: {id: "op1", name: "Giovanna Bianchi", gender: "F"}

5. BookingManager crea prenotazione con ID effettivi
"""
