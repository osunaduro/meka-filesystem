"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - grep()

Purpose:
    Search text inside files using ripgrep.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.grep

Public API:
    grep

Dependencies:
    json
    subprocess
    pathlib
    sdk.internal.project
    sdk.internal.path

Thread Safe:
    yes

Pure:
    no
"""

# ==========================================================================
# Imports
# ==========================================================================

import json
import subprocess

from pathlib import Path
from typing import Iterator

from workspace.core.models import GrepMatch
from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Public API
# ==========================================================================

def grep(
    root: Path,
    pattern: str,
    path: str | Path = ".",
) -> Iterator[GrepMatch]:
    """Search text inside files.

    Parameters
    ----------
    project : str
        Project name.

    pattern : str
        Search pattern.

    path : str | Path, optional
        Directory where the search starts.

    Yields
    ------
    GrepMatch
        Matching results.
    """

    # ----------------------------------------------------------------------
    # Resolve project context.
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Resolve search root.
    # ----------------------------------------------------------------------

    search_root = resolve_path(root, path)

    # ----------------------------------------------------------------------
    # Execute ripgrep.
    #
    # ripgrep is used as the reference implementation for text searching.
    #
    # JSON output is consumed instead of the human-readable format to
    # provide a stable interface independent of console formatting.
    # ----------------------------------------------------------------------

    process = subprocess.Popen(
        [
            "rg",
            "--json",
            pattern,
            str(search_root),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    assert process.stdout is not None

    for line in process.stdout:

        event = json.loads(line)

        if event["type"] != "match":
            continue

        data = event["data"]

        yield GrepMatch(
            path=Path(data["path"]["text"]),
            line=data["line_number"],
            column=data["submatches"][0]["start"] + 1,
            text=data["lines"]["text"].rstrip("\n"),
        )

    process.wait()
