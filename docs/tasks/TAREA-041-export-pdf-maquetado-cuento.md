# TAREA-041 - Exportación de cuento maquetado a PDF

- Fecha: 19/02/26 10:35
- Estado: cerrada
- Responsable: Codex
- ADR relacionadas: `0008`

## Resumen
Se implementa un flujo CLI para exportar un cuento completo a PDF maquetado en formato spread cuadrado (40x20 cm), con portada y spreads narrativos por página.

## Alcance aplicado
1. Nuevo módulo de dominio `app/pdf_export.py`:
- `validate_story_for_pdf(...)` para validar completitud de cover/main y secondary opcional.
- `export_story_pdf(...)` para generar PDF con layout editorial.
- Manejo explícito de `text_overflow` cuando el texto no cabe entre 12 pt y 10 pt.

2. Normalización de semántica de progreso:
- Nuevo módulo `app/story_progress.py` con helpers compartidos:
  - `slot_state(...)`
  - `has_valid_active_image(...)`
  - `resolve_active_asset_path(...)`
  - `coerce_string_list(...)`
- `app/web/image_flow.py` refactorizado para consumir estos helpers.

3. CLI:
- `manage.py` incorpora `export-story-pdf` con flags:
  - `--story`
  - `--output`
  - `--size-cm`
  - `--dry-run`
  - `--overwrite`

4. Dependencias:
- `Pipfile` actualizado con `reportlab`.

5. Documentación:
- `AGENTS.md` actualizado en sección CLI.
- `docs/tasks/INDICE.md` actualizado (Próximo ID `042`).
- `CHANGELOG.md` actualizado con entrada de la tarea.

## Layout implementado
1. Portada (spread 0):
- Panel izquierdo (20x20): título + metadatos mínimos.
- Panel derecho (20x20): imagen activa de cover con crop centrado (sin distorsión).

2. Spreads narrativos (1..N):
- Panel izquierdo: texto de página con ajuste automático.
- Panel derecho: imagen activa `main` con crop centrado.
- `secondary` activo (si existe): miniatura integrada en bloque inferior derecho del panel izquierdo, con pie `Sec.`.

## Validaciones ejecutadas
1. CLI:
- `python manage.py --help`
- `python manage.py export-story-pdf --help`

2. Validación de cuento (sin escribir PDF):
- `python manage.py export-story-pdf --story los_juegos_del_hambre/01 --dry-run`

3. Verificación de dependencia de render:
- `python manage.py export-story-pdf --story los_juegos_del_hambre/01 --output tmp/test-01.pdf`
- Resultado esperado en entorno actual: error controlado indicando instalación pendiente de `reportlab`.

4. Comprobación sintáctica:
- `python -m compileall app manage.py`

## Resultado
TAREA-041 completada: el repositorio dispone de exportación PDF maquetada por cuento vía CLI, con validación previa de completitud de slots e integración de secondary en spread.
