from httpx import AsyncClient

API_PREFIX = "/api/v1/auth"


class TestRegister:
    async def test_register_success(self, client: AsyncClient, user_data: dict) -> None:
        resp = await client.post(f"{API_PREFIX}/register", json=user_data)
        assert resp.status_code == 201
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_register_duplicate_email(
        self, client: AsyncClient, user_data: dict, registered_user: object
    ) -> None:
        resp = await client.post(f"{API_PREFIX}/register", json=user_data)
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{API_PREFIX}/register",
            json={"email": "not-an-email", "password": "password123", "full_name": "Test"},
        )
        assert resp.status_code == 422

    async def test_register_short_password(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{API_PREFIX}/register",
            json={"email": "a@b.com", "password": "short", "full_name": "Test"},
        )
        assert resp.status_code == 422


class TestLogin:
    async def test_login_success(
        self, client: AsyncClient, user_data: dict, registered_user: object
    ) -> None:
        resp = await client.post(
            f"{API_PREFIX}/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_wrong_password(
        self, client: AsyncClient, user_data: dict, registered_user: object
    ) -> None:
        resp = await client.post(
            f"{API_PREFIX}/token",
            data={"username": user_data["email"], "password": "wrongpass"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{API_PREFIX}/token",
            data={"username": "nobody@example.com", "password": "password123"},
        )
        assert resp.status_code == 401


class TestRefresh:
    async def test_refresh_success(
        self, client: AsyncClient, user_data: dict, registered_user: object
    ) -> None:
        login_resp = await client.post(
            f"{API_PREFIX}/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        refresh_token = login_resp.json()["refresh_token"]

        resp = await client.post(
            f"{API_PREFIX}/refresh", json={"refresh_token": refresh_token}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body

    async def test_refresh_invalid_token(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{API_PREFIX}/refresh", json={"refresh_token": "invalid-token"}
        )
        assert resp.status_code == 401

    async def test_refresh_with_access_token(
        self, client: AsyncClient, user_data: dict, registered_user: object
    ) -> None:
        login_resp = await client.post(
            f"{API_PREFIX}/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        access_token = login_resp.json()["access_token"]

        resp = await client.post(
            f"{API_PREFIX}/refresh", json={"refresh_token": access_token}
        )
        assert resp.status_code == 401
