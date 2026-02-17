import pytest
from fastapi import HTTPException

from app.schemas import MemberCreate, MemberUpdate
from app.services import member_service


def test_create_member_success(db_session):
    payload = MemberCreate(name="Jane Doe", email="jane@example.com", phone="123")

    member = member_service.create_member(db_session, payload)

    assert member.id is not None
    assert member.email == "jane@example.com"


def test_create_member_duplicate_email_raises_409(db_session):
    payload = MemberCreate(name="Jane Doe", email="jane@example.com", phone="123")
    member_service.create_member(db_session, payload)

    with pytest.raises(HTTPException) as exc:
        member_service.create_member(db_session, payload)

    assert exc.value.status_code == 409


def test_update_member_fields(db_session):
    member = member_service.create_member(
        db_session,
        MemberCreate(name="Jane Doe", email="jane@example.com", phone="123"),
    )

    updated = member_service.update_member(db_session, member.id, MemberUpdate(name="Jane Smith"))

    assert updated.name == "Jane Smith"
