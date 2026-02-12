from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from peewee import IntegrityError

from .config import BASE_DIR
from .models import (
    Ancla,
    AnclaVersion,
    Cuento,
    HistorialEdicion,
    Imagen,
    ImagenRequisito,
    Libro,
    Pagina,
    ReferenciaPDF,
    Saga,
)
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


def parse_int(raw: str | None, default: int) -> int:
    try:
        value = int(str(raw))
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def parse_lines(text: str) -> list[str]:
    return [line.strip().lstrip("-").strip() for line in text.splitlines() if line.strip()]


def image_exists(rel_path: str) -> bool:
    if not rel_path:
        return False
    return (BASE_DIR / rel_path).exists()


def page_state(cuento: Cuento, selected_raw: str | None) -> dict:
    pages = list(Pagina.select().where(Pagina.cuento == cuento).order_by(Pagina.numero.asc()))
    numbers = [p.numero for p in pages]
    if not numbers:
        return {
            "numbers": [],
            "selected_num": 1,
            "selected_page": None,
            "prev_num": None,
            "next_num": None,
        }
    selected = parse_int(selected_raw, numbers[0])
    if selected not in numbers:
        selected = numbers[0]
    idx = numbers.index(selected)
    return {
        "numbers": numbers,
        "selected_num": selected,
        "selected_page": pages[idx],
        "prev_num": numbers[idx - 1] if idx > 0 else None,
        "next_num": numbers[idx + 1] if idx < len(numbers) - 1 else None,
    }


def requirement_vm(req: ImagenRequisito) -> dict:
    if req.origen_tipo == "ancla_version" and req.ancla_version:
        refs = [
            {
                "id": img.id,
                "ruta_relativa": img.ruta_relativa,
                "exists": image_exists(img.ruta_relativa),
                "url": url_for("web.media_file", rel_path=img.ruta_relativa) if img.ruta_relativa else "",
            }
            for img in req.ancla_version.imagenes.order_by(Imagen.orden.asc(), Imagen.id.asc())
        ]
        return {
            "id": req.id,
            "origen_tipo": "ancla_version",
            "etiqueta": f"{req.ancla_version.ancla.nombre} / {req.ancla_version.nombre_version}",
            "refs": refs,
            "nota": req.nota,
        }
    if req.origen_tipo == "imagen" and req.imagen_referencia:
        rel = req.imagen_referencia.ruta_relativa
        return {
            "id": req.id,
            "origen_tipo": "imagen",
            "etiqueta": f"Imagen {req.imagen_referencia.id[:8]}",
            "refs": [
                {
                    "id": req.imagen_referencia.id,
                    "ruta_relativa": rel,
                    "exists": image_exists(rel),
                    "url": url_for("web.media_file", rel_path=rel) if rel else "",
                }
            ],
            "nota": req.nota,
        }
    return {"id": req.id, "origen_tipo": req.origen_tipo, "etiqueta": "Referencia invalida", "refs": [], "nota": req.nota}


def image_vm(image: Imagen) -> dict:
    reqs = [
        requirement_vm(req)
        for req in image.requisitos.order_by(ImagenRequisito.orden.asc(), ImagenRequisito.id.asc())
    ]
    return {
        "id": image.id,
        "owner_tipo": image.owner_tipo,
        "rol": image.rol,
        "principal_activa": bool(image.principal_activa),
        "ruta_relativa": image.ruta_relativa,
        "prompt_texto": image.prompt_texto,
        "requisitos_libres": "\n".join(image.get_requisitos_libres()),
        "orden": image.orden,
        "estado": image.estado,
        "exists": image_exists(image.ruta_relativa),
        "url": url_for("web.media_file", rel_path=image.ruta_relativa) if image.ruta_relativa else "",
        "requisitos": reqs,
    }


