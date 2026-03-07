import threading
from PyQt5.QtCore import QObject, pyqtSignal
import scraper
import data_service

class ThreadingManager(QObject):
    # progress bar (nilai 0–100)
    update_progress = pyqtSignal(int)

    # nampilin pesan di terminal GUI
    log_message = pyqtSignal(str)

    # pas data hasil scraping siap ditampilin di tabel GUI
    data_ready = pyqtSignal(list)

    # pas muncul error, GUI nampilin notifikasi
    error_occurred = pyqtSignal(str)

    # constructor
    def __init__(self, parent=None):
       
        super().__init__(parent)

        # referensi ke worker thread aktif (None jika lagi ga jalan)
        self._worker_thread: threading.Thread | None = None


    #  publlic method yg bakal dipanggil gui_manager
    def start_scraping_task(self, target_url: str, keywords: list, limit: int) -> None:
    
        # biar ga double-run kalo tombolnya diteken pas scraping masih jalan
        if self._worker_thread and self._worker_thread.is_alive():
            self.log_message.emit(
                "[WARNING] Scraping sedang berlangsung, harap tunggu selesai."
            )
            return

        # buat worker thread; daemon=True biar thread ikut mati
        # kalo aplikasi ditutup paksa oleh pengguna
        self._worker_thread = threading.Thread(
            target=self._run_engine,
            args=(target_url, keywords, limit),
            daemon=True,
        )
        self._worker_thread.start()

    # private method yg bakal jalan di dalem worker thread
    def _run_engine(self, target_url: str, keywords: list, limit: int) -> None:
        try:
            self.log_message.emit("Mencari daftar tautan artikel...")
            self.update_progress.emit(10)

            # 1. Ambil daftar link (Ganti extract_data menjadi scrape_tautan)
            links = scraper.scrape_tautan(target_url, max_tautan=limit)

            if not links:
                self.error_occurred.emit("Tidak ada artikel ditemukan di URL tersebut.")
                return

            self.update_progress.emit(30)
            hasil_akhir = []

            # 2. Ambil konten dari setiap link yang ditemukan
            for i, link in enumerate(links):
                self.log_message.emit(f"Mengekstrak ({i+1}/{len(links)}): {link}")
                
                # Ganti extract_data menjadi scrape_konten
                data = scraper.scrape_konten(link)
                cocok = False
                # Filter sederhana berdasarkan keyword (opsional jika scraper belum filter)
                if keywords:
                    teks_gabungan = (data['judul'] + data['isi']).lower()
                    cocok = False
                    for k in keywords:
                        if k.lower() in teks_gabungan: # .lower() di sini kuncinya
                            cocok = True
                            break
                    if cocok:
                        hasil_akhir.append(data)
                        self.log_message.emit(f"✅ Cocok: {data['judul'][:50]}...")
                    else:
                        self.log_message.emit(f"⏩ Lewati (tidak ada keyword): {data['judul'][:50]}...")
                else:
                    # Jika tidak pakai keyword, masukkan semua
                    hasil_akhir.append(data)

            # Update progress secara dinamis
            persen = 30 + int(((i + 1) / len(links)) * 60)
            self.update_progress.emit(persen)

            # 3. Kirim hasil ke GUI
            self.data_ready.emit(hasil_akhir)
            self.update_progress.emit(100)
            self.log_message.emit("✅ Proses Selesai!")

        except Exception as e:
            self.error_occurred.emit(str(e))
            self.log_message.emit(f"[ERROR] {e}")

        finally:
            self.log_message.emit("Proses selesai, mematikan mesin scraping...")
            self._worker_thread = None