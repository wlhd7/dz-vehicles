from flask import Blueprint, render_template, request, jsonify
from vehicles.db import get_db
from .lock import admin_required

bp = Blueprint('vehicle', __name__, url_prefix='/vehicle')


@bp.route('/manage')
@admin_required
def manage():
    db = get_db()
    vehicles = db.execute('SELECT * FROM vehicles').fetchall()
    return render_template('vehicle/manage.html', vehicles=vehicles)
    
    
@bp.post('/add')
@admin_required
def add():
    data = request.get_json()
    if not data:
        return jsonify({'error': '没有接收到数据'}), 400

    plate = data.get('plate')
    insurance = data.get('insurance')
    inspection = data.get('inspection')
    maintenance = data.get('maintenance')

    if not all([plate, insurance, inspection, maintenance]):
        return jsonify({'error': '所有字段是必填的'}), 400

    try:
        db = get_db()
        cur = db.execute(
            'INSERT INTO vehicles (plate, insurance, inspection, maintenance) VALUES (?, ?, ?, ?)',
            (plate, insurance, inspection, maintenance)
        )
        db.commit()
        vid = cur.lastrowid
        return jsonify({'message': '添加成功', 'id': vid}), 200
    except Exception as e:
        print(f"添加车辆错误: {e}")
        return jsonify({'error': '添加失败'}), 500


@bp.post('/delete')
@admin_required
def delete():
    data = request.get_json()
    if not data:
        return jsonify({'error': '没有接收到数据'}), 400

    vehicle_id = data.get('id')
    if not vehicle_id:
        return jsonify({'error': '车辆ID是必填的'}), 400

    try:
        db = get_db()
        db.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
        db.commit()
        return jsonify({'message': '删除成功', 'id': vehicle_id}), 200
    except Exception as e:
        print(f"删除车辆错误: {e}")
        return jsonify({'error': '删除失败'}), 500