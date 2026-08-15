"""STDIO FastMCP server for a single bounded filesystem workspace.

Local transport for MCP clients such as Claude Desktop, VS Code, Cursor and
Windsurf. It reuses the exact same MCP tools as the HTTP adapter, backed by the
same ``workspace.core`` domain, but exposes no network: communication happens
over stdin/stdout via ``command`` + ``args``.
"""

import sys
from pathlib import Path

# Allow direct execution (`python workspace/servers/filesystem_stdio.py`) by
# putting the repository root on sys.path so that the `workspace` package is
# importable regardless of the invoking working directory.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


from fastmcp import FastMCP  # noqa: E402

from workspace.servers._tools import INSTRUCTIONS, register_tools  # noqa: E402

__all__ = ["mcp", "main"]


def build_server() -> FastMCP:
    server = FastMCP(
        "MEKA Filesystem",
        instructions=INSTRUCTIONS,
    )
    register_tools(server)
    return server


mcp = build_server()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
