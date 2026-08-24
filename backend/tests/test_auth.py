from unittest.mock import MagicMock, patch

from app.models.user import User
from app.routers.auth import login, register
from app.schemas.auth import UserLogin, UserRegister


def test_register_creates_user():
    db = MagicMock()

    # No existing user.
    db.scalar.return_value = None

    user_data = UserRegister(
        email="test@example.com",
        password="password123",
    )

    with patch(
        "app.routers.auth.hash_password",
        return_value="hashed_password",
    ):
        result = register(user_data=user_data, db=db)

    assert isinstance(result, User)
    assert result.email == "test@example.com"
    assert result.password_hash == "hashed_password"

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_register_rejects_duplicate_user():
    db = MagicMock()

    existing_user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed_password",
    )

    db.scalar.return_value = existing_user

    user_data = UserRegister(
        email="test@example.com",
        password="password123",
    )

    from fastapi import HTTPException

    try:
        register(user_data=user_data, db=db)
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 409
        assert exc.detail == "User already exists"


def test_login_returns_access_token():
    db = MagicMock()

    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed_password",
    )

    db.scalar.return_value = user

    user_data = UserLogin(
        email="test@example.com",
        password="password123",
    )

    with patch(
        "app.routers.auth.verify_password",
        return_value=True,
    ), patch(
        "app.routers.auth.create_access_token",
        return_value="test-token",
    ):
        result = login(user_data=user_data, db=db)

    assert result.access_token == "test-token"
    assert result.token_type == "bearer"


def test_login_rejects_invalid_password():
    db = MagicMock()

    user = User(
        id=1,
        email="test@example.com",
        password_hash="hashed_password",
    )

    db.scalar.return_value = user

    user_data = UserLogin(
        email="test@example.com",
        password="wrongpassword",
    )

    from fastapi import HTTPException

    with patch(
        "app.routers.auth.verify_password",
        return_value=False,
    ):
        try:
            login(user_data=user_data, db=db)
            assert False, "Expected HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 401
            assert exc.detail == "Invalid email or password"
