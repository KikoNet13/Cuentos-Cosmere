---
name: adaptacion-ingesta-inicial
description: Skill para ingesta inicial interactiva de propuestas en library/_inbox (NN.md + NN.pdf) hacia NN.json y sidecars de contexto/issues, con preguntas de target_age, book_rel_path y glosario ambiguo.
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
2. Si `phase=awaiting_user`, pregunta al usuario todo `pending_questions[]`.
3. Construye un JSON de respuestas y vuelve a ejecutar:
```bash
python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "<titulo>" --answers-json "<ruta-json>"
```
4. Si `phase=completed`, reporta `written_outputs[]`, metrica e issues.

## Reglas operativas
- Procesa batch de todos los `NN.md` del libro.
- Excluye rutas con `_ignore`.
- Si falta `NN.pdf`, no bloquea el libro: abre issue `critical`.
- Si falta parser PDF, abre issue `major` y continua.
- No usar `input()` ni prompts bloqueantes en script.

## Formato de respuestas
Ver `references/contracts.md`.

## Validaciones recomendadas
```bash
python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py --help
python .codex/skills/adaptacion-ingesta-inicial/scripts/ingesta_inicial.py run --inbox-book-title "El imperio final" --dry-run
```
