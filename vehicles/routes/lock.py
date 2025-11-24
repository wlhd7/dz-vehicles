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
        if 'user_id' not in session or not user or user['username'] != 'admin':
            flash('管理员权限不足。')
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view
