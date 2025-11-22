import sqlite3
from flask import g, current_app
import click
from datetime import datetime


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory=sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        # Normal pattern: commit when there was no exception, rollback on error.
        if e is None:
            try:
                db.commit()
            except Exception:
                # If commit fails, ensure the connection is closed.
                pass
        else:
            db.rollback()

        db.close()


def init_database():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


@click.command('init-db')
def init_db_command():
    init_database()
    click.echo('Initialized the database')


sqlite3.register_converter('timestamp', lambda v: datetime.fromisoformat(v.decode()))


def init_db(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
