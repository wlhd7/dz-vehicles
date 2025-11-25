from flask import Blueprint, render_template, request
from vehicles.db import get_db

bp = Blueprint('record', __name__, url_prefix='/record')


@bp.route('/vehicle')
def vehicle():
    db = get_db()
    plate = (request.args.get('plate') or '').strip()
    if plate:
        rows = db.execute(
            """
            SELECT rv.id, rv.action, rv.timestamp, v.plate AS vehicle_plate, u.username
            FROM record_vehicles rv
            LEFT JOIN vehicles v ON rv.vehicle_id = v.id
            LEFT JOIN users u ON rv.user_id = u.id
            WHERE v.plate = ?
            ORDER BY rv.id DESC
            LIMIT 200
            """,
            (plate,)
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT rv.id, rv.action, rv.timestamp, v.plate AS vehicle_plate, u.username
            FROM record_vehicles rv
            LEFT JOIN vehicles v ON rv.vehicle_id = v.id
            LEFT JOIN users u ON rv.user_id = u.id
            ORDER BY rv.id DESC
            LIMIT 200
            """
        ).fetchall()
    return render_template('record/vehicle.html', records=rows, plate=plate)


@bp.route('/gas')
def gas():
    db = get_db()
    card = (request.args.get('card') or '').strip()
    if card:
        rows = db.execute(
            """
            SELECT rg.id, rg.action, rg.timestamp, g.card_number AS gas_card_number, g.balance AS balance, u.username
            FROM record_gas_cards rg
            LEFT JOIN gas_cards g ON rg.gas_card_id = g.id
            LEFT JOIN users u ON rg.user_id = u.id
            WHERE g.card_number = ?
            ORDER BY rg.id DESC
            LIMIT 200
            """,
            (card,)
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT rg.id, rg.action, rg.timestamp, g.card_number AS gas_card_number, g.balance AS balance, u.username
            FROM record_gas_cards rg
            LEFT JOIN gas_cards g ON rg.gas_card_id = g.id
            LEFT JOIN users u ON rg.user_id = u.id
            ORDER BY rg.id DESC
            LIMIT 200
            """
        ).fetchall()
    return render_template('record/gas.html', records=rows, card=card)