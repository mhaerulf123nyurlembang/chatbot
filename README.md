# chatbot
# 📊 Enterprise RAG Chatbot Pro (DocuMind AI)

Aplikasi **Agentic-RAG (Retrieval-Augmented Generation) Chatbot** berskala *enterprise* yang dirancang untuk membantu pengguna menganalisis dokumen internal (PDF) secara instan, akurat, dan bebas dari informasi palsu (*AI hallucination*). 

Proyek ini dibangun menggunakan **Streamlit** untuk antarmuka web, ditenagai oleh **Groq API** untuk inferensi LLM super cepat, serta menggunakan arsitektur pencarian dokumen berbasis matematika **TF-IDF & Cosine Similarity** bawaan (*in-memory*).

---

## 🚀 Fitur Utama

* **Analisis Dokumen PDF Instan (RAG):** Unggah dokumen (SOP, laporan keuangan, jurnal) dan biarkan AI menjawab pertanyaan Anda hanya berdasarkan isi dokumen tersebut.
* **Sistem Multi-Persona:** Bot dapat berganti kepribadian secara instan melalui menu *dropdown* (Asisten Umum, *Customer Service* Ramah, *Senior Programmer*, *Data Analyst*).
* **Metrik Performa Transparan:** Menampilkan *Response Time* (kecepatan respons) secara *real-time* di layar pasca-eksekusi.
* **Transparansi Referensi (*Grounding Evidence*):** Menyediakan fitur *expander* untuk melihat potongan asli teks PDF yang diambil sebagai dasar jawaban AI guna menghindari halusinasi data.
* **Ekspor Riwayat Percakapan:** Tombol unduh otomatis untuk menyimpan seluruh riwayat obrolan ke dalam file `.txt`.

---

## 🛠️ Tech Stack yang Digunakan

* **Frontend & UI:** Streamlit
* **AI Engine & LLM:** Groq API (`qwen/qwen3.8-27b` / `openai/gpt-oss-120b`)
* **Information Retrieval (IR):** Scikit-Learn (`TfidfVectorizer` & `cosine_similarity`)
* **Document Parser:** PyPDF2
* **Language:** Python 3.9+

---

## 📐 Arsitektur Teoretis & Algoritma (Standar Evaluasi Hacktiv8)

Proyek ini menghindari penggunaan *Dense Embeddings* komersial dan memilih menggunakan pendekatan **Sparse Retrieval** berbasis memori lokal untuk efisiensi biaya dan kecepatan:
1. **Data Ingestion & Chunking:** Teks dari PDF diekstrak dan dipotong menjadi bagian-bagian kecil (*chunk size*: 600 kata, *overlap*: 120 kata) untuk menjaga konteks kalimat di antara batas potongan.
2. **Vectorization (TF-IDF):** Mengubah kata-kata di dalam dokumen dan pertanyaan pengguna menjadi representasi matriks pembobotan frekuensi kata.
3. **Similarity Matching (Cosine Similarity):** Mengukur sudut kosinus antara vektor kueri pengguna dengan vektor potongan dokumen untuk mengambil `top_k=3` dokumen dengan tingkat kemiripan tertinggi untuk disuntikkan ke dalam *System Prompt* LLM.

---

## 💻 Cara Menjalankan Proyek Secara Lokal

### 1. Kloning Repositori
```bash
git clone https://github.com
cd nama-repositori
```

### 2. Instal Dependensi
Pastikan Anda sudah menginstal Python, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi API Key
Dapatkan API Key gratis di [Groq Cloud Console](https://groq.com).
* **Di Terminal (Linux/macOS):**
  ```bash
  export GROQ_API_KEY="gsk_kunci_anda_di_sini"
  ```
* **Di Command Prompt (Windows):**
  ```cmd
  set GROQ_API_KEY=gsk_kunci_anda_di_sini
  ```

### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```

---

## 🔒 Konfigurasi Streamlit Cloud Deployment

Saat melakukan *deployment* ke **Streamlit Community Cloud**, jangan memasukkan API Key ke dalam kode. Gunakan fitur **Advanced Settings > Secrets** di dashboard Streamlit Anda dan masukkan format berikut:

```toml
GROQ_API_KEY = "gsk_KunciGroqAsliAndaTanpaTandaKutipBerlebih"
```

---
*Proyek ini diajukan sebagai **Final Project** pada Program Pelatihan Digital Bootcamp **Hacktiv8 Indonesia**.*
