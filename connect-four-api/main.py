import asyncio
import os
import websockets

from core.constants import WEBSOCKET_HOST, WEBSOCKET_PORT
from core.game_state import GameState
from core.logger import logger
from api.websocket_handler import WebSocketHandler

game_state = GameState()


async def main():
    ws_host = os.getenv("WEBSOCKET_HOST", WEBSOCKET_HOST)
    ws_port = int(os.getenv("WEBSOCKET_PORT", WEBSOCKET_PORT))

    websocket_handler = WebSocketHandler(game_state)

    server = await websockets.serve(
        websocket_handler.handle_connection, ws_host, ws_port
    )

    logger.info(f"WebSocket server started on ws://{ws_host}:{ws_port}")

    try:
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        server.close()
        await server.wait_closed()


def run():
    """Entry point for the application"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Application stopped")


if __name__ == "__main__":
    run()
