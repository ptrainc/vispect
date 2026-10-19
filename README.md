# Vispect — Visual Inspection System

**Vispect** adalah prototipe aplikasi *visual inspection* untuk mengklasifikasikan foto produk ke dalam dua kategori, yaitu **OK** (produk baik) dan **NG** (produk cacat). Aplikasi menyediakan antarmuka pemeriksaan berbasis web serta penyimpanan hasil pemeriksaan agar dapat ditinjau kembali melalui halaman riwayat.

> **Status proyek:** prototipe / pengembangan. Hasil prediksi AI perlu diverifikasi oleh pemeriksa dan belum ditujukan sebagai satu-satunya dasar keputusan kualitas produksi.

## Fitur

- Memilih foto produk atau menyeret (*drag and drop*) gambar ke area unggah.
- Pratinjau gambar sebelum analisis.
- Mendukung file **JPG/JPEG, PNG, dan WEBP** dengan batas ukuran 2 MB pada antarmuka.
- Mengklasifikasikan gambar menjadi **OK** atau **NG** menggunakan model Teachable Machine.
- Menampilkan nilai prediksi untuk kelas OK dan NG serta nilai keyakinan (*confidence*).
- Menyimpan gambar dan hasil prediksi ke MySQL.
- Menampilkan riwayat pemeriksaan yang telah tersimpan.

## Teknologi

- **PHP** — proses backend dan penyimpanan hasil.
- **HTML, CSS, JavaScript** — antarmuka web dan interaksi pengguna.
- **TensorFlow.js** dan **Teachable Machine Image** — menjalankan model klasifikasi gambar di browser.
- **MySQL/MariaDB** — menyimpan riwayat pemeriksaan.
- **XAMPP** — lingkungan pengembangan lokal.

Model saat ini hanya memiliki dua kelas, yaitu `OK` dan `NG`. Kelas `FAILED` untuk gambar yang tidak jelas atau tidak dapat dinilai belum didukung oleh model ini.

## Alur kerja

1. Pengguna memilih atau menyeret foto produk.
2. Browser memvalidasi format dan ukuran gambar, lalu menampilkan pratinjau.
3. Model AI yang dimuat dari folder `ai/` memprediksi gambar di browser.
4. Aplikasi menampilkan prediksi OK/NG, persentase kedua kelas, dan nilai confidence.
5. Gambar serta hasil prediksi dikirim ke endpoint PHP untuk disimpan ke folder `uploads/` dan tabel `pemeriksaan` di database.
6. Data yang berhasil disimpan dapat dilihat di halaman **Riwayat**.

**Catatan:** nilai *confidence* adalah tingkat keyakinan prediksi model untuk gambar yang sedang dianalisis, bukan nilai akurasi model berdasarkan pengujian dataset.

## Struktur proyek

```text
vispect-php/
├── ai/                  # Model Teachable Machine dan metadata
├── config/
│   └── koneksi.php      # Konfigurasi koneksi MySQL
├── css/                 # Stylesheet aplikasi
├── dataset/             # Dataset pendukung proyek
├── includes/
│   └── view.php         # Komponen/layout halaman dan tabel riwayat
├── js/
│   └── script.js        # Validasi gambar, pemuatan model, dan prediksi
├── proses/
│   ├── upload.php       # Menyimpan gambar dan hasil pemeriksaan
│   └── riwayat.php      # Halaman riwayat pemeriksaan
├── uploads/             # Gambar hasil pemeriksaan yang diunggah
├── index.php            # Halaman pemeriksaan
├── inspection.php       # Halaman pemeriksaan tambahan
├── struktur.txt         # Catatan struktur proyek
└── test.php             # File pengujian
```

## Persiapan dan instalasi lokal

### 1. Siapkan aplikasi

Pastikan sudah memasang [XAMPP](https://www.apachefriends.org/) yang menyediakan Apache, PHP, dan MySQL/MariaDB, serta Git jika ingin mengkloning repository.

Buka terminal/CMD, lalu jalankan:

```bash
cd C:\xampp\htdocs
git clone https://github.com/ptrainc/vispect-php.git
```

Jika repository sudah ada di komputer, lewati langkah `git clone` dan pastikan folder proyek berada di `C:\xampp\htdocs\vispect-php`.

### 2. Jalankan Apache dan MySQL

Buka XAMPP Control Panel, lalu klik **Start** pada Apache dan MySQL.

### 3. Buat database

Buka `http://localhost/phpmyadmin`, pilih tab **SQL**, lalu jalankan:

```sql
CREATE DATABASE IF NOT EXISTS visual_inspection
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE visual_inspection;

CREATE TABLE IF NOT EXISTS pemeriksaan (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nama_gambar VARCHAR(255) NOT NULL,
    hasil VARCHAR(20) NOT NULL,
    akurasi DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    persentase_ok DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    persentase_ng DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    tanggal DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

SQL di atas mengikuti kolom yang digunakan oleh kode PHP di repository. Jika database atau tabel sudah ada, periksa strukturnya terlebih dahulu sebelum menjalankan perubahan.

### 4. Periksa konfigurasi database

Buka `config/koneksi.php`. Konfigurasi bawaan menggunakan database `visual_inspection` dan pengguna MySQL `root` tanpa kata sandi, sesuai konfigurasi XAMPP standar. Sesuaikan nilai berikut jika konfigurasi lokal berbeda:

```php
$host = "localhost";
$user = "root";
$password = "";
$database = "visual_inspection";
```

### 5. Pastikan file model tersedia

Periksa bahwa folder `ai/` berisi `model.json`, `metadata.json`, serta semua file bobot model yang dirujuk oleh `model.json`. File-file ini diperlukan untuk menjalankan prediksi.

### 6. Buka aplikasi

Kunjungi:

- Pemeriksaan: [http://localhost/vispect-php/](http://localhost/vispect-php/)
- Riwayat: [http://localhost/vispect-php/proses/riwayat.php](http://localhost/vispect-php/proses/riwayat.php)

Koneksi internet diperlukan saat aplikasi pertama kali memuat pustaka TensorFlow.js dan Teachable Machine dari CDN.

## Catatan dan batasan

- Model yang digunakan saat ini hanya mengklasifikasikan dua kelas: OK dan NG.
- Hasil sangat dipengaruhi kualitas foto, pencahayaan, sudut pengambilan gambar, dan kesesuaian dataset pelatihan.
- Validasi format serta ukuran 2 MB pada antarmuka dilakukan di browser. Validasi sisi server, pembatasan akses, dan pengamanan unggahan perlu ditingkatkan sebelum aplikasi digunakan di lingkungan produksi.
- Backend menyimpan hasil prediksi yang dikirim dari browser; kode PHP tidak menjalankan ulang inferensi model secara mandiri.
- Fitur kamera langsung, pemantauan IoT, dan integrasi Laravel belum dijelaskan sebagai fitur yang tersedia pada versi ini.

## Pengembangan berikutnya

- Menambahkan penanganan gambar yang buram atau tidak dapat dinilai (*FAILED / perlu review*).
- Mengevaluasi model menggunakan dataset uji yang terpisah dan melaporkan metrik evaluasi yang sesuai.
- Memperkuat validasi unggahan, penamaan file, dan keamanan penyimpanan.
- Mengembangkan dukungan kamera langsung serta pemantauan proses inspeksi.
- Mengevaluasi integrasi backend dengan Laravel pada tahap pengembangan berikutnya.

## Kontribusi

Proyek ini masih dalam tahap pengembangan. Saran, pelaporan masalah, dan kontribusi dapat disampaikan melalui [GitHub Issues](https://github.com/ptrainc/vispect-php/issues).
