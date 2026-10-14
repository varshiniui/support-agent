import re

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import FAQDocument

STOPWORDS = {"what", "your", "this", "that", "with", "have", "about", "does", "when", "where", "which", "there"}


class FAQService:
    def __init__(self, db: Session):
        self.db = db

    def search(self, query: str, limit: int = 3) -> list[FAQDocument]:
        words = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 3 and w not in STOPWORDS]
        if not words:
            return []
        conditions = []
        for word in words:
            pattern = f"%{word}%"
            conditions.append(FAQDocument.title.ilike(pattern))
            conditions.append(FAQDocument.content.ilike(pattern))
        stmt = select(FAQDocument).where(or_(*conditions)).limit(limit)
        return list(self.db.scalars(stmt))