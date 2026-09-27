import streamlit as st
import os
from groq import Groq
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="RAG AI Chatbot Pro", page_icon="📚", layout="wide")

# ==========================================
# KONEKSI API OTOMATIS (Membaca dari Sistem)
# ==========================================
if "GROQ_API_KEY" in st.secrets:
    api_key_env = st.secrets["GROQ_API_KEY"]
elif os.environ.get("GROQ_API_KEY"):
    api_key_env = os.environ.get("GROQ_API_KEY")
else:
    api_key_env = None

# ==========================================
# FUNGSI MESIN UTAMA RAG (Sistem Ekstraksi & Pencarian Dokumen)
# ==========================================
def extract_text_from_pdf(pdf_file):
    """Membaca isi teks dari file PDF."""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def split_text_into_chunks(text, chunk_size=700, chunk_overlap=150):
    """Memotong teks panjang menjadi fragmen kecil (chunk) dengan overlap aman."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def retrieve_relevant_context(query, chunks, top_k=3):
    """Mencari potongan dokumen (chunks) yang paling relevan dengan pertanyaan user menggunakan TF-IDF."""
    if not chunks:
        return ""
    
    # Menghitung bobot kata pada dokumen & query
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunks)
    query_vector = vectorizer.transform([query])
    
    # Menghitung tingkat kemiripan kosinus
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    # Mengambil indeks top_k potongan dokumen dengan skor tertinggi
    top_indices = similarities.argsort()[-top_k:][::-1]
    
    relevant_chunks = [chunks[idx] for idx in top_indices if similarities[idx] > 0.05]
    return "\n\n".join(relevant_chunks)

# ==========================================
# 2. KONFIGURASI SIDEBAR (Fitur Unggah Dokumen RAG)
# ==========================================
with st.sidebar:
    st.title("⚙️ Panel Kontrol RAG")
    st.write("Status API: ✅ Terhubung" if api_key_env else "❌ Kunci Belum Dikonfigurasi")
    st.markdown("---")
    
    # MENU UTAMA RAG: Unggah File Basis Pengetahuan
    st.subheader("📚 Sumber Basis Data (RAG)")
    uploaded_file = st.file_uploader(
        "Unggah Dokumen Referensi (PDF):", 
        type=["pdf"],
        help="Unggah dokumen PDF seperti SOP, katalog produk, atau materi studi agar AI dapat menjawab berdasarkan file ini."
    )
    
    # Memproses dokumen secara instan saat diunggah
    document_chunks = []
    if uploaded_file is not None:
        with st.spinner("Sedang mengekstrak & memproses dokumen..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            if raw_text.strip():
                document_chunks = split_text_into_chunks(raw_text)
                st.success(f"Berhasil memuat {len(document_chunks)} fragmen data dokumen!")
            else:
                st.error("Gagal mengekstrak teks. Pastikan PDF Anda tidak dikunci atau berupa gambar (scan).")
    st.markdown("---")
    
    # Pilihan Model Terbaru Groq yang Aktif
    st.subheader("🤖 Pengaturan Model")
    selected_model = st.selectbox(
        "Pilih Model AI:",
        ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"],
        index=0
    )
    
    # Pengaturan Instruksi Sistem Dasar
    system_instruction = st.text_area(
        "Instruksi Kepribadian:",
        value="Anda adalah asisten AI yang ramah, sopan, dan membantu menjawab dalam bahasa Indonesia."
    )
    st.markdown("---")
    
    # Tombol Kontrol (Hapus Chat)
    if st.button("🔄 Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 3. KONTEN UTAMA CHATBOT
# ==========================================
st.title("📚 RAG AI Enterprise Chatbot (Groq)")
st.write("Jika Anda mengunggah dokumen PDF di sidebar, bot akan secara otomatis mencari jawaban dari dalam dokumen tersebut.")

# Menghentikan aplikasi jika API Key belum terpasang
if not api_key_env:
    st.error("⚠️ API Key tidak ditemukan! Harap pasang 'GROQ_API_KEY' pada konfigurasi sistem Anda.")
    st.markdown("[👉 Dapatkan API Key Groq Gratis di Sini](https://groq.com)")
    st.stop()

# Inisialisasi Riwayat Obrolan di Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan Riwayat Obrolan dari Sesi Sebelumnya
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Logika Utama saat Pengguna Mengirim Pesan
if prompt := st.chat_input("Tanyakan sesuatu ke AI..."):
    # Tampilkan pesan pengguna di layar
    with st.chat_message("user"):
        st.markdown(prompt)

    # ALUR PROSES RAG: Cari Konteks Relevan dari PDF
    context = ""
    if document_chunks:
        context = retrieve_relevant_context(prompt, document_chunks, top_k=3)

    # Kirim ke Groq API beserta Konteks Dokumen (Jika Ada)
    try:
        client = Groq(api_key=api_key_env.strip())
        
        # Menyusun paket pesan komparatif
        api_messages = []
        
        # Memodifikasi instruksi sistem dinamis berdasarkan ketersediaan data RAG
        base_instruction = system_instruction.strip()
        if context:
            base_instruction += (
                f"\n\n[PENTING] Anda dibekali dokumen referensi resmi di bawah ini. Jawablah pertanyaan pengguna "
                f"hanya berdasarkan informasi relevan ini. Jika jawabannya tidak ada di dokumen, katakan secara jujur "
                f"bahwa informasi tersebut tidak tercantum dalam dokumen yang diunggah.\n\nKonteks Dokumen:\n{context}"
            )
            
        api_messages.append({"role": "system", "content": base_instruction})
        
        # Tambahkan riwayat obrolan lama & pesan baru
        for msg in st.session_state.messages:
            api_messages.append(msg)
        api_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            # Jika ada dokumen yang dipakai, berikan notifikasi transparansi (Kriteria Nilai Tambah Hacktiv8)
            if context:
                st.caption("📑 *AI sedang menganalisis dokumen referensi Anda...*")
                
            completion = client.chat.completions.create(
                model=selected_model,
                messages=api_messages,
                temperature=0.3, # Diperkecil agar AI patuh pada konteks dokumen dan menghindari halusinasi
                stream=True
            )
            
            def stream_response():
                for chunk in completion:
                    if chunk.choices.delta.content:
                        yield chunk.choices.delta.content
                        
            response_text = st.write_stream(stream_response())
            
        # Simpan riwayat chat yang baru
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Terjadi kesalahan pada Groq API: {e}")
