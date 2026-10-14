from langchain_core.tools import BaseTool, tool
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import Customer
from app.schemas.ticket import TicketCreate
from app.services.faq_service import FAQService
from app.services.order_service import OrderService
from app.services.ticket_service import TicketService


def build_tools(db: Session, customer: Customer) -> list[BaseTool]:
    """Create the tools for ONE logged-in customer. The customer is fixed here, not chosen by the AI."""
    orders = OrderService(db)
    tickets = TicketService(db)
    faqs = FAQService(db)
    tickets_created = {"count": 0}

    def clean_order_number(value: str) -> str:
        number = value.strip().lstrip("#").strip()
        if not number.isdigit() or len(number) > 20:
            raise AppError("Order numbers contain digits only, for example 1234.")
        return number

    def order_summary(order) -> dict:
        return {
            "order_number": order.order_number,
            "status": order.status,
            "total_amount": str(order.total_amount),
            "placed_on": order.placed_at.date().isoformat(),
            "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
        }

    @tool
    def check_order_status(order_number: str | None = None) -> dict:
        """Look up the status and estimated delivery of the customer's order by its order number.
        If the customer gave no order number, leave order_number empty to get their 3 most recent orders.
        Use this when the customer asks where their order or package is."""
        try:
            if order_number is None or not order_number.strip():
                items, _ = orders.list_orders(customer.id, limit=3)
                return {"recent_orders": [order_summary(o) for o in items]}
            return order_summary(orders.get_by_number(customer.id, clean_order_number(order_number)))
        except AppError as exc:
            return {"error": exc.message}

    @tool
    def get_customer_details() -> dict:
        """Get the logged-in customer's name, email and phone number."""
        return {"full_name": customer.full_name, "email": customer.user.email, "phone": customer.phone}

    @tool
    def search_faq(query: str) -> dict:
        """Search the shop's help articles about refunds, returns, shipping, cancellations and damaged items.
        Use this for any question about store policies. Pass a short query such as 'refund policy'."""
        results = faqs.search(query)
        if not results:
            return {"results": [], "note": "No matching help article found."}
        return {"results": [{"title": r.title, "content": r.content} for r in results]}

    @tool(args_schema=TicketCreate)
    def create_support_ticket(
        subject: str, description: str, priority: str = "medium", order_number: str | None = None
    ) -> dict:
        """Create a support ticket for the customer. Only use this when the customer clearly asks to
        raise a complaint or ticket, and you already know what the problem is. Include order_number
        if the problem is about a specific order."""
        if tickets_created["count"] >= 1:
            return {"error": "A ticket was already created for this message."}
        try:
            data = TicketCreate(
                subject=subject,
                description=description,
                priority=priority,
                order_number=clean_order_number(order_number) if order_number else None,
            )
            ticket = tickets.create_ticket(customer.id, data)
        except AppError as exc:
            return {"error": exc.message}
        tickets_created["count"] += 1
        return {"ticket_id": ticket.id, "status": ticket.status, "subject": ticket.subject}

    @tool
    def get_ticket_status(ticket_id: int | None = None) -> dict:
        """Get the status of one of the customer's support tickets by ticket id.
        If no id is given, return their 3 most recent tickets. Use this when the customer asks
        about a previous complaint or ticket."""
        try:
            if ticket_id is not None:
                found = [tickets.get_ticket(customer.id, ticket_id)]
            else:
                found = tickets.list_tickets(customer.id, limit=3)
        except AppError as exc:
            return {"error": exc.message}
        return {
            "tickets": [
                {
                    "id": t.id,
                    "subject": t.subject,
                    "status": t.status,
                    "priority": t.priority,
                    "created_on": t.created_at.date().isoformat(),
                }
                for t in found
            ]
        }

    return [check_order_status, get_customer_details, search_faq, create_support_ticket, get_ticket_status]