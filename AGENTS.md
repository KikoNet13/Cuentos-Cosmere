# AGENTS.md

## Purpose
This repository is a personal but professional project. Work must optimize for:
- clear context
- reproducible decisions
- safe operation
- traceable task outcomes

## Operational Rules
1. Do not run long-lived commands unless explicitly requested by the user.
2. `runserver`, watchers, and interactive loops are forbidden by default.
3. Prefer one-shot checks (`--help`, finite scripts, bounded validation).
4. Before destructive actions, confirm intent in task docs and commit scope.
5. Keep changes scoped to one planned task at a time.

## Validation Rules
1. Prefer finite validation commands with explicit time bounds.
2. Record what was validated in the task file.
3. If a check cannot be run, document the gap and reason.

## Documentation System
1. Task details live in `docs/tasks/TASK-*.md`.
2. Task index lives in `docs/tasks/INDEX.md`.
3. Architectural decisions live in `docs/adr/`.
4. `CHANGELOG.md` stays short and links to task files.

## ADR Policy
Create an ADR only for architectural decisions, such as:
- data model or persistence policy changes
- import/export contracts
- repository-wide process or governance changes

Allowed ADR status:
- proposed
- accepted
- superseded
- obsolete

## Git Workflow (Main-only)
1. Single branch policy: `main` only.
2. One commit per planned task.
3. Commit message format:
- `task(TASK-YYYYMMDD-HHMM): <short-summary>`
4. No feature branches by default.

## Data Policy
1. SQLite stays in `db/`.
2. Database files are local state and should not be versioned.
3. Keep backup/export flows documented and repeatable.

## Context Hygiene
1. Keep active context in `docs/context/`.
2. Remove generated or redundant exports when canonical markdown exists.
3. Keep visual references in `docs/assets/style_refs/`.
