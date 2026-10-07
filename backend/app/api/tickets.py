from fastapi import APIRouter, HTTPException, Query

from app.schemas.ticket import TicketCreate, TicketOut

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Temporary storage. Replaced by PostgreSQL in Phase 3.
fake_db: list[TicketOut] = []


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketCreate):
    ticket = TicketOut(id=len(fake_db) + 1, **payload.model_dump())
    fake_db.append(ticket)
    return ticket


@router.get("", response_model=list[TicketOut])
def list_tickets(status: str | None = None, limit: int = Query(10, ge=1, le=50)):
    results = fake_db
    if status:
        results = [t for t in results if t.status == status]
    return results[:limit]


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int):
    for ticket in fake_db:
        if ticket.id == ticket_id:
            return ticket
    raise HTTPException(status_code=404, detail="Ticket not found")