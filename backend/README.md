# Backend - Neighborhood Library Service

Python + FastAPI + PostgreSQL backend for library operations.

## Data Model

- `books`: catalog records and available copy counts
- `members`: library member profile/contact info
- `loans`: borrow/return transaction records

## Run Backend Server (this repo)

From the backend folder in this repo:

```bash
cd /Users/swethareddy/projects/Library/backend
```

1. Start PostgreSQL:

```bash
docker compose up -d db
```

2. Configure env:

```bash
cp .env.example .env
```

3. Install dependencies:

```bash
pip3 install -r requirements.txt
```

4. Start the API server:

```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API base: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## API Documentation

Start backend server:

```bash
cd /Users/swethareddy/projects/Library/backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open generated API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Run Backend Tests

From backend repo folder:

```bash
cd /Users/swethareddy/projects/Library/backend
python3 -m pytest -q
```

## Core Endpoints

- `POST /books` - create book
- `GET /books` - list books
- `GET /books/{book_id}` - get one book
- `PUT /books/{book_id}` - update book
- `POST /members` - create member
- `GET /members` - list members
- `GET /members/{member_id}` - get one member
- `PUT /members/{member_id}` - update member
- `POST /loans/borrow` - borrow book
- `POST /loans/{loan_id}/return` - return book
- `GET /members/{member_id}/borrowed-books` - list member borrowed books
- `GET /loans` - list loans with filters
- `GET /loans/overdue` - list active overdue loans (optional `member_id` filter)

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

curl http://127.0.0.1:8000/loans/overdue
```

## Demo Script

Run an end-to-end demo (create book/member, borrow, list borrowed books):

```bash
./scripts/demo.sh
```
