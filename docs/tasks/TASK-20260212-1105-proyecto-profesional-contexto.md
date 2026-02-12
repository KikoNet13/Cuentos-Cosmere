# TASK-20260212-1105-proyecto-profesional-contexto

## Metadata
- Task ID: TASK-20260212-1105-proyecto-profesional-contexto
- Date: 2026-02-12 11:05
- Status: done
- Owner: local
- Related ADRs: 0001, 0002, 0003

## Objective
Formalize repository governance and scalable traceability with AGENTS, ADRs, task files, short changelog policy, and folder curation for context assets.

## Context
The repository had runtime code and data but lacked:
- root operating contract
- architectural decision records
- scalable task documentation structure
- git baseline and ignore policy
- curated placement of context and example assets

## Plan
- Create governance documents and templates.
- Create ADR baseline for process/data/import contracts.
- Introduce task tracking structure with index and one task entry.
- Curate `contexto/` and `ejemplos/` into `docs/` structure.
- Initialize Git main-only policy and update ignore rules.

## Decisions
- Use detailed task files plus short changelog entries.
- Keep SQLite under `db/` and ignore local DB files in Git.
- Keep ADR creation limited to architectural decisions.
- Forbid long-lived commands by default in repo contract.

## Changes Applied
- Added root governance files: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `.gitignore`.
- Added process docs: `docs/project_standards.md`, `docs/operations.md`, `docs/git_workflow.md`.
- Added ADR system and initial ADRs in `docs/adr/`.
- Added task system files in `docs/tasks/`.
- Curated context/example assets into `docs/context/` and `docs/assets/style_refs/`.

## Validation Executed
- Repository structure and file existence checks.
- Reference scans to detect stale links to removed html exports.
- Finite command policy preserved (no long-lived server execution).

## Risks
- Some historical markdown content may reference old path conventions and may require incremental editorial cleanup.

## Follow-ups
- Connect remote GitHub and push `main`.
- Add next task file for doc-link normalization and optional UTF-8 cleanup.

## Commit
- Commit message: task(TASK-20260212-1105): profesionalizar gobernanza y trazabilidad
- Commit hash: pending-local-commit
