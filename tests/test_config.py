"""Configuration tests for MEKA authentication modes."""

import importlib
import os
import sys

import pytest


_MODULES = (
    "workspace.servers.filesystem_http",
    "workspace.servers.filesystem_server",
    "workspace.internal.config",
    "workspace.internal.config.config",
)


def _load_config(env: dict) -> object:
    for name in _MODULES:
        sys.modules.pop(name, None)
    os.environ.clear()
    os.environ.update(env)
    return importlib.import_module("workspace.internal.config")


@pytest.fixture(autouse=True)
def _clean_imports():
    yield
    for name in _MODULES:
        sys.modules.pop(name, None)


def test_default_auth_mode_is_api_key():
    config = _load_config({})
    assert config.AUTH_MODE == "api-key"


def test_auth_mode_reads_environment():
    config = _load_config({"MEKA_AUTH_MODE": "none"})
    assert config.AUTH_MODE == "none"


def test_invalid_auth_mode_raises():
    with pytest.raises(ValueError, match="MEKA_AUTH_MODE"):
        _load_config({"MEKA_AUTH_MODE": "bogus"})


def test_api_key_reads_environment():
    config = _load_config({"MEKA_AUTH_MODE": "api-key", "MEKA_API_KEY": "secret"})
    assert config.MEKA_API_KEY == "secret"


def test_oidc_environment_forwarded():
    env = {
        "MEKA_AUTH_MODE": "oidc",
        "MEKA_OIDC_ISSUER": "https://issuer.example.com",
        "MEKA_OIDC_AUDIENCE": "https://api.example.com/mcp",
        "MEKA_OIDC_JWKS_URL": "https://issuer.example.com/certs",
        "MEKA_OIDC_RESOURCE_URL": "https://archivo.example.com/mcp",
    }
    config = _load_config(env)
    assert config.MEKA_OIDC_ISSUER == "https://issuer.example.com"
    assert config.MEKA_OIDC_AUDIENCE == "https://api.example.com/mcp"
    assert config.MEKA_OIDC_JWKS_URL == "https://issuer.example.com/certs"
    assert config.MEKA_OIDC_RESOURCE_URL == "https://archivo.example.com/mcp"


@pytest.mark.parametrize(
    "missing",
    [
        "MEKA_OIDC_ISSUER",
        "MEKA_OIDC_AUDIENCE",
        "MEKA_OIDC_JWKS_URL",
        "MEKA_OIDC_RESOURCE_URL",
    ],
)
def test_oidc_missing_variable_fails_at_import(missing):
    env = {
        "MEKA_AUTH_MODE": "oidc",
        "MEKA_OIDC_ISSUER": "https://issuer.example.com",
        "MEKA_OIDC_AUDIENCE": "https://api.example.com/mcp",
        "MEKA_OIDC_JWKS_URL": "https://issuer.example.com/certs",
        "MEKA_OIDC_RESOURCE_URL": "https://archivo.example.com/mcp",
    }
    env.pop(missing)
    os.environ.clear()
    os.environ.update(env)
    sys.modules.pop("workspace.internal.config", None); sys.modules.pop("workspace.internal.config.config", None)
    sys.modules.pop("workspace.servers.filesystem_http", None); sys.modules.pop("workspace.servers.filesystem_server", None)
    with pytest.raises(ValueError, match=missing):
        importlib.import_module("workspace.servers.filesystem_http")


def test_resource_url_must_be_absolute():
    env = {
        "MEKA_AUTH_MODE": "oidc",
        "MEKA_OIDC_ISSUER": "https://issuer.example.com",
        "MEKA_OIDC_AUDIENCE": "https://api.example.com/mcp",
        "MEKA_OIDC_JWKS_URL": "https://issuer.example.com/certs",
        "MEKA_OIDC_RESOURCE_URL": "archivo.example.com/mcp",
    }
    os.environ.clear()
    os.environ.update(env)
    sys.modules.pop("workspace.internal.config", None); sys.modules.pop("workspace.internal.config.config", None)
    sys.modules.pop("workspace.servers.filesystem_http", None); sys.modules.pop("workspace.servers.filesystem_server", None)
    with pytest.raises(ValueError, match="absolute"):
        importlib.import_module("workspace.servers.filesystem_http")


def test_resource_url_must_not_have_query():
    env = {
        "MEKA_AUTH_MODE": "oidc",
        "MEKA_OIDC_ISSUER": "https://issuer.example.com",
        "MEKA_OIDC_AUDIENCE": "https://api.example.com/mcp",
        "MEKA_OIDC_JWKS_URL": "https://issuer.example.com/certs",
        "MEKA_OIDC_RESOURCE_URL": "https://archivo.example.com/mcp?token=1",
    }
    os.environ.clear()
    os.environ.update(env)
    sys.modules.pop("workspace.internal.config", None); sys.modules.pop("workspace.internal.config.config", None)
    sys.modules.pop("workspace.servers.filesystem_http", None); sys.modules.pop("workspace.servers.filesystem_server", None)
    with pytest.raises(ValueError, match="query string"):
        importlib.import_module("workspace.servers.filesystem_http")