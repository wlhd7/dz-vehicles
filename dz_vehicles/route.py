from flask import render_template, request, jsonify
from .db import get_db


def init_route(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        db = get_db()
        vehicles = db.execute(
                'SELECT * FROM vehicles'
            ).fetchall()
        return render_template('index.html', vehicles=vehicles)


    @app.route('/add-vehicle', methods=['GET', 'POST'])
    def add_vehicle():
        if request.method == 'POST':
            data = request.get_json()

            if not data:
                return jsonify({'error': '没有接受到数据'}), 400

            plate = data.get('plate')
            insurance = data.get('insurance')
            inspection = data.get('inspection')
            maintenance = data.get('maintenance')

            if not all([plate, insurance, inspection, maintenance]):
                return jsonify({'error': '所有字段是必填的'}), 400

            print(f"接受到数据: {plate}, {insurance}, {inspection}, {maintenance}")

            db = get_db()
            db.execute(
                    'INSERT INTO vehicles (plate, insurance, inspection, maintenance)'
                    ' VALUES (?, ?, ?, ?)',
                    (plate, insurance, inspection, maintenance)
                )
            db.commit()

            return jsonify({
                'message': '汽车信息添加成功',
                'data': {
                    'plate': plate,
                    'insurance': insurance,
                    'inspection': inspection,
                    'maintenance': maintenance
                }
            }), 200

        return render_template('add-vehicle.html')


    @app.post('/update-insurance')
    def update_insurance():
        pass


    @app.post('/update-inspection')
    def update_inspection():
        pass


    @app.post('/update-maintenance')
    def update_maintenance():
        pass


    @app.post('/update-mileage')
    def update_mileage():
        data = request.get_json()

        if not data:
            return jsonify({'error': '没有接收到数据'}), 400
        
        vehicle_id = data.get('vehicle_id')
        mileage = data.get('mileage')
        
        if not vehicle_id or not mileage:
            return jsonify({'error': '车辆ID和里程是必填的'}), 400
        
        try:
            db = get_db()
            # 更新数据库中的里程
            db.execute(
                'UPDATE vehicles SET mileage = ? WHERE id = ?',
                (mileage, vehicle_id)
            )
            db.commit()
            
            print(f"更新车辆 {vehicle_id} 的里程为: {mileage}")
            
            return jsonify({
                'message': '里程更新成功',
                'data': {
                    'vehicle_id': vehicle_id,
                    'mileage': mileage
                }
            }), 200
            
        except Exception as e:
            print(f"更新里程错误: {e}")
            return jsonify({'error': '数据库更新失败'}), 500
