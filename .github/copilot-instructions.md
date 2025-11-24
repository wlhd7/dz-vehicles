## Purpose

This file gives concise, actionable guidance to AI coding agents and contributors working on the `dz-vehicles` Flask project so they can be productive immediately.

## Big picture

- App type: Lightweight Flask web app (package `vehicles`) using an application factory `create_app` in `vehicles/__init__.py`.
- Data storage: SQLite database stored under the `instance/` directory (default: `instance/vehicles.sqlite`). Canonical schema is `vehicles/schema.sql`.
- UI & routes: Server-rendered Jinja templates in `vehicles/templates/` with small vanilla JS for form UX. Routes live under `vehicles/routes/` (e.g., `home`, `auth`, `lock`).

## Quick start

1. Create and activate a virtualenv:

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

Note: `init-db` loads `vehicles/schema.sql` via `current_app.open_resource('schema.sql')`.

## Key files

- `vehicles/__init__.py`: app factory and blueprint registration.
- `vehicles/db.py`: `get_db()`, `close_db()`, CLI `init-db` helper.
- `vehicles/routes/`: blueprint modules, including `auth.py` and `lock.py`.
- `vehicles/schema.sql`: canonical DB schema.
- `vehicles/templates/`: Jinja templates.

## Important flows & behaviors

- Authentication and identification: `vehicles/routes/auth.py` handles register/login and an identification workflow; `is_identified` flag on `users` is used for gating some flows.
- Temporary passwords and assignments: The app persists temporary passwords in a `passwords` table and records issuances in an `assignments` table. Retrieval and return flows update `vehicles` and `gas_cards` statuses and insert `assignments` rows.
- Resource status semantics: `vehicles.status` and `gas_cards.status` track `taken` vs `returned`; routes rely on these to decide take vs return behavior.

## Conventions & patterns

- Use `create_app(test_config=...)` for tests and manual runs; avoid a global `app` instance.
- Use `get_db()` for DB access; it returns `sqlite3.Row` objects.
- Prefer consistent JSON shapes for API endpoints (e.g., `{message: ..., error: ...}`) when adding JSON routes.

## Troubleshooting & quirks

- `vehicles/db.py` teardown behavior commits when no exception and rolls back on errors; be cautious when changing teardown logic.
- Some routes create tables on-demand with `CREATE TABLE IF NOT EXISTS` for backward compatibility; the canonical schema is `schema.sql`.

## Maintenance recommendations

- Replace admin-by-username checks with an `is_admin` boolean on `users` for proper authorization.
- Consider adding an admin dashboard to manage `passwords` and `assignments`.

## Testing suggestions

- Use a temporary on-disk SQLite DB for integration tests (avoid `:memory:` across multiple connections).
- Use `create_app(test_config={...})` to configure `DATABASE` and `SECRET_KEY` for tests.

## Common tasks

- Add an endpoint: create a blueprint in `vehicles/routes/`, use `get_db()` for DB work, call `db.execute(...)` and `db.commit()`.
- Add `passwords`/`assignments` to schema: update `vehicles/schema.sql` and run `flask --app vehicles init-db` (destructive).

If you want, I can:
- Add the `passwords` and `assignments` DDL to `vehicles/schema.sql` and update `init-db` documentation.
- Implement an `is_admin` migration and update auth checks.
- Add a pytest-based integration test for the take/return/password lifecycle.
## Purpose

This file gives concise, actionable guidance to AI coding agents working on the `dz-vehicles` Flask project so they can be productive immediately.

## Big Picture




