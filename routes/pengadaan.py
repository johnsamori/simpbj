from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from models import Pengadaan, Penyedia, AnggaranKode, db
from utils.helpers import log_audit
import datetime
import pandas as pd
import io

pengadaan_bp = Blueprint('pengadaan', __name__)

@pengadaan_bp.route('/')
@login_required
def index():
    items = Pengadaan.query.all()
    return render_template('pengadaan/index.html', items=items)

@pengadaan_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        # Auto-generate kode paket: PBJ-{tahun}-{sequence}
        tahun = request.form.get('tahun_anggaran')
        count = Pengadaan.query.filter_by(tahun_anggaran=tahun).count() + 1
        kode_paket = f"PBJ-{tahun}-{str(count).zfill(4)}"
        
        new_item = Pengadaan(
            kode_paket=kode_paket,
            nama_paket=request.form.get('nama_paket'),
            tahun_anggaran=tahun,
            jenis_pengadaan=request.form.get('jenis_pengadaan'),
            metode=request.form.get('metode'),
            sumber_dana=request.form.get('sumber_dana'),
            nilai_pagu=request.form.get('nilai_pagu', 0),
            nilai_hps=request.form.get('nilai_hps', 0),
            status='Perencanaan',
            user_id=current_user.id
        )
        
        db.session.add(new_item)
        db.session.commit()
        log_audit('CREATE', 'pengadaan', new_item.id, {'nama': new_item.nama_paket})
        flash('Data pengadaan berhasil ditambahkan', 'success')
        return redirect(url_for('pengadaan.index'))
        
    return render_template('pengadaan/form.html')

@pengadaan_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    item = Pengadaan.query.get_or_404(id)
    if request.method == 'POST':
        item.nama_paket = request.form.get('nama_paket')
        item.jenis_pengadaan = request.form.get('jenis_pengadaan')
        item.metode = request.form.get('metode')
        item.sumber_dana = request.form.get('sumber_dana')
        item.nilai_pagu = request.form.get('nilai_pagu')
        item.nilai_hps = request.form.get('nilai_hps')
        item.nilai_kontrak = request.form.get('nilai_kontrak')
        item.status = request.form.get('status')
        
        # Date fields
        if request.form.get('tgl_mulai'):
            item.tgl_mulai = datetime.datetime.strptime(request.form.get('tgl_mulai'), '%Y-%m-%d').date()
        if request.form.get('tgl_selesai'):
            item.tgl_selesai = datetime.datetime.strptime(request.form.get('tgl_selesai'), '%Y-%m-%d').date()
        
        item.no_kontrak = request.form.get('no_kontrak')
        if request.form.get('tgl_kontrak'):
            item.tgl_kontrak = datetime.datetime.strptime(request.form.get('tgl_kontrak'), '%Y-%m-%d').date()
            
        db.session.commit()
        log_audit('UPDATE', 'pengadaan', item.id, {'nama': item.nama_paket})
        flash('Data pengadaan berhasil diperbarui', 'success')
        return redirect(url_for('pengadaan.index'))
        
    return render_template('pengadaan/form.html', item=item)

@pengadaan_bp.route('/hapus/<int:id>')
@login_required
def delete(id):
    item = Pengadaan.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Data pengadaan berhasil dihapus', 'success')
    return redirect(url_for('pengadaan.index'))

@pengadaan_bp.route('/export')
@login_required
def export_excel():
    items = Pengadaan.query.all()
    data = []
    for item in items:
        data.append({
            'Kode Paket': item.kode_paket,
            'Nama Paket': item.nama_paket,
            'Tahun Anggaran': item.tahun_anggaran,
            'Jenis Pengadaan': item.jenis_pengadaan,
            'Metode': item.metode,
            'Sumber Dana': item.sumber_dana,
            'Nilai Pagu': float(item.nilai_pagu) if item.nilai_pagu else 0,
            'Nilai HPS': float(item.nilai_hps) if item.nilai_hps else 0,
            'Nilai Kontrak': float(item.nilai_kontrak) if item.nilai_kontrak else 0,
            'Status': item.status,
            'No Kontrak': item.no_kontrak if item.no_kontrak else ''
        })
    
    if not data:
        flash('Tidak ada data untuk diekspor', 'warning')
        return redirect(url_for('pengadaan.index'))
        
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Pengadaan')
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f"Data_Pengadaan_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@pengadaan_bp.route('/import', methods=['POST'])
@login_required
def import_excel():
    if 'file' not in request.files:
        flash('Tidak ada file yang dipilih', 'danger')
        return redirect(url_for('pengadaan.index'))
        
    file = request.files['file']
    if file.filename == '':
        flash('Nama file kosong', 'danger')
        return redirect(url_for('pengadaan.index'))
    
    if file and file.filename.endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(file)
            imported_count = 0
            
            # Helper to handle NaN/None values from Excel
            def get_val(row, col, default=None):
                val = row.get(col)
                if pd.isna(val):
                    return default
                return val

            for index, row in df.iterrows():
                nama_paket = get_val(row, 'Nama Paket')
                if not nama_paket:
                    continue
                
                tahun = int(get_val(row, 'Tahun Anggaran', datetime.datetime.now().year))
                
                # Check if kode exists by checking our columns
                kode = get_val(row, 'Kode Paket')
                if not kode:
                    # Generate kode
                    count = Pengadaan.query.filter_by(tahun_anggaran=tahun).count() + 1
                    kode = f"PBJ-{tahun}-{str(count).zfill(4)}"
                
                # Check if already exists
                existing = Pengadaan.query.filter_by(kode_paket=kode).first()
                if existing:
                    # Update or skip? Let's skip for now or update if you want.
                    # For simple import, let's just skip duplicates
                    continue

                new_item = Pengadaan(
                    kode_paket=kode,
                    nama_paket=nama_paket,
                    tahun_anggaran=tahun,
                    jenis_pengadaan=get_val(row, 'Jenis Pengadaan', 'Barang'),
                    metode=get_val(row, 'Metode', 'Pengadaan Langsung'),
                    sumber_dana=get_val(row, 'Sumber Dana', 'PNBP'),
                    nilai_pagu=get_val(row, 'Nilai Pagu', 0),
                    nilai_hps=get_val(row, 'Nilai HPS', 0),
                    nilai_kontrak=get_val(row, 'Nilai Kontrak', 0),
                    status=get_val(row, 'Status', 'Perencanaan'),
                    no_kontrak=get_val(row, 'No Kontrak'),
                    user_id=current_user.id
                )
                db.session.add(new_item)
                imported_count += 1
            
            db.session.commit()
            flash(f'Berhasil mengimpor {imported_count} data pengadaan', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal mengimpor data: {str(e)}', 'danger')
    else:
        flash('Format file harus Excel (.xlsx, .xls)', 'danger')
    
    return redirect(url_for('pengadaan.index'))

@pengadaan_bp.route('/download-template')
@login_required
def download_template():
    # Define template data with headers and one sample row
    data = [{
        'Nama Paket': 'Contoh: Pengadaan Laptop Kantor',
        'Tahun Anggaran': 2026,
        'Jenis Pengadaan': 'Barang',
        'Metode': 'E-Purchasing',
        'Sumber Dana': 'PNBP',
        'Nilai Pagu': 50000000,
        'Nilai HPS': 49500000,
        'Nilai Kontrak': 0,
        'Status': 'Perencanaan',
        'No Kontrak': ''
    }]
    
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Template Import')
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name="Template_Import_Pengadaan.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
