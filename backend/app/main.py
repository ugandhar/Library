from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Neighborhood Library Service", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/books", response_model=schemas.BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: schemas.BookCreate, db: Session = Depends(get_db)):
    book = models.Book(
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        published_year=payload.published_year,
        total_copies=payload.total_copies,
        available_copies=payload.total_copies,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.get("/books", response_model=list[schemas.BookOut])
def list_books(db: Session = Depends(get_db)):
    return db.scalars(select(models.Book).order_by(models.Book.title)).all()


@app.put("/books/{book_id}", response_model=schemas.BookOut)
def update_book(book_id: int, payload: schemas.BookUpdate, db: Session = Depends(get_db)):
    book = db.get(models.Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    checked_out = book.total_copies - book.available_copies
    fields = payload.model_dump(exclude_unset=True)
    for key, value in fields.items():
        setattr(book, key, value)

    if "total_copies" in fields:
        if book.total_copies < checked_out:
            raise HTTPException(status_code=400, detail="total_copies cannot be less than checked-out copies")
        book.available_copies = book.total_copies - checked_out

    db.commit()
    db.refresh(book)
    return book


@app.post("/members", response_model=schemas.MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(payload: schemas.MemberCreate, db: Session = Depends(get_db)):
    member = models.Member(**payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@app.get("/members", response_model=list[schemas.MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.scalars(select(models.Member).order_by(models.Member.name)).all()


@app.put("/members/{member_id}", response_model=schemas.MemberOut)
def update_member(member_id: int, payload: schemas.MemberUpdate, db: Session = Depends(get_db)):
    member = db.get(models.Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(member, key, value)

    db.commit()
    db.refresh(member)
    return member


@app.post("/loans", response_model=schemas.LoanOut, status_code=status.HTTP_201_CREATED)
def borrow_book(payload: schemas.LoanCreate, db: Session = Depends(get_db)):
    member = db.get(models.Member, payload.member_id)
    if not member or not member.is_active:
        raise HTTPException(status_code=400, detail="Member is invalid or inactive")

    book = db.get(models.Book, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No copies available")

    loan = models.Loan(member_id=payload.member_id, book_id=payload.book_id, due_date=payload.due_date)
    book.available_copies -= 1

    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@app.post("/returns", response_model=schemas.LoanOut)
def return_book(payload: schemas.ReturnBookRequest, db: Session = Depends(get_db)):
    loan = db.get(models.Loan, payload.loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.returned_at is not None:
        raise HTTPException(status_code=400, detail="Loan already returned")

    loan.returned_at = datetime.utcnow()
    book = db.get(models.Book, loan.book_id)
    if book:
        book.available_copies += 1

    db.commit()
    db.refresh(loan)
    return loan


@app.get("/loans", response_model=list[schemas.LoanOut])
def list_loans(
    member_id: int | None = Query(default=None),
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    query = select(models.Loan)

    filters = []
    if member_id is not None:
        filters.append(models.Loan.member_id == member_id)
    if active_only:
        filters.append(models.Loan.returned_at.is_(None))

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(models.Loan.borrowed_at.desc())
    return db.scalars(query).all()
