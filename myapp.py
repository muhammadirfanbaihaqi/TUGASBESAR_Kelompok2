from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config.db_config import init_db#MENGIMPORT FUNGSI init_db yang sudah didefinisikan di FILE KONFIGURASI YANG KITA BUAT DI DALAM FOLDER config
import math
import os
from werkzeug.utils import secure_filename


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
            # return redirect(url_for('home'))
            if user[3] == 'owner':
                return redirect(url_for('homeOwner'))
            else:
                return redirect(url_for('homePetugas'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html')

@app.route('/homeOwner', methods=['GET', 'POST'])
def homeOwner():
    return render_template('homeOwner.html')





@app.route('/checkinOwner', methods=['GET', 'POST'])
def checkinOwner():
    return render_template('checkinOwner.html')


@app.route('/checkoutOwner', methods=['GET', 'POST'])
def checkoutOwner():
    return render_template('checkoutOwner.html')


@app.route('/booking_listOwner', methods=['GET', 'POST'])
def booking_listOwner():
    return render_template('booking_listOwner.html')


# @app.route('/room_listOwner', methods=['GET', 'POST'])
# def room_listOwner():
#     return render_template('room_listOwner.html')
# Route untuk menampilkan daftar kamar
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
        "SELECT Kode_Kamar, foto, Kategori, harga_kamar FROM mskamar LIMIT %s OFFSET %s",
        (per_page, offset)
    )
    rooms = cur.fetchall()
    cur.close()

    room_list = [
        {'id_kamar': r['Kode_Kamar'], 'foto': r['foto'], 'tipe_kamar': r['Kategori'], 'harga_kamar': r['harga_kamar']}
        for r in rooms
    ]

    return render_template('room_listOwner.html', rooms=room_list, total_pages=total_pages, current_page=page)

# Route untuk menghapus kamar
@app.route('/delete-room/<id>', methods=['POST'])
def delete_room(id):
    try:

        # Koneksi ke database
        conn = mysql.connection
        cur = mysql.connection.cursor()

        # Hapus kamar berdasarkan id
        cur.execute("DELETE FROM mskamar WHERE Kode_Kamar = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return '', 200
    except Exception as e:
        print(e)
        return 'Failed to delete room.', 500

# Route untuk menambahkan kamar
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

        conn = mysql.connection
        cursor = conn.cursor()

        # Tambah data ke database
        cursor.execute(
            "INSERT INTO mskamar (Kode_Kamar, Kategori, harga_kamar, foto, lantai_ke) VALUES (%s, %s, %s, %s, %s)",
            (kode_kamar, kategori, harga_kamar, filename, lantai_ke)
        )
        conn.commit()

        cursor.execute("SELECT Kode_Kamar FROM mskamar WHERE Kode_Kamar = %s", (kode_kamar,))
        room_id = cursor.fetchone()['Kode_Kamar']

        conn.close()

        return jsonify({
            'id_kamar': room_id,
            'kategori': kategori,
            'harga_kamar': harga_kamar,
            'foto': filename
        }), 201
    except Exception as e:
        print(e)
        return 'Failed to add room.', 500


@app.route('/managePetugas', methods=['GET', 'POST'])
def managePetugas():
    return render_template('managePetugas.html')



@app.route('/homePetugas', methods=['GET', 'POST'])
def homePetugas():
    return render_template('homePetugas.html')

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    return render_template('checkin.html')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html')

@app.route('/booking_list', methods=['GET', 'POST'])
def booking_list():
    return render_template('booking_list.html')


# @app.route('/room_list', methods=['GET', 'POST'])
# def room_list():
#     return render_template('room_list.html')\
@app.route('/room_list', methods=['GET'])
def room_list():
    # Parameters
    per_page = 9
    page = int(request.args.get('page', 1))

    # Connect to database
    cur = mysql.connection.cursor()


    # Count total rooms
    cur.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cur.fetchone()[0]

    # Calculate pagination
    total_pages = math.ceil(total_rooms / per_page)
    offset = (page - 1) * per_page

    # Fetch rooms for the current page
    cur.execute("SELECT id_kamar, foto, tipe_kamar, harga_kamar FROM rooms LIMIT ? OFFSET ?", (per_page, offset))
    rooms = cur.fetchall()
    cur.close()

    # Prepare data for template
    room_list = [
        {'id_kamar': r[0], 'foto': r[1], 'tipe_kamar': r[2], 'harga_kamar': r[3]}
        for r in rooms
    ]

    return render_template(
        'room_list.html',
        rooms=room_list,
        total_pages=total_pages,
        current_page=page
    )




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
