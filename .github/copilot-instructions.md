## Purpose

This file gives concise, actionable guidance to AI coding agents working on the `dz-vehicles` Flask project so they can be productive immediately.

## Big Picture

- **App type**: Lightweight Flask web app (package `vehicles`) with an application factory `create_app` in `vehicles/__init__.py`.
- **Data storage**: SQLite database stored under the `instance/` directory (default path: `instance/vehicles.sqlite`). Schema is defined in `vehicles/schema.sql`.
- **Routes & UI**: Server-rendered Jinja templates in `vehicles/templates/` drive the UI; some client-side logic (vanilla JS) calls JSON endpoints (e.g. `/add-vehicle`, `/update-mileage`).

## How to run & common CLI tasks

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

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install flask
    ```

  - Run the app (using Flask CLI with the factory):

    ```bash
    # start server in debug
    flask --app vehicles --debug run

    # or set env and run
    export FLASK_APP=vehicles
    flask run
    ```

  - Initialize the database (CLI command registered in `vehicles/db.py`):

    ```bash
    flask --app vehicles init-db
    ```

    Note: `init-db` reads `vehicles/schema.sql` via `current_app.open_resource('schema.sql')` and writes to `instance/vehicles.sqlite`.

  ## Key files and what they show

  - `vehicles/__init__.py`: application factory; sets `DATABASE` to `os.path.join(app.instance_path, 'vehicles.sqlite')`, loads `instance/config.py` if present, calls `init_db(app)`, and registers blueprints from `vehicles/routes/`.
  - `vehicles/db.py`: sqlite helper functions: `get_db()`, `close_db()`, `init_db()` (registers the `init-db` CLI). Uses `g` and `current_app`.
  - `vehicles/routes/`: package containing route blueprints. Important modules:
    - `vehicles/routes/home.py` — home blueprint that renders `home/index.html`.
    - `vehicles/routes/registration.py` — vehicle CRUD and JSON endpoints like `/registration/add-vehicle`, `/registration/update-mileage`.
    - `vehicles/routes/auth.py` — authentication and identification workflows (register, login, identification application, admin audit endpoints).
  - `vehicles/schema.sql`: DB schema. It now includes `users.is_identified INTEGER DEFAULT 0` and an `applications` table used by the admin-audit flow.
  - `vehicles/templates/`: Jinja templates. Client-side JS uses `fetch` to send JSON to server endpoints (see `templates/add-vehicle.html` and `templates/index.html` scripts).

  ## Conventions & patterns to follow

  - Use the `create_app` factory when starting or testing the app; do not assume a global `app` object.
  - Database access should go through `get_db()` (it uses `g` and returns rows with `sqlite3.Row`).
  - Use blueprint modules under `vehicles/routes/` to add endpoints; register them by adding to `vehicles/routes/__init__.py` if needed.
  - Templates use `url_for('static', filename='...')` and live under `vehicles/static/` and `vehicles/templates/`.
  - JSON endpoints return objects with `message` and/or `error` keys — follow this shape for consistency.

  ## Recent behavior & important app flows

  - Authentication: `vehicles/routes/auth.py` provides `register` and `login` handlers. Passwords are hashed with Werkzeug (`generate_password_hash` / `check_password_hash`).
  - Identification: users apply for identification via `POST /auth/identification`. That creates a row in `applications` with status `pending`.
  - Admin audit: admins review pending applications at `GET /auth/audit` and accept/reject at `POST /auth/audit/decide`. The current code checks `g.user['username'] == 'admin'` to determine admin privileges; consider adding an `is_admin` column to `users` for a robust permission model.

  ## Discovered quirks & things to watch

  - `vehicles/db.py` — `close_db(e=None)` currently rolls back when `e is None` and commits when `e` is present. That is the inverse of the usual pattern (commit on normal shutdown, rollback on exception). Be cautious when changing DB teardown behavior.
  - `vehicles/schema.sql` previously contained a typo `DEFAUTL`; the current file contains `mileage TEXT DEFAULT 'no'` and `is_identified INTEGER DEFAULT 0` — reinitialize the DB to apply schema edits.
  - Admin detection is currently implemented by username equality (`'admin'`); migrating to an `is_admin` column is recommended for correctness.

  ## Typical code tasks examples

  - Add a new endpoint that updates insurance for a vehicle:
    - Add to `vehicles/routes/registration.py` a JSON POST handler `@bp.post('/update-insurance')` accepting `{vehicle_id, insurance}`.
    - Use `db = get_db(); db.execute(...); db.commit()` and return `jsonify({'message': '...','data': {...}})` on success.

  - Implement admin creation helper (common):
    - Add a small CLI command in `vehicles/db.py` to insert an admin user (or run a one-off script). This avoids manual SQLite edits.

  ## DB & local development notes

  - Recreate the DB when you change `vehicles/schema.sql`:
    ```bash
    flask --app vehicles init-db
    ```
    Warning: this drops and recreates tables defined in `schema.sql`.

  - To create an admin quickly (manual example):
    ```python
    from vehicles import create_app
    from vehicles.db import get_db

    app = create_app()
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO users (username, password, is_identified) VALUES (?, ?, ?)",
                   ('admin', generate_password_hash('yourpassword'), 1))
        db.commit()
    ```

  ## Tests & CI

  - There are no tests or CI configuration present. When adding tests, use the `create_app(test_config=...)` factory parameter to provide an isolated `DATABASE` path for tests.

  ## When in doubt

  - Run the app locally and exercise the UI (home/register/login/identification/audit) to validate end-to-end behaviors.
  - Inspect `vehicles/templates/` and `vehicles/routes/` to understand expected JSON shapes and endpoint names before adding/changing handlers.

  ---

  If you want I can: add a `flask` CLI command to create an admin user, migrate admin detection to `is_admin`, or add a small integration test that exercises the identification → audit flow. Tell me which and I'll implement it.

  ````
