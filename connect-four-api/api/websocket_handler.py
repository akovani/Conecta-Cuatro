import json
import websockets
from typing import Dict, Any

from core.constants import SELECTABLE_ALGORITHMS
from core.game_state import GameState
from core.game_loop import GameLoop
from core.logger import logger
from util import get_algorithm_params


class WebSocketHandler:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.game_loop = GameLoop(game_state)

    # inform client about successful connection and available algorithms
    async def send_initial_message(self, websocket):
        await websocket.send(
            json.dumps(
                {
                    "status": "connection_established",
                    "algorithms": SELECTABLE_ALGORITHMS,
                }
            )
        )

    async def handle_connection(self, websocket):
        logger.info("Client connected!")
        await self.send_initial_message(websocket)
        try:
            async for message in websocket:
                try:
                    response = await self.process_message(websocket, message)
                    if response:
                        await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON format"}))
        except websockets.ConnectionClosed:
            logger.warning("Client disconnected!")
        finally:
            self.game_state.end_game()

            # Log that the websocket connection is closing due to navigation away or disconnection.
            logger.info(
                "Websocket connection is closing. Client may have navigated away."
            )

            # Close the connection
            await websocket.close()

    async def process_message(self, websocket, message) -> Dict[str, Any]:
        data = json.loads(message)
        logger.info(f"Received message: {data}")

        if "algorithm" in data and data["algorithm"] in SELECTABLE_ALGORITHMS:
            difficulty = data.get("difficulty", 2)

            try:
                algorithm_params = get_algorithm_params(data["algorithm"], difficulty)
                self.game_state.start_game(data["algorithm"], algorithm_params)
                await self.game_loop.run(websocket)

                return {
                    "status": "game_started",
                    "algorithm": data["algorithm"],
                    "difficulty": difficulty,
                }

            except ValueError as e:
                return {"error": str(e)}

        else:
            return {
                "error": f"Invalid input. Please choose algorithm from: {', '.join(SELECTABLE_ALGORITHMS)}"
            }
