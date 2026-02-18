# TAREA-014-edad-objetivo-dinamica-inicio-adaptacion

## Metadatos

- ID de tarea: `TAREA-014-edad-objetivo-dinamica-inicio-adaptacion`
- Fecha: 14/02/26 16:13
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Ajustar el pipeline editorial para que la edad objetivo (`target_age`) se solicite al inicio de la adaptación y se persista por libro en `adaptation_profile.json`, evitando ejecutar cascada cuando no exista edad definida.

## Alcance implementado

1. Nueva persistencia de perfil editorial por libro en `_reviews/adaptation_profile.json`.
2. Nueva API pública `run_contexto_adaptation_profile(...)` para crear/actualizar perfil y `target_age`.
3. `run_orquestador_editorial(...)` ahora acepta `target_age` opcional y:
   - detiene el pipeline en `phase=awaiting_target_age` si falta edad en input y perfil.
   - persiste edad cuando llega por parámetro.
4. Nueva API pública `run_orquestador_editorial_resume(...)` con el mismo gate de edad.
5. `run_contexto_canon(...)` expone `adaptation_profile` y `adaptation_profile_rel` para trazabilidad.
6. Skills y guías actualizadas para reflejar la pregunta obligatoria de edad al inicio.

## Decisiones

- No se asume edad por defecto cuando falta `target_age`.
- El estado de bloqueo por falta de edad es `awaiting_target_age`.
- `adaptation_profile.json` es la fuente de verdad de `target_age` por libro.
- Se mantienen umbrales base derivados por edad en `thresholds` como punto de partida editable.

## Cambios aplicados

- Lógica runtime:
  - `app/editorial_orquestador.py`
- Skills:
  - `.codex/skills/revision-contexto-canon/SKILL.md`
  - `.codex/skills/revision-orquestador-editorial/SKILL.md`
  - `.codex/skills/revision-texto-deteccion/SKILL.md`
  - `.codex/skills/revision-prompts-deteccion/SKILL.md`
- Documentación:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/guia-orquestador-editorial.md`
  - `docs/context/INDICE.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`
  - `docs/tasks/TAREA-014-edad-objetivo-dinamica-inicio-adaptacion.md`

## Sidecars

- Nuevo sidecar por libro:
  - `library/<book_rel_path>/_reviews/adaptation_profile.json`

## Validación ejecutada

1. `python -m py_compile app/editorial_orquestador.py`
2. Sin edad y sin perfil (ruta de prueba dedicada):
   - `python -c "from app.editorial_orquestador import run_orquestador_editorial; r=run_orquestador_editorial(inbox_book_title='El imperio final', book_rel_path='cosmere/tmp-target-age-test'); print(r.get('phase')); print(r.get('target_age'))"`
3. Resume sin edad y sin perfil:
   - `python -c "from app.editorial_orquestador import run_orquestador_editorial_resume; r=run_orquestador_editorial_resume(inbox_book_title='El imperio final', book_rel_path='cosmere/tmp-target-age-test'); print(r.get('phase')); print(r.get('target_age'))"`
4. Con edad informada:
   - `python -c "from app.editorial_orquestador import run_orquestador_editorial; r=run_orquestador_editorial(inbox_book_title='El imperio final', book_rel_path='cosmere/tmp-target-age-test', target_age=8); print(r.get('phase')); print(r.get('target_age')); print(bool(r.get('adaptation_profile_rel')) )"`
5. Reutilizando perfil guardado (sin parámetro):
   - `python -c "from app.editorial_orquestador import run_orquestador_editorial; r=run_orquestador_editorial(inbox_book_title='El imperio final', book_rel_path='cosmere/tmp-target-age-test'); print(r.get('phase')); print(r.get('target_age'))"`

## Riesgos y notas

1. Este ajuste implementa el gate de edad y persistencia del perfil; no altera todavía la lógica de adaptación semántica profunda por edad.
2. El sidecar `adaptation_profile.json` se inicializa con umbrales base y permite evolución por parches posteriores.

## Commit asociado

- Mensaje de commit: `Tarea 014: edad objetivo dinamica al inicio de adaptacion`
- Hash de commit: pendiente
