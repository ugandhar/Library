from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import Book, Loan, Member
from ..schemas import BorrowedBookView, MemberCreate, MemberUpdate


def create_member(db: Session, payload: MemberCreate) -> Member:
    existing = db.query(Member).filter(Member.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Member with this email already exists")

    member = Member(**payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def list_members(db: Session) -> list[Member]:
    return db.query(Member).order_by(Member.id.asc()).all()


def get_member_or_404(db: Session, member_id: int) -> Member:
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


def update_member(db: Session, member_id: int, payload: MemberUpdate) -> Member:
    member = get_member_or_404(db, member_id)

    if payload.email and payload.email != member.email:
        duplicate = db.query(Member).filter(Member.email == payload.email).first()
        if duplicate:
            raise HTTPException(status_code=409, detail="Member with this email already exists")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(member, field, value)

    db.commit()
    db.refresh(member)
    return member


def member_borrowed_books(db: Session, member_id: int, active_only: bool = True) -> list[BorrowedBookView]:
    get_member_or_404(db, member_id)

    query = db.query(Loan, Book).join(Book, Book.id == Loan.book_id).filter(Loan.member_id == member_id)
    if active_only:
        query = query.filter(Loan.returned_at.is_(None))

    rows = query.order_by(Loan.borrowed_at.desc()).all()
    today = date.today()

    response: list[BorrowedBookView] = []
    for loan, book in rows:
        response.append(
            BorrowedBookView(
                loan_id=loan.id,
                book_id=book.id,
                title=book.title,
                author=book.author,
                borrowed_at=loan.borrowed_at,
                due_date=loan.due_date,
                is_overdue=loan.returned_at is None and loan.due_date < today,
            )
        )
    return response
