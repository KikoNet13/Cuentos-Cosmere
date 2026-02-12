# 0003 - Contrato de importación y respaldo

- Estado: aceptado
- Fecha: 12/02/26

## Contexto

Los textos narrativos y metadatos de prompts requieren importación y
respaldo predecibles.

## Decisión

Adoptar el siguiente contrato:

- Los textos se modelan por página (`numero_pagina`).
- La cantidad de páginas depende del archivo importado.
- `manage.py import` sincroniza el contenido canónico.
- Los prompts se respaldan con exportación e importación JSON explícitas.

## Consecuencias

- Se separan entradas canónicas y estado de ejecución.
- Existe ruta de recuperación repetible para prompts.
- Requiere disciplina en comandos de importación y respaldo.