@web_bp.get("/")
def dashboard():
    sagas = list(Saga.select().order_by(Saga.nombre.asc()))
    stats = {
        "sagas": Saga.select().count(),
        "libros": Libro.select().count(),
        "cuentos": Cuento.select().count(),
        "paginas": Pagina.select().count(),
        "anclas": Ancla.select().count(),
        "versiones_ancla": AnclaVersion.select().count(),
        "imagenes": Imagen.select().count(),
        "requisitos": ImagenRequisito.select().count(),
        "pdf_refs": ReferenciaPDF.select().count(),
    }
    return render_template("dashboard.html", sagas=sagas, stats=stats)


@web_bp.post("/saga/create")
def create_saga():
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        flash("El nombre de saga es obligatorio.", "error")
        return redirect(url_for("web.dashboard"))
    slug = slugify(request.form.get("slug", "").strip() or nombre)
    try:
        Saga.create(slug=slug, nombre=nombre, descripcion=request.form.get("descripcion", "").strip(), created_at=now_utc(), updated_at=now_utc())
        flash("Saga creada.", "success")
    except IntegrityError:
        flash("El slug de la saga ya existe.", "error")
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
        flash("El titulo del libro es obligatorio.", "error")
        return redirect(url_for("web.saga_detail", saga_slug=saga.slug))
    slug = slugify(request.form.get("slug", "").strip() or titulo)
    try:
        Libro.create(saga=saga, slug=slug, titulo=titulo, orden=parse_int(request.form.get("orden"), 0), created_at=now_utc(), updated_at=now_utc())
        flash("Libro creado.", "success")
    except IntegrityError:
        flash("No se pudo crear el libro (slug duplicado en la saga).", "error")
    return redirect(url_for("web.saga_detail", saga_slug=saga.slug))


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
    if not CODIGO_CUENTO_RE.fullmatch(codigo):
        flash("El codigo debe tener 2 digitos (por ejemplo, 01).", "error")
        return redirect(url_for("web.libro_detail", saga_slug=saga.slug, libro_slug=libro.slug))
    titulo = request.form.get("titulo", "").strip() or codigo
    slug = slugify(request.form.get("slug", "").strip() or codigo)
    try:
        Cuento.create(libro=libro, slug=slug, codigo=codigo, titulo=titulo, estado="activo", orden=parse_int(request.form.get("orden"), 0), created_at=now_utc(), updated_at=now_utc())
        flash("Cuento creado.", "success")
    except IntegrityError:
        flash("No se pudo crear el cuento (codigo o slug duplicado).", "error")
    return redirect(url_for("web.libro_detail", saga_slug=saga.slug, libro_slug=libro.slug))


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
    state = page_state(cuento, request.args.get("pagina"))
    page = state["selected_page"]
    images = []
    if page:
        images = [image_vm(img) for img in page.imagenes.order_by(Imagen.orden.asc(), Imagen.id.asc())]
    ancla_versions = list(
        AnclaVersion.select()
        .join(Ancla)
        .where(Ancla.saga == saga)
        .order_by(Ancla.nombre.asc(), AnclaVersion.orden.asc(), AnclaVersion.nombre_version.asc())
    )
    page_images = [img for img in Imagen.select().where((Imagen.owner_tipo == "pagina") & (Imagen.pagina.is_null(False))).order_by(Imagen.id.asc())]
    return render_template(
        "cuento.html",
        saga=saga,
        libro=libro,
        cuento=cuento,
        page=page,
        page_numbers=state["numbers"],
        selected_page=state["selected_num"],
        prev_page=state["prev_num"],
        next_page=state["next_num"],
        image_items=images,
        ancla_versions=ancla_versions,
        all_page_images=page_images,
    )


