# KI-generierter code
import base64
import random
import requests

import chess
import chess.engine

STOCKFISH_PATH = "/usr/bin/stockfish"
API_BASE_URL = "http://localhost:5554"


def sf_best_move(board):
    print("STARTING CHESS MOVE")
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        result = engine.play(board, chess.engine.Limit(time=0.05))
        if result.move is None:
            return None
        print("CHESS MOVE DONE")
        return result.move.uci()


def eval_pos(board):
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        info = engine.analyse(board, chess.engine.Limit(depth=1))
        if "score" not in info:
            return None
        score = info["score"].white()
        return score.score(mate_score=10000)


def move_frequency(position: chess.Board, elo: int, move: chess.Move):
    """
    Return how often 'move' was played from 'position' at 'elo', as a fraction in [0,1]:
      move_times_played / parent_position.timesPlayed
    Falls back to sum(move_times_played) if timesPlayed is unavailable.
    """
    try:
        san = position.san(move)
    except Exception:
        return None

    fen_encoded = base64.b64encode(position.fen().encode("utf-8")).decode("utf-8")
    url_moves = f"{API_BASE_URL}/fen/{fen_encoded}/{elo}/moves"
    url_pos = f"{API_BASE_URL}/fen/{fen_encoded}/{elo}/position"

    parent_times = 0
    try:
        resp_pos = requests.get(url_pos, timeout=5)
        resp_pos.raise_for_status()
        pos_data = resp_pos.json()
        if isinstance(pos_data, dict):
            parent_times = int(pos_data.get("timesPlayed", 0) or 0)
    except (requests.RequestException, ValueError, TypeError):
        parent_times = 0

    try:
        resp_moves = requests.get(url_moves, timeout=5)
        resp_moves.raise_for_status()
        moves_data = resp_moves.json()
        if not isinstance(moves_data, list) or not moves_data:
            return None

        # Find the chosen move
        chosen = next((m for m in moves_data if m.get("moveSAN") == san), None)
        if chosen is None:
            return None

        # Fallback denominator if timesPlayed wasn't available
        if parent_times <= 0:
            try:
                parent_times = sum(
                    int(m.get("move_times_played", 0) or 0) for m in moves_data
                )
            except Exception:
                parent_times = 0

        if parent_times > 0:
            num = int(chosen.get("move_times_played", 0) or 0)
            return num / parent_times

        return None
    except (requests.RequestException, ValueError, TypeError):
        return None


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


def eval_pos_avg(position, elo):
    # Encode FEN position for URL
    fen_encoded = base64.b64encode(position.fen().encode("utf-8")).decode("utf-8")
    url = f"{API_BASE_URL}/fen/{fen_encoded}/{elo}/position"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        position_data = response.json()

        if (
            position_data
            and "whiteWins" in position_data
            and "timesPlayed" in position_data
        ):
            times_played = position_data["timesPlayed"]
            white_wins = position_data["whiteWins"]

            if times_played > 0:
                avg_winning_rate = white_wins / times_played
                return avg_winning_rate - 0.5

        return None
    except (requests.RequestException, KeyError, ValueError):
        return None


def avg_best_move(position, elo):
    """
    Get the move with the highest average performance (best win rate)
    from the API data for a given position and ELO rating.
    """
    # Encode FEN position for URL
    fen_encoded = base64.b64encode(position.fen().encode("utf-8")).decode("utf-8")

    url = f"{API_BASE_URL}/fen/{fen_encoded}/{elo}/moves"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        moves_data = response.json()

        if isinstance(moves_data, list) and moves_data:
            # Find move with best winning percentage
            best_move = None
            best_score = -1

            for move in moves_data:
                if (
                    "whiteWins" in move
                    and "timesPlayed" in move
                    and move["timesPlayed"] > 0
                ):
                    win_rate = move["whiteWins"] / move["timesPlayed"]

                    # Adjust score based on whose turn it is
                    if position.turn == chess.WHITE:
                        score = win_rate
                    else:
                        score = 1 - win_rate  # Black wants low white win rate

                    if score > best_score:
                        best_score = score
                        best_move = move["moveSAN"]

            return best_move

        return None
    except (requests.RequestException, KeyError, ValueError):
        return None


def avg_player_move_deterministic(position, elo):
    """
    Get the most commonly played move for a given position and ELO rating.
    Returns the move with the highest move_times_played count.
    """
    # Encode FEN position for URL
    fen_encoded = base64.b64encode(position.fen().encode("utf-8")).decode("utf-8")

    url = f"{API_BASE_URL}/fen/{fen_encoded}/{elo}/moves"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        moves_data = response.json()

        if isinstance(moves_data, list) and moves_data:
            # Find move with highest play count
            most_common_move = max(moves_data, key=lambda x: x["move_times_played"])
            return most_common_move["moveSAN"]

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


def recursiveworst_move(position, elo, color):
    """
    Chooses the move that is worst for the current player,
    i.e., the move that leads to the opponent's highest recursive score.
    """
    # Encode FEN position for URL
    fen_encoded = base64.b64encode(position.fen().encode("utf-8")).decode("utf-8")

    url = f"{API_BASE_URL}/fen/{fen_encoded}/{elo}/moves"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        moves_data = response.json()

        if isinstance(moves_data, list) and moves_data:
            # For WHITE, pick move maximizing opponent's recursiveScoreBlack
            # For BLACK, pick move maximizing opponent's recursiveScoreWhite
            if color is True:  # White to move
                worst_move = max(moves_data, key=lambda x: x["recursiveScoreBlack"])
            else:  # Black to move
                worst_move = max(moves_data, key=lambda x: x["recursiveScoreWhite"])

            return worst_move["moveSAN"]

        return None
    except (requests.RequestException, KeyError, ValueError):
        return None


ENGINE_FUNCTIONS = {
    "avg_player": avg_player_move,
    "avg_best": avg_best_move,
    "avg_player_deterministic": avg_player_move_deterministic,
    "recursive_worst": recursiveworst_move,
    "recursive_best": recursivebest_move,
    "sf": sf_best_move,
}

EVAL_FUNCTIONS = {
    "sf": eval_pos,
    "avg": eval_pos_avg,
}
