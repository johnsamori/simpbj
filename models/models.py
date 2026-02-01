from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class UnitKerja(db.Model):
    __tablename__ = 'unit_kerja'
    id = db.Column(db.Integer, primary_key=True)
    kode_unit = db.Column(db.String(50), unique=True, nullable=False)
    nama_unit = db.Column(db.String(255), nullable=False)
    
    users = db.relationship('User', backref='unit_kerja', lazy=True)
    anggaran_kode = db.relationship('AnggaranKode', backref='unit_kerja_ref', lazy=True)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nama = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False) # Admin, PPK, Unit Kerja, Viewer
    unit_kerja_id = db.Column(db.Integer, db.ForeignKey('unit_kerja.id'), nullable=True)
    
    pengadaan_ppk = db.relationship('Pengadaan', backref='ppk_user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Penyedia(db.Model):
    __tablename__ = 'penyedia'
    id = db.Column(db.Integer, primary_key=True)
    nama_perusahaan = db.Column(db.String(255), nullable=False)
    npwp = db.Column(db.String(20), unique=True, nullable=False)
    nama_direktur = db.Column(db.String(255))
    alamat = db.Column(db.Text)
    kota = db.Column(db.String(100))
    telepon = db.Column(db.String(20))
    email = db.Column(db.String(100))
    kualifikasi = db.Column(db.String(50)) # Kecil, Menengah, Besar
    status_aktif = db.Column(db.Boolean, default=True)
    catatan = db.Column(db.Text)
    
    pengadaan_list = db.relationship('Pengadaan', secondary='pengadaan_penyedia', back_populates='penyedia_list')

class AnggaranKode(db.Model):
    __tablename__ = 'anggaran_kode'
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(100), unique=True, nullable=False)
    tahun = db.Column(db.Integer, nullable=False)
    deskripsi = db.Column(db.Text)
    unit_kerja_id = db.Column(db.Integer, db.ForeignKey('unit_kerja.id'))
    status_aktif = db.Column(db.Boolean, default=True)

class AnggaranAkun(db.Model):
    __tablename__ = 'anggaran_akun'
    id = db.Column(db.Integer, primary_key=True)
    kode_akun = db.Column(db.String(100), unique=True, nullable=False)
    nama_akun = db.Column(db.String(255), nullable=False)
    kategori = db.Column(db.String(100))
    status_aktif = db.Column(db.Boolean, default=True)

class Pengadaan(db.Model):
    __tablename__ = 'pengadaan'
    id = db.Column(db.Integer, primary_key=True)
    kode_paket = db.Column(db.String(50), unique=True, nullable=False)
    nama_paket = db.Column(db.String(255), nullable=False)
    tahun_anggaran = db.Column(db.Integer, nullable=False)
    jenis_pengadaan = db.Column(db.String(50)) # Barang, Konstruksi, Jasa
    metode = db.Column(db.String(100))
    sumber_dana = db.Column(db.String(50)) # APBN, PNBP
    status = db.Column(db.String(50), default='Perencanaan') # Perencanaan, Proses, Selesai
    
    nilai_pagu = db.Column(db.Numeric(20, 2), default=0)
    nilai_hps = db.Column(db.Numeric(20, 2), default=0)
    nilai_kontrak = db.Column(db.Numeric(20, 2), default=0)
    
    tgl_mulai = db.Column(db.Date)
    tgl_selesai = db.Column(db.Date)
    no_kontrak = db.Column(db.String(100))
    tgl_kontrak = db.Column(db.Date)
    keterangan = db.Column(db.Text)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # PPK
    
    penyedia_list = db.relationship('Penyedia', secondary='pengadaan_penyedia', back_populates='pengadaan_list')
    anggaran_list = db.relationship('AnggaranKode', secondary='pengadaan_anggaran', backref='pengadaan_list')
    akun_list = db.relationship('AnggaranAkun', secondary='pengadaan_anggaran_akun', backref='pengadaan_list')

# Junction tables
pengadaan_penyedia = db.Table('pengadaan_penyedia',
    db.Column('pengadaan_id', db.Integer, db.ForeignKey('pengadaan.id'), primary_key=True),
    db.Column('penyedia_id', db.Integer, db.ForeignKey('penyedia.id'), primary_key=True)
)

pengadaan_anggaran = db.Table('pengadaan_anggaran',
    db.Column('pengadaan_id', db.Integer, db.ForeignKey('pengadaan.id'), primary_key=True),
    db.Column('kode_anggaran_id', db.Integer, db.ForeignKey('anggaran_kode.id'), primary_key=True)
)

pengadaan_anggaran_akun = db.Table('pengadaan_anggaran_akun',
    db.Column('pengadaan_id', db.Integer, db.ForeignKey('pengadaan.id'), primary_key=True),
    db.Column('akun_anggaran_id', db.Integer, db.ForeignKey('anggaran_akun.id'), primary_key=True)
)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(255))
    table_name = db.Column(db.String(100))
    record_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.Text)
