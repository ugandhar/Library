#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "Creating book"
BOOK=$(curl -s -X POST "$BASE_URL/books" \
  -H 'Content-Type: application/json' \
  -d '{"title":"Domain-Driven Design","author":"Eric Evans","isbn":"9780321125217","total_copies":3}')
BOOK_ID=$(echo "$BOOK" | sed -E 's/.*"id":([0-9]+).*/\1/')

echo "Creating member"
MEMBER=$(curl -s -X POST "$BASE_URL/members" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alex Smith","email":"alex@example.com","phone":"1234567890"}')
MEMBER_ID=$(echo "$MEMBER" | sed -E 's/.*"id":([0-9]+).*/\1/')

echo "Borrowing book"
LOAN=$(curl -s -X POST "$BASE_URL/loans/borrow" \
  -H 'Content-Type: application/json' \
  -d "{\"member_id\":$MEMBER_ID,\"book_id\":$BOOK_ID}")

echo "$LOAN"
echo "Listing member borrowed books"
curl -s "$BASE_URL/members/$MEMBER_ID/borrowed-books" | cat
