"""Tests for the OIDC Resource Server behaviour."""

import asyncio

import httpx
import pytest
from fastmcp.server.auth import AccessToken


def test_well_known_protected_resource_route(oidc_server):
    config, server = oidc_server

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=server.app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/.well-known/oauth-protected-resource/mcp"
            )
            return response, response.json()

    response, body = asyncio.run(run())
    assert response.status_code == 200
    assert body["resource"] == "https://archivo.example.com/mcp"
    assert body["authorization_servers"] == ["https://id.example.com/realms/meka"]
    assert body["scopes_supported"] == [
        "filesystem:read",
        "filesystem:write",
        "filesystem:delete",
    ]
    assert body["resource_name"] == "MEKA Filesystem"


def test_mcp_path_derived_from_resource_url(oidc_server):
    config, server = oidc_server
    assert server.mcp_path == "/mcp"


def test_scope_decorator_requires_token(oidc_server, monkeypatch):
    config, server = oidc_server
    calls = []

    def fake_token():
        return None

    monkeypatch.setattr(server, "get_access_token", fake_token)
    guarded = server._scope("filesystem:read")(lambda: calls.append(1))
    with pytest.raises(PermissionError):
        guarded()


def test_scope_decorator_rejects_missing_scope(oidc_server, monkeypatch):
    config, server = oidc_server
    token = AccessToken(
        token="x",
        client_id="client",
        scopes=["filesystem:read"],
        expires_at=None,
    )

    def fake_token():
        return token

    monkeypatch.setattr(server, "get_access_token", fake_token)
    guarded = server._scope("filesystem:write")(lambda: "ok")
    with pytest.raises(PermissionError, match="filesystem:write"):
        guarded()


def test_scope_decorator_accepts_required_scope(oidc_server, monkeypatch):
    config, server = oidc_server
    token = AccessToken(
        token="x",
        client_id="client",
        scopes=["filesystem:read", "filesystem:write"],
    )

    def fake_token():
        return token

    monkeypatch.setattr(server, "get_access_token", fake_token)
    guarded = server._scope("filesystem:read")(lambda: "ok")
    assert guarded() == "ok"


def test_supported_scopes_exposed(oidc_server):
    config, server = oidc_server
    assert server.SUPPORTED_SCOPES == [
        "filesystem:read",
        "filesystem:write",
        "filesystem:delete",
    ]


def test_oidc_provider_is_remote_resource_server(oidc_server):
    config, server = oidc_server
    assert server.mcp_auth is not None
    assert type(server.mcp_auth).__name__ == "OIDCResourceServer"