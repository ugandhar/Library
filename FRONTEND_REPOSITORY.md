# Frontend Repository Split

The Next.js frontend has been intentionally removed from this repository.

Please host it in a separate repository (for example `library-frontend`) and configure it to call this backend's REST API.

## Required backend endpoints

- `GET /health`
- `POST /books`, `GET /books`, `PUT /books/{book_id}`
- `POST /members`, `GET /members`, `PUT /members/{member_id}`
- `POST /loans`, `POST /returns`, `GET /loans?member_id=&active_only=`

## Local integration

Set the frontend API base URL to `http://localhost:8000` when running locally.
