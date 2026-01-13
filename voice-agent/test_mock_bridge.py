"""
Mock HTTP Bridge for testing Voice Agent integration.
Simulates the Tauri HTTP Bridge endpoints.
"""

import asyncio
import json
from aiohttp import web
from datetime import datetime, timedelta

# Mock data
MOCK_CLIENTS = [
    {"id": "c1", "nome": "Mario", "cognome": "Rossi", "telefono": "3331234567", "data_nascita": "1985-03-15"},
    {"id": "c2", "nome": "Mario", "cognome": "Rossi", "telefono": "3339876543", "data_nascita": "1990-07-22"},
    {"id": "c3", "nome": "Giulia", "cognome": "Bianchi", "telefono": "3335551234", "data_nascita": "1988-11-30"},
]

MOCK_VERTICALE = {
    "id": "salone_test",
    "nome_attivita": "Salone Aurora Test",
    "orario_apertura": "09:00",
    "orario_chiusura": "19:00",
    "giorni_lavorativi": "Lunedi-Sabato",
    "servizi": ["Taglio", "Piega", "Colore", "Barba", "Trattamento"]
}

MOCK_BOOKED_SLOTS = ["10:00", "11:30", "15:00"]


async def handle_health(request):
    return web.json_response({"status": "ok", "service": "mock-bridge", "version": "1.0.0"})


async def handle_verticale_config(request):
    return web.json_response(MOCK_VERTICALE)


async def handle_clienti_search(request):
    q = request.query.get("q", "").lower()
    matches = [c for c in MOCK_CLIENTS if q in c["nome"].lower() or q in c["cognome"].lower()]

    return web.json_response({
        "clienti": matches,
        "ambiguo": len(matches) > 1,
        "count": len(matches)
    })


async def handle_appuntamenti_occupati(request):
    return web.json_response({
        "slots": MOCK_BOOKED_SLOTS,
        "data": request.query.get("data", "")
    })


async def handle_appuntamenti_create(request):
    data = await request.json()
    booking_id = f"app_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return web.json_response({
        "success": True,
        "id": booking_id,
        "message": f"Appuntamento creato: {data.get('service')} il {data.get('date')} alle {data.get('time')}"
    })


async def handle_operatori_list(request):
    return web.json_response({
        "operatori": [
            {"id": "op1", "nome": "Anna", "cognome": "Verdi"},
            {"id": "op2", "nome": "Marco", "cognome": "Neri"},
        ]
    })


async def handle_waitlist_add(request):
    data = await request.json()
    return web.json_response({
        "success": True,
        "id": f"wl_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "priorita": data.get("priorita", "normale")
    })


def create_app():
    app = web.Application()
    app.router.add_get("/health", handle_health)
    app.router.add_get("/api/verticale/config", handle_verticale_config)
    app.router.add_get("/api/clienti/search", handle_clienti_search)
    app.router.add_get("/api/appuntamenti/occupati", handle_appuntamenti_occupati)
    app.router.add_post("/api/appuntamenti/create", handle_appuntamenti_create)
    app.router.add_get("/api/operatori/list", handle_operatori_list)
    app.router.add_post("/api/waitlist/add", handle_waitlist_add)
    return app


async def main():
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 3001)
    await site.start()
    print("=" * 60)
    print("Mock HTTP Bridge started on http://127.0.0.1:3001")
    print("=" * 60)
    print(f"Business: {MOCK_VERTICALE['nome_attivita']}")
    print(f"Clients: {len(MOCK_CLIENTS)}")
    print("=" * 60)

    # Keep running
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
