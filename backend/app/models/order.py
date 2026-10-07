from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="processing")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    placed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    estimated_delivery: Mapped[date | None] = mapped_column(Date)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    tickets: Mapped[list["SupportTicket"]] = relationship(back_populates="order")