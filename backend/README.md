# Backend - Neighborhood Library Service

Python + FastAPI + PostgreSQL backend for library operations.

## Data Model

- `books`: catalog records and available copy counts
- `members`: library member profile/contact info
- `loans`: borrow/return transaction records

## Quick Start

1. Start PostgreSQL:

```bash
cd backend
docker compose up -d db
```

2. Configure env:

```bash
cp .env.example .env
```

3. Create virtual env and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Run API server:

```bash
uvicorn app.main:app --reload
```

5. Open docs:

- Swagger UI: `http://127.0.0.1:8000/docs`

## Core Endpoints

- `POST /books` - create book
- `PUT /books/{book_id}` - update book
- `POST /members` - create member
- `PUT /members/{member_id}` - update member
- `POST /loans/borrow` - borrow book
- `POST /loans/{loan_id}/return` - return book
- `GET /members/{member_id}/borrowed-books` - list member borrowed books
- `GET /loans` - list loans with filters

## Sample API Calls

```bash
curl -X POST http://127.0.0.1:8000/books \
  -H 'Content-Type: application/json' \
  -d '{"title":"Clean Code","author":"Robert C. Martin","isbn":"9780132350884","total_copies":2}'

curl -X POST http://127.0.0.1:8000/members \
  -H 'Content-Type: application/json' \
  -d '{"name":"Jane Doe","email":"jane@example.com","phone":"1234567890"}'

curl -X POST http://127.0.0.1:8000/loans/borrow \
  -H 'Content-Type: application/json' \
  -d '{"member_id":1,"book_id":1}'

curl -X POST http://127.0.0.1:8000/loans/1/return
```
