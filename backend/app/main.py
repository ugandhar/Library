from datetime import date, datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import Book, Loan, Member
from .schemas import (
    BookCreate,
    BookResponse,
    BookUpdate,
    BorrowRequest,
    BorrowedBookView,
    LoanResponse,
    MemberCreate,
    MemberResponse,
    MemberUpdate,
    ReturnResponse,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
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
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.get("/books", response_model=list[BookResponse])
def list_books(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.id.asc()).all()


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

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

    db.commit()
    db.refresh(book)
    return book


@app.post("/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    existing = db.query(Member).filter(Member.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Member with this email already exists")

    member = Member(**payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@app.get("/members", response_model=list[MemberResponse])
def list_members(db: Session = Depends(get_db)):
    return db.query(Member).order_by(Member.id.asc()).all()


@app.get("/members/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@app.put("/members/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

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


@app.post("/loans/borrow", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(payload: BorrowRequest, db: Session = Depends(get_db)):
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


@app.post("/loans/{loan_id}/return", response_model=ReturnResponse)
def return_book(loan_id: int, db: Session = Depends(get_db)):
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


@app.get("/members/{member_id}/borrowed-books", response_model=list[BorrowedBookView])
def member_borrowed_books(
    member_id: int,
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

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


@app.get("/loans", response_model=list[LoanResponse])
def list_loans(
    member_id: int | None = Query(default=None),
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    query = db.query(Loan)
    if member_id is not None:
        query = query.filter(Loan.member_id == member_id)
    if active_only:
        query = query.filter(Loan.returned_at.is_(None))
    return query.order_by(Loan.borrowed_at.desc()).all()
