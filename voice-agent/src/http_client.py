"""
FLUXION Voice Agent - Shared HTTP Client

Singleton aiohttp.ClientSession con TCPConnector pooling.
Elimina il costo di nuova connessione TCP per ogni request verso il Bridge (porta 3001).

CoVe 2026-02-25: ogni `async with aiohttp.ClientSession()` creava un nuovo handshake TCP
(~75-200ms). Con 15 request per sessione = +1.1s latency evitabile.

Uso:
    from .http_client import get_http_session, close_http_session

    session = await get_http_session()
    async with session.get(url, timeout=...) as resp:
        data = await resp.json()

    # Al shutdown:
    await close_http_session()
"""

import aiohttp
from typing import Optional


class _SharedSessionContext:
    """
    Async context manager che cede la sessione condivisa senza chiuderla.

    Permette di usare `async with shared_session() as session:` identicamente
    a `async with aiohttp.ClientSession() as session:` ma senza creare
    una nuova connessione TCP ogni volta.
    """
    async def __aenter__(self) -> aiohttp.ClientSession:
        return await get_http_session()

    async def __aexit__(self, *args) -> None:
        pass  # Non chiudere: la sessione è condivisa per tutto il processo


def shared_session() -> _SharedSessionContext:
    """
    Drop-in replacement per `aiohttp.ClientSession()` come context manager.

    Uso:
        async with shared_session() as session:
            async with session.get(url) as resp:
                ...
    """
    return _SharedSessionContext()

_connector: Optional[aiohttp.TCPConnector] = None
_session: Optional[aiohttp.ClientSession] = None


async def get_http_session() -> aiohttp.ClientSession:
    """
    Restituisce la sessione HTTP condivisa (singleton).

    La sessione viene creata al primo accesso e riusata per tutta la durata
    del processo — stesso TCP connection pool per tutte le request al Bridge.

    TCPConnector config:
    - limit=50: max connessioni totali
    - limit_per_host=10: max connessioni verso lo stesso host (Bridge locale)
    - ttl_dns_cache=300: cache DNS 5 minuti (Bridge sempre su localhost)
    - keepalive_timeout=30: mantieni connessioni idle per 30s
    """
    global _connector, _session

    if _session is None or _session.closed:
        _connector = aiohttp.TCPConnector(
            limit=50,
            limit_per_host=10,
            ttl_dns_cache=300,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )
        _session = aiohttp.ClientSession(connector=_connector)
        print("[HTTPClient] Sessione condivisa creata (TCPConnector pooling attivo)")

    return _session


async def close_http_session() -> None:
    """Chiudi la sessione condivisa al shutdown del server."""
    global _connector, _session
    if _session and not _session.closed:
        await _session.close()
        _session = None
    if _connector and not _connector.closed:
        await _connector.close()
        _connector = None
    print("[HTTPClient] Sessione condivisa chiusa")
