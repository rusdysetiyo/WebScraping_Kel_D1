import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def setup_webdriver():
    """
    Fungsi untuk menginisialisasi dan mengonfigurasi Selenium WebDriver.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")

    # Optimasi: Load Eager dan Blokir Gambar
    options.page_load_strategy = 'eager'
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)

    # Batas waktu loading 30 detik
    driver.set_page_load_timeout(30)

    return driver

def scrape_tautan(url_utama, max_tautan=10):
    """
    Mengambil tautan artikel dari halaman utama berita.
    """
    driver = setup_webdriver()  
    kumpulan_tautan = []

    try:
        driver.get(url_utama)
        time.sleep(2)

        domain = urlparse(url_utama).netloc

        if "cnnindonesia.com" in domain:
            selector = "a[dtr-id]"
        elif "bbc.com" in domain:
            selector = "a[href*='/articles/']"
        elif "detik.com" in domain:
            selector = "a.media__link, article a"
        else:
            selector = "article a, h3 a"

        elemen_tautan = driver.find_elements(By.CSS_SELECTOR, selector)

        for el in elemen_tautan:
            href = el.get_attribute("href")

            if href and href.startswith("http") and href not in kumpulan_tautan:
                if len(href.split('/')) > 4:
                    kumpulan_tautan.append(href)

            if len(kumpulan_tautan) >= max_tautan:
                break

        return kumpulan_tautan

    except Exception as e:
        print(f"Terjadi kesalahan saat memproses {url_utama}: {e}")
        return []
    finally:
        driver.quit()

def scrape_konten(url):
    """
    Mengunjungi link artikel dan mengambil Judul, Tanggal, dan Isi Berita.
    """
    driver = setup_webdriver()  
    hasil_ekstraksi = {
        "url": url,
        "judul": "Tidak ditemukan",
        "tanggal": "Tidak ditemukan",
        "isi": "Tidak ditemukan"
    }

    try:
        time.sleep(random.uniform(2.0, 4.5))
        driver.get(url)

        domain = urlparse(url).netloc

        if "cnnindonesia.com" in domain:
            sel_judul = "h1"
            sel_tanggal = "div[class*='text-cnn_grey']"
            sel_body = "div[class*='detail-wrap'] p"

        elif "detik.com" in domain:
            sel_judul = "h1"
            sel_tanggal = "div[class*='detail__date'], time, div[class*='text-black-light3']"
            sel_body = "div[class*='detail__body'] p, div[class*='itp_bodycontent'] p, div[class*='detail__body'] h2, div[class*='detail__body'] h3"

        elif "bbc.com" in domain:
            sel_judul = "h1#content, h1[class*='article-heading']"
            sel_tanggal = "time"
            sel_body = "main[role='main'] p, main[role='main'] li"

        else:
            sel_judul = "h1"
            sel_tanggal = "time, .date, .publish-date"
            sel_body = "article p, .content p, article li"

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, sel_judul))
        )

        # Ekstraksi Judul
        elemen_judul = driver.find_elements(By.CSS_SELECTOR, sel_judul)
        if elemen_judul:
            hasil_ekstraksi["judul"] = elemen_judul[0].text.strip()

        # Ekstraksi Tanggal
        elemen_tanggal = driver.find_elements(By.CSS_SELECTOR, sel_tanggal)
        if elemen_tanggal:
            hasil_ekstraksi["tanggal"] = elemen_tanggal[0].text.strip()

        # Ekstraksi Isi Berita
        elemen_paragraf = driver.find_elements(By.CSS_SELECTOR, sel_body)
        if elemen_paragraf:
            kumpulan_teks = []
            for p in elemen_paragraf:
                teks = p.text.strip()
                if teks:
                    kumpulan_teks.append(teks)

            hasil_ekstraksi["isi"] = "\n\n".join(kumpulan_teks)

    except Exception as e:
        print(f"Gagal mengekstrak {url} -> {e}")
    finally:
        driver.quit()

    return hasil_ekstraksi


if __name__ == "__main__":
    print("Mulai proses testing scraper...")

    url_target = "https://www.cnnindonesia.com/nasional/politik"
    batas_link = 3 

    kumpulan_link = scrape_tautan(url_target, max_tautan=batas_link)

    if not kumpulan_link:
        print("Gagal mendapatkan tautan atau daftar tautan kosong.")
    else:
        print(f"Berhasil mendapatkan {len(kumpulan_link)} tautan:")
        for i, link in enumerate(kumpulan_link, 1):
            print(f"  {i}. {link}")

        print("\nMemulai ekstraksi informasi dari masing-masing artikel...")

        for i, link in enumerate(kumpulan_link, 1):
            print(f"\n--- Mengekstrak Artikel ke-{i} ---")
            print(f"URL Target: {link}")

            # Panggil fungsi scrape_konten
            data_artikel = scrape_konten(link)

            # Tampilkan hasilnya
            print(f"Judul   : {data_artikel['judul']}")
            print(f"Tanggal : {data_artikel['tanggal']}")

            # Memotong isi berita agar terminal tidak terlalu penuh saat testing
            isi_preview = data_artikel['isi'][:200].replace('\n', ' ')
            print(f"Isi     : {isi_preview}... [DIPOTONG UNTUK PREVIEW]")

    print("\nProses testing selesai!")
