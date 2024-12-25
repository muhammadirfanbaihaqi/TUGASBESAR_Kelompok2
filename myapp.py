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
        cur.execute("SELECT * FROM users WHERE id_pengguna = %s", [id_pengguna]) #MENGAMBIL DATA DARI DATABASE BERDASARKAN ID_PENGGUNA
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

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    #The None argument ensures that no error is raised if the key doesn't exist. 
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
