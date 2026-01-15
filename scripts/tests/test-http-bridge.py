#!/usr/bin/env python3
"""
FLUXION HTTP Bridge Integration Test
Tests all HTTP Bridge endpoints
"""

import asyncio
import httpx

async def test_http_bridge():
    """Test HTTP Bridge endpoints"""
    print("\n" + "="*80)
    print("HTTP Bridge Integration Test")
    print("="*80)

    base_url = "http://127.0.0.1:3001"

    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "path": "/health",
            "expected_status": 200,
        },
        {
            "name": "Search Clienti",
            "method": "POST",
            "path": "/api/clienti/search",
            "payload": {"query": "3459876543"},
            "expected_status": 200,
        },
        {
            "name": "List Servizi",
            "method": "GET",
            "path": "/api/servizi/list",
            "expected_status": 200,
        },
        {
            "name": "Voice Query",
            "method": "POST",
            "path": "/api/voice/query",
            "payload": {
                "client_id": "test_001",
                "user_input": "quanto costa?",
                "verticale": "auto",
            },
            "expected_status": 200,
        },
    ]

    async with httpx.AsyncClient() as client:
        for test in tests:
            print(f"\n{test['name']}")
            print(f"   {test['method']} {test['path']}")

            try:
                if test["method"] == "GET":
                    response = await client.get(f"{base_url}{test['path']}", timeout=5.0)
                else:
                    response = await client.post(
                        f"{base_url}{test['path']}",
                        json=test.get("payload", {}),
                        timeout=5.0,
                    )

                status_ok = response.status_code == test["expected_status"]
                print(f"   Status: {response.status_code} {'PASS' if status_ok else 'FAIL'}")

                if response.status_code == 200:
                    print(f"   Response: {str(response.json())[:100]}...")

            except Exception as e:
                print(f"   ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_http_bridge())
