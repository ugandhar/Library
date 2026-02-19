from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import BookCreate, BookResponse, BookUpdate
from ..services import book_service

router = APIRouter(tags=["books"])


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    return book_service.create_book(db, payload)


@router.get("/books", response_model=list[BookResponse])
def list_books(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return book_service.list_books(db, offset=offset, limit=limit)


@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    return book_service.get_book_or_404(db, book_id)


@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    return book_service.update_book(db, book_id, payload)
