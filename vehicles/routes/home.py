from flask import Blueprint, render_template
from vehicles.db import get_db

bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    db = get_db()
    vehicles = db.execute('SELECT * FROM vehicles').fetchall()
    gas_cards = db.execute('SELECT * FROM gas_cards').fetchall()
    return render_template('home/index.html', vehicles=vehicles, gas_cards=gas_cards)