import pytest
from fastapi import HTTPException

from app.models import Book
from app.schemas import BookCreate, BookUpdate
from app.services import book_service


def test_create_book_success(db_session):
    payload = BookCreate(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        total_copies=2,
    )

    book = book_service.create_book(db_session, payload)

    assert book.id is not None
    assert book.available_copies == 2


def test_create_book_duplicate_isbn_raises_409(db_session):
    payload = BookCreate(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        total_copies=2,
    )
    book_service.create_book(db_session, payload)

    with pytest.raises(HTTPException) as exc:
        book_service.create_book(db_session, payload)

    assert exc.value.status_code == 409


def test_update_book_rejects_total_copies_lower_than_checked_out(db_session):
    book = Book(
        title="DDD",
        author="Eric Evans",
        isbn="9780321125217",
        total_copies=3,
        available_copies=1,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    with pytest.raises(HTTPException) as exc:
        book_service.update_book(db_session, book.id, BookUpdate(total_copies=1))

    assert exc.value.status_code == 400
