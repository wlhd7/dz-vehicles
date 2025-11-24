from flask import Blueprint, render_template, request, jsonify
from vehicles.db import get_db
from .lock import admin_required

bp = Blueprint('gas_card', __name__, url_prefix='/gas_card')


@bp.route('/manage')
@admin_required
def manage():
    db = get_db()
    cards = db.execute('SELECT * FROM gas_cards').fetchall()
    return render_template('gas_card/manage.html', gas_cards=cards)


@bp.post('/add')
@admin_required
def add():
    data = request.get_json()
    if not data:
        return jsonify({'error': '没有接收到数据'}), 400

    card_number = data.get('card_number')
    balance = data.get('balance', 0.0)
    if not card_number:
        return jsonify({'error': '卡号是必填的'}), 400

    try:
        db = get_db()
        cur = db.execute('INSERT INTO gas_cards (card_number, balance) VALUES (?, ?)', (card_number, balance))
        db.commit()
        return jsonify({'message': '添加成功', 'id': cur.lastrowid}), 200
    except Exception as e:
        print(f"添加加油卡错误: {e}")
        return jsonify({'error': '添加失败'}), 500


@bp.post('/delete')
@admin_required
def delete():
    data = request.get_json()
    if not data:
        return jsonify({'error': '没有接收到数据'}), 400
    cid = data.get('id')
    if not cid:
        return jsonify({'error': '卡ID是必填的'}), 400

    try:
        db = get_db()
        db.execute('DELETE FROM gas_cards WHERE id = ?', (cid,))
        db.commit()
        return jsonify({'message': '删除成功', 'id': cid}), 200
    except Exception as e:
        print(f"删除加油卡错误: {e}")
        return jsonify({'error': '删除失败'}), 500