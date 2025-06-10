import engines
import chess


def test():
    board = chess.Board()
    avgMove = engines.avg_player_move(board, 1000)
    sfMove = engines.sf_best_move(board)
    rbm = engines.recursivebest_move(board, 1000, True)

    print(avgMove, sfMove, rbm)


test()
