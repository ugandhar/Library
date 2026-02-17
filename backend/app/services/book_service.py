from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import Book
from ..schemas import BookCreate, BookUpdate


def create_book(db: Session, payload: BookCreate) -> Book:
    existing = db.query(Book).filter(Book.isbn == payload.isbn).first()
    if existing:
        raise HTTPException(status_code=409, detail="Book with this ISBN already exists")

    book = Book(
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        publication_year=payload.publication_year,
        total_copies=payload.total_copies,
        available_copies=payload.total_copies,
    )
    try:
        db.add(book)
        db.commit()
        db.refresh(book)
        return book
    except Exception:
        db.rollback()
        raise


def list_books(db: Session) -> list[Book]:
    return db.query(Book).order_by(Book.id.asc()).all()


def get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def update_book(db: Session, book_id: int, payload: BookUpdate) -> Book:
    book = get_book_or_404(db, book_id)

    if payload.isbn and payload.isbn != book.isbn:
        duplicate = db.query(Book).filter(Book.isbn == payload.isbn).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="Book with this ISBN already exists")

    updates = payload.model_dump(exclude_unset=True)
    if "total_copies" in updates:
        new_total = updates["total_copies"]
        checked_out = book.total_copies - book.available_copies
        if new_total < checked_out:
            raise HTTPException(
                status_code=400,
                detail="total_copies cannot be lower than currently checked-out copies",
            )
        updates["available_copies"] = new_total - checked_out

    for field, value in updates.items():
        setattr(book, field, value)

    try:
        db.commit()
        db.refresh(book)
        return book
    except Exception:
        db.rollback()
        raise
