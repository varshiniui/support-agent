from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Order


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def list_orders(
        self, customer_id: int, limit: int = 10, offset: int = 0
    ) -> tuple[list[Order], int]:
        base = select(Order).where(Order.customer_id == customer_id)
        total = self.db.scalar(select(func.count()).select_from(base.subquery()))
        items = list(
            self.db.scalars(base.order_by(Order.id.desc()).limit(limit).offset(offset))
        )
        return items, total or 0

    def get_by_number(self, customer_id: int, order_number: str) -> Order:
        order = self.db.scalar(
            select(Order).where(
                Order.order_number == order_number,
                Order.customer_id == customer_id,
            )
        )
        if order is None:
            raise NotFoundError("Order not found")
        return order