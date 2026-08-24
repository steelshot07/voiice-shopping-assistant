from decimal import Decimal


def register_and_login(client):
    email = "shopping_test@example.com"
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


def test_get_items_requires_authentication(client):
    response = client.get("/items")

    assert response.status_code == 401


def test_create_shopping_item(client):
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Clean up any leftover items from previous test runs so
    # the create endpoint doesn't merge into an existing item.
    existing = client.get("/items", headers=headers)

    for item in existing.json():
        client.delete(f"/items/{item['id']}", headers=headers)

    response = client.post(
        "/items",
        headers=headers,
        json={
            "product_id": 1,
            "quantity": 2,
            "unit": "liters",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["product_id"] == 1
    assert Decimal(str(data["quantity"])) == Decimal("2")
    assert data["unit"] == "liters"
    assert data["completed"] is False


def test_update_shopping_item(client):
    token = register_and_login(client)

    create_response = client.post(
        "/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": 1,
            "quantity": 1,
            "unit": "liter",
        },
    )

    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    response = client.patch(
        f"/items/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "quantity": 3,
            "unit": None,
            "completed": True,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(str(data["quantity"])) == Decimal("3")
    assert data["unit"] is None
    assert data["completed"] is True


def test_update_quantity_cannot_be_null(client):
    token = register_and_login(client)

    create_response = client.post(
        "/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": 1,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    response = client.patch(
        f"/items/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "quantity": None,
        },
    )

    assert response.status_code == 422


def test_delete_shopping_item(client):
    token = register_and_login(client)

    create_response = client.post(
        "/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": 1,
            "quantity": 1,
        },
    )

    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/items/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/items/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert get_response.status_code == 404


def test_completing_item_creates_purchase_history(client):
    token = register_and_login(client)

    create_response = client.post(
        "/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": 1,
            "quantity": 2,
            "unit": "liters",
        },
    )

    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    response = client.patch(
        f"/items/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "completed": True,
        },
    )

    assert response.status_code == 200

    history_response = client.get(
        "/history/purchases",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert history_response.status_code == 200

    history = history_response.json()

    matching = [
        record
        for record in history
        if record["product_id"] == 1
        and float(record["quantity"]) == 2
    ]

    assert len(matching) >= 1
    assert matching[0]["unit"] == "liters"


def test_completing_already_completed_item_does_not_duplicate_history(client):
    token = register_and_login(client)

    create_response = client.post(
        "/items",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "product_id": 1,
            "quantity": 1,
            "unit": "liter",
        },
    )

    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    first_patch = client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"completed": True},
    )

    assert first_patch.status_code == 200

    first_history = client.get(
        "/history/purchases",
        headers=headers,
    )

    assert first_history.status_code == 200

    first_records = first_history.json()

    first_count = len(
        [
            record
            for record in first_records
            if record["product_id"] == 1
            and float(record["quantity"]) == 1
        ]
    )

    second_patch = client.patch(
        f"/items/{item_id}",
        headers=headers,
        json={"completed": True},
    )

    assert second_patch.status_code == 200

    second_history = client.get(
        "/history/purchases",
        headers=headers,
    )

    assert second_history.status_code == 200

    second_records = second_history.json()

    second_count = len(
        [
            record
            for record in second_records
            if record["product_id"] == 1
            and float(record["quantity"]) == 1
        ]
    )

    assert second_count == first_count