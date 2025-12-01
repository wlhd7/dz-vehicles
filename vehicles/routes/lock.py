from flask import Blueprint, render_template, session, g, flash, redirect, url_for, request
from functools import wraps
from vehicles.db import get_db
import secrets
import string
bp = Blueprint('lock', __name__, url_prefix='/lock')


def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        user = getattr(g, 'user', None)
        if 'user_id' not in session or not user or (user.get('username') if isinstance(user, dict) else user['username']) != 'admin':
            flash('管理员权限不足。')
            return redirect(url_for('auth.login'))
        return view(**kwargs)


    return wrapped_view


@bp.route('/password', methods=('GET', 'POST'))
@admin_required
def password():
    db = get_db()
    message = None
    if request.method == 'POST':
        pw = (request.form.get('password') or '').strip()
        if not pw:
            message = '请输入密码。'
        elif len(pw) != 8:
            message = '密码长度必须为 8 位。'
        else:
            try:
                # avoid inserting duplicate passwords
                exists = db.execute('SELECT id FROM passwords WHERE password = ? LIMIT 1', (pw,)).fetchone()
                if exists:
                    message = '该密码已存在。'
                else:
                    db.execute('INSERT INTO passwords (password) VALUES (?)', (pw,))
                    db.commit()
                    message = '已添加密码。'
            except Exception as e:
                print(f"添加密码错误: {e}")
                message = '添加密码失败。'
    rows = db.execute('SELECT id, password FROM passwords ORDER BY id DESC').fetchall()
    return render_template('lock_password.html', passwords=rows, message=message)

@bp.route('/submit', methods=['POST'])
def submit():
    db = get_db()
    vehicle_plate = (request.form.get('vehicle') or '').strip()
    gas_card_sel = (request.form.get('gasCard') or '').strip()
    gas_card_custom = (request.form.get('gasCard_custom') or '').strip()
    balance = (request.form.get('balance') or '').strip()

    # determine gas card number (prefers custom input if chosen)
    gas_card_number = ''
    if gas_card_sel == 'other' and gas_card_custom:
        gas_card_number = gas_card_custom
    elif gas_card_sel:
        gas_card_number = gas_card_sel

    if not vehicle_plate and not gas_card_number:
        flash('必须选择车辆或加油卡之一才能提交。')
        return redirect(url_for('home.index'))

    try:
        vehicle = None
        gas = None
        if vehicle_plate:
            vehicle = db.execute('SELECT * FROM vehicles WHERE plate = ?', (vehicle_plate,)).fetchone()
            if not vehicle:
                flash('未找到车辆。')
                return redirect(url_for('home.index'))

        if gas_card_number:
            gas = db.execute('SELECT * FROM gas_cards WHERE card_number = ?', (gas_card_number,)).fetchone()
            if not gas:
                flash('未找到加油卡。')
                return redirect(url_for('home.index'))

        # Apply status changes
        if vehicle:
            if vehicle['status'] == 'taken':
                db.execute('UPDATE vehicles SET status = ? WHERE plate = ?', ('returned', vehicle_plate))
            else:
                db.execute('UPDATE vehicles SET status = ? WHERE plate = ?', ('taken', vehicle_plate))

        if gas:
            if gas['status'] == 'taken':
                # When returning a taken gas card, balance is required and must be numeric
                if not balance:
                    flash('归还加油卡请填写余额。')
                    return redirect(url_for('home.index'))
                try:
                    bal_val = float(balance)
                except Exception:
                    flash('请输入有效的余额数字。')
                    return redirect(url_for('home.index'))
                db.execute('UPDATE gas_cards SET balance = ?, status = ? WHERE card_number = ?', (bal_val, 'returned', gas_card_number))
            else:
                db.execute('UPDATE gas_cards SET status = ? WHERE card_number = ?', ('taken', gas_card_number))

        db.commit()

        # Record in record_vehicles and record_gas_cards (keep latest 200 entries)
        try:
            uid = g.user['id'] if getattr(g, 'user', None) else None
            if vehicle and uid is not None:
                old = vehicle['status']
                action = 'returned' if old == 'taken' else 'taken'
                db.execute("INSERT INTO record_vehicles (vehicle_id, user_id, action, timestamp) VALUES (?, ?, ?, datetime('now', '+8 hours'))", (vehicle['id'], uid, action))
                db.execute("DELETE FROM record_vehicles WHERE id NOT IN (SELECT id FROM record_vehicles ORDER BY id DESC LIMIT 200)")
            if gas and uid is not None:
                oldg = gas['status']
                actiong = 'returned' if oldg == 'taken' else 'taken'
                db.execute("INSERT INTO record_gas_cards (user_id, gas_card_id, action, timestamp) VALUES (?, ?, ?, datetime('now', '+8 hours'))", (uid, gas['id'], actiong))
                db.execute("DELETE FROM record_gas_cards WHERE id NOT IN (SELECT id FROM record_gas_cards ORDER BY id DESC LIMIT 200)")
            db.commit()
        except Exception:
            # don't block main flow if logging fails
            try:
                db.rollback()
            except Exception:
                pass

        # Issue/delete a temporary password
        pw_row = db.execute("SELECT id, password FROM passwords ORDER BY id LIMIT 1").fetchone()
        if pw_row:
            issued = pw_row['password']
            try:
                db.execute('DELETE FROM passwords WHERE id = ?', (pw_row['id'],))
                db.commit()
            except Exception:
                issued = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        else:
            issued = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        return redirect(url_for('home.index', password=issued))
    except Exception as e:
        print(f"提交处理错误: {e}")
        flash('处理请求时出错。')

    return redirect(url_for('home.index'))