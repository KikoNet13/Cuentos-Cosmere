from __future__ import annotations

from flask import abort, redirect, render_template, request, url_for

from . import web_bp
from .common import first_story_page_number, is_editor_mode, normalize_rel_path, parse_positive_int
from .viewmodels import build_story_view_model


@web_bp.get("/story/<path:story_path>/page/<int:page_number>")
def story_read_page(story_path: str, page_number: int):
    story_rel_path = normalize_rel_path(story_path)
    view_model = build_story_view_model(story_rel_path, page_number, editor_mode=False)
    if not view_model:
        abort(404)

    if view_model["page_numbers"] and int(view_model["selected_page"]) != int(page_number):
        return redirect(
            url_for(
                "web.story_read_page",
                story_path=story_rel_path,
                page_number=int(view_model["selected_page"]),
            )
        )

    return render_template("story/read/page.html", **view_model)


@web_bp.get("/story/<path:story_path>")
def story_detail_legacy(story_path: str):
    story_rel_path = normalize_rel_path(story_path)
    selected_page = parse_positive_int(request.args.get("p"), first_story_page_number(story_rel_path))

    if is_editor_mode(request.args.get("editor")):
        return redirect(
            url_for(
                "web.story_editor_page",
                story_path=story_rel_path,
                page_number=selected_page,
            )
        )

    return redirect(
        url_for(
            "web.story_read_page",
            story_path=story_rel_path,
            page_number=selected_page,
        )
    )

