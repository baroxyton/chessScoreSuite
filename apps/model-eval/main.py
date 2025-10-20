# KI-generierter code
import argparse
import csv
import chess
import engines
import os

GRID_ELO_LEVELS = range(5)  # 0-3 inclusive for 16 pairings


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


def generate_opening_fen(moves=3, avg_engine_fn=None, elo=2):
    """
    Generate an opening FEN by letting the average player play the first `full_moves`
    on both sides (no stats recorded). Returns the resulting FEN.
    """
    board = chess.Board(chess.STARTING_FEN)
    if avg_engine_fn is None:
        avg_engine_fn = engines.ENGINE_FUNCTIONS["avg_player"]

    plies = moves
    for _ in range(plies):
        if board.is_game_over(claim_draw=True):
            break
        move_result = _call_engine(avg_engine_fn, board, elo, board.turn)
        if move_result is None:
            break
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

    return board.fen()


def play_game(
    evaluated_fn,
    baseline_fn,
    eval_function,
    start_fen,
    evaluated_color,
    evaluated_elo,
    baseline_elo,
    record_move_frequency=False,
    max_moves=None,
):
    """
    Plays a single game and returns the list of evaluations from the evaluated engine's perspective.
    If record_move_frequency is True, records the frequency (0..1) of the evaluated engine's played move
    relative to the parent position's movePlayed instead of a numeric evaluation.
    """
    board = chess.Board(start_fen)
    evaluations = []
    move_count = 0

    while not board.is_game_over(claim_draw=True):
        if max_moves is not None and move_count >= max_moves:
            break

        # When not recording frequency, evaluate the position BEFORE making the move
        if not record_move_frequency:
            if eval_function is engines.eval_pos_avg:
                eval_value = eval_function(board, evaluated_elo)
            else:
                eval_value = eval_function(board)

            if eval_value is not None:
                if evaluated_color == chess.BLACK:
                    eval_value = -eval_value
                evaluations.append(eval_value)

        # Decide whose turn and use the correct engine
        current_color = board.turn
        if current_color == evaluated_color:
            move_result = _call_engine(
                evaluated_fn, board, evaluated_elo, evaluated_color
            )
        else:
            move_result = _call_engine(
                baseline_fn,
                board,
                baseline_elo,
                chess.WHITE if evaluated_color == chess.BLACK else chess.BLACK,
            )

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

        # If recording frequency, record it for the evaluated engine's move before pushing
        if record_move_frequency and current_color == evaluated_color:
            freq = engines.move_frequency(board, evaluated_elo, move)
            if freq is not None:
                evaluations.append(freq)

        board.push(move)
        move_count += 1

    return evaluations


