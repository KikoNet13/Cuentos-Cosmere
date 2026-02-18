from __future__ import annotations

import base64
import mimetypes
import re
from typing import Any


def extract_image_payload(request: Any) -> tuple[bytes | None, str, str | None]:
    uploaded = request.files.get("image_file")
    if uploaded and uploaded.filename:
        payload = uploaded.read()
        mime_type = (uploaded.mimetype or "").strip()
        if not mime_type:
            mime_type = mimetypes.guess_type(uploaded.filename)[0] or "image/png"
        if payload:
            return payload, mime_type, None

    pasted = request.form.get("pasted_image_data", "").strip()
    if not pasted:
        return None, "image/png", "No se recibio ninguna imagen."

    mime_type = "image/png"
    encoded = pasted
    if pasted.startswith("data:"):
        match = re.match(r"^data:([^;]+);base64,(.*)$", pasted, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None, "image/png", "Formato de imagen pegada invalido."
        mime_type = match.group(1).strip() or "image/png"
        encoded = match.group(2)

    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (TypeError, ValueError):
        return None, "image/png", "No se pudo decodificar la imagen pegada."

    if not decoded:
        return None, "image/png", "La imagen pegada esta vacia."

    return decoded, mime_type, None
