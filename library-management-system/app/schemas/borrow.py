from pydantic import BaseModel
from datetime import datetime


class BorrowResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    book_title: str | None = None
    borrow_date: datetime
    return_date: datetime | None
    is_returned: bool

    model_config = {"from_attributes": True}