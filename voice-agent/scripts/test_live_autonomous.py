#!/usr/bin/env python3
"""
Fluxion Voice Agent - Test Live Autonomo
=========================================

Script di test live automatico da eseguire sull'iMac.
Memorizzato in: voice-agent/scripts/test_live_autonomous.py

Utilizzo:
    python3 scripts/test_live_autonomous.py

Questo script viene eseguito automaticamente quando necessario per verificare
lo stato del Voice Agent su iMac.

Autorun locations:
- voice-agent/scripts/test_live_autonomous.py (questo file)
- /tmp/fluxion_test_live.py (symlink temporaneo se necessario)

Data creazione: 2026-02-11
Versione: 1.0.0
"""

import sys
import os
import json
import urllib.request
import time
from datetime import datetime

# Configurazione
BASE_URL = "http://localhost:3002"
TEST_RESULTS = []

def log_test(name, status, details=""):
    """Logga risultato test."""
    result = {
        "name": name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    TEST_RESULTS.append(result)
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {name}: {status}")
    if details:
        print(f"   {details}")

def test_health_endpoint():
    """Test 1: Health endpoint."""
    try:
        with urllib.request.urlopen(f'{BASE_URL}/health', timeout=5) as r:
            health = json.loads(r.read())
        
        if health.get('status') == 'ok':
            log_test(
                "Health Endpoint", 
                "PASS", 
                f"v{health.get('version', 'unknown')} - {health.get('pipeline', 'unknown')}"
            )
            return True
        else:
            log_test("Health Endpoint", "FAIL", f"Status: {health.get('status')}")
            return False
    except Exception as e:
        log_test("Health Endpoint", "FAIL", str(e))
        return False

def test_state_machine():
    """Test 2: State Machine."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.booking_state_machine import BookingStateMachine, BookingState
        
        sm = BookingStateMachine()
        states = list(BookingState)
        
        if len(states) == 23:
            log_test("State Machine", "PASS", f"{len(states)} stati, init: {sm.context.state.value}")
            return True
        else:
            log_test("State Machine", "FAIL", f"Attesi 23 stati, trovati {len(states)}")
            return False
    except Exception as e:
        log_test("State Machine", "FAIL", str(e))
        return False

def test_intent_classification():
    """Test 3: Intent Classification."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.intent_classifier import classify_intent
        
        result = classify_intent('Vorrei prenotare')
        
        if result.category.value == 'prenotazione' and result.confidence > 0.5:
            log_test("Intent Classification", "PASS", f"{result.category.value} ({result.confidence:.2f})")
            return True
        else:
            log_test("Intent Classification", "FAIL", f"Intent: {result.category.value}, Conf: {result.confidence}")
            return False
    except Exception as e:
        log_test("Intent Classification", "FAIL", str(e))
        return False

def test_phonetic_matching():
    """Test 4: Phonetic Matching."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.disambiguation_handler import name_similarity
        
        score = name_similarity('gino', 'gigio')
        
        if score > 0.5:
            log_test("Phonetic Matching", "PASS", f"gino/gigio: {score:.2f}")
            return True
        else:
            log_test("Phonetic Matching", "FAIL", f"Score troppo basso: {score}")
            return False
    except Exception as e:
        log_test("Phonetic Matching", "FAIL", str(e))
        return False

def test_turn_tracker():
    """Test 5: Turn Tracker."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.turn_tracker import FluxionTurnTracker
        
        tt = FluxionTurnTracker(':memory:')
        log_test("Turn Tracker", "PASS", "Inizializzato correttamente")
        return True
    except Exception as e:
        log_test("Turn Tracker", "FAIL", str(e))
        return False

def test_latency_optimizer():
    """Test 6: Latency Optimizer."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.latency_optimizer import FluxionLatencyOptimizer
        
        opt = FluxionLatencyOptimizer('test-key')
        metrics = opt.start_tracking()
        
        if metrics is not None:
            log_test("Latency Optimizer", "PASS", "Inizializzato correttamente")
            return True
        else:
            log_test("Latency Optimizer", "FAIL", "Metrics is None")
            return False
    except ImportError as e:
        if 'aiohttp' in str(e):
            log_test("Latency Optimizer", "SKIP", "aiohttp non installato (opzionale)")
            return True
        raise
    except Exception as e:
        log_test("Latency Optimizer", "FAIL", str(e))
        return False

def test_performance():
    """Test 7: Performance."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.booking_state_machine import BookingStateMachine
        
        start = time.time()
        sm = BookingStateMachine()
        sm.process_message("Vorrei prenotare")
        elapsed = (time.time() - start) * 1000
        
        if elapsed < 2000:
            log_test("Performance", "PASS", f"{elapsed:.1f}ms")
            return True
        else:
            log_test("Performance", "FAIL", f"Troppo lento: {elapsed:.1f}ms")
            return False
    except Exception as e:
        log_test("Performance", "FAIL", str(e))
        return False

def test_process_endpoint():
    """Test 8: Process endpoint."""
    try:
        data = json.dumps({"text": "Buongiorno"}).encode('utf-8')
        req = urllib.request.Request(
            f'{BASE_URL}/api/voice/process',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=10) as r:
            response = json.loads(r.read())
        
        if 'response' in response or 'success' in response:
            log_test("Process Endpoint", "PASS", "Risposta ricevuta")
            return True
        else:
            log_test("Process Endpoint", "FAIL", "Risposta malformata")
            return False
    except Exception as e:
        log_test("Process Endpoint", "FAIL", str(e))
        return False

def run_all_tests():
    """Esegue tutti i test."""
    print("=" * 60)
    print("  FLUXION VOICE AGENT - TEST LIVE AUTONOMO")
    print("=" * 60)
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Server: {BASE_URL}")
    print("=" * 60)
    print()
    
    tests = [
        test_health_endpoint,
        test_state_machine,
        test_intent_classification,
        test_phonetic_matching,
        test_turn_tracker,
        test_latency_optimizer,
        test_performance,
        test_process_endpoint,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            log_test(test.__name__, "ERROR", str(e))
            failed += 1
    
    print()
    print("=" * 60)
    print("  RIEPILOGO")
    print("=" * 60)
    print(f"  ✅ Passati: {passed}")
    print(f"  ❌ Falliti: {failed}")
    print(f"  ⚠️  Skippati: {skipped}")
    print()
    
    if failed == 0:
        print("  🎉 TUTTI I TEST PASSED!")
        print("=" * 60)
        return 0
    else:
        print(f"  ⚠️  {failed} TEST FALLITI")
        print("=" * 60)
        return 1

def generate_report():
    """Genera report JSON."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "server": BASE_URL,
        "results": TEST_RESULTS,
        "summary": {
            "total": len(TEST_RESULTS),
            "passed": sum(1 for r in TEST_RESULTS if r["status"] == "PASS"),
            "failed": sum(1 for r in TEST_RESULTS if r["status"] == "FAIL"),
            "skipped": sum(1 for r in TEST_RESULTS if r["status"] == "SKIP")
        }
    }
    
    # Salva report
    report_path = os.path.expanduser("~/fluxion_test_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report salvato in: {report_path}")
    return report

if __name__ == "__main__":
    exit_code = run_all_tests()
    generate_report()
    sys.exit(exit_code)
