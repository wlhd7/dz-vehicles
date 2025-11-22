from flask import Flask
import os
from .db import init_db
from .routes import bps

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
           DATABASE=os.path.join(app.instance_path, 'vehicles.sqlite'),
        )

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