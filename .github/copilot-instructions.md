## Purpose

Practical contributor guidance for the `dz-vehicles` Flask project. This file explains the app structure, recent schema and workflow changes, testing tips, and recommended maintenance tasks so contributors (and automated assistants) can make safe, consistent edits.

## Big picture

- App: Flask package named `vehicles` using an application factory `create_app` in `vehicles/__init__.py`.
- DB: SQLite (default path `instance/vehicles.sqlite`). Canonical schema lives in `vehicles/schema.sql`.
- UI: Server-rendered Jinja templates in `vehicles/templates/` and small vanilla JS for interactivity.
- Routes: Blueprints live under `vehicles/routes/` (notable files: `auth.py`, `lock.py`, `vehicle.py`, `registration.py`, `gas_card.py`, `record.py`).

## Recent notable changes (summary)

- Vehicles table simplified: removed columns such as `mileage`, `insurance`, `inspection`, and `maintenance`. The `vehicles` table now stores `plate` and `status` only; code and tests must not reference removed columns.
- Password workflow: temporary passwords are stored in `passwords`. When a password is issued it is removed from `passwords` (deleted) and an issuance is recorded in `assignments`.
- Consolidated submit flow: the UI now supports a single submission from the index page that can take/return a vehicle, a gas card, or both in one request. Returning a gas card that was previously `taken` requires a numeric `balance` field and sets the gas card's `status` to `returned`.
- Records: new `record_vehicles` and `record_gas_cards` tables capture recent take/return events (UI pages under `/record` display the most recent entries, capped at 200 per resource).

## Quick start

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
```

2. Install dependencies (project keeps minimal dependencies; Flask is required):

```bash
pip install flask
```

3. Run locally in development mode:

```bash
export FLASK_APP=vehicles
flask run
```

4. Initialize the database (destructive — runs `vehicles/schema.sql`):

```bash
flask --app vehicles init-db
```

Note: If you change `vehicles/schema.sql`, re-run `init-db` in a development environment or write a migration script for production use.

## Key files

- `vehicles/__init__.py` — application factory and blueprint registration.
- `vehicles/db.py` — `get_db()`, `close_db()`, `init_db()` CLI helper.
- `vehicles/schema.sql` — canonical DB schema used by `init-db`.
- `vehicles/routes/lock.py` — core take/return logic and the admin password route at `/lock/password`.
- `vehicles/routes/record.py` — public record listing pages for vehicles and gas cards.
- `vehicles/templates/` — Jinja templates used throughout the app (notable: `home/index.html`, `lock_password.html`, `record/vehicle.html`, `record/gas.html`).
- `vehicles/static/css/` — CSS; some page-specific styles exist under `css/home/` and `css/registration/`.
- `tests/` — pytest integration tests.

## Important behaviors and conventions

- DB access: use `get_db()` (returns `sqlite3.Row`) and prefer parameterized SQL (`?` placeholders) to avoid injection.
- Application factory: use `create_app(test_config=...)` for tests and ephemeral environments.
- Status fields: `vehicles.status` and `gas_cards.status` use the strings `'taken'` and `'returned'` to drive business logic.
- Password issuance: when a password is issued it is removed from `passwords`. An `assignments` row records which user/resource received the password. (If auditability is important, consider switching to marking a password as used rather than deleting it.)
- Records: `record_vehicles` and `record_gas_cards` store recent events for public display; the application trims older rows to keep the latest ~200 entries per table.
- Admin detection: currently implemented by checking `g.user['username'] == 'admin'`. For robust RBAC, add an `is_admin` boolean to the `users` table and update `admin_required` checks.

## Testing notes

- Use an on-disk temporary SQLite DB for integration tests (avoid `:memory:` across multiple connections because Flask tests create separate connections per request).
- Make sure test `create_app` sets a `SECRET_KEY` when using session-based login helpers.
- Update tests to remove assertions or fixtures that expect removed vehicle columns (e.g., `mileage`, `inspection`).
- To run tests locally with pytest:

```bash
pytest -q
```

If tests don't run or report "No tests found", ensure you run `pytest` from the repository root and that `tests/` contains test files prefixed with `test_`.

## Database and migrations

- The project currently uses a single SQL file (`vehicles/schema.sql`) and a destructive `init-db` command. For production or more advanced development, add a migration tool (e.g., Alembic) and keep migration scripts in `migrations/`.
- If you change the schema, update `schema.sql` and the tests, then re-run `flask --app vehicles init-db` in a disposable environment.

## Maintenance suggestions

- Add `is_admin` to the `users` table and update `admin_required` to check that flag rather than comparing usernames.
- Consider marking passwords as `used` with `used_at` instead of deleting rows from `passwords` (improves auditability).
- Add an admin dashboard for `passwords` and `assignments` to manage and audit temporary passwords.
- Add a small migration script or documentation section describing the recent schema simplification (so other contributors know why columns were removed).
- Consolidate shared/global CSS into `vehicles/static/css/global.css` and keep page-specific rules under `css/home/` and `css/registration/`.

## Common tasks

- Start dev server:

```bash
export FLASK_APP=vehicles
flask run
```

- Initialize DB for development:

```bash
flask --app vehicles init-db
```

- Run tests:

```bash
pytest -q
```

## If you need help

- I can update tests and templates to remove references to removed vehicle columns.
- I can add a migration script or migration notes describing the schema changes.
- I can change password deletion behavior to marking `used` with `used_at` and add an admin UI for password management.
- I can create a `global.css` and update `base.html` to include it, moving mobile/responsive rules there.

If you'd like any of the above done, tell me which item to prioritize and I'll implement it.
