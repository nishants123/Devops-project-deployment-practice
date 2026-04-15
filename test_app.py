import pytest
from app import app


class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or {}
        self.last_query = None
        self.last_params = None

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params
        if "SELECT id FROM users WHERE email" in query:
            self._rows = self.rows.get("exists", [])
        elif "SELECT id, name, email FROM users WHERE email" in query:
            self._rows = self.rows.get("login", [])
        else:
            self._rows = []

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def close(self):
        pass


class FakeConnection:
    def __init__(self, rows=None):
        self._cursor = FakeCursor(rows)
        self.committed = False
        self.closed = False

    def cursor(self, dictionary=False):
        return self._cursor

    def commit(self):
        self.committed = True

    def is_connected(self):
        return not self.closed

    def close(self):
        self.closed = True


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Simple Python Login App" in response.data


def test_register_page_shows_form(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create Account" in response.data


def test_register_post_creates_user(monkeypatch, client):
    fake_conn = FakeConnection(rows={"exists": []})

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


def test_login_post_invalid_credentials(monkeypatch, client):
    fake_conn = FakeConnection(rows={"login": []})

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


def test_login_post_success_redirects(monkeypatch, client):
    fake_conn = FakeConnection(rows={"login": [{"id": 1, "name": "Test User", "email": "test@example.com"}]})

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
