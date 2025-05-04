import sqlite3
from chess_hash import fen2hash

FILE = "../models/results.sqlite"


class Database:
    def __init__(self):
        self.connect(FILE)

    def connect(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        # make read-only
        self.connection.execute("PRAGMA query_only = 1")
        print(f"Connected to database: {db_file}")

    def close(self):
        if self.connection:
            self.connection.close()
            print("Connection closed.")

    def get_position(self, position_hash):
        hash_blob = position_hash.to_bytes(16, byteorder="little")
        self.cursor.execute(
            "SELECT * FROM chessPosition WHERE positionID = ?",
            (hash_blob,),
        )
        result = self.cursor.fetchone()
        if result:
            return {
                "positionID": result[0],
                "timesPlayed": result[1],
                "whiteWins": result[2],
                "blackWins": result[3],
                "recursiveScoreWhite": result[4],
                "recursiveScoreBlack": result[5],
            }
        return None

    def get_next_moves(self, position_hash):
        hash_blob = position_hash.to_bytes(16, byteorder="little")
        self.cursor.execute(
            """SELECT 
                chessPosition.timesPlayed as pos_times_played ,
                chessPosition.positionID,
                chessPosition.whiteWins,
                chessPosition.blackWins,
                chessPosition.recursiveScoreWhite,
                chessPosition.recursiveScoreBlack,
                chessMove.timesPlayed as move_times_played
                FROM chessMove WHERE startPosition = ?
                JOIN chessPosition ON chessMove.endPosition = chessPosition.positionID
               """,
            (hash_blob,),
        )
        result = self.cursor.fetchall()
        if result:
            moves = []
            for row in result:
                moves.append(
                    {
                        "positionID": row[1],
                        "timesPlayed": row[0],
                        "whiteWins": row[2],
                        "blackWins": row[3],
                        "recursiveScoreWhite": row[4],
                        "recursiveScoreBlack": row[5],
                        "move_times_played": row[6],
                    }
                )
            return moves
        return None

    def get_position_by_fen(self, fen, rating):
        position_hash = fen2hash(fen, rating)
        return self.get_position(position_hash)

    def get_next_moves_by_fen(self, fen, rating):
        position_hash = fen2hash(fen, rating)
        return self.get_next_moves(position_hash)
