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


def test_create_book_admin(client, db):
    token = create_admin(client, db)

    response = client.post(
        "/books/",
        json={
            "title": "book one",
            "author": "author one",
            "isbn": "12345",
            "total_copies": 5
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert response.json()["title"] == "book one"


def test_create_book_member_forbidden(client):
    token = create_member(client)

    response = client.post(
        "/books/",
        json={
            "title": "book two",
            "author": "author two",
            "isbn": "67890",
            "total_copies": 3
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_get_books(client):
    response = client.get("/books/")
    assert response.status_code == 200


def test_update_book(client, db):
    token = create_admin(client, db)

    create = client.post(
        "/books/",
        json={
            "title": "update test",
            "author": "author",
            "isbn": "99999",
            "total_copies": 4
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    book_id = create.json()["id"]

    update = client.put(
        f"/books/{book_id}",
        json={"title": "updated"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert update.status_code == 200
    assert update.json()["title"] == "updated"


def test_delete_book(client, db):
    token = create_admin(client, db)

    create = client.post(
        "/books/",
        json={
            "title": "delete test",
            "author": "author",
            "isbn": "55555",
            "total_copies": 2
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    book_id = create.json()["id"]

    delete = client.delete(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert delete.status_code == 200