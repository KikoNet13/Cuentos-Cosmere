from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from peewee import IntegrityError

from .config import BASE_DIR, BIBLIOTECA_DIR
from .models import (
    Cuento,
    HistorialEdicion,
    ImagenPrompt,
    Libro,
    Prompt,
    ReferenciaPDF,
    Saga,
    Texto,
)
from .text_pages import EXPECTED_PAGE_COUNT
from .utils import slugify

web_bp = Blueprint("web", __name__)
CODIGO_CUENTO_RE = re.compile(r"^\d{2}$")


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def record_history(entity: str, entity_id: str, field: str, old: str, new: str) -> None:
    if old == new:
        return
    HistorialEdicion.create(
        entidad=entity,
        entidad_id=entity_id,
        campo=field,
        valor_anterior=old,
        valor_nuevo=new,
        timestamp=now_utc(),
    )


def canonical_image_rel(cuento: Cuento, id_prompt: str) -> str:
    return (
        BIBLIOTECA_DIR
        / cuento.libro.saga.slug
        / cuento.libro.slug
        / cuento.slug
        / "imagenes"
        / f"{id_prompt}.png"
    ).resolve().relative_to(BASE_DIR.resolve()).as_posix()


def parse_detalles(text_block: str) -> list[str]:
    lines = [line.strip().lstrip("-").strip() for line in text_block.splitlines()]
    return [line for line in lines if line]


def get_prompt_image(prompt: Prompt) -> ImagenPrompt | None:
    return ImagenPrompt.get_or_none(ImagenPrompt.prompt == prompt)


def prompt_vm(prompt: Prompt) -> dict:
    image = get_prompt_image(prompt)
    image_rel = image.ruta_relativa if image else canonical_image_rel(prompt.cuento, prompt.id_prompt)
    image_exists = bool(image.existe_archivo) if image else (BASE_DIR / image_rel).exists()
    return {
        "id_prompt": prompt.id_prompt,
        "bloque": prompt.bloque,
        "pagina": prompt.pagina,
        "tipo_imagen": prompt.tipo_imagen,
        "grupo": prompt.grupo,
        "generar_una_imagen_de": prompt.generar_una_imagen_de,
        "descripcion": prompt.descripcion,
        "detalles_importantes": prompt.get_detalles(),
        "detalles_texto": "\n".join(prompt.get_detalles()),
        "prompt_final_literal": prompt.prompt_final_literal,
        "bloque_copy_paste": prompt.bloque_copy_paste,
        "orden": prompt.orden,
        "estado": prompt.estado,
        "image_rel": image_rel,
        "image_exists": image_exists,
        "image_url": url_for("web.media_file", rel_path=image_rel) if image_rel else "",
    }


def text_vm(texto: Texto) -> dict:
    return {
        "id": texto.id,
        "numero_pagina": texto.numero_pagina,
        "contenido": texto.contenido,
    }


def query_prompts(cuento_id: str, q: str, tipo: str, grupo: str) -> list[Prompt]:
    query = Prompt.select().where(Prompt.cuento == cuento_id)
    if tipo:
        query = query.where(Prompt.tipo_imagen == tipo)
    if grupo:
        query = query.where(Prompt.grupo == grupo)
    if q:
        query = query.where(
            (Prompt.id_prompt.contains(q))
            | (Prompt.descripcion.contains(q))
            | (Prompt.generar_una_imagen_de.contains(q))
            | (Prompt.prompt_final_literal.contains(q))
            | (Prompt.bloque_copy_paste.contains(q))
            | (Prompt.detalles_importantes_json.contains(q))
        )
    return list(query.order_by(Prompt.orden.asc(), Prompt.id_prompt.asc()))


def parse_page_value(raw: str | None, default: int) -> int:
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value > 0 else default


def text_state(cuento: Cuento, selected_raw: str | None) -> dict:
    text_rows = list(
        Texto.select().where(Texto.cuento == cuento).order_by(Texto.numero_pagina.asc())
    )
    by_page = {row.numero_pagina: row for row in text_rows}
    detected_pages = sorted(by_page.keys())
    page_options = sorted(set(range(1, EXPECTED_PAGE_COUNT + 1)).union(detected_pages))
    default_page = detected_pages[0] if detected_pages else 1
    selected_page = parse_page_value(selected_raw, default_page)
    if selected_page not in page_options:
        selected_page = default_page
    missing_pages = [page for page in range(1, EXPECTED_PAGE_COUNT + 1) if page not in by_page]
    selected_text = by_page.get(selected_page)
    return {
        "page_options": page_options,
        "selected_page": selected_page,
        "missing_pages": missing_pages,
        "selected_text": selected_text,
    }


