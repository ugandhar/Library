import pytest
from fastapi import HTTPException

from app.models import Book
from app.schemas import BorrowRequest, MemberCreate
from app.services import loan_service, member_service


def test_borrow_book_creates_loan_and_decrements_available_copies(db_session):
    member = member_service.create_member(
        db_session,
        MemberCreate(name="Alex", email="alex@example.com", phone="123"),
    )
    book = Book(
        title="Refactoring",
        author="Martin Fowler",
        isbn="9780201485677",
        total_copies=2,
        available_copies=2,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    loan = loan_service.borrow_book(db_session, BorrowRequest(member_id=member.id, book_id=book.id))

    db_session.refresh(book)
    assert loan.id is not None
    assert book.available_copies == 1


def test_borrow_book_no_available_copies_raises_409(db_session):
    member = member_service.create_member(
        db_session,
        MemberCreate(name="Alex", email="alex@example.com", phone="123"),
    )
    book = Book(
        title="Refactoring",
        author="Martin Fowler",
        isbn="9780201485677",
        total_copies=1,
        available_copies=0,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    with pytest.raises(HTTPException) as exc:
        loan_service.borrow_book(db_session, BorrowRequest(member_id=member.id, book_id=book.id))

    assert exc.value.status_code == 409


def test_return_book_sets_returned_at_and_increments_available_copies(db_session):
    member = member_service.create_member(
        db_session,
        MemberCreate(name="Alex", email="alex@example.com", phone="123"),
    )
    book = Book(
        title="Refactoring",
        author="Martin Fowler",
        isbn="9780201485677",
        total_copies=2,
        available_copies=2,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)

    loan = loan_service.borrow_book(db_session, BorrowRequest(member_id=member.id, book_id=book.id))
    result = loan_service.return_book(db_session, loan.id)

    db_session.refresh(book)
    assert result.loan_id == loan.id
    assert result.returned_at is not None
    assert book.available_copies == 2
