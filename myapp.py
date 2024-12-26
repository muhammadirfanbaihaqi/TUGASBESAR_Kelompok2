from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config.db_config import init_db#MENGIMPORT FUNGSI init_db yang sudah didefinisikan di FILE KONFIGURASI YANG KITA BUAT DI DALAM FOLDER config
import math
import os
from werkzeug.utils import secure_filename
import base64
import random
from datetime import datetime



app = Flask(__name__)
app.secret_key = '123'
mysql = init_db(app) 

# Folder untuk menyimpan file upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_pengguna = request.form['id_pengguna']
        # nama_pengguna = request.form['nama_pengguna']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM msuser WHERE id_petugas = %s", [id_pengguna]) #MENGAMBIL DATA DARI DATABASE BERDASARKAN ID_PENGGUNA
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):  # Verifikasi password
            # MEMBUAT SESSION
            session['loggedin'] = True 
            session['id'] = user[0]
            session['name'] = user[1]
            flash('Login successful!', 'success')
            if user[3] == 'owner':
                return redirect(url_for('checkinOwner'))
            elif user[3] == 'Petugas':
                return redirect(url_for('checkin'))
        else:
            flash('Invalid id or password!', 'danger')

    return render_template('login.html')

@app.route('/checkinOwner', methods=['GET', 'POST'])
def checkinOwner():
    if request.method == 'POST':
        nik = request.form['nik']
        lantai_ke = request.form['lantai_ke']
        kategori = request.form['kategori']
        durasi = int(request.form['durasi'])
        id_petugas = session.get('id')  # ID petugas dari session
        print(id_petugas)
        waktu_checkin = datetime.now()
        id_booking = random.randint(1000, 9999)

        try:
            conn = mysql.connect
            cursor = conn.cursor()
            # Select kamar sesuai kriteria
            cursor.execute(
                """
                SELECT * FROM mskamar 
                WHERE lantai_ke = %s AND kategori = %s AND statuskamar = 'Tersedia'
                LIMIT 1
                """,
                (lantai_ke, kategori)
            )
            kamar = cursor.fetchone()

            if not kamar:
                flash("Tidak ada kamar yang tersedia sesuai kriteria.", "danger")
                return redirect(url_for('checkinOwner'))

            kode_kamar = kamar[0]
            harga_kamar = kamar[2]
            harga_bayar_awal = durasi * harga_kamar

            # Update status kamar
            cursor.execute(
                """
                UPDATE mskamar 
                SET statuskamar = 'Dibooking' 
                WHERE Kode_Kamar = %s
                """,
                (kode_kamar,)
            )
            conn.commit()

            # Insert booking data
            cursor.execute(
                """
                INSERT INTO trbooking (ID_Booking, NIK, ID_Petugas, Kode_Kamar, Waktu_Checkin, Durasi_Hari, HargaBayarAwal) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                (id_booking, nik, id_petugas, kode_kamar, waktu_checkin, durasi, harga_bayar_awal)
            )
            conn.commit()
            flash("Booking berhasil!", "success")

        except Exception as e:
            conn.rollback()
            flash(f"Terjadi kesalahan: {str(e)}", "danger")
        finally:
            conn.close()

        return redirect(url_for('checkinOwner'))

    return render_template('checkinOwner.html')



# @app.route('/checkoutOwner', methods=['GET', 'POST'])
# def checkoutOwner():
#     return render_template('checkoutOwner.html')


@app.route('/booking_listOwner', methods=['GET', 'POST'])
def booking_listOwner():
    return render_template('booking_listOwner.html')



@app.route('/room_listOwner', methods=['GET'])
def room_listOwner():
    per_page = 9
    page = int(request.args.get('page', 1))

    cur = mysql.connection.cursor()

    # Hitung jumlah total kamar
    cur.execute("SELECT COUNT(*) FROM mskamar")
    total_rooms = cur.fetchone()[0]

    total_pages = math.ceil(total_rooms / per_page)
    offset = (page - 1) * per_page

    # Ambil data kamar dengan pagination
    cur.execute(
        "SELECT Kode_Kamar, foto, Kategori, harga_kamar, statuskamar FROM mskamar LIMIT %s OFFSET %s",
        (per_page, offset)
    )
    rooms = cur.fetchall()
    cur.close()

    room_list = [
        {
            'id_kamar': r[0],
            'foto': 'data:image/jpeg;base64,' + base64.b64encode(r[1]).decode('utf-8'),  # Konversi byte ke base64
            'tipe_kamar': r[2],
            'harga_kamar': r[3],
            'statuskamar': r[4],
        }
        for r in rooms
    ]

    return render_template('room_listOwner.html', rooms=room_list, total_pages=total_pages, current_page=page)


# Route untuk menghapus kamar
@app.route('/delete-room/<id>', methods=['POST'])
def delete_room(id):
    try:
        # Koneksi ke database
        conn = mysql.connection
        cur = conn.cursor()

        # Hapus kamar berdasarkan id
        cur.execute("DELETE FROM mskamar WHERE Kode_Kamar = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 200
    except Exception as e:
        print(e)
        return 'Failed to delete room.', 500

# @app.route('/add-room', methods=['POST'])
# def add_room():
#     try:
#         kode_kamar = request.form['kode_kamar']
#         kategori = request.form['kategori']
#         harga_kamar = request.form['harga_kamar']
#         lantai_ke = request.form['lantai_ke']
#         foto = request.files['foto']

#         if foto:
#             filename = secure_filename(foto.filename)
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             foto.save(filepath)

#             # Baca file gambar sebagai byte
#             with open(filepath, 'rb') as file:
#                 byte_data = file.read()

#         conn = mysql.connection
#         cursor = conn.cursor()

#         # Simpan data byte ke database
#         cursor.execute(
#             "INSERT INTO mskamar (Kode_Kamar, Kategori, harga_kamar, foto, lantai_ke) VALUES (%s, %s, %s, %s, %s)",
#             (kode_kamar, kategori, harga_kamar, byte_data, lantai_ke)
#         )
#         conn.commit()

#         cursor.execute("SELECT Kode_Kamar FROM mskamar WHERE Kode_Kamar = %s", (kode_kamar,))
#         room_id = cursor.fetchone()[0]

#         conn.close()

#         return jsonify({
#             'id_kamar': room_id,
#             'kategori': kategori,
#             'harga_kamar': harga_kamar,
#             'foto': filename
#         }), 201
#     except Exception as e:
#         print(e)
#         return 'Failed to add room.', 500

@app.route('/add-room', methods=['POST'])
def add_room():
    try:
        kode_kamar = request.form['kode_kamar']
        kategori = request.form['kategori']
        harga_kamar = request.form['harga_kamar']
        lantai_ke = request.form['lantai_ke']
        foto = request.files['foto']

        if foto:
            filename = secure_filename(foto.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(filepath)

            # Baca file gambar sebagai byte
            with open(filepath, 'rb') as file:
                byte_data = file.read()

        conn = mysql.connection
        cursor = conn.cursor()

        # Simpan data byte ke database
        cursor.execute(
            "INSERT INTO mskamar (Kode_Kamar, Kategori, harga_kamar, foto, lantai_ke) VALUES (%s, %s, %s, %s, %s)",
            (kode_kamar, kategori, harga_kamar, byte_data, lantai_ke)
        )
        conn.commit()

        cursor.close()
        conn.close()

        flash('Berhasil menambahkan kamar!', 'success')
        response = redirect(url_for('room_listOwner'))
        response.headers['X-Success'] = 'true'  # Tambahkan header kustom
        return response
    except Exception as e:
        print(e)
        flash('Gagal menambahkan kamar.', 'danger')
        response = redirect(url_for('room_listOwner'))
        response.headers['X-Success'] = 'false'  # Tambahkan header kustom
        return response



@app.route('/managePetugas', methods=['GET', 'POST'])
def managePetugas():
    if request.method == 'POST':
        # Get form data
        id_petugas = random.randint(1000, 9999)
        nama_user = request.form['nama_user']
        password_user_hashed = request.form['password_user_hashed']
        role = request.form['role']

        # Hash the password
        hashed_password = generate_password_hash(password_user_hashed)

        # Insert new petugas into the database
        try:
            conn = mysql.connection
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO msuser (ID_Petugas, nama_user, password_user_hashed, role) VALUES (%s, %s, %s, %s)",
                (id_petugas, nama_user, hashed_password, role)
            )
            conn.commit()
            cur.close()
            conn.close()

            flash('Petugas baru berhasil ditambahkan!', 'success')
        except Exception as e:
            flash(f'Terjadi kesalahan: {e}', 'danger')
        return redirect(url_for('managePetugas'))
    
    # Fetch all petugas
    try:
        conn = mysql.connection
        cur = conn.cursor()
        cur.execute("SELECT ID_Petugas, nama_user, role FROM msuser")
        users = cur.fetchall()

        # Convert to dictionary
        users = [
            {
                'ID_Petugas': r[0],
                'nama_user': r[1],
                'role': r[2]
            }
            for r in users
        ]

        cur.close()
        # conn.close()
    except Exception as e:
        flash(f'Terjadi kesalahan: {e}', 'danger')
        users = []

    return render_template('managePetugas.html', users=users)


@app.route('/delete-user/<int:id>', methods=['POST'])
def delete_user(id):
    try:
        conn = mysql.connection
        cur = conn.cursor()
        cur.execute("DELETE FROM msuser WHERE ID_Petugas = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 200
    except Exception as e:
        return str(e), 500




@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        nik = request.form['nik']
        lantai_ke = request.form['lantai_ke']
        kategori = request.form['kategori']
        durasi = int(request.form['durasi'])
        id_petugas = session.get('id')  # ID petugas dari session
        print(id_petugas)
        waktu_checkin = datetime.now()
        id_booking = random.randint(1000, 9999)

        try:
            conn = mysql.connect
            cursor = conn.cursor()
            # Select kamar sesuai kriteria
            cursor.execute(
                """
                SELECT * FROM mskamar 
                WHERE lantai_ke = %s AND kategori = %s AND statuskamar = 'Tersedia'
                LIMIT 1
                """,
                (lantai_ke, kategori)
            )
            kamar = cursor.fetchone()

            if not kamar:
                flash("Tidak ada kamar yang tersedia sesuai kriteria.", "danger")
                return redirect(url_for('checkinOwner'))

            kode_kamar = kamar[0]
            harga_kamar = kamar[2]
            harga_bayar_awal = durasi * harga_kamar

            # Update status kamar
            cursor.execute(
                """
                UPDATE mskamar 
                SET statuskamar = 'Dibooking' 
                WHERE Kode_Kamar = %s
                """,
                (kode_kamar,)
            )
            conn.commit()

            # Insert booking data
            cursor.execute(
                """
                INSERT INTO trbooking (ID_Booking, NIK, ID_Petugas, Kode_Kamar, Waktu_Checkin, Durasi_Hari, HargaBayarAwal) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                (id_booking, nik, id_petugas, kode_kamar, waktu_checkin, durasi, harga_bayar_awal)
            )
            conn.commit()
            flash("Booking berhasil!", "success")

        except Exception as e:
            conn.rollback()
            flash(f"Terjadi kesalahan: {str(e)}", "danger")
        finally:
            conn.close()

        return redirect(url_for('checkin'))

    return render_template('checkin.html')


