#!/usr/bin/env python3
"""
Fluxion Voice Agent - Test Cross-Machine (CoVe Verified)
=========================================================

Questo test VERIFICA REALMENTE la connettività tra MacBook e iMac.
Da eseguire sul MacBook per testare il Voice Agent sull'iMac.

Memorizzato in: voice-agent/scripts/test_cross_machine.py

Uso:
    python3 voice-agent/scripts/test_cross_machine.py

CoVe Rule: Un test che gira in localhost NON verifica la connettività di rete.
"""

import urllib.request
import json
import sys

# IP statico iMac (CONFIGURARE SU ROUTER)
IMAC_IP = "192.168.1.7"
IMAC_PORT = 3002
BASE_URL = f"http://{IMAC_IP}:{IMAC_PORT}"

def test_cross_machine():
    """Test connettività MacBook → iMac."""
    print("=" * 60)
    print("  FLUXION - TEST CROSS-MACHINE (MacBook → iMac)")
    print("=" * 60)
    print(f"  Target: {BASE_URL}")
    print()
    
    # Test 1: Health
    try:
        with urllib.request.urlopen(f'{BASE_URL}/health', timeout=10) as r:
            health = json.loads(r.read())
        print(f"✅ Health: {health['status']} (v{health['version']})")
    except Exception as e:
        print(f"❌ Health FAILED: {e}")
        return False
    
    # Test 2: Process endpoint
    try:
        data = json.dumps({"text": "Ciao"}).encode()
        req = urllib.request.Request(
            f'{BASE_URL}/api/voice/process',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            response = json.loads(r.read())
        
        if 'response' in response:
            print(f"✅ Process: OK")
            print(f"   Response: {response['response'][:60]}...")
            return True
        else:
            print(f"❌ Process: risposta malformata")
            return False
    except Exception as e:
        print(f"❌ Process FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_cross_machine()
    print()
    print("=" * 60)
    if success:
        print("  ✅ TEST CROSS-MACHINE PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("  ❌ TEST CROSS-MACHINE FAILED")
        print("  Verifica:")
        print("  1. iMac acceso e connesso alla rete")
        print("  2. Voice Agent in esecuzione (python main.py)")
        print("  3. IP 192.168.1.7 raggiungibile")
        print("=" * 60)
        sys.exit(1)
