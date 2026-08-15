"""Shared pytest fixtures for MEKA Filesystem authentication tests.

The server reads all configuration from environment variables at import time,
so each test that needs a specific ``MEKA_AUTH_MODE`` must reload the config
and server modules against a controlled environment.
"""

import importlib
import os
import sys
from collections.abc import Iterator

import pytest


_MODULES = (
    "workspace.servers.filesystem_http",
    "workspace.servers.filesystem_server",
    "workspace.internal.config",
    "workspace.internal.config.config",
)


def _reload_module() -> tuple[object, object]:
    for name in _MODULES:
        sys.modules.pop(name, None)
    config = importlib.import_module("workspace.internal.config")
    server = importlib.import_module("workspace.servers.filesystem_http")
    return config, server


def _purge() -> None:
    for name in _MODULES:
        sys.modules.pop(name, None)


@pytest.fixture
def api_key_server() -> Iterator[tuple[object, object]]:
    os.environ["MEKA_AUTH_MODE"] = "api-key"
    os.environ["MEKA_API_KEY"] = "test-secret-key"
    yield _reload_module()
    _purge()


@pytest.fixture
def none_mode() -> Iterator[tuple[object, object]]:
    os.environ["MEKA_AUTH_MODE"] = "none"
    yield _reload_module()
    _purge()


def oidc_env() -> dict:
    return {
        "MEKA_OIDC_ISSUER": "https://id.example.com/realms/meka",
        "MEKA_OIDC_AUDIENCE": "https://archivo.example.com/mcp",
        "MEKA_OIDC_JWKS_URL": "https://id.example.com/realms/meka/protocol/openid-connect/certs",
        "MEKA_OIDC_RESOURCE_URL": "https://archivo.example.com/mcp",
    }


@pytest.fixture
def oidc_server() -> Iterator[tuple[object, object]]:
    os.environ["MEKA_AUTH_MODE"] = "oidc"
    for key, value in oidc_env().items():
        os.environ[key] = value
    yield _reload_module()
    _purge()