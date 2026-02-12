from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from peewee import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    SQL,
    TextField,
)

from .db import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def new_uuid() -> str:
    return str(uuid4())


class BaseModel(Model):
    class Meta:
        database = db


class Saga(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    slug = CharField(unique=True)
    nombre = CharField()
    descripcion = TextField(default="")
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)


class Libro(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    saga = ForeignKeyField(Saga, backref="libros", on_delete="CASCADE")
    slug = CharField()
    titulo = CharField()
    orden = IntegerField(default=0)
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        indexes = ((("saga", "slug"), True),)


class Cuento(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    libro = ForeignKeyField(Libro, backref="cuentos", on_delete="CASCADE")
    slug = CharField()
    codigo = CharField()
    titulo = CharField()
    estado = CharField(default="activo")
    orden = IntegerField(default=0)
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        indexes = (
            (("libro", "slug"), True),
            (("libro", "codigo"), True),
        )


class Pagina(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    cuento = ForeignKeyField(Cuento, backref="paginas", on_delete="CASCADE")
    numero = IntegerField()
    contenido = TextField(default="")
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        table_name = "pagina"
        indexes = ((("cuento", "numero"), True),)


class Ancla(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    saga = ForeignKeyField(Saga, backref="anclas", on_delete="CASCADE")
    slug = CharField()
    nombre = CharField()
    tipo = CharField(default="otro")
    descripcion_base = TextField(default="")
    estado = CharField(default="activo")
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        table_name = "ancla"
        indexes = ((("saga", "slug"), True),)


class AnclaVersion(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    ancla = ForeignKeyField(Ancla, backref="versiones", on_delete="CASCADE")
    nombre_version = CharField()
    descripcion = TextField(default="")
    orden = IntegerField(default=0)
    estado = CharField(default="activo")
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        table_name = "ancla_version"
        indexes = ((("ancla", "nombre_version"), True),)


class Imagen(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    pagina = ForeignKeyField(Pagina, backref="imagenes", on_delete="CASCADE", null=True)
    ancla_version = ForeignKeyField(
        AnclaVersion,
        backref="imagenes",
        on_delete="CASCADE",
        null=True,
    )
    owner_tipo = CharField(default="pagina")
    rol = CharField(default="principal")
    principal_activa = BooleanField(default=False)
    ruta_relativa = TextField(default="")
    prompt_texto = TextField(default="")
    requisitos_libres_json = TextField(default="[]")
    orden = IntegerField(default=0)
    estado = CharField(default="activo")
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        table_name = "imagen"
        indexes = (
            (("pagina", "orden"), False),
            (("ancla_version", "orden"), False),
        )
        constraints = [
            SQL(
                "CHECK (((pagina_id IS NOT NULL AND ancla_version_id IS NULL AND owner_tipo = 'pagina') "
                "OR (pagina_id IS NULL AND ancla_version_id IS NOT NULL AND owner_tipo = 'ancla_version')))"
            ),
            SQL("CHECK (rol IN ('principal', 'secundaria', 'referencia'))"),
            SQL("CHECK (owner_tipo IN ('pagina', 'ancla_version'))"),
        ]

    def get_requisitos_libres(self) -> list[str]:
        try:
            parsed = json.loads(self.requisitos_libres_json)
        except json.JSONDecodeError:
            return []
        if not isinstance(parsed, list):
            return []
        return [str(x) for x in parsed]

    def set_requisitos_libres(self, items: list[str]) -> None:
        self.requisitos_libres_json = json.dumps(items, ensure_ascii=False)


class ImagenRequisito(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    imagen = ForeignKeyField(Imagen, backref="requisitos", on_delete="CASCADE")
    origen_tipo = CharField(default="ancla_version")
    ancla_version = ForeignKeyField(
        AnclaVersion,
        backref="requisito_en_imagenes",
        on_delete="CASCADE",
        null=True,
    )
    imagen_referencia = ForeignKeyField(
        Imagen,
        backref="referenciada_en_requisitos",
        on_delete="CASCADE",
        null=True,
    )
    orden = IntegerField(default=0)
    nota = TextField(default="")

    class Meta:
        table_name = "imagen_requisito"
        indexes = (
            (("imagen", "orden"), False),
            (("imagen", "origen_tipo", "ancla_version"), False),
            (("imagen", "origen_tipo", "imagen_referencia"), False),
        )
        constraints = [
            SQL(
                "CHECK (((origen_tipo = 'ancla_version' AND ancla_version_id IS NOT NULL AND imagen_referencia_id IS NULL) "
                "OR (origen_tipo = 'imagen' AND imagen_referencia_id IS NOT NULL AND ancla_version_id IS NULL)))"
            ),
            SQL("CHECK (origen_tipo IN ('ancla_version', 'imagen'))"),
        ]


class ReferenciaPDF(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    cuento = ForeignKeyField(Cuento, backref="referencias_pdf", on_delete="CASCADE")
    ruta_pdf = TextField()
    notas = TextField(default="")
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        table_name = "referenciapdf"
        indexes = ((("cuento", "ruta_pdf"), True),)


class HistorialEdicion(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    entidad = CharField()
    entidad_id = CharField()
    campo = CharField()
    valor_anterior = TextField(default="")
    valor_nuevo = TextField(default="")
    timestamp = DateTimeField(default=utcnow)

    class Meta:
        table_name = "historialedicion"
