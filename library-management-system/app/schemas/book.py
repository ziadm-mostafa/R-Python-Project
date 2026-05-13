from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    total_copies: int = Field(..., ge=0)
    cover_url: str | None = None


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    total_copies: int | None = Field(default=None, ge=0)
    cover_url: str | None = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    cover_url: str | None = None
    total_copies: int
    available_copies: int

    model_config = {"from_attributes": True}