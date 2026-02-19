def test_create_member_returns_201(client):
    response = client.post(
        '/members',
        json={'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '1234567890'},
    )

    assert response.status_code == 201
    assert response.json()['email'] == 'jane@example.com'


def test_create_member_duplicate_email_returns_409(client):
    payload = {'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '1234567890'}
    client.post('/members', json=payload)

    response = client.post('/members', json=payload)

    assert response.status_code == 409


def test_update_member_returns_404_for_missing_member(client):
    response = client.put('/members/999', json={'name': 'Updated'})

    assert response.status_code == 404


def test_borrowed_books_endpoint_returns_empty_list_for_member_with_no_loans(client):
    create_response = client.post(
        '/members',
        json={'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '1234567890'},
    )
    member_id = create_response.json()['id']

    response = client.get(f'/members/{member_id}/borrowed-books')

    assert response.status_code == 200
    assert response.json() == []


def test_list_members_supports_offset_and_limit(client):
    client.post('/members', json={'name': 'A', 'email': 'a@example.com', 'phone': '1'})
    client.post('/members', json={'name': 'B', 'email': 'b@example.com', 'phone': '2'})
    client.post('/members', json={'name': 'C', 'email': 'c@example.com', 'phone': '3'})

    response = client.get('/members?offset=1&limit=1')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'B'


def test_member_borrowed_books_supports_offset_and_limit(client):
    member = client.post(
        '/members',
        json={'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '1234567890'},
    ).json()
    book1 = client.post(
        '/books',
        json={'title': 'Book 1', 'author': 'Author', 'isbn': '9780132350884', 'total_copies': 1},
    ).json()
    book2 = client.post(
        '/books',
        json={'title': 'Book 2', 'author': 'Author', 'isbn': '9780132350885', 'total_copies': 1},
    ).json()

    client.post('/loans/borrow', json={'member_id': member['id'], 'book_id': book1['id']})
    client.post('/loans/borrow', json={'member_id': member['id'], 'book_id': book2['id']})

    response = client.get(f"/members/{member['id']}/borrowed-books?offset=0&limit=1")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
