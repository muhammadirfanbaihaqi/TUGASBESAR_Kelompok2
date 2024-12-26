from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config.db_config import init_db#MENGIMPORT FUNGSI init_db yang sudah didefinisikan di FILE KONFIGURASI YANG KITA BUAT DI DALAM FOLDER config
import math
import os
from werkzeug.utils import secure_filename
import base64
import random
from datetime import datetime , timedelta
from flask import make_response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

app = Flask(__name__)
app.secret_key = '123'
mysql = init_db(app) 

# Folder untuk menyimpan file upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Struk:
    def __init__(self):
        pass
    @classmethod
    def cetak(cls, booking_id):
        # Ambil data booking berdasarkan ID
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                tr.ID_Booking, tr.nama_pelanggan, tr.ID_Petugas, 
                tr.Kode_Kamar, tr.Waktu_Checkin, tr.Waktu_Checkout, 
                tr.denda, tr.hargafinal
            FROM trbooking tr
            WHERE tr.ID_Booking = %s
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            flash("Data booking tidak ditemukan!", "danger")
            return redirect(url_for('booking_listOwner'))

        # Ambil data dari database
        data = {
            'ID Booking': booking[0],
            'Nama Pelanggan': booking[1],
            'ID Petugas': booking[2],
            'Kode Kamar': booking[3],
            'Waktu Checkin': booking[4].strftime('%Y-%m-%d %H:%M:%S'),
            'Waktu Checkout': booking[5].strftime('%Y-%m-%d %H:%M:%S') if booking[5] else "Belum Checkout",
            'Denda': f"Rp {booking[6]:,.2f}" if booking[6] else "0",
            'Harga Final': f"Rp {booking[7]:,.2f}"
        }

        # Buat file PDF di memori
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle("Struk Booking")

        # Header
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(300, 750, "STRUK BOOKING")
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(300, 735, "Hotel Asahi - Layanan Berkesan untuk Anda")
        pdf.line(50, 720, 550, 720)  # Garis horizontal

        # Konten Struk
        y = 700
        pdf.setFont("Helvetica", 12)
        for key, value in data.items():
            pdf.drawString(70, y, f"{key}:")
            pdf.drawString(200, y, f"{value}")
            y -= 20

        # Footer
        pdf.line(50, 100, 550, 100)  # Garis horizontal
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(300, 80, "Terima kasih telah menggunakan layanan kami!")
        pdf.drawCentredString(300, 65, "Hotel Asahi - Jalan Merdeka No. 123, Kota ABC")

        # Simpan PDF
        pdf.save()
        buffer.seek(0)

        return buffer


    
