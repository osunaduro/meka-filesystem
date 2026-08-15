"""Temporary compatibility alias for :mod:`workspace.servers.filesystem_http`.

Old integrations import the HTTP server as ``workspace.servers.filesystem_server``
(for example the Docker ``uvicorn`` command). This module re-exports the HTTP
transport while consumers migrate to ``workspace.servers.filesystem_http``.

It can be removed once all imports point to ``filesystem_http``.
"""

from workspace.servers.filesystem_http import app, mcp, mcp_auth, mcp_path  # noqa: F401

__all__ = ["app", "mcp", "mcp_auth", "mcp_path"]