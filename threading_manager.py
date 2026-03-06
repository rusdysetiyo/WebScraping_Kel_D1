import threading
from PyQt5.QtCore import QObject, pyqtSignal
import scraper_core
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
    def start_scraping_task(self, target_url: str, keywords: list) -> None:
    
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
            args=(target_url, keywords),
            daemon=True,
        )
        self._worker_thread.start()

    # private method yg bakal jalan di dalem worker thread
    def _run_engine(self, target_url: str, keywords: list) -> None:

        # `driver` di luar try biar blok 'finally' bisa
        # nutup browser walo ada error sebelum driver dibuat
        driver = None

        try:

            # inisialisasi browser
            self.log_message.emit("Memulai Browser...")
            self.update_progress.emit(10)

            driver = scraper_core.init_driver()

            # ekstraksi data (sama Selenium)
            self.log_message.emit(f"Membuka URL: {target_url}")
            self.update_progress.emit(30)

            raw_data = scraper_core.extract_data(driver, target_url, keywords)

            self.update_progress.emit(60)
            self.log_message.emit(
                f"Data berhasil diekstrak ({len(raw_data)} item), "
                "merapikan format..."
            )

            # cleaning n formatting (sama data_service)
            cleaned_data = data_service.clean_format(raw_data)

            self.update_progress.emit(90)

            # ngirim hasil ke GUI
            self.data_ready.emit(cleaned_data)
            self.update_progress.emit(100)
            self.log_message.emit("✅ Proses Selesai!")

        except Exception as e:
            # utk nampilin error di GUI pas lagi error
            self.error_occurred.emit(str(e))
            self.log_message.emit(f"[ERROR] {e}")

        finally:
            # buat nutup browser (biar chromedriver ga gantung di background)
            if driver is not None:
                scraper_core.close_browser(driver)
                self.log_message.emit("Browser ditutup.")
            # men de-alokasi