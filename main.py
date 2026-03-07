import sys
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

# Catatan: 
# Anda tidak perlu lagi membuat class AppController secara manual karena 
# semua koneksi sinyal (tm.update_progress, tm.data_ready, dll) 
# sudah dilakukan di dalam MainWindow._connect_signals() pada file gui.py.

def main():
    # Inisialisasi Aplikasi
    app = QApplication(sys.argv)
    
    # Set style ke Fusion agar tampilan modern dan konsisten
    app.setStyle("Fusion")
    
    # Membuat instance window utama (gui.py)
    # Di dalam MainWindow, ThreadingManager sudah otomatis dibuat (self.tm = ThreadingManager())
    window = MainWindow()
    
    # Tampilkan jendela
    window.show()
    
    # Jalankan event loop
    # Gunakan exec_() untuk PyQt5
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()