@web_bp.get("/")
def dashboard():
    sagas = list(Saga.select().order_by(Saga.nombre.asc()))
    stats = {
        "sagas": Saga.select().count(),
        "libros": Libro.select().count(),
        "cuentos": Cuento.select().count(),
        "textos": Texto.select().count(),
        "prompts": Prompt.select().count(),
        "imagenes": ImagenPrompt.select().count(),
        "pdf_refs": ReferenciaPDF.select().count(),
    }
    return render_template("dashboard.html", sagas=sagas, stats=stats)


@web_bp.post("/saga/create")
def create_saga():
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    if not nombre:
        flash("El nombre de saga es obligatorio.", "error")
        return redirect(url_for("web.dashboard"))
    slug = slugify(request.form.get("slug", "").strip() or nombre)
    try:
        Saga.create(slug=slug, nombre=nombre, descripcion=descripcion, created_at=now_utc(), updated_at=now_utc())
        flash("Saga creada.", "success")
    except IntegrityError:
        flash("El slug de la saga ya existe.", "error")
    return redirect(url_for("web.dashboard"))


@web_bp.post("/saga/<saga_id>/update")
def update_saga(saga_id: str):
    saga = Saga.get_or_none(Saga.id == saga_id)
    if not saga:
        abort(404)
    old = saga.nombre
    saga.nombre = request.form.get("nombre", saga.nombre).strip() or saga.nombre
    saga.descripcion = request.form.get("descripcion", saga.descripcion)
    new_slug = slugify(request.form.get("slug", saga.slug).strip() or saga.slug)
    saga.updated_at = now_utc()
    if new_slug != saga.slug:
        saga.slug = new_slug
    try:
        saga.save()
        record_history("saga", saga.id, "nombre", old, saga.nombre)
        flash("Saga actualizada.", "success")
    except IntegrityError:
        flash("No se pudo actualizar la saga (slug duplicado).", "error")
    return redirect(url_for("web.saga_detail", saga_slug=saga.slug))


@web_bp.post("/saga/<saga_id>/delete")
def delete_saga(saga_id: str):
    saga = Saga.get_or_none(Saga.id == saga_id)
    if not saga:
        abort(404)
    saga.delete_instance(recursive=True)
    flash("Saga eliminada.", "success")
    return redirect(url_for("web.dashboard"))


@web_bp.get("/saga/<saga_slug>")
def saga_detail(saga_slug: str):
    saga = Saga.get_or_none(Saga.slug == saga_slug)
    if not saga:
        abort(404)
    libros = list(Libro.select().where(Libro.saga == saga).order_by(Libro.orden.asc(), Libro.titulo.asc()))
    return render_template("saga.html", saga=saga, libros=libros)


@web_bp.post("/saga/<saga_slug>/libro/create")
def create_libro(saga_slug: str):
    saga = Saga.get_or_none(Saga.slug == saga_slug)
    if not saga:
        abort(404)
    titulo = request.form.get("titulo", "").strip()
    if not titulo:
        flash("El tÃ­tulo del libro es obligatorio.", "error")
        return redirect(url_for("web.saga_detail", saga_slug=saga.slug))
    slug = slugify(request.form.get("slug", "").strip() or titulo)
    orden = int(request.form.get("orden", "0") or 0)
    try:
        Libro.create(
            saga=saga,
            slug=slug,
            titulo=titulo,
            orden=orden,
            created_at=now_utc(),
            updated_at=now_utc(),
        )
        flash("Libro creado.", "success")
    except IntegrityError:
        flash("No se pudo crear el libro (slug duplicado en la saga).", "error")
    return redirect(url_for("web.saga_detail", saga_slug=saga.slug))


@web_bp.post("/libro/<libro_id>/update")
def update_libro(libro_id: str):
    libro = Libro.get_or_none(Libro.id == libro_id)
    if not libro:
        abort(404)
    old_title = libro.titulo
    libro.titulo = request.form.get("titulo", libro.titulo).strip() or libro.titulo
    libro.slug = slugify(request.form.get("slug", libro.slug).strip() or libro.slug)
    libro.orden = int(request.form.get("orden", str(libro.orden)) or libro.orden)
    libro.updated_at = now_utc()
    try:
        libro.save()
        record_history("libro", libro.id, "titulo", old_title, libro.titulo)
        flash("Libro actualizado.", "success")
    except IntegrityError:
        flash("No se pudo actualizar el libro (slug duplicado).", "error")
    return redirect(url_for("web.libro_detail", saga_slug=libro.saga.slug, libro_slug=libro.slug))


