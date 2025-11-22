from flask import Blueprint, render_template
from lock import admin_required

bp = Blueprint('vehicle', __name__, url_prefix='/vehicle')

@bp.route('/manage')
@admin_required
def manage():
    

    return render_template('vehicle/manage.html', vehicles=vehicles)