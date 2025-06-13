import engines
import chess

openings = []
file = open("openings.txt", "r")
for line in file:
    if line.strip() == "":
        continue
    openings.append(line.strip())
file.close()
openings = openings[:100]


def eval_to_perspective(score, color):
    if score is None:
        return None
    if color == chess.WHITE:
        return score
    else:
        return -score


def play_game(opening_fen: str, players_flip: bool, elo: int) -> list[dict]:
    board = chess.Board(opening_fen)
    result = []

    # Determine Stockfish's color based on the starting position and flip setting
    starting_turn = board.turn
    if not players_flip:
        # Stockfish plays as whoever's turn it is to start
        stockfish_color = starting_turn
    else:
        # Stockfish plays as the opposite color from who starts
        stockfish_color = not starting_turn

    ply = 0
    while not board.is_game_over():
        # Check if it's Stockfish's turn
        is_stockfish_turn = board.turn == stockfish_color

        # --- generate move --------------------------------------------------
        if is_stockfish_turn:
            san1 = engines.sf_best_move(
                board,  # elo, #board.turn == chess.WHITE
            )  # returns UCI or None
            if san1 is None:
                break
            move = board.parse_san(san1)
            move_str = san1
        else:
            san = engines.avg_player_move(board, elo)  # returns SAN or None
            if san is None:
                break
            move = board.parse_san(san)
            move_str = san

        board.push(move)

        # --- evaluate position ---------------------------------------------
        score_raw = engines.eval_pos(board)  # white-centred score
        score_stk = eval_to_perspective(score_raw, stockfish_color)

        result.append(
            {
                "fen": board.fen(),
                "move": move_str,
                "score": score_stk,
                "turn": board.turn,
                "ply": ply,
            }
        )
        ply += 1

    return result


def main():
    # eval for all openings, plot average score history
    all_games = []
    for opening in openings:
        print(f"Evaluating opening: {opening}")
        # Play games with both player configurations
        game1 = play_game(opening, players_flip=False, elo=1500)
        game2 = play_game(opening, players_flip=True, elo=1500)
        all_games.extend([game1, game2])

    # Calculate average score progression
    if all_games:
        max_moves = max(len(game) for game in all_games if game)
        avg_scores = []

        for move_idx in range(max_moves):
            scores_at_move = []
            for game in all_games:
                if move_idx < len(game) and game[move_idx]["score"] is not None:
                    scores_at_move.append(game[move_idx]["score"])

            if scores_at_move:
                avg_scores.append(sum(scores_at_move) / len(scores_at_move))

        print("Average score progression:")
        for i, score in enumerate(avg_scores):
            print(f"Move {i+1}: {score:.2f}")


if __name__ == "__main__":
    main()