@web_bp.post("/libro/<libro_id>/delete")
def delete_libro(libro_id: str):
    libro = Libro.get_or_none(Libro.id == libro_id)
    if not libro:
        abort(404)
    saga_slug = libro.saga.slug
    libro.delete_instance(recursive=True)
    flash("Libro eliminado.", "success")
    return redirect(url_for("web.saga_detail", saga_slug=saga_slug))


@web_bp.get("/libro/<saga_slug>/<libro_slug>")
def libro_detail(saga_slug: str, libro_slug: str):
    saga = Saga.get_or_none(Saga.slug == saga_slug)
    if not saga:
        abort(404)
    libro = Libro.get_or_none((Libro.saga == saga) & (Libro.slug == libro_slug))
    if not libro:
        abort(404)
    cuentos = list(Cuento.select().where(Cuento.libro == libro).order_by(Cuento.orden.asc(), Cuento.codigo.asc()))
    return render_template("libro.html", saga=saga, libro=libro, cuentos=cuentos)


@web_bp.post("/libro/<saga_slug>/<libro_slug>/cuento/create")
def create_cuento(saga_slug: str, libro_slug: str):
    saga = Saga.get_or_none(Saga.slug == saga_slug)
    if not saga:
        abort(404)
    libro = Libro.get_or_none((Libro.saga == saga) & (Libro.slug == libro_slug))
    if not libro:
        abort(404)
    codigo = request.form.get("codigo", "").strip()
    titulo = request.form.get("titulo", "").strip() or codigo
    if not codigo:
        flash("El cÃ³digo del cuento es obligatorio.", "error")
        return redirect(url_for("web.libro_detail", saga_slug=saga.slug, libro_slug=libro.slug))
    if not CODIGO_CUENTO_RE.fullmatch(codigo):
        flash("El cÃ³digo debe tener 2 dÃ­gitos (por ejemplo, 01).", "error")
        return redirect(url_for("web.libro_detail", saga_slug=saga.slug, libro_slug=libro.slug))
    slug = slugify(request.form.get("slug", "").strip() or codigo)
    orden = int(request.form.get("orden", "0") or 0)
    try:
        Cuento.create(
            libro=libro,
            slug=slug,
            codigo=codigo,
            titulo=titulo,
            estado="activo",
            orden=orden,
            created_at=now_utc(),
            updated_at=now_utc(),
        )
        flash("Cuento creado.", "success")
    except IntegrityError:
        flash("No se pudo crear el cuento (cÃ³digo o slug duplicado).", "error")
    return redirect(url_for("web.libro_detail", saga_slug=saga.slug, libro_slug=libro.slug))


@web_bp.post("/cuento/<cuento_id>/update")
def update_cuento(cuento_id: str):
    cuento = Cuento.get_or_none(Cuento.id == cuento_id)
    if not cuento:
        abort(404)
    old_title = cuento.titulo
    nuevo_codigo = request.form.get("codigo", cuento.codigo).strip() or cuento.codigo
    if not CODIGO_CUENTO_RE.fullmatch(nuevo_codigo):
        flash("El cÃ³digo debe tener 2 dÃ­gitos (por ejemplo, 01).", "error")
        return redirect(
            url_for(
                "web.cuento_detail",
                saga_slug=cuento.libro.saga.slug,
                libro_slug=cuento.libro.slug,
                cuento_slug=cuento.slug,
            )
        )
    cuento.codigo = nuevo_codigo
    cuento.titulo = request.form.get("titulo", cuento.titulo).strip() or cuento.titulo
    cuento.slug = slugify(request.form.get("slug", cuento.slug).strip() or cuento.slug)
    cuento.estado = request.form.get("estado", cuento.estado).strip() or cuento.estado
    cuento.orden = int(request.form.get("orden", str(cuento.orden)) or cuento.orden)
    cuento.updated_at = now_utc()
    try:
        cuento.save()
        record_history("cuento", cuento.id, "titulo", old_title, cuento.titulo)
        flash("Cuento actualizado.", "success")
    except IntegrityError:
        flash("No se pudo actualizar el cuento (slug o cÃ³digo duplicado).", "error")
    return redirect(
        url_for(
            "web.cuento_detail",
            saga_slug=cuento.libro.saga.slug,
            libro_slug=cuento.libro.slug,
            cuento_slug=cuento.slug,
        )
    )


