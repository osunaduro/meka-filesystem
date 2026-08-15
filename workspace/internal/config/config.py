"""
MEKA Core SDK

Domain:
    Internal

Component:
    Configuration

Purpose:
    Provide the runtime configuration used by the SDK.
"""

"""
MEKA Metadata

Domain:
    internal

Component:
    config

Public API:
    WORKSPACE_ROOT

Dependencies:
    os
    pathlib

Thread Safe:
    yes
"""

import os
from pathlib import Path


AUTH_MODES = frozenset({"none", "api-key", "oidc"})


def _environment(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


AUTH_MODE = (_environment("MEKA_AUTH_MODE") or "api-key").lower()

if AUTH_MODE not in AUTH_MODES:
    supported_modes = ", ".join(sorted(AUTH_MODES))
    raise ValueError(
        f"MEKA_AUTH_MODE must be one of: {supported_modes}. Received: {AUTH_MODE!r}."
    )

MEKA_API_KEY = _environment("MEKA_API_KEY")
MEKA_OIDC_ISSUER = _environment("MEKA_OIDC_ISSUER")
MEKA_OIDC_AUDIENCE = _environment("MEKA_OIDC_AUDIENCE")
MEKA_OIDC_JWKS_URL = _environment("MEKA_OIDC_JWKS_URL")
MEKA_OIDC_RESOURCE_URL = _environment("MEKA_OIDC_RESOURCE_URL")


WORKSPACE_ROOT: Path = Path(
    os.getenv(
        "MEKA_WORKSPACE_ROOT",
        "/home/martin/Documentos/Documentos-AI",
    )
)
