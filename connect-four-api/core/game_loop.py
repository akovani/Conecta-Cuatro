import json

from core.game_state import GameState
from core.logger import logger
from hardware.contour_recognition import detect_board_change

from hardware.plc_client import PLCClient
from agents.move_calculator import MoveCalculator
import asyncio


class GameLoop:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.plc_client = PLCClient()  # Initialize with your PLC settings
        self.move_calculator = MoveCalculator()

    async def run(self, websocket, wait_time: int = 15):
        try:
            logger.info("Game loop starting")
            while self.game_state.is_game_running():
                logger.info("Processing game turn")
                await self._process_game_turn(websocket, wait_time)
                # Add this line to yield control back to the event loop
                await asyncio.sleep(0)
        except Exception as e:
            logger.error(f"Error in game loop: {e}")
        finally:
            logger.info("Game loop ending")
            self.game_state.end_game()

    async def _process_game_turn(self, websocket, wait_time: int):
        logger.info("Processing game turn")
        logger.info(f"Waiting for {wait_time} seconds")
        logger.info("Current board state:")
        logger.info(self.game_state.board.board)
        await asyncio.sleep(wait_time)
        try:
            new_pos, is_cross = detect_board_change(self.game_state.board.board)
            # new_pos, is_cross = "C", True  # Placeholder for actual detection logic
            # new_pos = "C"
            self.plc_client.column_to_machine_coords(new_pos, is_cross)
            print(new_pos, is_cross)
        except Exception as e:
            logger.error(f"Error detecting board change: {e}")
            await websocket.send(json.dumps({"error": f"{e}"}, ensure_ascii=False))
            return
        if self.game_state.board.add_pos_to_board(column=new_pos, player=1):
            logger.info(f"New board state: \n {self.game_state.board.board}")
            await websocket.send(
                json.dumps(
                    {
                        "status": "human_move",
                        "position": new_pos,
                        "board": str(self.game_state.board.board.tolist()),
                    }
                )
            )
            await self._check_winner(websocket)
            await asyncio.sleep(1)
            await self._handle_ai_move(websocket)
            await self._check_winner(websocket)

    async def _handle_ai_move(self, websocket):
        best_column = self.move_calculator.get_best_move(
            self.game_state.board.board,
            self.game_state.current_algorithm,
            self.game_state.current_depth,
            self.game_state.current_sim,
        )

        logger.info(f"Computer chose column: {best_column}")

        if best_column is not None:
            self.plc_client.column_to_machine_coords(best_column, True)
            if self.game_state.board.add_pos_to_board(column=best_column, player=2):
                await websocket.send(
                    json.dumps(
                        {
                            "status": "computer_move",
                            "position": best_column,
                            "board": str(self.game_state.board.board.tolist()),
                        }
                    )
                )
        else:
            await websocket.send(
                json.dumps({"status": "error", "message": "No valid move calculated"})
            )

    async def _check_winner(self, websocket):
        winner = self.game_state.board.winner_check()
        if winner != 0:
            await websocket.send(
                json.dumps(
                    {
                        "status": "end",
                        "winner": str(winner),
                        "board": str(self.game_state.board.board.tolist()),
                    }
                )
            )
            self.game_state.end_game()
