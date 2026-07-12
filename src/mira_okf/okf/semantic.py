from __future__ import annotations

import re


def semantic_text(body: str) -> str:
    lines: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in body.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match is not None:
            marker = match.group(1)[0]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            continue
        if in_fence:
            continue
        lines.append(re.sub(r"`+[^`\n]*`+", "", line))
    return "\n".join(lines)
