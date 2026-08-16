"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - closest_match()

Purpose:
    Find the substring of a file's content that most closely resembles a
    piece of search text that failed to match exactly, so a NoMatchError
    can carry a helpful hint instead of a bare "not found".
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops._fuzzy_match

Public API:
    closest_match

Dependencies:
    difflib

Thread Safe:
    yes

Pure:
    yes
"""

# ==========================================================================
# Imports
# ==========================================================================

import difflib

# Below this similarity ratio, the closest window found is considered noise
# rather than a useful near-miss (e.g. whitespace/indentation drift).
_SIMILARITY_THRESHOLD = 0.6


# ==========================================================================
# Public API
# ==========================================================================

def closest_match(content: str, query: str) -> tuple[str | None, float | None]:
    """Find the window of ``content`` most similar to ``query``.

    Locates the best anchor point via the longest contiguous match between
    ``content`` and ``query``, expands a window around it roughly the
    length of ``query``, and scores that window's similarity to ``query``.

    Parameters
    ----------
    content : str
        Text to search within (typically a full file's contents).

    query : str
        Text that failed to match exactly.

    Returns
    -------
    tuple[str | None, float | None]
        ``(window, ratio)`` when a window scores at or above the
        similarity threshold, otherwise ``(None, None)``.
    """
    if not content or not query:
        return None, None

    matcher = difflib.SequenceMatcher(None, content, query, autojunk=False)
    block = matcher.find_longest_match(0, len(content), 0, len(query))

    if block.size == 0:
        return None, None

    # Expand a window around the matched block to roughly the length of
    # the query, centered on where the match was found.
    query_len = len(query)
    anchor = block.a + block.size // 2
    start = max(0, anchor - query_len // 2)
    end = min(len(content), start + query_len)
    start = max(0, end - query_len)

    window = content[start:end]
    ratio = difflib.SequenceMatcher(None, query, window, autojunk=False).ratio()

    if ratio < _SIMILARITY_THRESHOLD:
        return None, None

    return window, ratio
