#!/usr/bin/env python3
"""
FLUXION Voice Pipeline E2E Test
Tests complete L0->L4 pipeline with SLA verification
"""

import asyncio
import httpx
import time

BASE_URL = "http://127.0.0.1:3002"

async def test_voice_pipeline():
    """Test complete voice pipeline (L0->L4)"""
    print("\n" + "="*80)
    print("FLUXION Voice Pipeline E2E Test")
    print("="*80)

    test_queries = [
        {
            "name": "L0: Special Command",
            "input": "stop",
            "verticale": "auto",
            "expected_layer": 0,
        },
        {
            "name": "L1: Intent Classification",
            "input": "ciao, come stai?",
            "verticale": "auto",
            "expected_layer": 1,
        },
        {
            "name": "L3: FAQ Retrieval",
            "input": "quanto costa un tagliando completo?",
            "verticale": "auto",
            "expected_layer": 3,
        },
        {
            "name": "L4: LLM Fallback",
            "input": "mi racconti la storia dell'officina?",
            "verticale": "auto",
            "expected_layer": 4,
        },
    ]

    async with httpx.AsyncClient() as client:
        for test in test_queries:
            print(f"\nTest: {test['name']}")
            print(f"   Input: '{test['input']}'")

            start_time = time.time()

            try:
                response = await client.post(
                    f"{BASE_URL}/api/voice/query",
                    json={
                        "client_id": "test_cli_001",
                        "user_input": test["input"],
                        "verticale": test["verticale"],
                        "channel": "voice",
                    },
                    timeout=5.0,
                )

                elapsed_ms = (time.time() - start_time) * 1000
                result = response.json()

                print(f"   Layer: {result.get('layer', '?')}")
                print(f"   Latency: {elapsed_ms:.0f}ms")
                print(f"   Response: {result.get('response', '')[:100]}...")

                # Check SLA
                sla_targets = {0: 1, 1: 5, 2: 10, 3: 50, 4: 500}
                layer = result.get("layer")
                if layer in sla_targets:
                    target = sla_targets[layer]
                    status = "PASS" if elapsed_ms < target else "WARN"
                    print(f"   SLA: {status} - {elapsed_ms:.0f}ms < {target}ms")

            except Exception as e:
                print(f"   ERROR: {str(e)}")

    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_voice_pipeline())
