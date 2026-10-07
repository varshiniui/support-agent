from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Order, SupportTicket
from app.schemas.ticket import TicketCreate


class TicketService:
    def __init__(self, db: Session):
        self.db = db

    def create_ticket(self, customer_id: int, data: TicketCreate) -> SupportTicket:
        order_id = None
        if data.order_number:
            order = self.db.scalar(
                select(Order).where(
                    Order.order_number == data.order_number,
                    Order.customer_id == customer_id,
                )
            )
            if order is None:
                raise NotFoundError("Order not found")
            order_id = order.id

        ticket = SupportTicket(
            customer_id=customer_id,
            order_id=order_id,
            subject=data.subject,
            description=data.description,
            priority=data.priority,
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def get_ticket(self, customer_id: int, ticket_id: int) -> SupportTicket:
        ticket = self.db.scalar(
            select(SupportTicket).where(
                SupportTicket.id == ticket_id,
                SupportTicket.customer_id == customer_id,
            )
        )
        if ticket is None:
            raise NotFoundError("Ticket not found")
        return ticket

    def list_tickets(
        self, customer_id: int, status: str | None = None, limit: int = 10
    ) -> list[SupportTicket]:
        stmt = select(SupportTicket).where(SupportTicket.customer_id == customer_id)
        if status:
            stmt = stmt.where(SupportTicket.status == status)
        stmt = stmt.order_by(SupportTicket.id.desc()).limit(limit)
        return list(self.db.scalars(stmt))