@web_bp.post("/pagina/<pagina_id>/update")
def update_pagina(pagina_id: str):
    pagina = Pagina.get_or_none(Pagina.id == pagina_id)
    if not pagina:
        abort(404)
    old = pagina.contenido
    pagina.contenido = request.form.get("contenido", pagina.contenido)
    pagina.updated_at = now_utc()
    pagina.save()
    record_history("pagina", pagina.id, "contenido", old, pagina.contenido)
    return redirect(
        url_for(
            "web.cuento_detail",
            saga_slug=pagina.cuento.libro.saga.slug,
            libro_slug=pagina.cuento.libro.slug,
            cuento_slug=pagina.cuento.slug,
            pagina=pagina.numero,
        )
    )


@web_bp.post("/pagina/<pagina_id>/imagen/create")
def create_imagen_pagina(pagina_id: str):
    pagina = Pagina.get_or_none(Pagina.id == pagina_id)
    if not pagina:
        abort(404)
    rol = request.form.get("rol", "principal").strip() or "principal"
    principal_activa = request.form.get("principal_activa") == "on"
    image = Imagen.create(
        pagina=pagina,
        ancla_version=None,
        owner_tipo="pagina",
        rol=rol,
        principal_activa=principal_activa if rol == "principal" else False,
        ruta_relativa=request.form.get("ruta_relativa", "").strip().replace("\\", "/"),
        prompt_texto=request.form.get("prompt_texto", ""),
        requisitos_libres_json=json.dumps(parse_lines(request.form.get("requisitos_libres_text", "")), ensure_ascii=False),
        orden=parse_int(request.form.get("orden"), 0),
        estado=request.form.get("estado", "activo").strip() or "activo",
        created_at=now_utc(),
        updated_at=now_utc(),
    )
    if image.rol == "principal" and image.principal_activa:
        (
            Imagen.update(principal_activa=False)
            .where((Imagen.owner_tipo == "pagina") & (Imagen.pagina == pagina) & (Imagen.rol == "principal") & (Imagen.id != image.id))
            .execute()
        )
    flash("Imagen de pagina creada.", "success")
    return redirect(
        url_for("web.cuento_detail", saga_slug=pagina.cuento.libro.saga.slug, libro_slug=pagina.cuento.libro.slug, cuento_slug=pagina.cuento.slug, pagina=pagina.numero)
    )


@web_bp.post("/imagen/<imagen_id>/update")
def update_imagen(imagen_id: str):
    image = Imagen.get_or_none(Imagen.id == imagen_id)
    if not image:
        abort(404)
    image.rol = request.form.get("rol", image.rol).strip() or image.rol
    image.principal_activa = (request.form.get("principal_activa") == "on") if image.rol == "principal" else False
    image.ruta_relativa = request.form.get("ruta_relativa", image.ruta_relativa).strip().replace("\\", "/")
    image.prompt_texto = request.form.get("prompt_texto", image.prompt_texto)
    image.requisitos_libres_json = json.dumps(parse_lines(request.form.get("requisitos_libres_text", "")), ensure_ascii=False)
    image.orden = parse_int(request.form.get("orden"), image.orden)
    image.estado = request.form.get("estado", image.estado).strip() or image.estado
    image.updated_at = now_utc()
    image.save()
    if image.owner_tipo == "pagina" and image.rol == "principal" and image.principal_activa:
        (
            Imagen.update(principal_activa=False)
            .where((Imagen.owner_tipo == "pagina") & (Imagen.pagina == image.pagina) & (Imagen.rol == "principal") & (Imagen.id != image.id))
            .execute()
        )
    flash("Imagen actualizada.", "success")
    if image.owner_tipo == "pagina" and image.pagina:
        return redirect(url_for("web.cuento_detail", saga_slug=image.pagina.cuento.libro.saga.slug, libro_slug=image.pagina.cuento.libro.slug, cuento_slug=image.pagina.cuento.slug, pagina=image.pagina.numero))
    if image.owner_tipo == "ancla_version" and image.ancla_version:
        return redirect(url_for("web.anclas_saga", saga_slug=image.ancla_version.ancla.saga.slug))
    return redirect(url_for("web.dashboard"))


