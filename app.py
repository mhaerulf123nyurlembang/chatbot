import streamlit as st
import os
import time
from groq import Groq
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="Enterprise RAG Chatbot Pro", page_icon="📊", layout="wide")

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
# FUNGSI MESIN UTAMA RAG & PEMROSES DATA
# ==========================================
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def split_text_into_chunks(text, chunk_size=600, chunk_overlap=120):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def retrieve_relevant_context(query, chunks, top_k=3):
    if not chunks:
        return [], ""
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunks)
    query_vector = vectorizer.transform([query])
    
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    actual_k = min(top_k, len(chunks))
    top_indices = similarities.argsort()[-actual_k:][::-1]
    
    relevant_chunks = [chunks[idx] for idx in top_indices if similarities[idx] > 0.04]
    return relevant_chunks, "\n\n".join(relevant_chunks)

def generate_chat_download_text():
    download_str = "=== RIWAYAT PERCAKAPAN CHATBOT AI ===\n\n"
    for msg in st.session_state.messages:
        role_label = "PENGGUNA" if msg["role"] == "user" else "ASISTEN AI"
        download_str += f"[{role_label}]:\n{msg['content']}\n\n-------------------------\n\n"
    return download_str

# ==========================================
# 2. KONFIGURASI SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Kontrol Sistem Pro")
    st.write("Status API: ✅ Terhubung" if api_key_env else "❌ Kunci Belum Dikonfigurasi")
    st.markdown("---")
    
    st.subheader("📚 Sumber Basis Data (RAG)")
    uploaded_file = st.file_uploader(
        "Unggah Dokumen PDF:", 
        type=["pdf"],
        help="Unggah berkas seperti SOP atau laporan bisnis."
    )
    
    document_chunks = []
    if uploaded_file is not None:
        with st.spinner("Sedang memproses dokumen..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            if raw_text.strip():
                document_chunks = split_text_into_chunks(raw_text)
                st.success(f"Berhasil memproses {len(document_chunks)} fragmen data!")
                # Simpan chunks ke session state agar tetap ada saat halaman rerun
                st.session_state.document_chunks = document_chunks
            else:
                st.error("Teks tidak dapat diekstrak.")
                
    # Ambil chunks dari session state jika ada data tersimpan sebelumnya
    if "document_chunks" in st.session_state:
        document_chunks = st.session_state.document_chunks
        
    st.markdown("---")
    
    st.subheader("🤖 Pengaturan Otak & Peran")
    selected_model = st.selectbox(
        "Pilih Model AI:",
        ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"],
        index=0
    )
    
    preset_kepribadian = st.selectbox(
        "Pilih Preset Peran:",
        ["Asisten Umum", "Customer Service Ramah", "Senior Programmer", "Data Analyst & Researcher", "Kustom"],
        index=0
    )
    
    default_prompt = "Anda adalah asisten AI yang ramah, sopan, dan membantu menjawab dalam bahasa Indonesia."
    if preset_kepribadian == "Customer Service Ramah":
        default_prompt = "Anda adalah seorang Customer Service yang sangat sabar, ramah, dan profesional. Selalu gunakan sapaan hangat kepada pelanggan."
    elif preset_kepribadian == "Senior Programmer":
        default_prompt = "Anda adalah seorang Senior Software Engineer yang ahli. Berikan contoh kode yang bersih (clean code) dan jelaskan algoritmanya secara logis."
    elif preset_kepribadian == "Data Analyst & Researcher":
        default_prompt = "Anda adalah seorang Data Analyst dan Peneliti Senior. Analisis informasi secara kritis dengan pendekatan berbasis data dan poin terstruktur."
    elif preset_kepribadian == "Kustom":
        default_prompt = ""

    system_instruction = st.text_area("Modifikasi System Prompt:", value=default_prompt)
    st.markdown("---")
    
    st.subheader("💾 Manajemen Sesi")
    if st.button("🔄 Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        if "document_chunks" in st.session_state:
            del st.session_state.document_chunks
        st.rerun()

# ==========================================
# 3. KONTEN UTAMA CHATBOT
# ==========================================
st.title("📊 Enterprise Agentic-RAG System")
st.caption(f"Model: `{selected_model}` | Persona: `{preset_kepribadian}`")

if not api_key_env:
    st.error("⚠️ API Key 'GROQ_API_KEY' belum dikonfigurasi di menu Secrets Streamlit Cloud.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan tombol unduh jika riwayat chat sudah ada isinya
if len(st.session_state.messages) > 0:
    chat_text_data = generate_chat_download_text()
    st.download_button(
        label="📥 Ekspor & Unduh Riwayat Chat (.txt)",
        data=chat_text_data,
        file_name="riwayat_chat_ai.txt",
        mime="text/plain"
    )

# Tampilkan Riwayat Obrolan dari Sesi Sebelumnya
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Alur Eksekusi Utama saat Pertanyaan Dikirim
if prompt := st.chat_input("Tanyakan analisis dokumen atau instruksi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ALUR PROSES RAG
    raw_chunks_list, context_string = [], ""
    if document_chunks:
        raw_chunks_list, context_string = retrieve_relevant_context(prompt, document_chunks, top_k=3)

    try:
        client = Groq(api_key=api_key_env.strip())
        api_messages = []
        
        base_instruction = system_instruction.strip()
        if context_string:
            base_instruction += (
                f"\n\n[PENTING] Jawablah hanya berdasarkan dokumen referensi resmi di bawah ini. "
                f"Tetap gunakan gaya bahasa peran Anda ({preset_kepribadian}). "
                f"Jika jawabannya tidak ada di teks, katakan jujur bahwa data tidak ditemukan.\n\n"
                f"Konteks Dokumen:\n{context_string}"
            )
            
        api_messages.append({"role": "system", "content": base_instruction})
        
        for msg in st.session_state.messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant"):
            status_placeholder = st.empty()
            status_placeholder.caption("📡 *Sedang menghitung pencarian dokumen & mengirim token ke Groq...*")
            
            # Pengukuran Waktu Respons
            start_time = time.time()
            
            completion = client.chat.completions.create(
                model=selected_model,
                messages=api_messages,
                temperature=0.2,
                stream=True
            )
            
            def stream_response():
                for chunk in completion:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            response_text = st.write_stream(stream_response())
            end_time = time.time()
            waktu_proses = round(end_time - start_time, 2)
            
            status_placeholder.empty()
            st.info(f"⚡ *Response Time:* {waktu_proses} detik | *Sumber Data:* {'Dokumen RAG (PDF)' if context_string else 'General Knowledge'}")
            
            # Tampilkan potongan referensi asli (Grounding Evidence) jika RAG aktif
            if raw_chunks_list:
                with st.expander("📄 Lihat Potongan Dokumen Asli (Referensi RAG)"):
                    for idx, chunk in enumerate(raw_chunks_list):
                        st.markdown(f"**Fragmen Data ke-{idx+1}:**")
                        st.caption(f"\"{chunk}\"")
                        st.markdown("---")
            
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()

    except Exception as e:
        st.error(f"Terjadi kesalahan pada Groq API: {e}")
