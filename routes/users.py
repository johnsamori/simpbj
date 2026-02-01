from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, UnitKerja, db
from werkzeug.security import generate_password_hash
from utils.decorators import admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@login_required
@admin_required
def index():
    items = User.query.all()
    return render_template('users/index.html', items=items)

@users_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nama = request.form.get('nama')
        role = request.form.get('role')
        unit_kerja_id = request.form.get('unit_kerja_id')
        
        if not unit_kerja_id or unit_kerja_id == '':
            unit_kerja_id = None

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username sudah digunakan', 'danger')
            return redirect(url_for('users.create'))

        new_user = User(
            username=username,
            nama=nama,
            role=role,
            unit_kerja_id=unit_kerja_id
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('User berhasil ditambahkan', 'success')
        return redirect(url_for('users.index'))
    
    units = UnitKerja.query.all()
    return render_template('users/form.html', units=units, item=None)

@users_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    item = User.query.get_or_404(id)
    if request.method == 'POST':
        item.username = request.form.get('username')
        item.nama = request.form.get('nama')
        item.role = request.form.get('role')
        
        unit_kerja_id = request.form.get('unit_kerja_id')
        item.unit_kerja_id = unit_kerja_id if unit_kerja_id and unit_kerja_id != '' else None
        
        password = request.form.get('password')
        if password:
            item.set_password(password)
            
        db.session.commit()
        flash('User berhasil diperbarui', 'success')
        return redirect(url_for('users.index'))
    
    units = UnitKerja.query.all()
    return render_template('users/form.html', units=units, item=item)

@users_bp.route('/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    if current_user.id == id:
        flash('Tidak dapat menghapus diri sendiri', 'danger')
        return redirect(url_for('users.index'))
        
    item = User.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('User berhasil dihapus', 'success')
    return redirect(url_for('users.index'))
