from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ticket import TicketCreate, TicketOut
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])


def get_ticket_service(db: Session = Depends(get_db)) -> TicketService:
    return TicketService(db)


# TEMPORARY: customer_id comes from the URL until Phase 4 adds login.
# Never trust this in a real system. Phase 4 takes it from the logged-in user.
@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(
    payload: TicketCreate,
    customer_id: int,
    service: TicketService = Depends(get_ticket_service),
):
    return service.create_ticket(customer_id, payload)


@router.get("", response_model=list[TicketOut])
def list_tickets(
    customer_id: int,
    status: str | None = None,
    limit: int = Query(10, ge=1, le=50),
    service: TicketService = Depends(get_ticket_service),
):
    return service.list_tickets(customer_id, status, limit)


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(
    ticket_id: int,
    customer_id: int,
    service: TicketService = Depends(get_ticket_service),
):
    return service.get_ticket(customer_id, ticket_id)