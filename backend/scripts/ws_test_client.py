"""
Client de test du WebSocket front /ws/positions/.
Se connecte, attend une position pendant N secondes, l'affiche et sort.

Usage : python scripts/ws_test_client.py [secondes]
(nécessite daphne servant config.asgi sur :8000, et le WS bridge actif)
"""
import asyncio
import sys

from websockets.asyncio.client import connect


async def main(timeout: float, token: str | None):
    url = "ws://localhost:8000/ws/positions/"
    if token:
        url += f"?token={token}"
    try:
        async with connect(url) as ws:
            print(f"Connecté — attente d'une position ({timeout}s)...")
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
                print("POSITION REÇUE:", msg)
            except asyncio.TimeoutError:
                print("Connecté mais aucune position reçue dans le délai.")
    except Exception as exc:  # noqa: BLE001
        print(f"CONNEXION REJETÉE: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 20
    tok = sys.argv[2] if len(sys.argv) > 2 else None
    asyncio.run(main(secs, tok))
