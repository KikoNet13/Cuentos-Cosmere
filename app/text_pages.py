from __future__ import annotations

import re

EXPECTED_PAGE_COUNT = 32
PAGE_HEADER_RE = re.compile(
    r"^\s*##\s*P(?:a|\u00e1)gina\s+(\d+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def parse_markdown_pages(markdown: str) -> tuple[dict[int, str], list[str]]:
    warnings: list[str] = []
    pages: dict[int, str] = {}
    matches = list(PAGE_HEADER_RE.finditer(markdown))

    if not matches:
        warnings.append("No se detectaron encabezados '## Pagina N'.")
        return pages, warnings

    for idx, match in enumerate(matches):
        numero_pagina = int(match.group(1))
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        if numero_pagina in pages:
            warnings.append(
                f"Pagina {numero_pagina} repetida; se conserva la ultima aparicion."
            )
        pages[numero_pagina] = body

    return pages, warnings
