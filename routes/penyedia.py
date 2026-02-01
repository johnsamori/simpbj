from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from models import Penyedia, db
import pandas as pd
import io
import datetime

penyedia_bp = Blueprint('penyedia', __name__)

@penyedia_bp.route('/')
@login_required
def index():
    items = Penyedia.query.all()
    return render_template('penyedia/index.html', items=items)

@penyedia_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        new_item = Penyedia(
            nama_perusahaan=request.form.get('nama_perusahaan'),
            npwp=request.form.get('npwp'),
            nama_direktur=request.form.get('nama_direktur'),
            alamat=request.form.get('alamat'),
            kota=request.form.get('kota'),
            telepon=request.form.get('telepon'),
            email=request.form.get('email'),
            kualifikasi=request.form.get('kualifikasi'),
            status_aktif=True
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Data penyedia berhasil ditambahkan', 'success')
        return redirect(url_for('penyedia.index'))
    return render_template('penyedia/form.html', item=None)

@penyedia_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    item = Penyedia.query.get_or_404(id)
    if request.method == 'POST':
        item.nama_perusahaan = request.form.get('nama_perusahaan')
        item.npwp = request.form.get('npwp')
        item.nama_direktur = request.form.get('nama_direktur')
        item.alamat = request.form.get('alamat')
        item.kota = request.form.get('kota')
        item.telepon = request.form.get('telepon')
        item.email = request.form.get('email')
        item.kualifikasi = request.form.get('kualifikasi')
        item.status_aktif = True if request.form.get('status_aktif') == 'on' else False
        
        db.session.commit()
        flash('Data penyedia berhasil diperbarui', 'success')
        return redirect(url_for('penyedia.index'))
    return render_template('penyedia/form.html', item=item)

@penyedia_bp.route('/hapus/<int:id>', methods=['POST'])
@login_required
def delete(id):
    item = Penyedia.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Data penyedia berhasil dihapus', 'success')
    return redirect(url_for('penyedia.index'))

@penyedia_bp.route('/export')
@login_required
def export_excel():
    items = Penyedia.query.all()
    data = []
    for item in items:
        data.append({
            'Nama Perusahaan': item.nama_perusahaan,
            'NPWP': item.npwp,
            'Nama Direktur': item.nama_direktur if item.nama_direktur else '',
            'Alamat': item.alamat if item.alamat else '',
            'Kota': item.kota if item.kota else '',
            'Telepon': item.telepon if item.telepon else '',
            'Email': item.email if item.email else '',
            'Kualifikasi': item.kualifikasi if item.kualifikasi else '',
            'Status Aktif': 'Aktif' if item.status_aktif else 'Non-Aktif'
        })
    
    if not data:
        flash('Tidak ada data untuk diekspor', 'warning')
        return redirect(url_for('penyedia.index'))
        
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Penyedia')
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f"Data_Penyedia_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@penyedia_bp.route('/import', methods=['POST'])
@login_required
def import_excel():
    if 'file' not in request.files:
        flash('Tidak ada file yang dipilih', 'danger')
        return redirect(url_for('penyedia.index'))
        
    file = request.files['file']
    if file.filename == '':
        flash('Nama file kosong', 'danger')
        return redirect(url_for('penyedia.index'))
    
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(file)
            imported_count = 0
            
            def get_val(row, col, default=None):
                val = row.get(col)
                if pd.isna(val):
                    return default
                return val

            for index, row in df.iterrows():
                nama_perusahaan = get_val(row, 'Nama Perusahaan')
                npwp = str(get_val(row, 'NPWP'))
                
                if not nama_perusahaan or not npwp:
                    continue
                
                # Check duplicate NPWP
                existing = Penyedia.query.filter_by(npwp=npwp).first()
                if existing:
                    continue

                new_item = Penyedia(
                    nama_perusahaan=nama_perusahaan,
                    npwp=npwp,
                    nama_direktur=get_val(row, 'Nama Direktur'),
                    alamat=get_val(row, 'Alamat'),
                    kota=get_val(row, 'Kota'),
                    telepon=get_val(row, 'Telepon'),
                    email=get_val(row, 'Email'),
                    kualifikasi=get_val(row, 'Kualifikasi', 'Kecil'),
                    status_aktif=True
                )
                db.session.add(new_item)
                imported_count += 1
            
            db.session.commit()
            flash(f'Berhasil mengimpor {imported_count} data penyedia', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengimpor data: {str(e)}', 'danger')
    else:
        flash('Format file harus Excel (.xlsx, .xls)', 'danger')
    
    return redirect(url_for('penyedia.index'))

@penyedia_bp.route('/download-template')
@login_required
def download_template():
    data = [{
        'Nama Perusahaan': 'Contoh: PT. Maju Bersama',
        'NPWP': '01.234.567.8-910.000',
        'Nama Direktur': 'Budi Santoso',
        'Alamat': 'Jl. Merdeka No. 10',
        'Kota': 'Jayapura',
        'Telepon': '08123456789',
        'Email': 'info@majubersama.com',
        'Kualifikasi': 'Kecil'
    }]
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Template Import')
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name="Template_Import_Penyedia.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
