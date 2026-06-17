# Migration Notes

This project uses the lightweight runner in `migrations/migrate.py`.

## Rules

- Put migration files in `migrations/versions/`.
- Name files as `NNNN_short_description.py`.
- Each file must expose async `upgrade(conn)` and `downgrade(conn)`.
- Prefer idempotent DDL:
  - Use `CREATE TABLE IF NOT EXISTS` where MySQL supports it.
  - For `ADD COLUMN`, check `information_schema.COLUMNS` first.
  - For indexes and constraints, check `information_schema.STATISTICS` or catch duplicate errors narrowly.
- Keep one logical schema change per migration file.
- Do not edit already-applied migration files except to fix a broken migration before it reaches another environment.
- Run `python migrations/migrate.py --status` before and after schema work.

## Current Caveats

- This is not Alembic; branch merge conflict handling is manual.
- Downgrades are best-effort and should be tested before relying on them.
- Migrations run against the configured `DATABASE_URL`; double-check the target database before applying.
