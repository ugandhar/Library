from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import BorrowRequest, LoanListResponse, LoanResponse, ReturnResponse
from ..services import loan_service

router = APIRouter(tags=["loans"])


@router.post("/loans/borrow", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def borrow_book(payload: BorrowRequest, db: Session = Depends(get_db)):
    return loan_service.borrow_book(db, payload)


@router.post("/loans/{loan_id}/return", response_model=ReturnResponse)
def return_book(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.return_book(db, loan_id)


@router.get("/loans", response_model=list[LoanListResponse])
def list_loans(
    member_id: Optional[int] = Query(default=None),
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return loan_service.list_loans_with_details(db, member_id=member_id, active_only=active_only)


@router.get("/loans/overdue", response_model=list[LoanListResponse])
def list_overdue_loans(
    member_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    return loan_service.list_overdue_loans_with_details(db, member_id=member_id)
