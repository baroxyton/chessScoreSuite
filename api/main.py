from db import Database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import base64

# Initialize both databases
db_default = Database("../models/results.sqlite")
db_min50 = Database("../models/results_min50.sqlite")

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

def should_use_min50_db(position_hash: int = None, fen: str = None, rating: int = None) -> bool:
    """
    Determine whether to use min50 database based on data completeness.
    Returns True if we should use min50 database, False for default database.
    """
    try:
        # Get position data from default database
        if position_hash is not None:
            position = db_default.get_position(position_hash)
            moves = db_default.get_next_moves(position_hash)
        elif fen is not None and rating is not None:
            position = db_default.get_position_by_fen(fen, rating)
            moves = db_default.get_next_moves_by_fen(fen, rating)
        else:
            return True 
        
        if not position or not moves: # Use min50 for chance of data completeness
            return True
        
        parent_times_played = position.get("timesPlayed", 0)
        if parent_times_played == 0:
            return True
        
        # Sum up child positions' timesPlayed
        child_times_played_sum = sum(move.get("move_times_played", 0) for move in moves)
        
        # If parent has significantly more plays than sum of children 
        # it suggests incomplete move data, so use min50 database
        if parent_times_played > child_times_played_sum * 2:
            return True
        
        return False
    
    except Exception:
        # On any error, default to original database
        return False

def get_appropriate_db(position_hash: int = None, fen: str = None, rating: int = None) -> Database:
    """Get the appropriate database based on data completeness."""
    if should_use_min50_db(position_hash, fen, rating):
        return db_min50
    return db_default


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/position/{position_hash}")
async def get_position(position_hash: int):
    db = get_appropriate_db(position_hash=position_hash)
    position = db.get_position(position_hash)
    if position:
        return {
            "positionID": str(int.from_bytes(position["positionID"], "little")),
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
    db = get_appropriate_db(position_hash=position_hash)
    moves = db.get_next_moves(position_hash)
    if moves:
        return [
            {
                "positionID": str(
                    int.from_bytes(move["positionID"], byteorder="little")
                ),
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
    db = get_appropriate_db(fen=fen_dec, rating=rating)
    position = db.get_position_by_fen(fen_dec, rating)
    if position:
        return {
            "positionID": str(
                int.from_bytes(position["positionID"], byteorder="little")
            ),
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
    db = get_appropriate_db(fen=fen_dec, rating=rating)
    moves = db.get_next_moves_by_fen(fen_dec, rating)
    if moves:
        return [
            {
                "positionID": str(
                    int.from_bytes(move["positionID"], byteorder="little")
                ),
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