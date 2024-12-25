# @app.route('/register', methods = ['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         password = request.form['password']

#         #Hash pasword sebelum disimpan ke database
#         hashed_password = generate_password_hash(password)

#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
#         mysql.connection.commit()
#         cur.close()

#         flash('You have succesfully registered! Please log in.', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html')

import mysql.connector
from mysql.connector import Error
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

def koneksi():
    try:
        # Koneksi ke database
        connection = mysql.connector.connect(
            host='localhost',       
            database='hotel',  
            user='root',       
            password='' 
        )
        return connection

    except Error as e:
        print("Error saat mencoba menghubungkan ke MySQL", e)
        return None

class Owner:
    def __init__(self, id, nama, password) -> None:
        self.id = id
        self.nama = nama
        self.password = password
        # Hash password sebelum disimpan ke database
        hashed_password = generate_password_hash(password)
        self.tambahowner(id, nama, hashed_password)

    @classmethod
    def tambahowner(cls, id, nama, hashed_password):
        conn = koneksi()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO msuser (id_petugas, nama_user, password_user_hashed) VALUES (%s, %s, %s)", (id, nama, hashed_password))
                # nama memang memakai kolom id_petugas
                conn.commit()
                print("Owner berhasil ditambahkan")
            except Error as e:
                print("Error saat menambahkan owner:", e)
            finally:
                cur.close()
                conn.close()
            return True
        else:
            return False

def create_owner():
    try:
        id = int(input("Masukkan ID Owner: "))
        nama = input("Masukkan Nama Owner: ")
        password = input("Masukkan Password Owner: ")
        owner = Owner(id, nama, password)
    except ValueError:
        print("Terjadi kesalahan pada inputan! ID harus angka")

if __name__ == '__main__':
    create_owner()
