from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import BorrowedBookView, MemberCreate, MemberResponse, MemberUpdate
from ..services import member_service

router = APIRouter(tags=["members"])


@router.post("/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    return member_service.create_member(db, payload)


@router.get("/members", response_model=list[MemberResponse])
def list_members(db: Session = Depends(get_db)):
    return member_service.list_members(db)


@router.get("/members/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return member_service.get_member_or_404(db, member_id)


@router.put("/members/{member_id}", response_model=MemberResponse)
def update_member(member_id: int, payload: MemberUpdate, db: Session = Depends(get_db)):
    return member_service.update_member(db, member_id, payload)


@router.get("/members/{member_id}/borrowed-books", response_model=list[BorrowedBookView])
def member_borrowed_books(
    member_id: int,
    active_only: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    return member_service.member_borrowed_books(db, member_id, active_only=active_only)
