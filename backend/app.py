from fastapi import FastAPI, Query
from pydantic import BaseModel, validator, Required
from random import choice
from copy import deepcopy

app = FastAPI()


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
def get_random_move(board_state: BoardState = Required):
    """OPPONENT MODEL - Random Move
    
    Must receive a BoardState object to parse through its .state attribute
    Returns a random valid move to play in response
    """
    board = board_state.state
    valid_moves = [i for i, x in enumerate(board) if x is None]
    if not valid_moves:
        return {"ai_move": None}
    random_move = choice(valid_moves)
    return {"ai_move": random_move}

        
@app.post("/api/ai-move/minmax")
def get_minmax_move(board_state: BoardState = Required):
    # TODO
    """OPPONENT MODEL - Minmax
    
    Must receive a BoardState object to parse through its .state attribute
    Returns the optimal move by the next player per the minimax algorithm  
    """
    board = board_state.state
    
    return {"ai_move": minmax(board)}


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
    populate search pahts
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


def minmax(board: list[str | None]):
    """Returns the optimal move value and index based on board input board
    
    This implements the minmax algorithm *without* alpha-beta pruning or depth-, 
    limiting, using full depth-first search. X is assumed the maximizing player
    """

    def max_value(board):
        value = -2
        move = None
        
        for action in available_actions(board):
            res = result_of_move(board, action)
            if is_terminal(res):
                return (board_utility(res), action)
            
            v = max(min_value(res)[0], value)
            
            if v >= value:
                value = v
                move = action
        return (value, move)
    
    def min_value(board):
        value = 2
        move = None
        
        for action in available_actions(board):
            res = result_of_move(board, action)
            if is_terminal(res):
                return (board_utility(res), action)
            
            v = min(max_value(res)[0], value)
            
            if v <= value:
                value = v
                move = action
            return (value, move)
        
    if is_terminal(board):
        return None
    
    if player(board) == "X":
        return max_value(board)[1]
    else:
        return min_value(board)[1]