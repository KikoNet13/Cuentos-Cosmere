# Git Workflow

## Branch Strategy
- Single branch: `main`.
- No feature branches by default for this project.

## Commit Convention
- One commit per planned task.
- Format: `task(TASK-YYYYMMDD-HHMM): <summary>`.

## Task Closure Checklist
1. Task file updated (`docs/tasks/TASK-*.md`).
2. Task index updated (`docs/tasks/INDEX.md`).
3. Changelog brief updated (`CHANGELOG.md`).
4. Finite validation commands documented.
5. Single closing commit created.

## Local Setup
1. `git init`
2. `git branch -M main`

## Remote Setup (Later)
When GitHub repo is ready:
1. `git remote add origin <repo-url>`
2. `git push -u origin main`
