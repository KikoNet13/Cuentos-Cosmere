---
name: adaptacion-ingesta-inicial
description: Skill para ingesta inicial interactiva de propuestas en library/_inbox (NN.md + NN.pdf) hacia NN.json y sidecars de contexto/issues con contraste canonico obligatorio.
---

# Adaptacion Ingesta Inicial

## Objetivo
Convertir propuestas de `library/_inbox/<book>/NN.md` + `NN.pdf` a:
- `library/<book_rel_path>/NN.json`
- `library/<book_rel_path>/_reviews/adaptation_context.json`
- `library/<book_rel_path>/_reviews/NN.issues.json`

Sin llamadas API desde scripts. La interaccion ocurre en chat Codex.

## Flujo
1. Ejecuta deteccion inicial sin respuestas:
```bash
python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "<titulo>"
```
2. Interpreta salida:
   - `phase=failed`: no hay contraste canonico suficiente. Corregir PDF/dependencias y relanzar.
   - `phase=awaiting_user`: preguntar al usuario todo `pending_questions[]`.
3. Construye un JSON de respuestas y vuelve a ejecutar:
```bash
python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "<titulo>" --answers-json "<ruta-json>"
```
4. Si `phase=completed`, reporta `written_outputs[]`, metrica e issues.

## Reglas operativas
- Procesa batch de todos los `NN.md` del libro.
- Excluye rutas con `_ignore`.
- Gate PDF obligatorio por lote:
  - Si falta `NN.pdf`: `phase=failed` con `input.missing_pdf`.
  - Si no hay parser (`pdfplumber`/`pypdf`): `phase=failed` con `pdf.parser_unavailable`.
  - Si no se puede extraer texto: `phase=failed` con `pdf.unreadable`.
  - Si hay paginas sin texto util y OCR no lo resuelve: `phase=failed` con `pdf.page_unreadable`.
- OCR es opcional. Solo se intenta cuando existen `pdf2image`, `pytesseract` y binario `tesseract`.
- No usar `input()` ni prompts bloqueantes en script.
- Para revision visual puntual de PDF, usar la skill `pdf` del sistema.

## Formato de respuestas
Ver `references/contracts.md`.

## Dependencias recomendadas
```bash
python -m pip install pdfplumber pypdf pdf2image pytesseract
```

## Validaciones recomendadas
```bash
python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py --help
python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "El imperio final" --dry-run
```
