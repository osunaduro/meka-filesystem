"""Tests for the API-key Bearer authentication middleware."""

import asyncio

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse


async def _http_request(headers: dict | None = None):
    raw = []
    for key, value in (headers or {}).items():
        raw.append((key.lower().encode(), value.encode()))
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/mcp",
        "raw_path": b"/mcp",
        "query_string": b"",
        "root_path": "",
        "headers": raw,
        "client": ("testclient", 5000),
        "server": ("testserver", 80),
    }
    return Request(scope)


async def _call_next(request):
    return JSONResponse({"passed": True}, status_code=200)


@pytest.fixture
def middleware(api_key_server):
    config, server = api_key_server
    return server.BearerTokenMiddleware(app=lambda scope, receive, send: None)


def test_missing_authorization_is_401(middleware):
    async def run():
        request = await _http_request()
        response = await middleware.dispatch(request, _call_next)
        return response

    response = asyncio.run(run())
    assert response.status_code == 401
    assert response.headers.get("content-type", "").startswith("application/json")


def test_wrong_token_is_401(middleware):
    async def run():
        request = await _http_request({"Authorization": "Bearer wrong-token"})
        response = await middleware.dispatch(request, _call_next)
        return response

    assert asyncio.run(run()).status_code == 401


def test_non_bearer_scheme_is_401(middleware):
    async def run():
        request = await _http_request({"Authorization": "Basic abc"})
        response = await middleware.dispatch(request, _call_next)
        return response

    assert asyncio.run(run()).status_code == 401


def test_correct_token_allows_through(middleware):
    async def run():
        request = await _http_request({"Authorization": "Bearer test-secret-key"})
        response = await middleware.dispatch(request, _call_next)
        return response

    response = asyncio.run(run())
    assert response.status_code == 200


def test_oidc_mode_has_no_bearer_middleware(oidc_server):
    config, server = oidc_server
    assert server.http_middleware == []


def test_none_mode_has_no_bearer_middleware(none_mode):
    config, server = none_mode
    assert server.http_middleware == []