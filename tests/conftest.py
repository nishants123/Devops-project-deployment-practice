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


@pytest.fixture
def fake_connection_factory():
    def make_fake_connection(rows=None):
        return FakeConnection(rows)
    return make_fake_connection