# @app.route('/checkout', methods=['GET', 'POST'])
# def checkout():
#     return render_template('checkout.html')

@app.route('/booking_list', methods=['GET', 'POST'])
def booking_list():
    return render_template('booking_list.html')



@app.route('/room_list', methods=['GET'])
def room_list():
    per_page = 9
    page = int(request.args.get('page', 1))

    cur = mysql.connection.cursor()

    # Hitung jumlah total kamar
    cur.execute("SELECT COUNT(*) FROM mskamar")
    total_rooms = cur.fetchone()[0]

    total_pages = math.ceil(total_rooms / per_page)
    offset = (page - 1) * per_page

    # Ambil data kamar dengan pagination
    cur.execute(
        "SELECT Kode_Kamar, foto, Kategori, harga_kamar, statuskamar FROM mskamar LIMIT %s OFFSET %s",
        (per_page, offset)
    )
    rooms = cur.fetchall()
    cur.close()

    room_list = [
        {
            'id_kamar': r[0],
            'foto': 'data:image/jpeg;base64,' + base64.b64encode(r[1]).decode('utf-8'),  # Konversi byte ke base64
            'tipe_kamar': r[2],
            'harga_kamar': r[3],
            'statuskamar': r[4],
        }
        for r in rooms
    ]

    return render_template('room_list.html', rooms=room_list, total_pages=total_pages, current_page=page)




@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    #The None argument ensures that no error is raised if the key doesn't exist. 
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
