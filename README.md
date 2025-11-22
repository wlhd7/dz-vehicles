dz-vehicles — minimal Flask vehicle info app
=========================================

Quickstart
----------

- Create a virtualenv and install Flask:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -U pip
  pip install flask
  ```

- (Recommended) create `instance/config.py` and set a secure `SECRET_KEY`.
  The project already loads `instance/config.py` automatically. See the example in `instance/config.py`.

- Initialize the database and run the app:

  ```bash
  # create the DB from schema.sql
  flask --app vehicles init-db

  # run in debug mode
  flask --app vehicles --debug run
  ```

About `SECRET_KEY`
------------------

Flask uses `SECRET_KEY` to sign session cookies (and for CSRF if you add Flask-WTF). Do not commit secret keys to source control. Create `instance/config.py` (the folder is created by the application factory) and add a generated secret there. Example generation:

```bash
python - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
```

Security & deployment notes
---------------------------

- For production, prefer injecting a secret from your environment or a secrets manager rather than storing it on disk.
- `vehicles/schema.sql` contains a DROP statement and will recreate the `vehicles` table when you run `flask --app vehicles init-db`.

Support / Development
---------------------

Key files:
- `vehicles/__init__.py` — app factory
- `vehicles/db.py` — sqlite helpers, `init-db` CLI command
- `vehicles/route.py` — request handlers and JSON endpoints
- `vehicles/templates/` — Jinja templates and client-side JS

If you want, I can also:
- Fix the `mileage` column typo in `vehicles/schema.sql` (`DEFAUTL -> DEFAULT`) and reinitialize the DB.
- Add a small test harness or dev Makefile.
