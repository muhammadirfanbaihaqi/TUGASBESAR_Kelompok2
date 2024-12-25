from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config.db_config import init_db #MENGIMPORT FUNGSI init_db yang sudah didefinisikan di FILE KONFIGURASI YANG KITA BUAT DI DALAM FOLDER config

app = Flask(__name__)
app.secret_key = '123'
mysql = init_db(app) 

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


@app.route('/room_listOwner', methods=['GET', 'POST'])
def room_listOwner():
    return render_template('room_listOwner.html')


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


@app.route('/room_list', methods=['GET', 'POST'])
def room_list():
    return render_template('room_list.html')




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
