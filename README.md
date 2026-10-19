# Vispect — Visual Inspection AI (Python + Streamlit)

**Vispect** adalah proyek eksperimen *visual inspection* berbasis Python untuk membantu mengelompokkan foto komponen menjadi **OK** atau **NG (Not Good)**. Aplikasi menyediakan antarmuka web lokal menggunakan Streamlit, menampilkan hasil analisis gambar, dan menyimpan riwayat pemeriksaan.

> **Status proyek: eksperimental.** Model dan alur keputusan saat ini belum divalidasi untuk menentukan kelulusan produk di lini produksi. Hasil prediksi harus diperiksa manusia.

## Fitur

- Mengunggah foto produk berformat JPG, JPEG, PNG, WEBP, atau BMP.
- Menganalisis gambar menggunakan MobileNetV2 sebagai ekstraktor fitur dan SVM untuk klasifikasi.
- Menampilkan hasil seperti `OK`, `NG`, `PERLU REVIEW`, `TIDAK DIKENALI`, atau `FAILED`.
- Menyimpan riwayat pemeriksaan secara lokal menggunakan SQLite.
- Menampilkan informasi skor SVM dan kemiripan referensi untuk membantu evaluasi eksperimen.
- Dirancang agar bisa dijalankan di CPU; CUDA tidak diperlukan.

## Teknologi

- **Python** — bahasa pemrograman utama.
- **Streamlit** — antarmuka aplikasi web lokal.
- **PyTorch dan Torchvision** — menjalankan model MobileNetV2 pretrained.
- **scikit-learn** — model klasifikasi SVM.
- **Pillow, NumPy, Pandas, Joblib** — pemrosesan gambar, data, dan penyimpanan model.
- **SQLite** — penyimpanan riwayat inspeksi.

## Alur kerja model

1. Pengguna mengunggah foto melalui aplikasi Streamlit.
2. Gambar diperiksa dan diproses: orientasi EXIF diperbaiki, gambar diubah ke grayscale lalu RGB, dan dipad ke ukuran `224 × 224` tanpa memotong tepi gambar.
3. MobileNetV2 pretrained digunakan untuk mengekstrak fitur visual. Model ini berfungsi sebagai ekstraktor fitur; SVM dilatih untuk membedakan contoh OK dan NG.
4. Aplikasi menggabungkan skor SVM dan pemeriksaan kemiripan terhadap referensi untuk memilih status hasil.
5. Hasil dan informasi pemeriksaan disimpan dalam database SQLite lokal.

**Catatan penting:** skor SVM dan nilai kemiripan **bukan persentase akurasi atau probabilitas**. Batas keputusan `PERLU REVIEW` masih berupa heuristik eksperimen dan belum dikalibrasi.

## Struktur proyek

```text
vispect/
├── app_v21.py                 # Aplikasi Streamlit
├── requirements.txt           # Dependensi utama
├── requirements-v21.txt       # Dependensi versi MobileNetV2 + SVM
├── MULAI_2_1.md               # Catatan instalasi dan evaluasi versi 2.1
├── dataset_base/
│   ├── OK/                    # Foto referensi produk OK
│   └── NG/                    # Foto referensi produk NG
├── models/
│   ├── mobilenet_svm.joblib   # Model terlatih yang digunakan aplikasi
│   └── evaluation_transfer.json  # Laporan evaluasi, jika sudah dibuat
├── src/
│   ├── transfer.py            # Ekstraksi fitur dan aturan keputusan
│   └── database.py            # Penyimpanan riwayat SQLite
└── data/
    └── inspection_v21.db      # Database lokal, dibuat saat aplikasi berjalan
```

Beberapa file di `models/` dan `data/` merupakan hasil proses training atau runtime, sehingga belum tentu tersedia sebelum proyek dijalankan. Struktur di atas menjelaskan peran file/folder yang digunakan oleh versi 2.1.

## Persiapan

Disarankan menggunakan Windows dan Python 3.10 atau versi yang kompatibel dengan dependensi proyek. Instalasi pertama memerlukan koneksi internet untuk mengunduh paket Python dan bobot pretrained MobileNetV2.

### 1. Clone repository

```bash
git clone https://github.com/ptrainc/vispect.git
cd vispect
```

Atau unduh repository sebagai ZIP dari GitHub, lalu ekstrak ke folder kerja.

### 2. Buat virtual environment

Di PowerShell pada folder proyek:

```powershell
python -m venv .venv
```

### 3. Instal dependensi untuk CPU

