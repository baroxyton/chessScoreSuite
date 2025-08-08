import argparse
import csv
import chess
import engines


def _call_engine(engine_fn, board, elo, player_color):
    """
    Uniformly call an engine function regardless of its signature.
    - sf_best_move(board)
    - avg_*/(recursive*) engines expect (board, elo) or (board, elo, color)
    """
    if engine_fn is engines.sf_best_move:
        return engine_fn(board)
    if engine_fn in (engines.recursivebest_move, engines.recursiveworst_move):
        return engine_fn(board, elo, player_color)
    return engine_fn(board, elo)


def play_game(evaluated_fn, baseline_fn, eval_function, start_fen, evaluated_color, elo):
    """
    Plays a single game and returns the list of evaluations from the evaluated engine's perspective.
    """
    board = chess.Board(start_fen)
    evaluations = []

    while not board.is_game_over(claim_draw=True):
        # Evaluate position BEFORE making the move, from evaluated engine's perspective
        if eval_function is engines.eval_pos_avg:
            eval_value = eval_function(board, elo)
        else:
            eval_value = eval_function(board)

        if eval_value is not None:
            if evaluated_color == chess.BLACK:
                eval_value = -eval_value
            evaluations.append(eval_value)

        # Decide whose turn and use the correct engine
        current_color = board.turn
        if current_color == evaluated_color:
            move_result = _call_engine(evaluated_fn, board, elo, evaluated_color)
        else:
            move_result = _call_engine(baseline_fn, board, elo, chess.WHITE if evaluated_color == chess.BLACK else chess.BLACK)

        if move_result is None:
            break

        # Try parsing as UCI first, then SAN
        try:
            try:
                move = chess.Move.from_uci(move_result)
                if move not in board.legal_moves:
                    raise ValueError("Invalid UCI move")
            except (ValueError, chess.InvalidMoveError):
                move = board.parse_san(move_result)
        except (ValueError, chess.InvalidMoveError, chess.IllegalMoveError):
            break

        board.push(move)

    return evaluations


def main():
    parser = argparse.ArgumentParser(description="Evaluate a chess engine against a baseline engine.")
    parser.add_argument(
        "--evaluated",
        type=str,
        required=True,
        choices=engines.ENGINE_FUNCTIONS.keys(),
        help="The engine being evaluated."
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default="avg_player",
        choices=engines.ENGINE_FUNCTIONS.keys(),
        help="The baseline engine (default: avg_player)."
    )
    parser.add_argument(
        "--eval",
        type=str,
        default="sf",
        choices=engines.EVAL_FUNCTIONS.keys(),
        help="The evaluation method to use for recording scores."
    )
    parser.add_argument(
        "--games",
        type=int,
        default=10,
        help="Number of games to play."
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results.csv",
        help="Output CSV file name."
    )
    parser.add_argument(
        "--elo",
        type=int,
        default=2000,
        help="ELO rating for API-based engines."
    )
    parser.add_argument(
        "--openings",
        type=str,
        default="openings.txt",
        help="Path to a file with FEN lines."
    )

    args = parser.parse_args()

    evaluated_fn = engines.ENGINE_FUNCTIONS[args.evaluated]
    baseline_fn = engines.ENGINE_FUNCTIONS[args.baseline]
    eval_function = engines.EVAL_FUNCTIONS[args.eval]

    try:
        with open(args.openings, "r") as f:
            openings = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Openings file not found: {args.openings}")
        return

    openings_to_play = openings[:min(len(openings), args.games)]
    all_game_evals = []

    print(f"Playing {len(openings_to_play)} games...")

    for i, fen in enumerate(openings_to_play):
        evaluated_color = chess.WHITE if i % 2 == 0 else chess.BLACK
        print(f"Game {i+1}/{len(openings_to_play)}: Evaluated plays as {'White' if evaluated_color == chess.WHITE else 'Black'}")

        game_evals = play_game(evaluated_fn, baseline_fn, eval_function, fen, evaluated_color, args.elo)
        all_game_evals.append(game_evals)

    print(f"Saving results to {args.output}...")
    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        for evals in all_game_evals:
            writer.writerow(evals)

    print("Done.")


if __name__ == "__main__":
    main()