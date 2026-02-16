---
name: "adaptacion-contexto"
description: "Prepara el contexto base de adaptacion por libro: inventario de inbox, perfil por edad objetivo y limpieza de sidecars legacy."
---

# Skill: adaptacion-contexto

## Objetivo
- Inicializar el flujo editorial con `target_age` obligatorio.
- Detectar propuestas `NN.md` en `library/_inbox/<book>/`.
- Preparar contexto base del libro antes de texto/prompts.

## Script
- `scripts/contexto.py`

## Input CLI
- `--inbox-book-title`
- `--book-rel-path`
- `--target-age`

## Output JSON
- Inventario de propuestas encontradas.
- Perfil de edad activo.
- Contexto base del flujo.
- Resultado de limpieza de sidecars legacy.

## Regla
- No ejecutar logica editorial desde `app/`.
- Si hace falta logica, se implementa dentro de esta skill.