@web_bp.post("/imagen/<imagen_id>/delete")
def delete_imagen(imagen_id: str):
    image = Imagen.get_or_none(Imagen.id == imagen_id)
    if not image:
        abort(404)
    page = image.pagina
    saga_slug = image.ancla_version.ancla.saga.slug if image.ancla_version else None
    image.delete_instance(recursive=True)
    flash("Imagen eliminada.", "success")
    if page:
        return redirect(url_for("web.cuento_detail", saga_slug=page.cuento.libro.saga.slug, libro_slug=page.cuento.libro.slug, cuento_slug=page.cuento.slug, pagina=page.numero))
    if saga_slug:
        return redirect(url_for("web.anclas_saga", saga_slug=saga_slug))
    return redirect(url_for("web.dashboard"))


@web_bp.post("/imagen/<imagen_id>/activar-principal")
def activate_principal(imagen_id: str):
    image = Imagen.get_or_none(Imagen.id == imagen_id)
    if not image or image.owner_tipo != "pagina" or not image.pagina:
        abort(404)
    if image.rol != "principal":
        flash("Solo imagenes principales pueden activarse.", "error")
    else:
        (
            Imagen.update(principal_activa=False)
            .where((Imagen.owner_tipo == "pagina") & (Imagen.pagina == image.pagina) & (Imagen.rol == "principal"))
            .execute()
        )
        image.principal_activa = True
        image.updated_at = now_utc()
        image.save()
        flash("Imagen principal activa actualizada.", "success")
    return redirect(url_for("web.cuento_detail", saga_slug=image.pagina.cuento.libro.saga.slug, libro_slug=image.pagina.cuento.libro.slug, cuento_slug=image.pagina.cuento.slug, pagina=image.pagina.numero))


@web_bp.post("/imagen/<imagen_id>/requisito/create")
def create_requisito(imagen_id: str):
    image = Imagen.get_or_none(Imagen.id == imagen_id)
    if not image:
        abort(404)
    origen_tipo = request.form.get("origen_tipo", "").strip()
    orden = parse_int(request.form.get("orden"), 0)
    nota = request.form.get("nota", "")
    if origen_tipo == "ancla_version":
        version = AnclaVersion.get_or_none(AnclaVersion.id == request.form.get("ancla_version_id", "").strip())
        if not version:
            flash("Version de ancla no valida.", "error")
        else:
            ImagenRequisito.create(imagen=image, origen_tipo="ancla_version", ancla_version=version, orden=orden, nota=nota)
            flash("Requisito anadido.", "success")
    elif origen_tipo == "imagen":
        ref = Imagen.get_or_none(Imagen.id == request.form.get("imagen_referencia_id", "").strip())
        if not ref:
            flash("Imagen de referencia no valida.", "error")
        else:
            ImagenRequisito.create(imagen=image, origen_tipo="imagen", imagen_referencia=ref, orden=orden, nota=nota)
            flash("Requisito anadido.", "success")
    else:
        flash("Tipo de requisito no valido.", "error")
    if image.owner_tipo == "pagina" and image.pagina:
        return redirect(url_for("web.cuento_detail", saga_slug=image.pagina.cuento.libro.saga.slug, libro_slug=image.pagina.cuento.libro.slug, cuento_slug=image.pagina.cuento.slug, pagina=image.pagina.numero))
    return redirect(url_for("web.dashboard"))


@web_bp.post("/requisito/<requisito_id>/delete")
def delete_requisito(requisito_id: str):
    req = ImagenRequisito.get_or_none(ImagenRequisito.id == requisito_id)
    if not req:
        abort(404)
    image = req.imagen
    req.delete_instance()
    flash("Requisito eliminado.", "success")
    if image.owner_tipo == "pagina" and image.pagina:
        return redirect(url_for("web.cuento_detail", saga_slug=image.pagina.cuento.libro.saga.slug, libro_slug=image.pagina.cuento.libro.slug, cuento_slug=image.pagina.cuento.slug, pagina=image.pagina.numero))
    if image.owner_tipo == "ancla_version" and image.ancla_version:
        return redirect(url_for("web.anclas_saga", saga_slug=image.ancla_version.ancla.saga.slug))
    return redirect(url_for("web.dashboard"))


