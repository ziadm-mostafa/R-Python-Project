from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from datetime import datetime, timezone
from app.database.session import Base


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))

    borrow_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    return_date = Column(DateTime, nullable=True)

    is_returned = Column(Boolean, default=False)