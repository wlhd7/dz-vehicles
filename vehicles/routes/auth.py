from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for, g
)
from functools import wraps
from vehicles.db import get_db
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('请先登录。')
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.pop('user', None)
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        try:
            hashed_password = generate_password_hash(password)
            cur = db.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed_password)
            )
            db.commit()
            # Auto-login the newly created user
            session.clear()
            user_id = cur.lastrowid
            session['user_id'] = user_id
            session.permanent = True

            # Auto-submit identification application and mark user as pending (2)
            try:
                # prevent duplicate pending applications just in case
                existing = db.execute(
                    "SELECT * FROM applications WHERE username = ? AND status = 'pending'",
                    (username,)
                ).fetchone()
                if not existing:
                    db.execute('INSERT INTO applications (username, status) VALUES (?, ?)', (username, 'pending'))
                    db.execute('UPDATE users SET is_identified = 2 WHERE id = ?', (user_id,))
                    db.commit()
                    flash('注册并自动提交了核实申请。', 'success')
                else:
                    flash('注册成功，已有待处理的核实申请。', 'success')
            except Exception as e:
                # don't fail registration if auto-application fails
                db.rollback()
                flash('注册成功，但自动提交核实申请时发生错误，请手动提交核实。', 'warning')
            # Redirect to home (user is already logged in)
            return redirect(url_for('home.index'))
        except sqlite3.IntegrityError:
            flash(f"用户 {username} 已存在。", 'error')

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = '用户名不存在。'
        elif not check_password_hash(user['password'], password):
            error = '密码错误。'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True
            return redirect(url_for('home.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/identification', methods=('GET', 'POST'))
@login_required
def identification():
    """User submits an application for identification. Admin will audit and
    approve/reject. No code is required in this workflow.
    """
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash('请先登录。', 'error')
            return redirect(url_for('auth.login'))

        db = get_db()
        username = g.user['username']

        # prevent duplicate pending applications
        existing = db.execute(
            "SELECT * FROM applications WHERE username = ? AND status = 'pending'",
            (username,)
        ).fetchone()
        if existing:
            flash('核实中，请等待管理员处理。', 'error')
            return redirect(url_for('home.index'))

        db.execute('INSERT INTO applications (username, status) VALUES (?, ?)', (username, 'pending'))
        # mark user as pending (2)
        db.execute('UPDATE users SET is_identified = 2 WHERE username = ?', (username,))
        db.commit()
        flash('申请已提交，请联系网管通过核实。', 'success')
        return redirect(url_for('home.index'))

    return render_template('auth/identification.html')


@bp.route('/audit', methods=('GET',))
@login_required
def audit():
    # admin-only
    if g.user is None or g.user['username'] != 'admin':
        flash('仅管理员可访问。', 'error')
        return redirect(url_for('home.index'))

    db = get_db()
    apps = db.execute("SELECT * FROM applications WHERE status = 'pending'").fetchall()
    return render_template('auth/audit.html', applications=apps)


@bp.route('/audit/decide', methods=('POST',))
@login_required
def audit_decide():
    # admin-only
    if g.user is None or g.user['username'] != 'admin':
        flash('仅管理员可操作。', 'error')
        return redirect(url_for('home.index'))

    app_id = request.form.get('application_id') or (request.get_json() or {}).get('application_id')
    action = request.form.get('action') or (request.get_json() or {}).get('action')
    if not app_id or action not in ('approve', 'reject'):
        flash('参数缺失或不正确。', 'error')
        return redirect(url_for('auth.audit'))

    db = get_db()
    application = db.execute('SELECT * FROM applications WHERE id = ?', (app_id,)).fetchone()
    if not application:
        flash('未找到申请。', 'error')
        return redirect(url_for('auth.audit'))

    username = application['username']
    if action == 'approve':
        try:
            # mark user as approved (1)
            db.execute('UPDATE users SET is_identified = 1 WHERE username = ?', (username,))
            db.execute("UPDATE applications SET status = 'approved' WHERE id = ?", (app_id,))
            db.commit()
            flash(f'已通过 {username} 的申请。', 'success')
        except Exception as e:
            print(f"审核通过更新错误: {e}")
            flash('审核处理失败。', 'error')
    else:
        # mark user as rejected (3)
        db.execute('UPDATE users SET is_identified = 3 WHERE username = ?', (username,))
        db.execute("UPDATE applications SET status = 'rejected' WHERE id = ?", (app_id,))
        db.commit()
        flash(f'已拒绝 {username} 的认证申请。', 'info')

    return redirect(url_for('auth.audit'))