@web_bp.post("/cuento/<cuento_id>/delete")
def delete_cuento(cuento_id: str):
    cuento = Cuento.get_or_none(Cuento.id == cuento_id)
    if not cuento:
        abort(404)
    saga_slug = cuento.libro.saga.slug
    libro_slug = cuento.libro.slug
    cuento.delete_instance(recursive=True)
    flash("Cuento eliminado.", "success")
    return redirect(url_for("web.libro_detail", saga_slug=saga_slug, libro_slug=libro_slug))


@web_bp.get("/cuento/<saga_slug>/<libro_slug>/<cuento_slug>")
def cuento_detail(saga_slug: str, libro_slug: str, cuento_slug: str):
    saga = Saga.get_or_none(Saga.slug == saga_slug)
    if not saga:
        abort(404)
    libro = Libro.get_or_none((Libro.saga == saga) & (Libro.slug == libro_slug))
    if not libro:
        abort(404)
    cuento = Cuento.get_or_none((Cuento.libro == libro) & (Cuento.slug == cuento_slug))
    if not cuento:
        abort(404)

    prompts = query_prompts(cuento.id, "", "", "")
    prompt_items = [prompt_vm(p) for p in prompts]
    texts = text_state(cuento, request.args.get("pagina"))
    tipos = sorted({p.tipo_imagen for p in prompts})
    grupos = sorted({p.grupo for p in prompts})

    return render_template(
        "cuento.html",
        saga=saga,
        libro=libro,
        cuento=cuento,
        prompt_items=prompt_items,
        text_item=text_vm(texts["selected_text"]) if texts["selected_text"] else None,
        selected_page=texts["selected_page"],
        page_options=texts["page_options"],
        missing_pages=texts["missing_pages"],
        prompt_tipos=tipos,
        prompt_grupos=grupos,
    )


@web_bp.post("/cuento/<cuento_id>/prompt/create")
def create_prompt(cuento_id: str):
    cuento = Cuento.get_or_none(Cuento.id == cuento_id)
    if not cuento:
        abort(404)
    id_prompt = request.form.get("id_prompt", "").strip()
    if not id_prompt:
        flash("El ID del prompt es obligatorio.", "error")
        return redirect(
            url_for(
                "web.cuento_detail",
                saga_slug=cuento.libro.saga.slug,
                libro_slug=cuento.libro.slug,
                cuento_slug=cuento.slug,
            )
        )
    try:
        prompt = Prompt.create(
            cuento=cuento,
            id_prompt=id_prompt,
            bloque=request.form.get("bloque", cuento.codigo).strip(),
            pagina=request.form.get("pagina", "").strip(),
            tipo_imagen=request.form.get("tipo_imagen", "principal").strip(),
            grupo=request.form.get("grupo", "otro").strip(),
            generar_una_imagen_de=request.form.get("generar_una_imagen_de", "").strip(),
            descripcion=request.form.get("descripcion", "").strip(),
            prompt_final_literal=request.form.get("prompt_final_literal", "").strip(),
            bloque_copy_paste=request.form.get("bloque_copy_paste", "").strip(),
            orden=int(request.form.get("orden", "0") or 0),
            estado="activo",
            updated_at=now_utc(),
        )
        prompt.set_detalles(parse_detalles(request.form.get("detalles_importantes_text", "")))
        prompt.save()

        image_rel = canonical_image_rel(cuento, id_prompt)
        exists = (BASE_DIR / image_rel).exists()
        ImagenPrompt.create(prompt=prompt, ruta_relativa=image_rel, existe_archivo=exists, updated_at=now_utc())
        flash("Prompt creado.", "success")
    except IntegrityError:
        flash("No se pudo crear el prompt (id_prompt duplicado).", "error")

    return redirect(
        url_for(
            "web.cuento_detail",
            saga_slug=cuento.libro.saga.slug,
            libro_slug=cuento.libro.slug,
            cuento_slug=cuento.slug,
        )
    )


