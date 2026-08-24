def register_and_login(client):
    email = "products_test@example.com"
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


def auth_headers(client):
    token = register_and_login(client)

    return {
        "Authorization": f"Bearer {token}",
    }


def test_get_products_requires_authentication(client):
    response = client.get("/products")

    assert response.status_code == 401


def test_get_products(client):
    response = client.get(
        "/products",
        headers=auth_headers(client),
    )

    assert response.status_code == 200

    products = response.json()

    assert isinstance(products, list)
    assert len(products) >= 1

    product = products[0]

    assert "id" in product
    assert "name" in product
    assert "brand_id" in product
    assert "category_id" in product
    assert "price" in product
    assert "currency" in product
    assert "available" in product


def test_search_products(client):
    response = client.get(
        "/products",
        params={"q": "milk"},
        headers=auth_headers(client),
    )

    assert response.status_code == 200

    products = response.json()

    assert len(products) >= 1

    names = [product["name"].lower() for product in products]

    assert any("milk" in name for name in names)


def test_product_price_filter(client):
    response = client.get(
        "/products",
        params={
            "min_price": 50,
            "max_price": 110,
        },
        headers=auth_headers(client),
    )

    assert response.status_code == 200

    products = response.json()

    for product in products:
        price = float(product["price"])

        assert 50 <= price <= 110


def test_invalid_price_range(client):
    response = client.get(
        "/products",
        params={
            "min_price": 200,
            "max_price": 100,
        },
        headers=auth_headers(client),
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Minimum price cannot exceed maximum price"


def test_get_product(client):
    list_response = client.get(
        "/products",
        headers=auth_headers(client),
    )

    assert list_response.status_code == 200

    products = list_response.json()

    assert len(products) >= 1

    product_id = products[0]["id"]

    response = client.get(
        f"/products/{product_id}",
        headers=auth_headers(client),
    )

    assert response.status_code == 200

    product = response.json()

    assert product["id"] == product_id


def test_get_nonexistent_product(client):
    response = client.get(
        "/products/999999",
        headers=auth_headers(client),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