@web_bp.get("/saga/<saga_slug>/anclas")
def anclas_saga(saga_slug: str):
    saga = Saga.get_or_none(Saga.slug == saga_slug)
    if not saga:
        abort(404)
    anclas = list(Ancla.select().where(Ancla.saga == saga).order_by(Ancla.nombre.asc()))
    return render_template("anclas.html", saga=saga, anclas=anclas)


@web_bp.post("/saga/<saga_slug>/ancla/create")
def create_ancla(saga_slug: str):
    saga = Saga.get_or_none(Saga.slug == saga_slug)
    if not saga:
        abort(404)
    nombre = request.form.get("nombre", "").strip()
    if not nombre:
        flash("El nombre de ancla es obligatorio.", "error")
        return redirect(url_for("web.anclas_saga", saga_slug=saga.slug))
    slug = slugify(request.form.get("slug", "").strip() or nombre)
    try:
        Ancla.create(saga=saga, slug=slug, nombre=nombre, tipo=request.form.get("tipo", "otro").strip() or "otro", descripcion_base=request.form.get("descripcion_base", ""), estado="activo", created_at=now_utc(), updated_at=now_utc())
        flash("Ancla creada.", "success")
    except IntegrityError:
        flash("No se pudo crear el ancla (slug duplicado).", "error")
    return redirect(url_for("web.anclas_saga", saga_slug=saga.slug))


@web_bp.post("/ancla/<ancla_id>/version/create")
def create_ancla_version(ancla_id: str):
    ancla = Ancla.get_or_none(Ancla.id == ancla_id)
    if not ancla:
        abort(404)
    nombre_version = request.form.get("nombre_version", "").strip()
    if not nombre_version:
        flash("El nombre de version es obligatorio.", "error")
        return redirect(url_for("web.anclas_saga", saga_slug=ancla.saga.slug))
    try:
        AnclaVersion.create(ancla=ancla, nombre_version=nombre_version, descripcion=request.form.get("descripcion", ""), orden=parse_int(request.form.get("orden"), 0), estado=request.form.get("estado", "activo"), created_at=now_utc(), updated_at=now_utc())
        flash("Version creada.", "success")
    except IntegrityError:
        flash("No se pudo crear la version (nombre duplicado en ancla).", "error")
    return redirect(url_for("web.anclas_saga", saga_slug=ancla.saga.slug))


@web_bp.post("/ancla-version/<version_id>/imagen/create")
def create_ancla_image(version_id: str):
    version = AnclaVersion.get_or_none(AnclaVersion.id == version_id)
    if not version:
        abort(404)
    Imagen.create(
        pagina=None,
        ancla_version=version,
        owner_tipo="ancla_version",
        rol="referencia",
        principal_activa=False,
        ruta_relativa=request.form.get("ruta_relativa", "").strip().replace("\\", "/"),
        prompt_texto=request.form.get("prompt_texto", ""),
        requisitos_libres_json=json.dumps(parse_lines(request.form.get("requisitos_libres_text", "")), ensure_ascii=False),
        orden=parse_int(request.form.get("orden"), 0),
        estado=request.form.get("estado", "activo").strip() or "activo",
        created_at=now_utc(),
        updated_at=now_utc(),
    )
    flash("Imagen de ancla creada.", "success")
    return redirect(url_for("web.anclas_saga", saga_slug=version.ancla.saga.slug))


@web_bp.get("/media/<path:rel_path>")
def media_file(rel_path: str):
    target = (BASE_DIR / rel_path).resolve()
    base = BASE_DIR.resolve()
    if base not in target.parents and target != base:
        abort(403)
    if not target.exists() or not target.is_file():
        abort(404)
    return send_file(target)
