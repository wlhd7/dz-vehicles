from flask import Flask
from datetime import timedelta
import os
from .db import init_db
from .routes import bps

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # Keep session cookies persistent between device/browser restarts
    # Set a very long lifetime (10 years) so 'permanent' sessions effectively do not expire
    app.permanent_session_lifetime = timedelta(days=3650)
    app.config.from_mapping(
           DATABASE=os.path.join(app.instance_path, 'vehicles.sqlite'),
        )

    secret_path = os.path.join(app.instance_path, 'secret_key')

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Ensure a persistent SECRET_KEY so sessions survive server restarts/reboots.
    # Prefer SECRET_KEY from `app.config` (config.py or test_config) or environment.
    # Only generate/persist a secret if none was provided.
    try:
        if 'SECRET_KEY' not in app.config and 'SECRET_KEY' not in os.environ:
            if os.path.exists(secret_path):
                try:
                    with open(secret_path, 'rb') as f:
                        app.config['SECRET_KEY'] = f.read().strip()
                except Exception:
                    app.config['SECRET_KEY'] = os.urandom(32)
            else:
                # generate and persist a random key
                key = os.urandom(32)
                try:
                    with open(secret_path, 'wb') as f:
                        f.write(key)
                except Exception:
                    pass
                app.config['SECRET_KEY'] = key
    except Exception:
        # fallback
        app.config.setdefault('SECRET_KEY', os.urandom(32))

    init_db(app)

    for bp in bps:
        app.register_blueprint(bp)

    return app