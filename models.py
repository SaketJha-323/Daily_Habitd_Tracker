from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class HabitCreate(BaseModel):
    name: str
    goal_days: int

class HabitOut(BaseModel):
    name: str
    goal_days: int
    completed: int
    streak: int
    consistency: float
