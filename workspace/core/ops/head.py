"""Read the first lines of a text file."""

from pathlib import Path

from workspace.internal.path import resolve as resolve_path


def head(
    root: Path,
    path: str | Path,
    lines: int = 10,
    *,
    encoding: str = "utf-8",
) -> str:
    """Return at most ``lines`` first lines from a project file."""
    if lines < 0:
        raise ValueError("'lines' cannot be negative.")
    target = resolve_path(root, path)
    with target.open("r", encoding=encoding) as file:
        return "".join(line for _, line in zip(range(lines), file))
