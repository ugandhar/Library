from datetime import date, timedelta


def test_borrow_and_return_flow(client):
    book = client.post(
        '/books',
        json={
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'total_copies': 1,
        },
    ).json()
    member = client.post(
        '/members',
        json={'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '1234567890'},
    ).json()

    borrow_response = client.post(
        '/loans/borrow',
        json={'member_id': member['id'], 'book_id': book['id']},
    )

    assert borrow_response.status_code == 201
    loan_id = borrow_response.json()['id']

    return_response = client.post(f'/loans/{loan_id}/return')

    assert return_response.status_code == 200
    assert return_response.json()['loan_id'] == loan_id


def test_borrow_book_when_unavailable_returns_409(client):
    book = client.post(
        '/books',
        json={
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'total_copies': 1,
        },
    ).json()
    member1 = client.post(
        '/members',
        json={'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '1234567890'},
    ).json()
    member2 = client.post(
        '/members',
        json={'name': 'John Doe', 'email': 'john@example.com', 'phone': '1234567890'},
    ).json()

    client.post('/loans/borrow', json={'member_id': member1['id'], 'book_id': book['id']})
    response = client.post('/loans/borrow', json={'member_id': member2['id'], 'book_id': book['id']})

    assert response.status_code == 409


def test_overdue_loans_endpoint_returns_only_past_due_active_loans(client):
    book = client.post(
        '/books',
        json={
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '9780132350884',
            'total_copies': 2,
        },
    ).json()
    member = client.post(
        '/members',
        json={'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '1234567890'},
    ).json()

    overdue_due_date = (date.today() - timedelta(days=1)).isoformat()
    client.post(
        '/loans/borrow',
        json={'member_id': member['id'], 'book_id': book['id'], 'due_date': overdue_due_date},
    )

    response = client.get('/loans/overdue')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['member_name'] == 'Jane Doe'
    assert data[0]['book_title'] == 'Clean Code'
