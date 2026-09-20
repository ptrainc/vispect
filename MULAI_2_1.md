# Visual Inspection 2.1 — MobileNetV2 + SVM

Ekstrak ZIP ke folder baru. Jangan hapus proyek lama, dataset, atau model lama.
Di File Explorer buka folder yang berisi app_v21.py, klik address bar,
ketik powershell lalu Enter. Terminal akan berada di folder yang benar.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements-v21.txt
.\.venv\Scripts\python.exe train_transfer.py
.\.venv\Scripts\python.exe -m streamlit run app_v21.py
```

Internet diperlukan saat pemasangan dan unduhan bobot MobileNetV2 pertama.
Jika unduhan gagal, training berhenti; tidak ada penggantian diam-diam dengan
model acak. Versi ini menggunakan CPU; tidak membutuhkan TensorFlow/CUDA.

## Apa yang berubah

- MobileNetV2 IMAGENET1K_V2 dibekukan sebagai ekstraktor fitur; SVM linear dilatih.
- Grayscale + padding konsisten saat training dan upload; tidak memotong tepi produk.
- Skor SVM bukan persentase. Batas review ±0,5 hanyalah heuristik eksperimen.
- TIDAK DIKENALI memakai kemiripan terhadap referensi. Bukan detektor universal
  BUKAN PRODUK; foto asing bisa lolos, sudut produk baru bisa ditolak.
- FAILED hanya untuk foto hampir tanpa detail atau sangat kecil. Deteksi blur
  dan validasi objek produksi belum tersedia.
- Riwayat 2.1 terpisah dan hasil dibersihkan saat isi gambar berubah.

## Evaluasi jujur

Jalankan pada dataset_base (9 foto asli), bukan dataset augmentasi.
Satu foto sumber beserta semua variasinya dikeluarkan dari training per fold.
Evaluasi dihitung pada 9 foto asli, bukan 135 variasi. Model akhir kemudian
dilatih ulang pada semua 9 foto; menguji ulang foto-foto itu bukan uji independen.
Laporan disimpan ke models/evaluation_transfer.json, termasuk keputusan review.
Foto unit fisik/sesi yang sama masih dapat menyebabkan kebocoran. Belum ada uji
unit baru, validasi batas review, maupun uji penolakan non-produk representatif.
Tidak ada jaminan lebih akurat dibanding Random Forest sebelum uji yang setara.

Gunakan foto asli, hindari gambar generatif yang bisa mengubah komponen.
Kumpulkan OK/NG pada latar sama dan beberapa unit fisik berbeda. Grayscale tidak
menghapus kecerahan/tekstur latar. Semua keputusan harus diperiksa manusia.

Referensi arsitektur: https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.mobilenet_v2.html