@web_bp.get("/htmx/prompts")
def htmx_prompts():
    cuento_id = request.args.get("cuento_id", "").strip()
    cuento = Cuento.get_or_none(Cuento.id == cuento_id)
    if not cuento:
        abort(404)
    q = request.args.get("q", "").strip()
    tipo = request.args.get("tipo", "").strip()
    grupo = request.args.get("grupo", "").strip()
    prompts = query_prompts(cuento.id, q, tipo, grupo)
    items = [prompt_vm(p) for p in prompts]
    return render_template("partials/prompts_list.html", prompt_items=items)


@web_bp.post("/prompt/<id_prompt>/update")
def update_prompt(id_prompt: str):
    prompt = Prompt.get_or_none(Prompt.id_prompt == id_prompt)
    if not prompt:
        abort(404)

    old_desc = prompt.descripcion
    prompt.bloque = request.form.get("bloque", prompt.bloque).strip()
    prompt.pagina = request.form.get("pagina", prompt.pagina).strip()
    prompt.tipo_imagen = request.form.get("tipo_imagen", prompt.tipo_imagen).strip()
    prompt.grupo = request.form.get("grupo", prompt.grupo).strip()
    prompt.generar_una_imagen_de = request.form.get(
        "generar_una_imagen_de", prompt.generar_una_imagen_de
    ).strip()
    prompt.descripcion = request.form.get("descripcion", prompt.descripcion).strip()
    prompt.prompt_final_literal = request.form.get("prompt_final_literal", prompt.prompt_final_literal).strip()
    prompt.bloque_copy_paste = request.form.get("bloque_copy_paste", prompt.bloque_copy_paste).strip()
    prompt.orden = int(request.form.get("orden", str(prompt.orden)) or prompt.orden)
    prompt.estado = request.form.get("estado", prompt.estado).strip() or prompt.estado
    prompt.set_detalles(parse_detalles(request.form.get("detalles_importantes_text", "")))
    prompt.updated_at = now_utc()
    prompt.save()

    record_history("prompt", prompt.id_prompt, "descripcion", old_desc, prompt.descripcion)
    item = prompt_vm(prompt)
    return render_template("partials/prompt_card.html", item=item)


@web_bp.post("/prompt/<id_prompt>/imagen-activa")
def update_prompt_image(id_prompt: str):
    prompt = Prompt.get_or_none(Prompt.id_prompt == id_prompt)
    if not prompt:
        abort(404)
    rel = request.form.get("ruta_relativa", "").strip()
    if not rel:
        rel = canonical_image_rel(prompt.cuento, prompt.id_prompt)
    rel = rel.replace("\\", "/")
    exists = (BASE_DIR / rel).exists()
    image, created = ImagenPrompt.get_or_create(
        prompt=prompt,
        defaults={"ruta_relativa": rel, "existe_archivo": exists, "updated_at": now_utc()},
    )
    if not created:
        old = image.ruta_relativa
        image.ruta_relativa = rel
        image.existe_archivo = exists
        image.updated_at = now_utc()
        image.save()
        record_history("imagen_prompt", prompt.id_prompt, "ruta_relativa", old, rel)

    item = prompt_vm(prompt)
    return render_template("partials/prompt_card.html", item=item)


@web_bp.get("/htmx/textos")
def htmx_textos():
    cuento_id = request.args.get("cuento_id", "").strip()
    cuento = Cuento.get_or_none(Cuento.id == cuento_id)
    if not cuento:
        abort(404)
    texts = text_state(cuento, request.args.get("pagina"))
    return render_template(
        "partials/texts_list.html",
        cuento_id=cuento.id,
        page_options=texts["page_options"],
        selected_page=texts["selected_page"],
        missing_pages=texts["missing_pages"],
        text_item=text_vm(texts["selected_text"]) if texts["selected_text"] else None,
    )


@web_bp.post("/texto/<texto_id>/update")
def update_texto(texto_id: str):
    texto = Texto.get_or_none(Texto.id == texto_id)
    if not texto:
        abort(404)
    old = texto.contenido
    texto.contenido = request.form.get("contenido", texto.contenido)
    texto.updated_at = now_utc()
    texto.save()
    record_history("texto", texto.id, "contenido", old, texto.contenido)
    return render_template("partials/text_card.html", item=text_vm(texto))


@web_bp.get("/media/<path:rel_path>")
def media_file(rel_path: str):
    target = (BASE_DIR / rel_path).resolve()
    base = BASE_DIR.resolve()
    if base not in target.parents and target != base:
        abort(403)
    if not target.exists() or not target.is_file():
        abort(404)
    return send_file(target)

