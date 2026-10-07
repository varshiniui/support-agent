from typing import Literal

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10)
    priority: Literal["low", "medium", "high"] = "medium"


class TicketOut(TicketCreate):
    id: int
    status: str = "open"