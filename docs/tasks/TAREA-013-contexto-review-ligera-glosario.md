# TAREA-013-contexto-review-ligera-glosario

## Metadatos

- ID de tarea: `TAREA-013-contexto-review-ligera-glosario`
- Fecha: 14/02/26 15:15
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Añadir una revisión interactiva ligera de terminología en la etapa de contexto/canon/glosario, con persistencia en sidecar dedicado y aplicación efectiva en el runtime editorial sin bloquear el orquestador.

## Alcance implementado

1. Nuevo sidecar de libro `context_review.json` en `library/<book_rel_path>/_reviews/`.
2. Función pública `run_contexto_revision_glosario(...)` para registrar decisiones y regenerar glosario efectivo.
3. `run_contexto_canon(...)` ahora consume decisiones previas cuando existe `context_review.json`.
4. En el glosario efectivo se expone `replacement_target` por término.
5. Los findings de tipo `glossary_forbidden_term` proponen reemplazo con `replacement_target`.
6. Skills y guías actualizadas para dejar explícito que la revisión ligera es manual desde `revision-contexto-canon`.
7. Inclusión de cambios de `library/.../el-imperio-final` para pruebas del flujo desde cero.

## Diseño aplicado

### `context_review.json`

- Campos raíz:
  - `schema_version`, `generated_at`, `updated_at`
  - `book_rel_path`, `inbox_book_title`
  - `mode: "light"`
  - `blocking: false`
  - `replacement_policy: "preferred_alias_else_canonical"`
  - `pending_policy: "no_impact"`
  - `decisions[]`
  - `metrics`
- Cada decisión:
  - `term_key`, `term`
  - `decision` (`accepted|rejected|defer|pending`)
  - `preferred_alias`
  - `allowed_add[]`
  - `forbidden_add[]`
  - `notes`
  - `updated_at`
- Métricas:
  - `total`, `accepted`, `rejected`, `defer`, `pending`, `ignored_missing_term`

## Decisiones

- La revisión ligera es por libro y no bloqueante.
- `pending`/`defer` no alteran reglas activas.
- Solo decisiones `accepted` aplican cambios de alias y listas `allowed/forbidden`.
- El orquestador no dispara esta revisión; la consume si ya existe sidecar.

## Cambios aplicados

- Lógica editorial:
  - `app/editorial_orquestador.py`
- Skills:
  - `.codex/skills/revision-contexto-canon/SKILL.md`
  - `.codex/skills/revision-orquestador-editorial/SKILL.md`
- Documentación operativa:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/guia-orquestador-editorial.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`
- Tarea:
  - `docs/tasks/TAREA-013-contexto-review-ligera-glosario.md`
- Datos de prueba (incluidos a petición del usuario):
  - `library/cosmere/nacidos-de-la-bruma-era-1/el-imperio-final/*`

## Validación ejecutada

1. `python -m py_compile app/editorial_orquestador.py`
2. `python -c "from app.editorial_orquestador import run_contexto_canon, run_contexto_revision_glosario; b='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final'; t='El imperio final'; r1=run_contexto_canon(inbox_book_title=t, book_rel_path=b); r2=run_contexto_revision_glosario(inbox_book_title=t, book_rel_path=b, decisions=[{'term_key':'niebla','term':'Niebla','decision':'accepted','preferred_alias':'Bruma','allowed_add':['bruma'],'forbidden_add':['niebla eterna'],'notes':'adaptacion narrativa'}]); print(bool(r1.get('glossary_merged_rel'))); print(r2.get('context_review_rel','')); print(r2.get('context_review',{}).get('metrics',{}).get('accepted',0))"`
3. `python -c "from app.editorial_orquestador import run_contexto_canon; b='cosmere/nacidos-de-la-bruma-era-1/el-imperio-final'; t='El imperio final'; r=run_contexto_canon(inbox_book_title=t, book_rel_path=b); print('context_review_rel' in r); print('glossary_merged' in r)"`

## Riesgos y notas

1. Si el glosario base no contiene términos, `context_review.json` conserva trazabilidad pero no aplica cambios efectivos.
2. El reemplazo de términos prohibidos se mantiene como sustitución de cadena simple sobre `text.current`.

## Commit asociado

- Mensaje de commit: `Tarea 013: revision ligera de glosario en contexto canon`
- Hash de commit: pendiente
