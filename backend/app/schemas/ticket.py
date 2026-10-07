from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10)
    priority: Literal["low", "medium", "high"] = "medium"
    order_number: str | None = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    description: str
    priority: str
    status: str
    order_id: int | None
    created_at: datetime

class TicketStatusUpdate(BaseModel):
    status: Literal["open", "in_progress", "resolved", "closed"]