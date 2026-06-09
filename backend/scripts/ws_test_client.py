"""
Client de test du WebSocket front /ws/positions/.
Se connecte, attend une position pendant N secondes, l'affiche et sort.

Usage : python scripts/ws_test_client.py [secondes]
(nécessite daphne servant config.asgi sur :8000, et le WS bridge actif)
"""
import asyncio
import sys

from websockets.asyncio.client import connect


async def main(timeout: float):
    url = "ws://localhost:8000/ws/positions/"
    async with connect(url) as ws:
        print(f"Connecté à {url} — attente d'une position ({timeout}s)...")
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
            print("POSITION REÇUE:", msg)
        except asyncio.TimeoutError:
            print("Aucune position reçue dans le délai.")


if __name__ == "__main__":
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 20
    asyncio.run(main(secs))