def play_games_for_openings(
    evaluated_fn,
    baseline_fn,
    eval_function,
    openings,
    evaluated_elo,
    baseline_elo,
    generate_openings,
    record_move_frequency,
    status_prefix="",
    max_moves=None,
):
    prefix = f"{status_prefix} " if status_prefix else ""
    total_games = len(openings)
    results = []
    for i, base_fen in enumerate(openings):
        evaluated_color = chess.WHITE if i % 2 == 0 else chess.BLACK
        print(
            f"{prefix}Game {i+1}/{total_games}: Evaluated plays as {'White' if evaluated_color == chess.WHITE else 'Black'}"
        )
        fen = base_fen
        if generate_openings:
            fen = generate_opening_fen(
                moves=4,
                avg_engine_fn=engines.ENGINE_FUNCTIONS["avg_player"],
                elo=baseline_elo,
            )
        results.append(
            play_game(
                evaluated_fn,
                baseline_fn,
                eval_function,
                fen,
                evaluated_color,
                evaluated_elo,
                baseline_elo,
                record_move_frequency=record_move_frequency,
                max_moves=max_moves,
            )
        )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate a chess engine against a baseline engine."
    )
    parser.add_argument(
        "--evaluated",
        type=str,
        required=True,
        choices=engines.ENGINE_FUNCTIONS.keys(),
        help="The engine being evaluated.",
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default="avg_player",
        choices=engines.ENGINE_FUNCTIONS.keys(),
        help="The baseline engine (default: avg_player).",
    )
    parser.add_argument(
        "--eval",
        type=str,
        default="sf",
        choices=engines.EVAL_FUNCTIONS.keys(),
        help="The evaluation method to use for recording scores.",
    )
    parser.add_argument(
        "--games", type=int, default=10, help="Number of games to play."
    )
    parser.add_argument(
        "--output", type=str, default="results.csv", help="Output CSV file name."
    )
    parser.add_argument(
        "--evaluated-elo",
        type=int,
        default=2,
        help="ELO rating for the evaluated engine (API-based engines).",
    )
    parser.add_argument(
        "--baseline-elo",
        type=int,
        default=2,
        help="ELO rating for the baseline engine (API-based engines).",
    )
    parser.add_argument(
        "--openings",
        type=str,
        default="openings.txt",
        help="Path to a file with FEN lines.",
    )
    parser.add_argument(
        "--all-startpos",
        action="store_true",
        help="If set, all games start from the standard initial chess position (ignores --openings).",
    )
    parser.add_argument(
        "--generate-openings",
        action="store_true",
        help="Override --openings/--all-startpos: play 3 full moves with avg player on both sides, then start evaluation.",
    )
    parser.add_argument(
        "--record-move-frequency",
        action="store_true",
        help="Instead of evaluating positions, record the evaluated engine's move frequency (times this move was played / parent timesPlayed).",
    )
    parser.add_argument(
        "--recursive-avg-grid-dir",
        type=str,
        help="Write recursive-vs-avg pairings to a directory of CSV files (16 total).",
    )
    parser.add_argument(
        "--max-moves",
        type=int,
        help="Maximum number of moves per game (stops game early if reached).",
    )

    args = parser.parse_args()

    # Re-added: map CLI names to actual engine/eval callables
    evaluated_fn = engines.ENGINE_FUNCTIONS[args.evaluated]
    baseline_fn = engines.ENGINE_FUNCTIONS[args.baseline]
    eval_function = engines.EVAL_FUNCTIONS[args.eval]

    if args.generate_openings:
        openings_to_play = [chess.STARTING_FEN] * args.games
        print(
            f"Generating openings: 3 full with avg_player on both sides for all {args.games} games (overrides --openings and --all-startpos)."
        )
    elif args.all_startpos:
        openings_to_play = [chess.STARTING_FEN] * args.games
        print(f"Using standard starting position for all {args.games} games.")
    else:
        try:
            with open(args.openings, "r") as f:
                openings = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Openings file not found: {args.openings}")
            return
        openings_to_play = openings[: min(len(openings), args.games)]
    if not openings_to_play:
        print("No openings available.")
        return
    if args.recursive_avg_grid_dir:
        os.makedirs(args.recursive_avg_grid_dir, exist_ok=True)
        grid_pairs = len(GRID_ELO_LEVELS) ** 2
        print(
            f"Running recursive vs avg grid ({grid_pairs} pairings) with {len(openings_to_play)} games each..."
        )
        recursive_fn = engines.ENGINE_FUNCTIONS["recursive_best"]
        avg_fn = engines.ENGINE_FUNCTIONS["avg_player"]
        for recursive_elo in GRID_ELO_LEVELS:
            for avg_elo in GRID_ELO_LEVELS:
                status = f"[rec {recursive_elo} vs avg {avg_elo}]"
                series = play_games_for_openings(
                    recursive_fn,
                    avg_fn,
                    eval_function,
                    openings_to_play,
                    recursive_elo,
                    avg_elo,
                    args.generate_openings,
                    args.record_move_frequency,
                    status_prefix=status,
                    max_moves=args.max_moves,
                )
                outfile = os.path.join(
                    args.recursive_avg_grid_dir,
                    f"recursive_{recursive_elo}_avg_{avg_elo}.csv",
                )
                with open(outfile, "w", newline="") as f:
                    writer = csv.writer(f)
                    for row in series:
                        writer.writerow(row)
        print("Done.")
        return
    print(f"Playing {len(openings_to_play)} games...")
    all_game_evals = play_games_for_openings(
        evaluated_fn,
        baseline_fn,
        eval_function,
        openings_to_play,
        args.evaluated_elo,
        args.baseline_elo,
        args.generate_openings,
        args.record_move_frequency,
        max_moves=args.max_moves,
    )

    print(f"Saving results to {args.output}...")
    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        for evals in all_game_evals:
            writer.writerow(evals)

    print("Done.")


if __name__ == "__main__":
    main()
