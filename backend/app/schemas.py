from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    isbn: str | None = Field(default=None, max_length=32)
    published_year: int | None = Field(default=None, ge=0)
    total_copies: int = Field(default=1, ge=1)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    isbn: str | None = Field(default=None, max_length=32)
    published_year: int | None = Field(default=None, ge=0)
    total_copies: int | None = Field(default=None, ge=1)


class BookOut(BookBase):
    id: int
    available_copies: int
    created_at: datetime

    class Config:
        from_attributes = True


class MemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    is_active: bool = True


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = None
    is_active: bool | None = None


class MemberOut(MemberBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    due_date: date | None = None


class LoanOut(BaseModel):
    id: int
    member_id: int
    book_id: int
    borrowed_at: datetime
    due_date: date | None = None
    returned_at: datetime | None = None

    class Config:
        from_attributes = True


class ReturnBookRequest(BaseModel):
    loan_id: int
