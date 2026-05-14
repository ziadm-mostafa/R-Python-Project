from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone
import logging

from app.database.session import get_db
from app.models.book import Book
from app.models.borrow_record import BorrowRecord
from app.schemas.borrow import BorrowResponse
from app.core.dependencies import get_current_user, get_current_admin
from app.cache.redis_client import redis_client


logger = logging.getLogger("library.borrow")

router = APIRouter(prefix="/borrow", tags=["borrow"])

max_borrow_limit = 3


def _invalidate_book_cache(book_id: int) -> None:
    try:
        redis_client.delete("books:all")
        redis_client.delete(f"book:{book_id}")
    except Exception:
        logger.warning("redis cache invalidation failed")


def _enrich_with_book_titles(records: list[BorrowRecord], db: Session) -> None:
    book_ids = {r.book_id for r in records}
    books = db.query(Book).filter(Book.id.in_(book_ids)).all()
    book_map = {b.id: b.title for b in books}
    for record in records:
        record.book_title = book_map.get(record.book_id)


@router.post("/{book_id}", response_model=BorrowResponse)
def borrow_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
) -> BorrowRecord:
    book = db.query(Book).filter(Book.id == book_id).with_for_update().first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found"
        )

    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="book not available"
        )

    active_borrows = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.is_returned == False
    ).count()

    if active_borrows >= max_borrow_limit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="borrow limit reached"
        )

    existing = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.book_id == book_id,
        BorrowRecord.is_returned == False
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="book already borrowed"
        )

    try:
        record = BorrowRecord(
            user_id=current_user.id,
            book_id=book_id
        )

        book.available_copies -= 1

        db.add(record)
        db.commit()
        db.refresh(record)

        _invalidate_book_cache(book_id)

        logger.info(f"book borrowed user={current_user.id} book={book_id}")

        return record

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"database error during borrow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="borrow operation failed"
        )


@router.post("/return/{book_id}", response_model=BorrowResponse)
def return_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
) -> BorrowRecord:
    record = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == current_user.id,
        BorrowRecord.book_id == book_id,
        BorrowRecord.is_returned == False
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="active borrow record not found"
        )

    book = db.query(Book).filter(Book.id == book_id).with_for_update().first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found"
        )

    try:
        record.is_returned = True
        record.return_date = datetime.now(timezone.utc)

        book.available_copies += 1

        db.commit()
        db.refresh(record)

        _invalidate_book_cache(book_id)

        logger.info(f"book returned user={current_user.id} book={book_id}")

        return record

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"database error during return: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="return operation failed"
        )


@router.get("/my-history", response_model=list[BorrowResponse])
def my_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
) -> list[BorrowRecord]:
    records = db.query(BorrowRecord).filter(
        BorrowRecord.user_id == current_user.id
    ).all()
    _enrich_with_book_titles(records, db)
    return records


@router.get("/all", response_model=list[BorrowResponse])
def all_records(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
) -> list[BorrowRecord]:
    records = db.query(BorrowRecord).all()
    _enrich_with_book_titles(records, db)
    return records