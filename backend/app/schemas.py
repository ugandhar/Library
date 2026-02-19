from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    isbn: str = Field(min_length=10, max_length=32)
    publication_year: Optional[int] = Field(default=None, ge=0, le=9999)
    total_copies: int = Field(default=1, ge=1)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    author: Optional[str] = Field(default=None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(default=None, min_length=10, max_length=32)
    publication_year: Optional[int] = Field(default=None, ge=0, le=9999)
    total_copies: Optional[int] = Field(default=None, ge=1)
    active: Optional[bool] = None


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    isbn: str
    publication_year: Optional[int]
    total_copies: int
    available_copies: int
    active: bool


class MemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=32)
    address: Optional[str] = Field(default=None, max_length=255)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=32)
    address: Optional[str] = Field(default=None, max_length=255)
    active: Optional[bool] = None


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    address: Optional[str]
    active: bool


class BorrowRequest(BaseModel):
    member_id: int
    book_id: int
    due_date: Optional[date] = None


class ReturnResponse(BaseModel):
    loan_id: int
    returned_at: datetime


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    book_id: int
    borrowed_at: datetime
    due_date: date
    returned_at: Optional[datetime]


class LoanListResponse(LoanResponse):
    member_name: str
    book_title: str


class BorrowedBookView(BaseModel):
    loan_id: int
    book_id: int
    title: str
    author: str
    borrowed_at: datetime
    due_date: date
    is_overdue: bool
