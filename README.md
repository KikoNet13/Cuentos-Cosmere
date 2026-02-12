# Cuentos Cosmere

Small personal project with professional repository governance.

## Stack
- Flask
- Peewee
- SQLite
- HTMX
- Pipenv

## Quick Start
1. `pipenv install`
2. `pipenv run python manage.py init-db`
3. `pipenv run python manage.py migrate-texto-pages`
4. `pipenv run python manage.py import`
5. `pipenv run python manage.py runserver --help`

## Repository Conventions
- Operational contract: `AGENTS.md`
- Task tracking: `docs/tasks/`
- Architecture decisions: `docs/adr/`
- Process standards: `docs/project_standards.md`
- Operations safety: `docs/operations.md`
- Git workflow: `docs/git_workflow.md`

## Data and Content
- Canonical story assets: `biblioteca/`
- Local DB state: `db/` (not versioned)
- Prompt backup JSON: `biblioteca/.../prompts/era1_prompts_data.json`

## Current App Reference
App-specific onboarding remains in `app/README.md`.
