from app import create_app
from models import db, User, UnitKerja, Pengadaan, Penyedia
from werkzeug.security import generate_password_hash
import datetime

app = create_app()

with app.app_context():
    # Create tables
    db.create_all()

    # Seed Unit Kerja
    if not UnitKerja.query.filter_by(kode_unit='UNCEN001').first():
        unit = UnitKerja(kode_unit='UNCEN001', nama_unit='Fakultas Teknik')
        db.session.add(unit)
        db.session.commit()
    
    # Seed User
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            nama='Administrator SIMPBJ',
            role='Admin'
        )
        db.session.add(admin)
        db.session.commit()

    # Seed Penyedia
    if not Penyedia.query.first():
        p1 = Penyedia(
            nama_perusahaan='PT. Papua Maju Terus',
            npwp='01.234.567.8-910.000',
            kualifikasi='Menengah',
            kota='Jayapura',
            status_aktif=True
        )
        db.session.add(p1)
        db.session.commit()

    # Seed Pengadaan
    if not Pengadaan.query.first():
        user = User.query.first()
        pkg1 = Pengadaan(
            kode_paket='PBJ-2026-0001',
            nama_paket='Pengadaan Server Data Center UNCEN',
            tahun_anggaran=2026,
            jenis_pengadaan='Barang',
            metode='Tender',
            sumber_dana='PNBP',
            nilai_pagu=1500000000,
            nilai_hps=1450000000,
            status='Proses',
            tgl_selesai=datetime.date(2026, 6, 30),
            user_id=user.id
        )
        pkg2 = Pengadaan(
            kode_paket='PBJ-2026-0002',
            nama_paket='Pembangunan Gedung Dekanat Baru',
            tahun_anggaran=2026,
            jenis_pengadaan='Konstruksi',
            metode='Tender',
            sumber_dana='APBN',
            nilai_pagu=5000000000,
            nilai_hps=4800000000,
            status='Perencanaan',
            tgl_selesai=datetime.date(2026, 12, 15),
            user_id=user.id
        )
        db.session.add_all([pkg1, pkg2])
        db.session.commit()

    print("Database seeded successfully!")
