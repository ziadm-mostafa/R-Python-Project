from sqlalchemy import Column, Integer, String, DateTime, Unicode
from datetime import datetime, timezone
from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(Unicode(100), unique=True, nullable=False)
    email = Column(Unicode(150), unique=True, nullable=False)

    password_hash = Column(String(255), nullable=False)

    role = Column(String(50), default="member")  # admin or member

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))