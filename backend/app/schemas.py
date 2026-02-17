from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    isbn: str = Field(min_length=10, max_length=32)
    publication_year: int | None = Field(default=None, ge=0, le=9999)
    total_copies: int = Field(default=1, ge=1)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    isbn: str | None = Field(default=None, min_length=10, max_length=32)
    publication_year: int | None = Field(default=None, ge=0, le=9999)
    total_copies: int | None = Field(default=None, ge=1)
    active: bool | None = None


class BookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str
    isbn: str
    publication_year: int | None
    total_copies: int
    available_copies: int
    active: bool


class MemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=255)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    address: str | None = Field(default=None, max_length=255)
    active: bool | None = None


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: str | None
    address: str | None
    active: bool


class BorrowRequest(BaseModel):
    member_id: int
    book_id: int
    due_date: date | None = None


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
    returned_at: datetime | None


class BorrowedBookView(BaseModel):
    loan_id: int
    book_id: int
    title: str
    author: str
    borrowed_at: datetime
    due_date: date
    is_overdue: bool