- Create a venv and install minimal dependency:

  ````instructions
  ## Purpose

  This file gives concise, actionable guidance to AI coding agents working on the `dz-vehicles` Flask project so they can be productive immediately.

  ## Big Picture

  - **App type**: Lightweight Flask web app (package `vehicles`) using an application factory `create_app` in `vehicles/__init__.py`.
  - **Data storage**: SQLite database stored under the `instance/` directory (default path: `instance/vehicles.sqlite`). Schema is defined in `vehicles/schema.sql`.
  - **Routes & UI**: Server-rendered Jinja templates in `vehicles/templates/` drive the UI; some client-side logic (vanilla JS) calls JSON endpoints (e.g. `/registration/add-vehicle`, `/registration/update-mileage`).

  ## How to run & common CLI tasks

  - Create a venv and install minimal dependency:

    ## Purpose

    Concise, actionable guidance for AI coding agents and contributors working on the `dz-vehicles` Flask project.

    ## Big picture

    - App: Small Flask app packaged as `vehicles` using an application factory `create_app` in `vehicles/__init__.py`.
    - DB: SQLite under `instance/vehicles.sqlite`. Canonical schema is `vehicles/schema.sql` but some tables are created on-demand in code (see notes below).
    - UI: Server-rendered Jinja templates under `vehicles/templates/`. Small client-side scripts (vanilla JS) handle form UX and validation.

    ## Quick start

    1. Create and activate a venv:

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

    Note: `init-db` reads `vehicles/schema.sql` via `current_app.open_resource('schema.sql')`.

    ## Key files

    - `vehicles/__init__.py`: app factory and blueprint registration.
    - `vehicles/db.py`: `get_db()`, `close_db()`, `init_db()` (CLI `init-db`). Uses `g` and `current_app`.
    - `vehicles/routes/`: blueprints for `home`, `auth`, `lock`, `vehicle`, `gas_card`, `registration`.
    - `vehicles/schema.sql`: canonical DB schema (run `init-db` to recreate).
    - `vehicles/templates/`: Jinja templates and light client JS.

    ## Important runtime flows and current behaviors

    - Authentication: `vehicles/routes/auth.py` handles register/login and identification workflows. Passwords are hashed with Werkzeug helpers.
    - Identification: Users apply via `POST /auth/identification`; admins audit at `GET /auth/audit` and decide via `POST /auth/audit/decide`.
    - Temporary passwords and assignments:
      - The app persists temporary passwords in a `passwords` table and records password issuance in an `assignments` table.
        - These tables are included in `vehicles/schema.sql` so `flask --app vehicles init-db` will create them. The route handlers still guard with `CREATE TABLE IF NOT EXISTS` for backward compatibility.
      - Retrieval (`/lock/retrieve`) issues or reuses a password, marks resources `taken`, and inserts an `assignments` row linking the vehicle and/or gas card to the issued password.
      - Return (`/lock/return/<id>`) requires updating mileage and/or gas balance before marking the resource(s) `returned`; the return flow issues a new password immediately (reuses available DB password or generates one) and records an assignment for that issuance.

    - Resource status semantics:
      - `vehicles.status` and `gas_cards.status` are used to track whether a resource is `taken` or `returned`. Routes check these statuses to decide whether to show return forms or block retrievals.

    - Admin detection: currently the code treats the username `admin` as privileged (`g.user['username'] == 'admin'`). For production, add an `is_admin` boolean column to `users` and replace username checks with role checks.

    ## Conventions & patterns

    - Always use `create_app(test_config=...)` when running or testing; do not rely on a global `app` instance.
    - Use `get_db()` for DB access; it returns `sqlite3.Row` objects.
    - Return JSON endpoints with `{message: ..., error: ...}` shape for consistency.

    ## Troubleshooting & quirks

    - `vehicles/db.py` teardown: be cautious — current commit/rollback semantics were changed in this repo and may differ from usual Flask patterns.
    - `base.html` does not render `get_flashed_messages()` by default; some routes pass transient messages using query parameters (e.g., `?password=...`). Consider adding flash rendering to the base template for clearer UX.

    ## Maintenance recommendations

    - `passwords` and `assignments` DDL have been added to `vehicles/schema.sql`. Run `flask --app vehicles init-db` to recreate the DB and include these tables.
    - Replace admin-by-username checks with an `is_admin` column on `users` and update authorization logic.
    - Add an admin dashboard for `assignments` and `passwords` to improve observability and to allow manual correction if needed.

    ## Testing suggestions

    - Manual smoke test sequence:
      1. As admin: add a temporary password via the admin UI (`/lock/password`).
      2. As an identified user: retrieve a password selecting a vehicle and/or gas card; confirm an `assignments` row is recorded and resource `status` becomes `taken`.
      3. Attempt retrieve again without returning: the app should redirect to the return flow.
      4. Return the resource(s) and confirm mileage/balance are updated, resource `status` becomes `returned`, and a password is issued.

    ## Common tasks examples

    - Add an endpoint: use blueprints in `vehicles/routes/`, access DB via `get_db()`, then `db.execute(...)` and `db.commit()`.
    - Add `passwords`/`assignments` to schema: add CREATE TABLE statements into `vehicles/schema.sql` and re-run `flask --app vehicles init-db` (destructive)

    If you want, I can:
    - Add the `passwords` and `assignments` DDL to `vehicles/schema.sql` and update `init-db` documentation,
    - Implement an `is_admin` migration and update auth checks,
    - Add a small pytest-based integration test for take/return/password lifecycle.
