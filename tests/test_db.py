import os
import uuid
import mysql.connector
import pytest


def get_test_db_config():
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", 3306)),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", "password"),
        "database": os.environ.get("MYSQL_DATABASE", "devops_test_db"),
    }


def can_connect_to_db():
    try:
        cfg = get_test_db_config()
        conn = mysql.connector.connect(**cfg)
        conn.close()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def real_db_available():
    if not can_connect_to_db():
        pytest.skip("Real MySQL test database not available")
    return get_test_db_config()


@pytest.fixture
def real_db_connection(real_db_available):
    conn = mysql.connector.connect(**real_db_available)
    yield conn
    conn.close()


def test_real_database_insert_and_select(real_db_connection):
    cursor = real_db_connection.cursor(dictionary=True)
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "name VARCHAR(100) NOT NULL, "
        "email VARCHAR(255) NOT NULL UNIQUE, "
        "password VARCHAR(255) NOT NULL, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )
    real_db_connection.commit()

    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        ("DB Test User", test_email, "secret"),
    )
    real_db_connection.commit()

    cursor.execute(
        "SELECT id, name, email FROM users WHERE email = %s",
        (test_email,),
    )
    row = cursor.fetchone()

    assert row is not None
    assert row["email"] == test_email
    assert row["name"] == "DB Test User"

    cursor.execute("DELETE FROM users WHERE email = %s", (test_email,))
    real_db_connection.commit()
    cursor.close()