Gunakan Python dari virtual environment agar paket terpasang di lingkungan proyek:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements-v21.txt
```

File `requirements-v21.txt` juga memasang dependensi yang tercantum di `requirements.txt`.

### 4. Siapkan dataset

Tempatkan foto asli di folder berikut:

```text
dataset_base/
├── OK/
└── NG/
```

Gunakan foto nyata dengan variasi unit, sudut, dan kondisi pengambilan yang relevan. Usahakan pencahayaan serta latar belakang kedua kelas seimbang. Jangan memasukkan beberapa variasi dari foto sumber yang sama ke data training dan evaluasi sekaligus.

### 5. Latih model

Catatan setup versi 2.1 merujuk pada skrip `train_transfer.py` di folder utama proyek. Jika skrip tersebut tersedia di salinan lokal, jalankan:

```powershell
.\.venv\Scripts\python.exe train_transfer.py
```

Skrip training perlu menghasilkan file model `models/mobilenet_svm.joblib` agar aplikasi dapat melakukan prediksi. **Jika `train_transfer.py` atau file model tersebut tidak ada, tahap training belum dapat dijalankan dan aplikasi tidak akan bisa melakukan analisis prediksi sampai file yang diperlukan tersedia.**

### 6. Jalankan aplikasi

```powershell
.\.venv\Scripts\python.exe -m streamlit run app_v21.py
```

Streamlit akan menampilkan alamat lokal di terminal, biasanya `http://localhost:8501`. Buka alamat tersebut di browser.

## Status hasil

| Status | Makna dalam eksperimen |
|---|---|
| `OK` | Model menilai foto cenderung cocok dengan kelas OK. Tetap verifikasi secara manual. |
| `NG` | Model menilai foto cenderung cocok dengan kelas NG. Periksa kondisi komponen. |
| `PERLU REVIEW` | Skor dekat batas keputusan; perlu pemeriksaan manusia. |
| `TIDAK DIKENALI` | Foto kurang mirip dengan referensi training. Ini **tidak** membuktikan bahwa foto bukan produk. |
| `FAILED` | Foto terlalu kecil atau hampir tidak memiliki detail yang bisa digunakan. Ambil ulang gambar. |

Status tersebut merupakan hasil dari aturan eksperimen, bukan sertifikasi mutu produk.

## Evaluasi dan keterbatasan

- Catatan versi 2.1 menjelaskan eksperimen awal dengan **9 foto asli**. Jumlah ini terlalu kecil untuk menyimpulkan performa pada kondisi nyata.
- Evaluasi pada dataset kecil dapat memberikan gambaran yang terlalu optimistis, khususnya bila beberapa foto berasal dari unit atau sesi pengambilan yang sama.
- Grayscale mengurangi informasi warna, tetapi tidak menghilangkan pengaruh tekstur, latar belakang, dan pencahayaan.
- Penolakan gambar asing belum diuji dengan kumpulan gambar non-produk yang representatif; foto produk dari sudut baru juga bisa ditandai tidak dikenali.
- Deteksi blur dan validasi objek yang andal belum tersedia.
- Versi ini belum merupakan sistem inspeksi kamera langsung, IoT, atau sistem otomatis untuk meloloskan produk produksi.

Untuk evaluasi yang lebih kuat, kumpulkan lebih banyak foto asli dari beberapa unit fisik, pisahkan data training dan pengujian berdasarkan unit/sesi bila memungkinkan, lalu laporkan metrik evaluasi pada data uji yang benar-benar terpisah.

## Keamanan

File model Joblib dapat menjalankan kode saat dimuat. Jalankan aplikasi hanya dengan file model yang dibuat sendiri atau berasal dari sumber yang dipercaya; jangan memuat file `.joblib` yang tidak dikenal.

## Pengembangan berikutnya

- Menambah dataset OK/NG yang representatif dan mengevaluasi model dengan data uji independen.
- Meninjau dan mengkalibrasi aturan `PERLU REVIEW` serta `TIDAK DIKENALI`.
- Menambah validasi kualitas gambar dan pencatatan evaluasi model.
- Mengeksplorasi integrasi kamera langsung dan monitoring IoT setelah validasi model memadai.

## Repository

- Source code: https://github.com/ptrainc/vispect
- Catatan setup dan evaluasi: [`MULAI_2_1.md`](MULAI_2_1.md)

---

Dibuat sebagai proyek pembelajaran dan eksperimen AI untuk visual inspection.
