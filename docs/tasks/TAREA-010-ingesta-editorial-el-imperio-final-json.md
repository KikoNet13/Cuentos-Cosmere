# TAREA-010-ingesta-editorial-el-imperio-final-json

## Metadatos

- ID de tarea: `TAREA-010-ingesta-editorial-el-imperio-final-json`
- Fecha: 13/02/26 13:49
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Procesar editorialmente `library/_inbox/El imperio final` con la skill `revision-adaptacion-editorial` y publicar los cuentos en formato canonico `NN.json` en `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final`.

## Contexto

El libro habia sido limpiado para reiniciar desde cero. Las propuestas disponibles estaban en:

- `library/_inbox/El imperio final/01.md`
- `library/_inbox/El imperio final/02.md`
- `library/_inbox/El imperio final/03.md`
- `library/_inbox/El imperio final/_future/04.md`
- `library/_inbox/El imperio final/_future/05.md`

## Plan

1. Leer propuestas `NN.md` del inbox del libro.
2. Construir `NN.json` canonicos en la ruta destino acordada.
3. Validar estructura y carga por runtime (`story_store` + catalogo).
4. Registrar trazabilidad documental y cerrar con commit unico.

## Decisiones

- Se procesaron los cinco cuentos disponibles (`01` a `05`), incluyendo los ubicados en `_future`.
- Se preservo comparativa editorial con `text.original/current` y `prompt.original/current`.
- Se inicializo `images.main` en todas las paginas con `active_id` vacio y `alternatives` vacia.
- `images.secondary` no se agrego en esta pasada al no existir valor editorial adicional en la propuesta base.

## Cambios aplicados

- Nuevos cuentos canonicos:
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final/01.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final/02.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final/03.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final/04.json`
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final/05.json`
- Trazabilidad:
  - `docs/tasks/TAREA-010-ingesta-editorial-el-imperio-final-json.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

- `python -c "import json; ..."` sobre `01.json` a `05.json` para verificar cantidad de paginas y slot `main`.
- `python -c "from app.story_store import list_story_json_files, load_story; ..."` para validar lectura por runtime y `book_rel_path`.
- `git status --short`

## Riesgos

- La calidad editorial de `current` parte igual a `original`; ajustes finos de estilo quedan para una iteracion posterior.
- No se generaron alternativas visuales ni `active_id`; quedan pendientes de curaduria de imagen.

## Seguimiento

1. Revisar en UI pagina por pagina para ajustar `text.current` y `prompt.current` donde haga falta.
2. Cargar alternativas de imagen por slot y definir `active_id` en los casos priorizados.

## Commit asociado

- Mensaje de commit: `Tarea 010: ingesta editorial de El imperio final a JSON canonico`
- Hash de commit: pendiente
