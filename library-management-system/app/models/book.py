from sqlalchemy import Column, Integer, String, DateTime, Unicode
from datetime import datetime, timezone
from app.database.session import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(Unicode(200), nullable=False)
    author = Column(Unicode(200), nullable=False)
    isbn = Column(String(50), unique=True, nullable=False)
    cover_url = Column(String(500), nullable=True)

    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))