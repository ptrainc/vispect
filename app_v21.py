import hashlib
import io
from pathlib import Path
import joblib
import numpy as np
import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError
from src.transfer import embed, decide
from src.database import init_database, save_inspection, get_history

ROOT = Path(__file__).resolve().parent
MODEL = ROOT/'models/mobilenet_svm.joblib'
DB = ROOT/'data/inspection_v21.db'
st.set_page_config(page_title='Visual Inspection 2.1',page_icon='🔍',layout='wide')
init_database(DB)
st.title('Visual Inspection 2.1')
st.caption('MobileNetV2 + SVM · Eksperimen 9 foto · Bukan sistem pelolosan produksi')

@st.cache_resource
def load_model(stamp):
    return joblib.load(MODEL)  # Only load models trained by you, never untrusted joblib.

bundle = load_model(MODEL.stat().st_mtime_ns) if MODEL.exists() else None
with st.sidebar:
    st.subheader('Model 2.1')
    st.write('MobileNetV2 pretrained → SVM')
    st.info('Skor SVM bukan persen akurasi atau probabilitas.')
    if bundle is not None:
        st.write(f"Foto sumber: {len(bundle['names'])}")
    st.caption('TIDAK DIKENALI berarti jauh dari contoh latihan; belum membuktikan gambar bukan produk.')

inspection, history, guide = st.tabs(['Pemeriksaan','Riwayat','Cara belajar'])
with inspection:
    if bundle is None:
        st.warning('Model 2.1 belum dilatih. Jalankan train_transfer.py dahulu.')
    left,right = st.columns(2)
    with left:
        file = st.file_uploader('Foto produk',type=['jpg','jpeg','png','webp','bmp'])
        im = None
        key = None
        if file:
            try:
                raw = file.getvalue()
                if len(raw) > 20*1024*1024:
                    raise ValueError('Maksimal 20 MB.')
                im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB')
                key = hashlib.sha256(raw).hexdigest()+str(MODEL.stat().st_mtime_ns if MODEL.exists() else 0)
                st.image(im,use_container_width=True)
            except (OSError,UnidentifiedImageError,ValueError,Image.DecompressionBombError) as e:
                st.error(f'Gambar tidak dapat dibaca: {e}')
    with right:
        st.subheader('Hasil pemeriksaan')
        if st.button('Analisis gambar',type='primary',disabled=im is None or bundle is None):
            try:
                with st.spinner('Membaca ciri produk...'):
                    gray = np.asarray(im.convert('L'),dtype=float)
                    # Only hard fail on near-empty / unusably tiny images; no brightness-only rejection.
                    if min(im.size)<32 or gray.std()<0.5:
                        result = dict(status='FAILED',margin=None,similarity=None)
                    else:
                        features = embed([im])
                        margin = float(bundle['model'].decision_function(features)[0])
                        similarity = float((bundle['references'] @ features[0]).max())
                        result = dict(status=decide(margin,similarity,bundle['gate']),margin=margin,similarity=similarity)
                    save_inspection(DB,file.name,result['status'],None,*im.size,float(gray.mean()),0.0,'MobileNetV2 + SVM',raw)
                    st.session_state['v21_result'] = (key,result)
            except Exception as e:
                st.error(f'Analisis belum berhasil: {e}')
        saved = st.session_state.get('v21_result')
        if im is not None and saved and saved[0] == key:
            r = saved[1]
            st.subheader(r['status'])
            explanations = {'OK':'Cenderung OK; tetap verifikasi operator pada tahap eksperimen.',
                'NG':'Cenderung NG; periksa kondisi komponen.',
                'PERLU REVIEW':'Skor terlalu dekat batas keputusan. Jangan otomatis meloloskan produk.',
                'TIDAK DIKENALI':'Tidak cukup mirip contoh latihan. Bisa gambar asing atau sudut produk baru.',
                'FAILED':'Foto hampir tanpa detail atau resolusinya sangat kecil. Ambil ulang.'}
            st.write(explanations[r['status']])
            if r['margin'] is not None:
                st.write(f"Skor SVM: {r['margin']:+.3f}")
                st.caption('Negatif → NG; positif → OK; antara −0,5 dan +0,5 → review. Batas eksperimen, belum dikalibrasi.')
                with st.expander('Detail kemiripan'):
                    st.write(f"Kemiripan: {r['similarity']:.3f}; batas: {bundle['gate']:.3f}")
                    st.caption('Kemiripan bukan probabilitas. Penolakan gambar asing belum diuji dengan dataset negatif yang representatif.')
        else:
            st.info('Pilih foto, lalu tekan Analisis gambar.')
with history:
    rows = get_history(DB)
    if rows:
        st.dataframe(rows,use_container_width=True,hide_index=True)
    else:
        st.info('Belum ada riwayat versi 2.1.')
with guide:
    st.write('Training memakai foto asli dalam dataset_base/OK dan dataset_base/NG. Tidak perlu prepare_dataset.py atau --clean.')
    st.code('.venv\\Scripts\\python.exe train_transfer.py')
    st.write('Augmentasi hanya masuk sisi latihan. Evaluasi satu foto sumber ditahan bergantian; jika beberapa foto berasal dari unit yang sama, hasil tetap bisa optimistis.')
    st.write('Grayscale menghilangkan warna, bukan perbedaan background. Foto kedua kelas tetap perlu diambil pada latar dan pencahayaan seimbang.')
    st.write('Gunakan foto kamera asli untuk uji; gambar generatif dapat mengubah detail cacat. Hasil dari foto yang sudah dilatih bukan ukuran akurasi baru.')
