from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Book, Loan, Member
from ..schemas import BorrowRequest, ReturnResponse


def borrow_book(db: Session, payload: BorrowRequest) -> Loan:
    member = db.query(Member).filter(Member.id == payload.member_id, Member.active.is_(True)).first()
    if not member:
        raise HTTPException(status_code=404, detail="Active member not found")

    book = db.query(Book).filter(Book.id == payload.book_id, Book.active.is_(True)).first()
    if not book:
        raise HTTPException(status_code=404, detail="Active book not found")

    if book.available_copies <= 0:
        raise HTTPException(status_code=409, detail="No available copies for this book")

    already_open = (
        db.query(Loan)
        .filter(
            Loan.member_id == payload.member_id,
            Loan.book_id == payload.book_id,
            Loan.returned_at.is_(None),
        )
        .first()
    )
    if already_open:
        raise HTTPException(status_code=409, detail="Member already has this book checked out")

    due_date = payload.due_date or (date.today() + timedelta(days=settings.default_loan_days))

    loan = Loan(member_id=payload.member_id, book_id=payload.book_id, due_date=due_date)
    book.available_copies -= 1

    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_book(db: Session, loan_id: int) -> ReturnResponse:
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.returned_at is not None:
        raise HTTPException(status_code=409, detail="Loan is already closed")

    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found for this loan")

    loan.returned_at = datetime.now(timezone.utc)
    book.available_copies += 1

    db.commit()
    return ReturnResponse(loan_id=loan.id, returned_at=loan.returned_at)


def list_loans(db: Session, member_id: Optional[int] = None, active_only: bool = False) -> list[Loan]:
    query = db.query(Loan)
    if member_id is not None:
        query = query.filter(Loan.member_id == member_id)
    if active_only:
        query = query.filter(Loan.returned_at.is_(None))
    return query.order_by(Loan.borrowed_at.desc()).all()
