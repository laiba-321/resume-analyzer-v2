from pydantic import BaseModel
from typing import List


class AIResponse(BaseModel):
    score: int
    summary: str
    suggestions: List[str]
    skills: List[str]