# data_service.py
import csv
import os
from datetime import datetime

def format_date(raw_date):
    """Menstandarisasi format tanggal (Fungsi Helper)."""
    # Contoh sederhana: Membersihkan teks tanggal dari karakter aneh
    return raw_date.strip() if raw_date else "N/A"

def export_to_csv(data_list, filename="hasil_scraping.csv"):
    """
    Menyimpan list of dict ke dalam file CSV.
    Return: bool (Success status).
    """
    if not data_list:
        return False
        
    keys = data_list[0].keys()
    file_exists = os.path.isfile(filename)
    
    try:
        # Menggunakan mode 'a' (append) agar data baru tidak menghapus data lama
        with open(filename, 'a', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            if not file_exists:
                dict_writer.writeheader()  # Tulis header jika file baru
            dict_writer.writerows(data_list)
        return True
    except Exception as e:
        print(f"Error saat menyimpan CSV: {e}")
        return False