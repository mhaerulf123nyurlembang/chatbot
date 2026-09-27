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
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def split_text_into_chunks(text, chunk_size=700, chunk_overlap=150):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def retrieve_relevant_context(query, chunks, top_k=3):
    if not chunks:
        return ""
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunks)
    query_vector = vectorizer.transform([query])
    
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[-k:][::-1] if len(chunks) >= top_k else similarities.argsort()[::-1]
    
    relevant_chunks = [chunks[idx] for idx in top_indices if similarities[idx] > 0.05]
    return "\n\n".join(relevant_chunks)

# ==========================================
# 2. KONFIGURASI SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Panel Kontrol RAG")
    st.write("Status API: ✅ Terhubung" if api_key_env else "❌ Kunci Belum Dikonfigurasi")
    st.markdown("---")
    
    st.subheader("📚 Sumber Basis Data (RAG)")
    uploaded_file = st.file_uploader(
        "Unggah Dokumen Referensi (PDF):", 
        type=["pdf"],
        help="Unggah dokumen PDF agar AI dapat menjawab berdasarkan file ini."
    )
    
    document_chunks = []
    if uploaded_file is not None:
        with st.spinner("Sedang mengekstrak & memproses dokumen..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            if raw_text.strip():
                document_chunks = split_text_into_chunks(raw_text)
                st.success(f"Berhasil memuat {len(document_chunks)} fragmen data!")
            else:
                st.error("Gagal mengekstrak teks. Pastikan PDF tidak dikunci atau berupa gambar scan.")
    st.markdown("---")
    
    st.subheader("🤖 Pengaturan Model")
    selected_model = st.selectbox(
        "Pilih Model AI:",
        ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"],
        index=0
    )
    st.markdown("---")
    
    # NEW FEATURE: MENU PILIHAN KEPRIBADIAN INSTAN
    st.subheader("👤 Kepribadian Bot")
    preset_kepribadian = st.selectbox(
        "Pilih Peran Preset:",
        [
            "Asisten Umum", 
            "Customer Service Ramah", 
            "Senior Programmer", 
            "Data Analyst & Researcher", 
            "Kustom (Tulis Sendiri)"
        ],
        index=0
    )
    
    # Logika penentuan teks instruksi sistem bawaan berdasarkan dropdown
    default_prompt = "Anda adalah asisten AI yang ramah, sopan, dan membantu menjawab dalam bahasa Indonesia."
    if preset_kepribadian == "Customer Service Ramah":
        default_prompt = "Anda adalah seorang Customer Service yang sangat sabar, ramah, dan profesional. Selalu gunakan sapaan hangat kepada pelanggan dan jawab dengan bahasa yang santun serta solutif."
    elif preset_kepribadian == "Senior Programmer":
        default_prompt = "Anda adalah seorang Senior Software Engineer yang ahli. Jawablah pertanyaan teknis pemrograman dengan langsung pada inti masalah, berikan contoh kode yang bersih (clean code), efisien, aman, serta jelaskan algoritma di balik solusi tersebut secara logis."
    elif preset_kepribadian == "Data Analyst & Researcher":
        default_prompt = "Anda adalah seorang Data Analyst dan Peneliti Senior. Analisis informasi yang diberikan secara kritis, gunakan pendekatan berbasis data, jelaskan korelasi sebab-akibat dengan jelas, dan sajikan poin penting secara analitis terstruktur."
    elif preset_kepribadian == "Kustom (Tulis Sendiri)":
        default_prompt = ""

    # Kolom teks interaktif yang nilainya berubah mengikuti pilihan di atas
    system_instruction = st.text_area(
        "Modifikasi Instruksi Khusus (System Prompt):",
        value=default_prompt,
        placeholder="Tulis kepribadian kustom Anda di sini jika memilih opsi 'Kustom'..."
    )
    st.markdown("---")
    
    if st.button("🔄 Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ==========================================
# 3. KONTEN UTAMA CHATBOT
# ==========================================
st.title("📚 RAG AI Enterprise Chatbot (Groq)")
st.write(f"Mode Aktif: **{preset_kepribadian}** | Bot akan menjawab menggunakan basis pengetahuan dari dokumen jika diunggah.")

if not api_key_env:
    st.error("⚠️ API Key tidak ditemukan! Harap pasang 'GROQ_API_KEY' pada menu Secrets Streamlit Cloud.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Tanyakan sesuatu ke AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    context = ""
    if document_chunks:
        context = retrieve_relevant_context(prompt, document_chunks, top_k=3)

    try:
        client = Groq(api_key=api_key_env.strip())
        api_messages = []
        
        base_instruction = system_instruction.strip()
        if context:
            base_instruction += (
                f"\n\n[PENTING] Jawablah pertanyaan pengguna hanya berdasarkan dokumen referensi di bawah ini. "
                f"Tetap pertahankan gaya bahasa sesuai dengan kepribadian Anda ({preset_kepribadian}). "
                f"Jika jawabannya tidak ada di dokumen, katakan secara jujur bahwa informasi tersebut tidak tercantum.\n\n"
                f"Konteks Dokumen:\n{context}"
            )
            
        api_messages.append({"role": "system", "content": base_instruction})
        
        for msg in st.session_state.messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant"):
            if context:
                st.caption("📑 *AI sedang menganalisis dokumen referensi Anda...*")
                
            completion = client.chat.completions.create(
                model=selected_model,
                messages=api_messages,
                temperature=0.3,
                stream=True
            )
            
            def stream_response():
                for chunk in completion:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            response_text = st.write_stream(stream_response())
            
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Terjadi kesalahan pada Groq API: {e}")
