from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_customer
from app.core.database import get_db
from app.models import Customer
from app.schemas.order import OrderOut, Page
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)


@router.get("", response_model=Page[OrderOut])
def list_orders(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    customer: Customer = Depends(get_current_customer),
    service: OrderService = Depends(get_order_service),
):
    items, total = service.list_orders(customer.id, limit, offset)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/{order_number}", response_model=OrderOut)
def get_order(
    order_number: str,
    customer: Customer = Depends(get_current_customer),
    service: OrderService = Depends(get_order_service),
):
    return service.get_by_number(customer.id, order_number)