from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from pydantic import BaseModel, validator, Required
from random import choice
from copy import deepcopy
from dotenv import load_dotenv
from os import getenv
from math import inf

app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=['*']
    )

load_dotenv()

async def validate_api_key(X_API_KEY: Annotated[str|None, Header(convert_underscores=False)]):
    """Pulls API Key from request header and compares it to environment variable"""
    if X_API_KEY == getenv("API_KEY"):
        return X_API_KEY
    else:
        raise HTTPException(status_code="HTTP_401_UNAUTHORIZED")

#
api_key_required = Annotated[str|None, Depends(validate_api_key)]

 
class BoardState(BaseModel):
    state: list[str | None]
    
    @validator("state")    
    def validate_board_state(cls, state):
        valid_values = ["X", "O", None]
        if len(state) != 9:
            raise ValueError("Board state must have exactly 9 elements")
        for value in state:
            if value not in valid_values:
                raise ValueError("Invalid value in board state")
        return state

    
@app.post("/api/ai-move/random")
def get_random_move(board_state: BoardState = Required, X_API_KEY: api_key_required = None):
    """OPPONENT MODEL - Random Move
    
    Must receive a BoardState object to parse through its .state attribute
    Returns a random valid move to play in response
    """
    board = board_state.state
    valid_moves = [i for i, x in enumerate(board) if x is None]
    if not valid_moves:
        return {"ai_move": None}
    random_move = choice(valid_moves)
    return {"ai_move": random_move,
            }

        
@app.post("/api/ai-move/minmax")
def get_minmax_move(board_state: BoardState = Required, X_API_KEY: api_key_required = None):
    """OPPONENT MODEL - Minmax
    
    Must receive a BoardState object to parse through its .state attribute
    Returns the optimal move by the next player per the minimax algorithm  
    """
    board = board_state.state
    
    return {"ai_move": minmax(board, -inf, inf),
            "player":player(board)}


def player(board: list[str | None]):
    """Returns the next player for a given board
    
    Assumes that X goes first for any given game
    """
    if board.count("X") > board.count("O"): 
        return "O"
    return "X"
    

def result_of_move(board: list[str | None], move:int) -> list[str | None]:
    """Returns resultant board from a given move, based on current player
        
    <move> parameter must be an integer 0-8 (inclusive)
    Player move determined by player()
    For use by opponent models in determining resultant actions
    """
    if (move not in range(9)) or (board[move] != None):
        raise Exception("Invalid move!")

    board_copy = deepcopy(board)
    board_copy[move] = player(board)
    
    return board_copy


def available_actions(board: list[str | None]) -> list[int]:
    """Returns available move indices given a board state. 
    
    Agnostic to which player's turn it is, for use by opponent models to 
    populate search paths
    """
    options = []
    for i, x in enumerate(board):
        if x is None:
            options.append(i)
    return options

def winner(board: list[str | None]):
    """Takes a board and returns winner if any, else None"""
    win_states = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ]
    
    for line in win_states:
        a, b, c = line
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None
    

def is_terminal(board: list[str | None]) -> bool:
    """Returns whether game is over or not
    
    To be used as a base case check for recursive opponent models
    """
    if None not in board:
        return True
    if winner(board):
        return True
    return False

def board_utility(board: list[str | None]):
    if winner(board) == "X":
        return 1
    elif winner(board) == "O":
        return -1
    else:
        return 0


def minmax(board: list[str | None], alpha, beta):
    """Returns the optimal move value and index based on board input board"""
    if is_terminal(board):
        return None, board_utility(board)
    
    moves = available_actions(board)
    best_move = moves[0]
    
    if player(board) == "X":
        max_eval = -inf
        for move in moves:
            board_copy = result_of_move(board, move)
            current_eval = minmax(board_copy, alpha, beta)[1]
            if current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            alpha = max(alpha, current_eval)
            if beta <= alpha:
                break
        return best_move, max_eval
    
    if player(board) == "O":
        min_eval = inf
        for move in moves:
            board_copy = result_of_move(board, move)
            current_eval = minmax(board_copy, alpha, beta)[1]
            if current_eval < min_eval:
                min_eval = current_eval
                best_move = move
            beta = min(beta, current_eval)
            if beta <= alpha:
                break
        return best_move, min_eval

