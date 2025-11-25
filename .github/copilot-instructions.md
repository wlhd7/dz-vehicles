## Purpose

Concise guidance for contributors and AI assistants working on the `dz-vehicles` Flask project.

## Big picture

- App: Small Flask app packaged as `vehicles` using an application factory `create_app` in `vehicles/__init__.py`.
- DB: SQLite stored at `instance/vehicles.sqlite`. Canonical schema in `vehicles/schema.sql`.
- UI: Server-rendered Jinja templates in `vehicles/templates/` with small vanilla JS.
- Routes: Blueprints under `vehicles/routes/` (notably `auth`, `lock`, `vehicle`, `registration`, `gas_card`).

## Recent notable changes

- Vehicles table simplified: columns like `insurance`, `inspection`, `maintenance`, and `mileage` were removed. The `vehicles` table now stores `plate` and `status` only. Update code and tests to avoid referencing removed columns.
- Temporary-password workflow: passwords are stored in a `passwords` table and issued via assignments recorded in `assignments`. Admins can add passwords via the admin page at `/lock/password` (protected by `admin_required`).

## Quick start

1. Create a venv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install flask
```

2. Run the app:

```bash
export FLASK_APP=vehicles
flask run
```

3. Initialize the DB (destructive):

```bash
flask --app vehicles init-db
```

## Key files

- `vehicles/__init__.py` — app factory and blueprint registration.
- `vehicles/db.py` — `get_db()`, `close_db()`, `init_db()` CLI.
- `vehicles/schema.sql` — canonical DB DDL.
- `vehicles/routes/lock.py` — submit/take/return flows and admin password route.
- `vehicles/templates/` — Jinja templates used by views.
- `tests/` — pytest integration tests.

## Important behaviors and conventions

- Use `create_app(test_config=...)` for tests and ephemeral runs.
- Use `get_db()` for DB access; it returns `sqlite3.Row`.
- `vehicles.status` and `gas_cards.status` track `taken` vs `returned` and drive take/return logic.
- Password issuance: when a password is shown to a user it is deleted from the `passwords` table and an `assignments` row is recorded linking issued password to resources.
- Admin detection: currently done by checking `g.user['username'] == 'admin'`. Consider migrating to an `is_admin` column on `users` for robust RBAC.

## Testing notes

- For integration tests, prefer a temporary on-disk SQLite DB file (avoid `:memory:` across multiple connections).
- Set `SECRET_KEY` in test `create_app` config to use session-based login in tests.
- Update tests to reflect that vehicles no longer have `mileage` or other removed columns.

## Maintenance suggestions

- Add an `is_admin` boolean to `users` and switch `admin_required` checks to use it.
- Add an admin dashboard for `passwords` and `assignments` to allow manual management.
- Keep `vehicles/schema.sql` in sync with code; run `flask --app vehicles init-db` after schema changes.

If you'd like, I can:
- Update tests and templates to remove all references to removed vehicle columns.
- Add a migration script or `README` section describing the schema change.
- Add `is_admin` migration and update authorization checks.
