from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import AnggaranKode, AnggaranAkun, db

anggaran_bp = Blueprint('anggaran', __name__)

@anggaran_bp.route('/')
@login_required
def index():
    kode_items = AnggaranKode.query.all()
    akun_items = AnggaranAkun.query.all()
    return render_template('anggaran/index.html', kode_items=kode_items, akun_items=akun_items)

@anggaran_bp.route('/tambah-kode', methods=['GET', 'POST'])
@login_required
def create_kode():
    if request.method == 'POST':
        new_item = AnggaranKode(
            kode=request.form.get('kode'),
            tahun=request.form.get('tahun'),
            deskripsi=request.form.get('deskripsi'),
            status_aktif=True
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Data kode anggaran berhasil ditambahkan', 'success')
        return redirect(url_for('anggaran.index'))
    return render_template('anggaran/form_kode.html', item=None)

@anggaran_bp.route('/edit-kode/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_kode(id):
    item = AnggaranKode.query.get_or_404(id)
    if request.method == 'POST':
        item.kode = request.form.get('kode')
        item.tahun = request.form.get('tahun')
        item.deskripsi = request.form.get('deskripsi')
        item.status_aktif = True if request.form.get('status_aktif') == 'on' else False
        
        db.session.commit()
        flash('Data kode anggaran berhasil diperbarui', 'success')
        return redirect(url_for('anggaran.index'))
    return render_template('anggaran/form_kode.html', item=item)

@anggaran_bp.route('/hapus-kode/<int:id>', methods=['POST'])
@login_required
def delete_kode(id):
    item = AnggaranKode.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Data kode anggaran berhasil dihapus', 'success')
    return redirect(url_for('anggaran.index'))
