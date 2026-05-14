from app.models.user import User


def create_admin(client, db):
    client.post("/auth/register", json={
        "username": "adminuser",
        "email": "admin@test.com",
        "password": "123456"
    })

    user = db.query(User).filter_by(username="adminuser").first()
    user.role = "admin"
    db.commit()

    login = client.post("/auth/login", json={
        "username": "adminuser",
        "password": "123456"
    })

    return login.json()["access_token"]


def create_member(client):
    client.post("/auth/register", json={
        "username": "memberuser",
        "email": "member@test.com",
        "password": "123456"
    })

    login = client.post("/auth/login", json={
        "username": "memberuser",
        "password": "123456"
    })

    return login.json()["access_token"]


def create_book_as_admin(client, db):
    token = create_admin(client, db)

    response = client.post(
        "/books/",
        json={
            "title": "borrow book",
            "author": "author",
            "isbn": "borrowisbn",
            "total_copies": 2
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    return response.json()["id"]


def test_borrow_success(client, db):
    book_id = create_book_as_admin(client, db)
    token = create_member(client)

    response = client.post(
        f"/borrow/{book_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["is_returned"] is False


def test_borrow_limit(client, db):
    token = create_admin(client, db)
    member_token = create_member(client)

    book_ids = []
    for i in range(3):
        resp = client.post(
            "/books/",
            json={
                "title": f"limit book {i}",
                "author": "author",
                "isbn": f"limit_isbn_{i}",
                "total_copies": 5
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 201
        book_ids.append(resp.json()["id"])

    for book_id in book_ids:
        resp = client.post(
            f"/borrow/{book_id}",
            headers={"Authorization": f"Bearer {member_token}"}
        )
        assert resp.status_code == 200

    response = client.post(
        f"/borrow/{book_ids[0]}",
        headers={"Authorization": f"Bearer {member_token}"}
    )

    assert response.status_code == 400
    assert "borrow limit" in response.json()["detail"].lower()


def test_return_book(client, db):
    book_id = create_book_as_admin(client, db)
    token = create_member(client)

    client.post(
        f"/borrow/{book_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.post(
        f"/borrow/return/{book_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["is_returned"] is True