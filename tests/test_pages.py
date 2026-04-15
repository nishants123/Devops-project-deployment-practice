def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Simple Python Login App" in response.data


def test_register_page_shows_form(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create Account" in response.data


def test_login_page_shows_form(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign In" in response.data
