import pytest


def test_register_post_creates_user(monkeypatch, client, fake_connection_factory):
    fake_conn = fake_connection_factory(rows={"exists": []})

    def fake_get_db_connection():
        return fake_conn

    monkeypatch.setattr("app.get_db_connection", fake_get_db_connection)

    response = client.post(
        "/register",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "password": "secret",
            "confirm": "secret",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert fake_conn.committed is True
    assert fake_conn._cursor.last_query.startswith("INSERT INTO users")
    assert fake_conn._cursor.last_params == ("Test User", "test@example.com", "secret")


def test_login_post_invalid_credentials(monkeypatch, client, fake_connection_factory):
    fake_conn = fake_connection_factory(rows={"login": []})

    def fake_get_db_connection():
        return fake_conn

    monkeypatch.setattr("app.get_db_connection", fake_get_db_connection)

    response = client.post(
        "/login",
        data={"email": "wrong@example.com", "password": "badpass"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_login_post_success_redirects(monkeypatch, client, fake_connection_factory):
    fake_conn = fake_connection_factory(rows={"login": [{"id": 1, "name": "Test User", "email": "test@example.com"}]})

    def fake_get_db_connection():
        return fake_conn

    monkeypatch.setattr("app.get_db_connection", fake_get_db_connection)

    response = client.post(
        "/login",
        data={"email": "test@example.com", "password": "secret"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
