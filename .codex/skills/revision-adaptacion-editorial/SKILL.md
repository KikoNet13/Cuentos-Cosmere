---
name: revision-adaptacion-editorial
description: Flujo editorial manual para revisar y adaptar propuestas de `library/_inbox` al contrato canonico `library/.../NN.json`, con comparativa original/current y gestion de alternativas de imagen por slot.
---

# Revision y adaptacion editorial

## Objetivo

Guiar una ingesta editorial manual (sin CLI de ingesta) para convertir propuestas de `_inbox` en cuentos canonicos `NN.json` dentro de `library/`, priorizando calidad narrativa y trazabilidad.

## Cuando usar esta skill

- Cuando tengas propuestas `NN.md` en `library/_inbox/<libro>/`.
- Cuando necesites revisar/adaptar texto y prompts antes de publicar.
- Cuando quieras mantener comparativa `original/current`.
- Cuando quieras gestionar alternativas de imagen y activa por slot.

## Flujo operativo

1. Detectar libro en `library/_inbox/`.
2. Pedir al usuario la ruta destino de nodos (una vez por libro).
3. Procesar cuento por cuento:
   - leer propuesta `NN.md`
   - construir/actualizar `library/<ruta-libro>/NN.json`
   - conservar fuente en `text.original` y `prompt.original`
   - trabajar adaptacion en `text.current` y `prompt.current`
4. Revisar estructura JSON con el checklist.
5. Verificar en webapp:
   - comparativa original/current
   - alternativas activas por slot
6. No usar CLI de ingesta (`inbox-parse`, `inbox-apply`, etc.).

## Politica editorial

- Mantener fidelidad canonica.
- Mejorar claridad y tono infantil cuando aplique.
- Evitar contradicciones internas texto/prompt.
- Documentar cambios relevantes en notas de alternativa o tarea.

## Referencias

- `references/checklist.md`
- `references/esquema-json.md`
- `references/revision-editorial.md`
