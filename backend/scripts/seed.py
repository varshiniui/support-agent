from datetime import date, timedelta
from decimal import Decimal
from app.core.security import hash_password
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models import Customer, FAQDocument, Order, User

DEMO_PASSWORD = "demo12345"  # local demo data only
DEMO_HASH = hash_password(DEMO_PASSWORD)


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)):
            print("Database already has data, skipping.")
            return

        asha = Customer(
            full_name="Asha Raman",
            phone="9000000001",
            user=User(email="asha@example.com", hashed_password=DEMO_HASH),
        )
        ravi = Customer(
            full_name="Ravi Kumar",
            phone="9000000002",
            user=User(email="ravi@example.com", hashed_password=DEMO_HASH),
        )

        orders = [
            Order(order_number="1234", customer=asha, status="shipped",
                  total_amount=Decimal("1499.00"),
                  estimated_delivery=date.today() + timedelta(days=3)),
            Order(order_number="1235", customer=asha, status="processing",
                  total_amount=Decimal("499.50"),
                  estimated_delivery=date.today() + timedelta(days=6)),
            Order(order_number="2001", customer=ravi, status="delivered",
                  total_amount=Decimal("2999.00"),
                  estimated_delivery=date.today() - timedelta(days=2)),
        ]

        faqs = [
            FAQDocument(title="Refund policy", category="refunds",
                        content="Items can be returned within 14 days of delivery for a full refund. Refunds are issued to the original payment method within 5 to 7 business days after we receive the item."),
            FAQDocument(title="Shipping times", category="shipping",
                        content="Standard shipping takes 3 to 7 business days. Orders are dispatched within 24 hours of being placed. You receive a tracking update once the order ships."),
            FAQDocument(title="Cancelling an order", category="orders",
                        content="An order can be cancelled while its status is processing. Once it has shipped, it cannot be cancelled, but you can return it after delivery."),
            FAQDocument(title="Damaged or wrong item", category="returns",
                        content="If your item arrives damaged or is not what you ordered, raise a support ticket within 7 days of delivery with a short description, and we will arrange a replacement or refund."),
        ]
        staff = User(email="agent@shop.com", hashed_password=DEMO_HASH, role="staff")
        db.add_all([asha, ravi, *orders, *faqs,staff])
        db.commit()
        print("Seeded 2 customers, 3 orders, 4 FAQ documents.")


if __name__ == "__main__":
    seed()