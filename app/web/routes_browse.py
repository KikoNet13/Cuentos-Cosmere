from __future__ import annotations

from flask import abort, redirect, render_template, url_for

from ..catalog_provider import catalog_counts, get_node, list_children
from . import web_bp
from .common import build_breadcrumbs, decorate_children_for_cards, first_story_page_number, normalize_rel_path


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


@web_bp.get("/browse")
def browse_root():
    return redirect(url_for("web.dashboard"))


@web_bp.get("/browse/<path:node_path>")
def browse_node(node_path: str):
    normalized = normalize_rel_path(node_path)
    node = get_node(normalized)
    if not node:
        abort(404)

    if bool(node.get("is_story_leaf")):
        return redirect(
            url_for(
                "web.story_read_page",
                story_path=normalized,
                page_number=first_story_page_number(normalized),
            )
        )

    children = decorate_children_for_cards(list_children(normalized))
    return render_template(
        "browse/page.html",
        node_name=str(node.get("name", normalized)),
        node_path=normalized,
        breadcrumbs=build_breadcrumbs(normalized),
        children=children,
        counts=catalog_counts(),
    )


@web_bp.get("/n/<path:node_path>")
def node_detail_legacy(node_path: str):
    normalized = normalize_rel_path(node_path)
    return redirect(url_for("web.browse_node", node_path=normalized))

