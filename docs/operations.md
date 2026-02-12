# Operations

## Safe Command Policy
1. Do not run long-lived commands unless user explicitly asks.
2. Avoid default execution of `runserver` and watch loops.
3. Prefer finite checks (`--help`, scripts, bounded validation commands).

## Validation Policy
1. Run finite, reproducible checks.
2. Record executed checks in the task file.
3. Record limitations and skipped checks with reasons.

## Data Policy
1. SQLite database location: `db/`.
2. DB files are local runtime state and not versioned.
3. Keep import/export commands as repeatable backup mechanisms.

## Change Policy
1. One planned task at a time.
2. Keep edits scoped and reversible.
3. Update task docs, index, and changelog before closure.
