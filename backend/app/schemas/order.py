from datetime import date, datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: str
    total_amount: Decimal
    placed_at: datetime
    estimated_delivery: date | None


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int