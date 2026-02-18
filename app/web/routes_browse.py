from __future__ import annotations

from flask import abort, render_template, request

from ..catalog_provider import catalog_counts, get_node, list_children
from . import web_bp
from .common import (
    build_breadcrumbs,
    decorate_children_for_cards,
    first_story_page_number,
    is_editor_mode,
    normalize_rel_path,
    parse_positive_int,
)
from .viewmodels import build_story_view_model


@web_bp.get("/")
def dashboard():
    children = decorate_children_for_cards(list_children(""))
    return render_template(
        "browse/page.html",
        node_name="biblioteca",
        node_path="",
        breadcrumbs=[{"name": "biblioteca", "path": ""}],
        children=children,
        counts=catalog_counts(),
    )


@web_bp.get("/<path:path_rel>")
def node_or_story(path_rel: str):
    normalized = normalize_rel_path(path_rel)
    if not normalized:
        abort(404)

    node = get_node(normalized)
    if not node:
        abort(404)

    if bool(node.get("is_story_leaf")):
        default_page = first_story_page_number(normalized)
        selected_page = parse_positive_int(request.args.get("p"), default_page)
        editor_mode = is_editor_mode(request.args.get("editor"))

        view_model = build_story_view_model(normalized, selected_page, editor_mode=editor_mode)
        if not view_model:
            abort(404)

        if editor_mode and request.args.get("p") is None:
            return render_template("story/editor/cover.html", **view_model)

        if editor_mode:
            return render_template("story/editor/page.html", **view_model)

        return render_template("story/read/page.html", **view_model)

    children = decorate_children_for_cards(list_children(normalized))
    return render_template(
        "browse/page.html",
        node_name=str(node.get("name", normalized)),
        node_path=normalized,
        breadcrumbs=build_breadcrumbs(normalized),
        children=children,
        counts=catalog_counts(),
    )
