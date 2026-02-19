def test_create_book_returns_201(client):
    response = client.post(
        '/books',
        json={
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'total_copies': 2,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body['title'] == 'Clean Code'
    assert body['available_copies'] == 2


def test_create_book_duplicate_isbn_returns_409(client):
    payload = {
        'title': 'Clean Code',
        'author': 'Robert C. Martin',
        'isbn': '9780132350884',
        'total_copies': 2,
    }
    client.post('/books', json=payload)

    response = client.post('/books', json=payload)

    assert response.status_code == 409


def test_update_book_returns_404_for_missing_book(client):
    response = client.put('/books/999', json={'title': 'Updated'})

    assert response.status_code == 404


def test_list_books_returns_created_book(client):
    client.post(
        '/books',
        json={
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'total_copies': 2,
        },
    )

    response = client.get('/books')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['isbn'] == '9780132350884'
