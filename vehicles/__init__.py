from flask import Flask
import os
from .db import init_db
from .routes import bps

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
           DATABASE=os.path.join(app.instance_path, 'vehicles.sqlite'),
        )

    # Ensure a persistent SECRET_KEY so sessions survive server restarts/reboots.
    # If the user provides SECRET_KEY via instance/config.py or env, that will be used.
    secret_path = os.path.join(app.instance_path, 'secret_key')
    if 'SECRET_KEY' not in os.environ:
        # try to load from instance/secret_key, otherwise generate and persist one
        try:
            if os.path.exists(secret_path):
                with open(secret_path, 'rb') as f:
                    app.config['SECRET_KEY'] = f.read().strip()
            else:
                # generate a random 32-byte key and save it for future runs
                key = os.urandom(32)
                try:
                    # ensure instance path exists; create_app creates it below but be safe
                    os.makedirs(app.instance_path, exist_ok=True)
                    with open(secret_path, 'wb') as f:
                        f.write(key)
                except Exception:
                    # if writing fails, still set the key in-memory
                    pass
                app.config['SECRET_KEY'] = key
        except Exception:
            # last-resort fallback
            app.config['SECRET_KEY'] = os.urandom(32)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    init_db(app)

    for bp in bps:
        app.register_blueprint(bp)

    return app