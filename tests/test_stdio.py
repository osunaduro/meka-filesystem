"""Tests for the STDIO transport adapter and the legacy compatibility alias."""

import asyncio
import importlib
import sys

import pytest


async def _tool_names(server) -> set[str]:
    tools = await server.mcp.list_tools()
    return {tool.name for tool in tools}


def test_stdio_exposes_same_tools_as_http(none_mode):
    config, server = none_mode
    from workspace.servers import filesystem_http
    from workspace.servers import filesystem_stdio

    async def run():
        stdio_names = await _tool_names(filesystem_stdio)
        http_names = await _tool_names(filesystem_http)
        return stdio_names, http_names

    stdio_names, http_names = asyncio.run(run())
    assert stdio_names == http_names
    assert len(stdio_names) == 35


def test_stdio_has_no_http_transport_imports(none_mode):
    config, server = none_mode
    sys.modules.pop("workspace.servers.filesystem_stdio", None)
    stdio = importlib.import_module("workspace.servers.filesystem_stdio")
    assert not hasattr(stdio, "app")
    assert not hasattr(stdio, "http_middleware")
    assert not hasattr(stdio, "mcp_auth")
    assert not hasattr(stdio, "BearerTokenMiddleware")


def test_stdio_module_is_runnable_entrypoint(none_mode):
    config, server = none_mode
    sys.modules.pop("workspace.servers.filesystem_stdio", None)
    stdio = importlib.import_module("workspace.servers.filesystem_stdio")
    assert callable(stdio.main)
    assert stdio.__name__ == "workspace.servers.filesystem_stdio"


def test_legacy_alias_re_exports_http_app(api_key_server):
    config, server = api_key_server
    from workspace.servers import filesystem_server

    assert filesystem_server.app is server.app
    assert filesystem_server.mcp is server.mcp