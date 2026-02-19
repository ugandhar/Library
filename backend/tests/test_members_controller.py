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
