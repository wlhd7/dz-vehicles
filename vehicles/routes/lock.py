from flask import Blueprint, render_template, session, g, flash, redirect, url_for, request
from functools import wraps

bp = Blueprint('lock', __name__, url_prefix='/lock')


def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        user = getattr(g, 'user', None)
        if 'user_id' not in session or not user or user['username'] != 'admin':
            flash('管理员权限不足。')
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


pws = []


@bp.route('/password', methods=['GET', 'POST'])
@admin_required
def password():
    global pws

    if request.method == 'POST' and request.form.get('action') == 'add_password':
        new_password = request.form['new_password']
        pws.append(new_password)
        flash(f'密码{new_password}已添加。')
        return redirect(url_for('lock.password', added=1))

    if request.method == 'POST' and request.form.get('action') == 'get_password':
        if pws:
            password = pws.pop(0)
            flash(f'取出密码: {password}')
            return redirect(url_for('lock.password', password=password))
        else:
            flash('没有可用密码。')
            return redirect(url_for('lock.password'))

    return render_template('lock/password.html')


@bp.route('/retrieve', methods=['POST'])
def retrieve():
    """Allow identified users (or admin) to retrieve a password from the queue.

    This is intended to be used from the home page (index.html).
    """
    global pws

    user = getattr(g, 'user', None)
    if 'user_id' not in session or not user:
        flash('请先登录。')
        return redirect(url_for('auth.login'))

    is_admin = (user['username'] == 'admin')
    try:
        raw = user['is_identified'] if 'is_identified' in user.keys() else 0
        identified = int(raw or 0) == 1
    except Exception:
        identified = False

    if not (identified or is_admin):
        flash('只有已认证用户或管理员可以获取密码。')
        return redirect(url_for('home.index'))

    if pws:
        password = pws.pop(0)
        return redirect(url_for('home.index', password=password))
    else:
        flash('没有可用密码。')
        return redirect(url_for('home.index'))