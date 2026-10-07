from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_customer, require_staff
from app.core.database import get_db
from app.models import Customer, User
from app.schemas.ticket import TicketCreate, TicketOut, TicketStatusUpdate
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


def get_ticket_service(db: Session = Depends(get_db)) -> TicketService:
    return TicketService(db)


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(
    payload: TicketCreate,
    customer: Customer = Depends(get_current_customer),
    service: TicketService = Depends(get_ticket_service),
):
    return service.create_ticket(customer.id, payload)


@router.get("", response_model=list[TicketOut])
def list_tickets(
    status: str | None = None,
    limit: int = Query(10, ge=1, le=50),
    customer: Customer = Depends(get_current_customer),
    service: TicketService = Depends(get_ticket_service),
):
    return service.list_tickets(customer.id, status, limit)


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    customer: Customer = Depends(get_current_customer),
    service: TicketService = Depends(get_ticket_service),
):
    return service.get_ticket(customer.id, ticket_id)


@router.patch("/{ticket_id}/status", response_model=TicketOut)
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    staff: User = Depends(require_staff),
    service: TicketService = Depends(get_ticket_service),
):
    return service.update_status(ticket_id, payload.status)