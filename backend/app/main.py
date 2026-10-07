from fastapi import FastAPI
from app.core.config import settings
app = FastAPI(title=settings.app_name, version="0.1.0")
from app.api import tickets

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(tickets.router)