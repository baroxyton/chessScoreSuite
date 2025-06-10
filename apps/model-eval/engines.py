import base64
import random
import requests

import chess
import chess.engine

STOCKFISH_PATH = "/usr/bin/stockfish"
API_BASE_URL = "http://localhost:5554"


def sf_best_move(board):
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        result = engine.play(board, chess.engine.Limit(depth=17))
        if result.move is None:
            return None
        return result.move.uci()


def eval_pos(board):
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        info = engine.analyse(board, chess.engine.Limit(depth=17))
        if "score" not in info:
            return None
        score = info["score"].white()
        return score.score(mate_score=10000)


def avg_player_move(position, elo):

    # Encode FEN position for URL
    fen_encoded = base64.b64encode(position.fen().encode("utf-8")).decode("utf-8")

    url = f"{API_BASE_URL}/fen/{fen_encoded}/{elo}/moves"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        moves_data = response.json()

        if isinstance(moves_data, list) and moves_data:
            # Use weighted random choice based on move_times_played
            moves = [move["moveSAN"] for move in moves_data]
            weights = [move["move_times_played"] for move in moves_data]
            return random.choices(moves, weights=weights)[0]

        return None
    except (requests.RequestException, KeyError, ValueError):
        return None


def recursivebest_move(position, elo, color):
    # Encode FEN position for URL
    fen_encoded = base64.b64encode(position.fen().encode("utf-8")).decode("utf-8")

    url = f"{API_BASE_URL}/fen/{fen_encoded}/{elo}/moves"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        moves_data = response.json()

        if isinstance(moves_data, list) and moves_data:
            # Choose move with best recursive score for the given color
            if color == True:
                best_move = max(moves_data, key=lambda x: x["recursiveScoreWhite"])
            else:  # black
                best_move = max(moves_data, key=lambda x: x["recursiveScoreBlack"])

            return best_move["moveSAN"]

        return None
    except (requests.RequestException, KeyError, ValueError):
        return None
