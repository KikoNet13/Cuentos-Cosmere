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


class Texto(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    cuento = ForeignKeyField(Cuento, backref="textos", on_delete="CASCADE")
    numero_pagina = IntegerField()
    contenido = TextField(default="")
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        indexes = ((("cuento", "numero_pagina"), True),)


class Prompt(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    cuento = ForeignKeyField(Cuento, backref="prompts", on_delete="CASCADE")
    id_prompt = CharField(unique=True)
    bloque = CharField(default="")
    pagina = CharField(default="")
    tipo_imagen = CharField(default="principal")
    grupo = CharField(default="piloto")
    generar_una_imagen_de = TextField(default="")
    descripcion = TextField(default="")
    detalles_importantes_json = TextField(default="[]")
    prompt_final_literal = TextField(default="")
    bloque_copy_paste = TextField(default="")
    orden = IntegerField(default=0)
    estado = CharField(default="activo")
    updated_at = DateTimeField(default=utcnow)

    def get_detalles(self) -> list[str]:
        try:
            parsed = json.loads(self.detalles_importantes_json)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except json.JSONDecodeError:
            pass
        return []

    def set_detalles(self, detalles: list[str]) -> None:
        self.detalles_importantes_json = json.dumps(detalles, ensure_ascii=False)


class ImagenPrompt(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    prompt = ForeignKeyField(
        Prompt,
        backref="imagen_items",
        on_delete="CASCADE",
        unique=True,
    )
    ruta_relativa = TextField(default="")
    existe_archivo = BooleanField(default=False)
    updated_at = DateTimeField(default=utcnow)


class ReferenciaPDF(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    cuento = ForeignKeyField(Cuento, backref="referencias_pdf", on_delete="CASCADE")
    ruta_pdf = TextField()
    notas = TextField(default="")
    updated_at = DateTimeField(default=utcnow)

    class Meta:
        indexes = ((("cuento", "ruta_pdf"), True),)


class HistorialEdicion(BaseModel):
    id = CharField(primary_key=True, default=new_uuid)
    entidad = CharField()
    entidad_id = CharField()
    campo = CharField()
    valor_anterior = TextField(default="")
    valor_nuevo = TextField(default="")
    timestamp = DateTimeField(default=utcnow)
