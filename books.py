from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
import json
import uuid
import os

from app.database.session import get_db
from app.models.book import Book
from app.models.borrow_record import BorrowRecord
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.core.dependencies import get_current_admin
from app.cache.redis_client import redis_client


logger = logging.getLogger("library.books")

router = APIRouter(prefix="/books", tags=["books"])

cache_ttl = 60


def serialize_book(book: Book) -> dict:
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "cover_url": book.cover_url,
        "total_copies": book.total_copies,
        "available_copies": book.available_copies
    }


def invalidate_book_cache(book_id: int | None = None) -> None:
    try:
        redis_client.delete("books:all")
        if book_id is not None:
            redis_client.delete(f"book:{book_id}")
    except Exception:
        logger.warning("redis cache invalidation failed")


UPLOAD_DIR = "static/uploads"


@router.post("/upload-cover", status_code=status.HTTP_200_OK)
def upload_cover(
    file: UploadFile = File(...),
    request: Request = None,
    current_user=Depends(get_current_admin)
) -> dict:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="only image files are allowed"
        )

    ext = os.path.splitext(file.filename or "image.jpg")[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        logger.error(f"failed to upload cover: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="upload failed"
        )
    finally:
        file.file.close()

    base = str(request.base_url).rstrip("/")
    url = f"{base}/static/uploads/{filename}"
    logger.info(f"cover uploaded: {url}")

    return {"url": url}


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
) -> Book:
    isbn = book_data.isbn.strip()

    existing = db.query(Book).filter(Book.isbn == isbn).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="book with this isbn already exists"
        )

    try:
        new_book = Book(
            title=book_data.title.strip(),
            author=book_data.author.strip(),
            isbn=isbn,
            cover_url=book_data.cover_url.strip() if book_data.cover_url else None,
            total_copies=book_data.total_copies,
            available_copies=book_data.total_copies
        )

        db.add(new_book)
        db.commit()
        db.refresh(new_book)

        invalidate_book_cache()

        logger.info(f"book created id={new_book.id}")

        return new_book

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"database error creating book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )


@router.get("/", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)) -> list[Book]:
    cache_key = "books:all"

    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("cache hit books:all")
            return json.loads(cached)
    except Exception:
        logger.warning("redis unavailable, fallback to db")

    books = db.query(Book).all()

    try:
        redis_client.setex(
            cache_key,
            cache_ttl,
            json.dumps([serialize_book(b) for b in books])
        )
    except Exception:
        logger.warning("redis set failed")

    return books


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)) -> Book:
    cache_key = f"book:{book_id}"

    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.info(f"cache hit book:{book_id}")
            return json.loads(cached)
    except Exception:
        logger.warning("redis unavailable, fallback to db")

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found"
        )

    try:
        redis_client.setex(
            cache_key,
            cache_ttl,
            json.dumps(serialize_book(book))
        )
    except Exception:
        logger.warning("redis set failed")

    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found"
        )

    try:
        if book_data.title is not None:
            book.title = book_data.title.strip()

        if book_data.author is not None:
            book.author = book_data.author.strip()

        if book_data.cover_url is not None:
            book.cover_url = book_data.cover_url.strip() or None

        if book_data.total_copies is not None:
            active_borrows = db.query(BorrowRecord).filter(
                BorrowRecord.book_id == book_id,
                BorrowRecord.is_returned == False
            ).count()
            if book_data.total_copies < active_borrows:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"cannot reduce total copies below {active_borrows} active borrows"
                )
            difference = book_data.total_copies - book.total_copies
            book.total_copies = book_data.total_copies
            book.available_copies += difference

            if book.available_copies < 0:
                book.available_copies = 0

        db.commit()
        db.refresh(book)

        invalidate_book_cache(book_id)

        logger.info(f"book updated id={book.id}")

        return book

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"database error updating book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )


@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
) -> dict:
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found"
        )

    active_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.book_id == book_id,
        BorrowRecord.is_returned == False
    ).count()

    if active_borrows > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot delete book with active borrow records"
        )

    try:
        db.query(BorrowRecord).filter(
            BorrowRecord.book_id == book_id
        ).delete(synchronize_session=False)
        db.delete(book)
        db.commit()

        invalidate_book_cache(book_id)

        logger.info(f"book deleted id={book_id}")

        return {"message": "book deleted successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"database error deleting book: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="database error"
        )