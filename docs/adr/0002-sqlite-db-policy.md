# 0002 - Local Data Persistence Policy (SQLite in db/)

- Status: accepted
- Date: 2026-02-12

## Context
The application uses a local SQLite database for runtime state.
The data is environment-specific and should not pollute source control history.

## Decision
Keep SQLite files in `db/` and exclude them from Git:
- `db/*.sqlite`
- `db/*.sqlite-shm`
- `db/*.sqlite-wal`

## Consequences
- Repository remains clean and portable.
- Local state is not preserved by Git automatically.
- Backup/export commands become essential operational tools.
