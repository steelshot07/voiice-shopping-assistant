def register_and_login(client, email: str):
    password = "password123"

    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code in (201, 409)

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def test_search_history_requires_authentication(client):
    response = client.get("/history/search")

    assert response.status_code == 401


def test_purchase_history_requires_authentication(client):
    response = client.get("/history/purchases")

    assert response.status_code == 401


def test_search_history(client):
    token = register_and_login(
        client,
        "history_search@example.com",
    )

    response = client.get(
        "/products",
        params={"q": "milk"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    history_response = client.get(
        "/history/search",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert isinstance(history, list)
    assert len(history) >= 1

    assert history[0]["query"] == "milk"


def test_search_history_pagination(client):
    token = register_and_login(
        client,
        "history_pagination@example.com",
    )

    for query in ["milk", "rice", "bread"]:
        response = client.get(
            "/products",
            params={"q": query},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    response = client.get(
        "/history/search",
        params={
            "limit": 2,
            "offset": 0,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    history = response.json()

    assert len(history) <= 2


def test_purchase_history_empty_initially(client):
    token = register_and_login(
        client,
        "purchase_history_empty@example.com",
    )

    response = client.get(
        "/history/purchases",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
