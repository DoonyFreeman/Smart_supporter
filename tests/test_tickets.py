from httpx import AsyncClient

from tests.conftest import create_ticket_payload

API_PREFIX = "/api/v1/tickets"


class TestCreateTicket:
    async def test_create_ticket_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        payload = create_ticket_payload()
        resp = await client.post(API_PREFIX, json=payload, headers=auth_headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == payload["title"]
        assert body["status"] == "new"
        assert "id" in body

    async def test_create_ticket_unauthenticated(self, client: AsyncClient) -> None:
        payload = create_ticket_payload()
        resp = await client.post(API_PREFIX, json=payload)
        assert resp.status_code == 401


class TestSubmitTicket:
    async def test_submit_ticket_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        payload = create_ticket_payload()
        resp = await client.post(
            f"{API_PREFIX}/submit", json=payload, headers=auth_headers
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == payload["title"]
        assert body["status"] == "processing"
        assert "id" in body

    async def test_submit_ticket_unauthenticated(self, client: AsyncClient) -> None:
        payload = create_ticket_payload()
        resp = await client.post(f"{API_PREFIX}/submit", json=payload)
        assert resp.status_code == 401


class TestListTickets:
    async def test_list_tickets_empty(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        resp = await client.get(API_PREFIX, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_tickets_with_data(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        await client.post(
            API_PREFIX, json=create_ticket_payload(), headers=auth_headers
        )
        await client.post(
            API_PREFIX,
            json=create_ticket_payload({"title": "Second ticket"}),
            headers=auth_headers,
        )
        resp = await client.get(API_PREFIX, headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_list_tickets_unauthenticated(self, client: AsyncClient) -> None:
        resp = await client.get(API_PREFIX)
        assert resp.status_code == 401


class TestGetTicket:
    async def test_get_ticket_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            API_PREFIX, json=create_ticket_payload(), headers=auth_headers
        )
        ticket_id = create_resp.json()["id"]

        resp = await client.get(f"{API_PREFIX}/{ticket_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == ticket_id

    async def test_get_ticket_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        resp = await client.get(f"{API_PREFIX}/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestUpdateTicket:
    async def test_update_ticket_title(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            API_PREFIX, json=create_ticket_payload(), headers=auth_headers
        )
        ticket_id = create_resp.json()["id"]

        resp = await client.patch(
            f"{API_PREFIX}/{ticket_id}",
            json={"title": "Updated title"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated title"

    async def test_update_ticket_status(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            API_PREFIX, json=create_ticket_payload(), headers=auth_headers
        )
        ticket_id = create_resp.json()["id"]

        resp = await client.patch(
            f"{API_PREFIX}/{ticket_id}",
            json={"status": "resolved"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "resolved"


class TestDeleteTicket:
    async def test_delete_ticket_as_admin(
        self, client: AsyncClient, admin_auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            API_PREFIX,
            json=create_ticket_payload(),
            headers=admin_auth_headers,
        )
        ticket_id = create_resp.json()["id"]

        resp = await client.delete(
            f"{API_PREFIX}/{ticket_id}", headers=admin_auth_headers
        )
        assert resp.status_code == 204

    async def test_delete_ticket_as_non_admin(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            API_PREFIX, json=create_ticket_payload(), headers=auth_headers
        )
        ticket_id = create_resp.json()["id"]

        resp = await client.delete(f"{API_PREFIX}/{ticket_id}", headers=auth_headers)
        assert resp.status_code == 403
