# Project Standards

## Context Engineering Principles
1. Keep source-of-truth files explicit.
2. Separate runtime assets from process documentation.
3. Minimize hidden assumptions by recording decisions.
4. Prefer repeatable commands over ad-hoc manual steps.
5. Keep task scope small, reviewable, and traceable.

## Documentation Layers
1. `AGENTS.md`: execution and governance contract.
2. `docs/adr/`: architectural decisions.
3. `docs/tasks/`: detailed task lifecycle records.
4. `CHANGELOG.md`: short release-facing summary.

## Decision Discipline
1. Record the "why", not only the "what".
2. Use ADRs only when decisions affect structure, contracts, or long-term maintenance.
3. Link task files to related ADRs when applicable.

## Quality Gate
A task is complete when:
1. scope is implemented
2. finite validation was executed
3. task file and index are updated
4. changelog brief entry exists
