from fastapi import FastAPI, Query
from typing import Annotated
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
    board = board_state.state
    valid_moves = [i for i, x in enumerate(board) if x is None]
    if not valid_moves:
        return {"ai_move": None}
    random_move = choice(valid_moves)
    return {"ai_move": random_move}
        
@app.post("/api/ai-move/minmax-o")
def get_minmax_move(board_state: BoardState = Required):
    board = board_state.state
    
    
    return {"ai_move": 2}