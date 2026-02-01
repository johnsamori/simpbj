from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Pengadaan, Penyedia, AnggaranKode, db
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Basic statistics
    stats = {
        'total_paket': Pengadaan.query.count(),
        'total_pagu': db.session.query(func.sum(Pengadaan.nilai_pagu)).scalar() or 0,
        'total_kontrak': db.session.query(func.sum(Pengadaan.nilai_kontrak)).scalar() or 0,
        'total_penyedia': Penyedia.query.count()
    }
    
    # Recent procurement
    recent_pengadaan = Pengadaan.query.order_by(Pengadaan.id.desc()).limit(5).all()

    # Status Chart Data
    status_counts = db.session.query(Pengadaan.status, func.count(Pengadaan.id)).group_by(Pengadaan.status).all()
    chart_data = {'labels': [], 'counts': []}
    for status, count in status_counts:
        chart_data['labels'].append(status)
        chart_data['counts'].append(count)
    
    import datetime
    today = datetime.date.today()
    deadlines = Pengadaan.query.filter(Pengadaan.tgl_selesai >= today).order_by(Pengadaan.tgl_selesai.asc()).limit(10).all()
    
    return render_template('dashboard/index.html', stats=stats, recent=recent_pengadaan, deadlines=deadlines, chart_data=chart_data, today=today)
