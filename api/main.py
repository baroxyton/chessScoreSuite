from db import Database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import base64

db = Database()
app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/position/{position_hash}")
async def get_position(position_hash: int):
    position = db.get_position(position_hash)
    if position:
        return {
            "positionID": int.from_bytes(position["positionID"], "little"),
            "timesPlayed": position["timesPlayed"],
            "whiteWins": position["whiteWins"],
            "blackWins": position["blackWins"],
            "recursiveScoreWhite": position["recursiveScoreWhite"],
            "recursiveScoreBlack": position["recursiveScoreBlack"],
            "elo": position["elo"],
        }
    return {"error": "Position not found"}


@app.get("/position/{position_hash}/moves")
async def get_next_moves(position_hash: int):
    moves = db.get_next_moves(position_hash)
    if moves:
        return [
            {
                "positionID": int.from_bytes(move["positionID"], byteorder="little"),
                "timesPlayed": move["timesPlayed"],
                "whiteWins": move["whiteWins"],
                "blackWins": move["blackWins"],
                "recursiveScoreWhite": move["recursiveScoreWhite"],
                "recursiveScoreBlack": move["recursiveScoreBlack"],
                "move_times_played": move["move_times_played"],
                "moveSAN": move["moveSAN"],
            }
            for move in moves
        ]
    return {"error": "No moves found for this position"}


@app.get("/fen/{fen}/{rating}/position")
async def get_position_by_fen(fen: str, rating: int):
    fen_dec = base64.b64decode(fen).decode("utf-8")
    position = db.get_position_by_fen(fen_dec, rating)
    if position:
        return {
            "positionID": int.from_bytes(position["positionID"], byteorder="little"),
            "timesPlayed": position["timesPlayed"],
            "whiteWins": position["whiteWins"],
            "blackWins": position["blackWins"],
            "recursiveScoreWhite": position["recursiveScoreWhite"],
            "recursiveScoreBlack": position["recursiveScoreBlack"],
            "elo": position["elo"],
        }
    return {"error": "Position not found"}


@app.get("/fen/{fen}/{rating}/moves")
async def get_next_moves_by_fen(fen: str, rating: int):
    fen_dec = base64.b64decode(fen).decode("utf-8")
    moves = db.get_next_moves_by_fen(fen_dec, rating)
    if moves:
        return [
            {
                "positionID": int.from_bytes(move["positionID"], byteorder="little"),
                "timesPlayed": move["timesPlayed"],
                "whiteWins": move["whiteWins"],
                "blackWins": move["blackWins"],
                "recursiveScoreWhite": move["recursiveScoreWhite"],
                "recursiveScoreBlack": move["recursiveScoreBlack"],
                "move_times_played": move["move_times_played"],
                "moveSAN": move["moveSAN"],
            }
            for move in moves
        ]
    return {"error": "No moves found for this position"}
