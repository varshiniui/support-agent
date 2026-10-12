from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.core.config import settings

model = ChatGroq(
    model=settings.llm_model,
    api_key=settings.groq_api_key,
    temperature=0.3,
    max_tokens=settings.llm_max_tokens,
)

print("--- 1. A chat model call ---")
reply = model.invoke("Say hello in five words.")
print(type(reply).__name__, "->", reply.content)
print("tokens:", reply.usage_metadata)

print("\n--- 2. A prompt template ---")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are {agent_name}, a support assistant. Be concise."),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)
values = {
    "agent_name": "Roh",
    "history": [
        HumanMessage(content="My name is Priya."),
        AIMessage(content="Nice to meet you, Priya!"),
    ],
    "input": "What is my name?",
}
for m in prompt.invoke(values).to_messages():
    print(f"{m.type:>6}: {m.content}")

print("\n--- 3. A chain ---")
chain = prompt | model | StrOutputParser()
print(chain.invoke(values))


print("\n--- 4. Structured output ---")


class Intent(BaseModel):
    intent: Literal["order_status", "refund_question", "complaint", "other"] = Field(
        description="What the customer wants"
    )
    order_number: str | None = Field(
        default=None, description="Order number if one was mentioned, digits only"
    )


extract_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Classify the customer's message. Respond as JSON."),
        ("human", "{input}"),
    ]
)
for method in ("json_schema", "function_calling", "json_mode"):
    try:
        extractor = extract_prompt | model.with_structured_output(Intent, method=method)
        result = extractor.invoke({"input": "My order #1234 hasn't arrived"})
        print(f"[{method}] works ->", repr(result))
        break
    except Exception as exc:
        print(f"[{method}] failed: {type(exc).__name__}: {str(exc)[:120]}")