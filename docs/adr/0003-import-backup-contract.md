# 0003 - Import and Backup Contract

- Status: accepted
- Date: 2026-02-12

## Context
Story text and prompt metadata require predictable import/backup behavior.
The project already uses page-based text parsing and prompt JSON backup commands.

## Decision
Adopt the following contract:
- Texts are page-based records (`numero_pagina`) parsed from markdown sources.
- `manage.py import` synchronizes canonical story content.
- Prompt backup is managed through explicit export/import commands.

## Consequences
- Clear separation between canonical inputs and runtime state.
- Repeatable recovery path for prompts.
- Requires disciplined use of import/backup commands.
