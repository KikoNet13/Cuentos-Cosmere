# 0003 - Contrato de importaci?n y respaldo

- Estado: aceptado
- Fecha: 2026-02-12

## Contexto

Los textos narrativos y metadatos de prompts requieren importaci?n y
respaldo predecibles.

## Decisi?n

Adoptar el siguiente contrato:

- Los textos se modelan por p?gina (`numero_pagina`).
- `manage.py import` sincroniza el contenido can?nico.
- Los prompts se respaldan con exportaci?n e importaci?n JSON expl?citas.

## Consecuencias

- Se separan entradas can?nicas y estado de ejecuci?n.
- Existe ruta de recuperaci?n repetible para prompts.
- Requiere disciplina en los comandos de importaci?n y respaldo.
