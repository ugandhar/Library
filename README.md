# Neighborhood Library Service

This repository implements a full take-home solution for a neighborhood library:

- **Backend:** Python + FastAPI REST service
- **Database:** PostgreSQL (with SQL schema script + Docker Compose)
- **Service Contract:** Protobuf service/messages (`proto/library_service.proto`)
- **Frontend:** moved to a separate repository (`library-frontend`, see section 6)

## 1) Project Structure

```text
backend/
  app/
    main.py         # FastAPI app + REST endpoints
    models.py       # SQLAlchemy ORM models
    schemas.py      # Pydantic request/response models
    database.py     # DB session + connection settings
  requirements.txt

db/schema.sql       # PostgreSQL DDL
proto/library_service.proto

docker-compose.yml  # PostgreSQL service
.env.example
```

## 2) Database Schema (PostgreSQL)

The schema uses three normalized tables:

- `books`
  - core metadata (`title`, `author`, `isbn`, `published_year`)
  - inventory counters (`total_copies`, `available_copies`)
- `members`
  - member profile + status (`is_active`)
- `loans`
  - links one member to one borrowed book
  - `borrowed_at`, optional `due_date`, optional `returned_at`

Foreign keys:

- `loans.member_id -> members.id`
- `loans.book_id -> books.id`

Indexes are included for common lookup/filter paths.

## 3) REST API

Base URL (default): `http://localhost:8000`

### Health
- `GET /health`

### Books
- `POST /books` – create book
- `GET /books` – list books
- `PUT /books/{book_id}` – update book

### Members
- `POST /members` – create member
- `GET /members` – list members
- `PUT /members/{member_id}` – update member

### Lending
- `POST /loans` – borrow a book
- `POST /returns` – return a borrowed book (by loan id)
- `GET /loans?member_id=&active_only=` – query loans

### Example Requests

Create a member:
```bash
curl -X POST http://localhost:8000/members \
  -H "Content-Type: application/json" \
  -d '{"name":"Alice Reader","email":"alice@example.com"}'
```

Create a book:
```bash
curl -X POST http://localhost:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"Dune","author":"Frank Herbert","total_copies":3}'
```

Borrow a book:
```bash
curl -X POST http://localhost:8000/loans \
  -H "Content-Type: application/json" \
  -d '{"member_id":1,"book_id":1}'
```

Return a book:
```bash
curl -X POST http://localhost:8000/returns \
  -H "Content-Type: application/json" \
  -d '{"loan_id":1}'
```

## 4) Protobuf Interface

A `.proto` service contract is provided at:

- `proto/library_service.proto`

It defines `Book`, `Member`, `Loan`, and RPC operations matching core workflows.

## 5) Setup Instructions

## Prerequisites

- Python 3.11+
- Docker + Docker Compose

### Step A: Start PostgreSQL

```bash
docker compose up -d postgres
```

This initializes the database using `db/schema.sql`.

### Step B: Run Backend API

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

## 6) Frontend Repository

The frontend has been moved out of this repository and should live in its own Git repository (recommended name: `library-frontend`).

Expected integration contract for the frontend repository:
- consume this backend API base URL (default `http://localhost:8000`)
- implement book/member CRUD interactions and lending flows via REST endpoints listed above

## 7) Validation & Error Handling Included

- Prevent borrowing when no copies are available.
- Prevent returning an already-returned loan.
- Validate member is active before borrow.
- Prevent lowering `total_copies` below currently checked out count.

## 8) Notes

- `backend/app/main.py` auto-creates ORM tables at startup (`Base.metadata.create_all`) for convenience.
- `db/schema.sql` remains the explicit PostgreSQL schema source for reproducible setup.
