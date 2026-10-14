from langchain_groq import ChatGroq
from sqlalchemy import select

from app.agent.tools import build_tools
from app.core.config import settings
from app.core.database import SessionLocal
from app.models import Customer, User

with SessionLocal() as db:
    asha = db.scalar(select(Customer).join(User).where(User.email == "asha@example.com"))
    tools = build_tools(db, asha)
    by_name = {t.name: t for t in tools}

    print("--- 1. What the AI sees ---")
    for t in tools:
        print(t.name, "| inputs:", list(t.args.keys()))

    print("\n--- 2. Running tools directly ---")
    print("own order  :", by_name["check_order_status"].invoke({"order_number": "#1234"}))
    print("not hers   :", by_name["check_order_status"].invoke({"order_number": "2001"}))
    print("bad input  :", by_name["check_order_status"].invoke({"order_number": "abc"}))
    print("faq        :", by_name["search_faq"].invoke({"query": "refund policy"}))
    print("details    :", by_name["get_customer_details"].invoke({}))

    print("\n--- 3. Which tool does the AI pick? ---")
    model = ChatGroq(
        model=settings.llm_model,
        api_key=settings.groq_api_key,
        temperature=0,
        max_tokens=settings.llm_max_tokens,
    )
    with_tools = model.bind_tools(tools)
    for question in [
        "Where is my order 1234?",
        "What is your refund policy?",
        "What is the status of my previous complaint?",
        "Hi there!",
    ]:
        reply = with_tools.invoke(question)
        print(repr(question), "->", reply.tool_calls or "no tool call")