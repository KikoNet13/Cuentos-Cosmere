from __future__ import annotations

import re

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
        page_number = int(match.group(1))
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(markdown)
        body = markdown[start:end].strip()
        if page_number in pages:
            warnings.append(
                f"Página {page_number} repetida; se conserva la última aparición."
            )
        pages[page_number] = body

    return pages, warnings
