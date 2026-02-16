from __future__ import annotations

from flask import Blueprint

web_bp = Blueprint("web", __name__)

# Route modules register endpoints via decorators on `web_bp`.
from . import routes_browse  # noqa: E402,F401
from . import routes_fragments  # noqa: E402,F401
from . import routes_story_editor  # noqa: E402,F401
from . import routes_story_read  # noqa: E402,F401
from . import routes_system  # noqa: E402,F401

