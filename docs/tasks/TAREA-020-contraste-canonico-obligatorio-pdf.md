# TAREA-020-contraste-canonico-obligatorio-pdf

## Metadatos

- ID de tarea: `TAREA-020-contraste-canonico-obligatorio-pdf`
- Fecha: 16/02/26 14:35
- Estado: cerrada
- Responsable: local
- ADR relacionadas: `0007`

## Objetivo

Endurecer `.codex/skills/adaptacion-ingesta-inicial` para que la ingesta inicial:

1. Haga contraste canonico obligatorio contra `NN.pdf`.
2. Bloquee el lote completo si no hay cobertura PDF util.
3. Enriquezca contrato de preguntas, issues y contexto.
4. Añada detecciones canonicas y de ajuste por edad (`target_age`, modo equilibrado).

## Alcance implementado

1. Refactor completo del script `ingesta_inicial.py` con preflight PDF por lote:
   - orden de parser: `pdfplumber` -> `pypdf`.
   - OCR opcional por pagina sin texto (`pdf2image` + `pytesseract` + `tesseract`).
   - bloqueo total por codigos: `input.missing_pdf`, `pdf.parser_unavailable`, `pdf.unreadable`, `pdf.page_unreadable`.
2. Nuevas detecciones por pagina:
   - `pdf.page_count_mismatch`
   - `canon.low_page_overlap`
   - `canon.missing_entity`
   - `canon.extra_entity`
   - `canon.numeric_mismatch`
   - `canon.quote_loss`
   - `canon.term_variant_noncanonical`
   - `age.too_complex`
   - `age.too_childish`
3. Contrato extendido:
   - `pending_questions[]` incluye `reason` y `evidence_pages`.
   - `NN.issues.json` incluye `review_mode`, `canon_source`, `metrics`.
   - issues incluyen opcional `source` + `detector` + `confidence`.
   - `adaptation_context.json` incluye `analysis_policy`, `canon_sources`.
   - `glossary[]` incluye `variants`, `source_presence`, `evidence_pages`.
4. Documentacion de skill y contrato actualizadas.
5. Documentacion operativa global alineada (`AGENTS.md`, `README.md`, `app/README.md`).

## Decisiones

1. Canon prioritario: PDF siempre.
2. Politica de bloqueo: `all_or_nothing` por lote.
3. OCR: opcional, pero si no hay texto util final la ejecucion falla.
4. Edad: umbrales fijos en modo equilibrado.
5. Glosario ambiguo: cobertura total de candidatos ambiguos detectados.
6. Sin llamadas LLM/API desde script.

## Cambios aplicados

- Skill:
  - `.codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py`
  - `.codex/skills/adaptacion-ingesta-inicial/SKILL.md`
  - `.codex/skills/adaptacion-ingesta-inicial/references/contracts.md`
- Documentacion:
  - `AGENTS.md`
  - `README.md`
  - `app/README.md`
  - `docs/tasks/TAREA-020-contraste-canonico-obligatorio-pdf.md`
  - `docs/tasks/INDICE.md`
  - `CHANGELOG.md`

## Validacion ejecutada

1. `python -m py_compile .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py`
2. `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py --help`
3. `python C:/Users/Kiko/.codex/skills/.system/skill-creator/scripts/quick_validate.py .codex/skills/adaptacion-ingesta-inicial`
   - Resultado: `Skill is valid!`.
4. Validacion de error por dependencias ausentes:
   - `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "El imperio final" --dry-run`
   - Resultado: `phase=failed` con `pdf.parser_unavailable`.
5. Instalacion local para validacion de parser:
   - `python -m pip install pypdf`
   - `python -m pip install pdfplumber`
   - `python -m pip install pyyaml`
6. Validacion de gate PDF real sobre lote principal:
   - `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "El imperio final" --dry-run`
   - Resultado: `phase=failed` con `pdf.page_unreadable` (bloqueo esperado sin OCR operativo).
7. Validacion de error por PDF faltante:
   - `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "TAREA-020-missing-pdf" --dry-run`
   - Resultado: `phase=failed` con `input.missing_pdf`.
8. Flujo positivo de referencia (inbox temporal controlado):
   - Se crea `library/_inbox/TAREA-020-legible-a/` con `01.md` + `01.pdf`.
   - `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "TAREA-020-legible-a" --dry-run`
   - Resultado: `phase=awaiting_user`.
9. Construccion de `answers_json` desde `pending_questions` y rerun:
   - `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "TAREA-020-legible-a" --answers-json tmp/tarea020_answers_v2.json --dry-run`
   - Resultado: `phase=completed`.
10. Escritura real:
   - `python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "TAREA-020-legible-a" --answers-json tmp/tarea020_answers_v2.json`
   - Resultado: `phase=completed` y `written_outputs` con `01.json`, `01.issues.json`, `adaptation_context.json`.
11. Compatibilidad runtime app:
   - `python -c "from app.story_store import load_story, save_page_edits; ..."`
   - Resultado: `story_title/cover/source_refs/ingest_meta` persisten antes y despues del roundtrip.

## Riesgos y notas

1. Con glosario en modo `todo ambiguo`, el volumen de preguntas puede ser muy alto.
2. Si el PDF tiene muchas paginas sin texto embebido, la ejecucion exigira OCR para poder completar.
3. El lote real `El imperio final` queda correctamente bloqueado hasta disponer de OCR/cobertura de texto suficiente.

## Commit asociado

- Mensaje de commit: `Tarea 020: contraste canonico obligatorio en ingesta inicial`
- Hash de commit: pendiente
