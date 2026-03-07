import threading
from PyQt5.QtCore import QObject, pyqtSignal
import scraper
import data_service

class ThreadingManager(QObject):
    update_progress = pyqtSignal(int)
    log_message = pyqtSignal(str)
    data_ready = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker_thread = None

    # Tambahkan parameter stop_flag berupa list untuk dilempar dari GUI
    def start_scraping_task(self, target_url: str, keywords: list, limit: int, stop_flag: list) -> None:
        if self._worker_thread and self._worker_thread.is_alive():
            self.log_message.emit("[WARNING] Scraping sedang berlangsung.")
            return

        self._worker_thread = threading.Thread(
            target=self._run_engine,
            args=(target_url, keywords, limit, stop_flag), # oper ke args
            daemon=True,
        )
        self._worker_thread.start()

    def _run_engine(self, target_url: str, keywords: list, limit: int, stop_flag: list) -> None:
        try:
            self.log_message.emit("Mencari daftar tautan artikel...")
            self.update_progress.emit(10)

            links = scraper.scrape_tautan(target_url, max_tautan=limit)

            if not links:
                self.error_occurred.emit("Tidak ada artikel ditemukan di URL tersebut.")
                return

            self.update_progress.emit(30)
            hasil_akhir = []

            for i, link in enumerate(links):
                # CEK TOMBOL STOP DI SINI
                if stop_flag[0]:
                    self.log_message.emit("Proses dihentikan oleh pengguna!")
                    break

                self.log_message.emit(f"Mengekstrak ({i+1}/{len(links)}): {link}")
                data = scraper.scrape_konten(link)
                
                if keywords:
                    teks_gabungan = (data['judul'] + data['isi']).lower()
                    cocok = any(k.lower() in teks_gabungan for k in keywords)
                    if cocok:
                        hasil_akhir.append(data)
                        self.log_message.emit(f"✅ Cocok: {data['judul'][:50]}...")
                    else:
                        self.log_message.emit(f"⏩ Lewati (tidak ada keyword): {data['judul'][:50]}...")
                else:
                    hasil_akhir.append(data)

                # PERBAIKAN INDENTASI: Progress bar diupdate di dalam loop
                persen = 30 + int(((i + 1) / len(links)) * 60)
                self.update_progress.emit(persen)

            self.data_ready.emit(hasil_akhir)
            self.update_progress.emit(100)
            self.log_message.emit("✅ Proses Selesai!")

        except Exception as e:
            self.error_occurred.emit(str(e))
            self.log_message.emit(f"[ERROR] {e}")
        finally:
            self._worker_thread = None
