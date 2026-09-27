import streamlit as st
import os
import json
from groq import Groq
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="Agentic RAG AI Chatbot", page_icon="🕵️‍♂️", layout="wide")

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
# FUNGSI UTAMA RAG (Sistem Ekstraksi & Pencarian Dokumen)
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

def tool_cari_di_dokumen(query):
    """Mencari potongan dokumen (chunks) yang relevan berdasarkan query user."""
    chunks = st.session_state.get("document_chunks", [])
    if not chunks:
        return "Dokumen kosong atau belum diunggah oleh pengguna."
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(chunks)
    query_vector = vectorizer.transform([query])
    
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[-3:][::-1]
    
    relevant_chunks = [chunks[idx] for idx in top_indices if similarities[idx] > 0.05]
    if not relevant_chunks:
        return "Tidak ditemukan informasi spesifik yang relevan di dalam dokumen."
    return "\n\n".join(relevant_chunks)

# ==========================================
# DEFINISI ALAT AGEN (Agent Tools)
# ==========================================
def tool_kalkulator_akurat(ekspresi_matematika):
    """Mengeksekusi perhitungan matematika string secara aman menggunakan Python eval()."""
    try:
        allowed_chars = "0123456789+-*/(). "
        if all(c in allowed_chars for c in ekspresi_matematika):
            hasil = eval(ekspresi_matematika)
            return f"Hasil perhitungan dari {ekspresi_matematika} adalah: {hasil}"
        else:
            return "Error: Ekspresi mengandung karakter terlarang demi keamanan."
    except Exception as e:
        return f"Gagal menghitung: {str(e)}"

# Kamus pemetaan string nama tool ke fungsi aslinya
AVAILABLE_TOOLS = {
    "tool_cari_di_dokumen": tool_cari_di_dokumen,
    "tool_kalkulator_akurat": tool_kalkulator_akurat
}

# Skema JSON deklarasi alat untuk dikirim ke API Groq
tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "tool_cari_di_dokumen",
            "description": "Gunakan alat ini ketika pengguna menanyakan informasi yang berkaitan dengan isi dokumen, berkas PDF, SOP, laporan, atau data khusus yang mereka unggah.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Kata kunci atau inti pertanyaan untuk melacak dokumen."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_kalkulator_akurat",
            "description": "Gunakan alat ini khusus saat pengguna meminta perhitungan matematika numerik presisi seperti penjumlahan, perkalian, pembagian, hitungan rumus, dsb.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ekspresi_matematika": {"type": "string", "description": "Ekspresi matematika mentah standar Python, contoh: '(25000 * 0.1) + 4500'"}
                },
                "required": ["ekspresi_matematika"]
            }
        }
    }
]

# ==========================================
# 2. KONFIGURASI SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🕵️‍♂️ Agen Kontrol Panel")
    st.write("Status API: ✅ Terhubung" if api_key_env else "❌ Belum Dikonfigurasi")
    st.markdown("---")
    
    st.subheader("📚 Knowledge Base (RAG)")
    uploaded_file = st.file_uploader("Unggah PDF Referensi:", type=["pdf"])
    
    if uploaded_file is not None and "document_chunks" not in st.session_state:
        with st.spinner("Mengekstrak berkas..."):
            raw_text = extract_text_from_pdf(uploaded_file)
            if raw_text.strip():
                st.session_state.document_chunks = split_text_into_chunks(raw_text)
                st.success(f"Berhasil memuat data dokumen!")
            else:
                st.error("Gagal mengekstrak teks.")
    st.markdown("---")
    
    st.subheader("🤖 Pengaturan Otak Agen")
    selected_model = st.selectbox(
        "Pilih Model (Wajib Model yang Dukung Tool Call):",
        ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"],
        index=0
    )
    
    system_instruction = st.text_area(
        "Instruksi Dasar Agen:",
        value="Anda adalah AI Agent Enterprise yang cerdas dan jujur. Anda dibekali alat (Tools) untuk mencari data dokumen dan berhitung matematika. Gunakan alat tersebut setiap kali relevan sebelum menjawab."
    )
    st.markdown("---")
    
    if st.button("🔄 Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        if "document_chunks" in st.session_state:
            del st.session_state.document_chunks
        st.rerun()

# ==========================================
# 3. KONTEN UTAMA CHATBOT
# ==========================================
st.title("🕵️‍♂️ Agentic RAG Multi-Tool Chatbot")
st.write("Agen cerdas ini secara mandiri menentukan kapan harus membaca dokumen RAG Anda atau kapan harus menggunakan kalkulator.")

if not api_key_env:
    st.error("⚠️ API Key tidak ditemukan! Harap pasang 'GROQ_API_KEY'.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Jalur Eksekusi Utama saat Chat Terkirim
if prompt := st.chat_input("Perintahkan agen sesuatu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = Groq(api_key=api_key_env.strip())
        
        # Susun riwayat pesan untuk API
        api_messages = [{"role": "system", "content": system_instruction.strip()}]
        for msg in st.session_state.messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
            
        with st.chat_message("assistant"):
            status_container = st.empty()
            status_container.caption("🧠 *Agen sedang menganalisis perintah...*")
            
            # PANGGILAN PERTAMA: Mengevaluasi kebutuhan penggunaan alat (Tool Call)
            response = client.chat.completions.create(
                model=selected_model,
                messages=api_messages,
                tools=tools_schema,
                tool_choice="auto",
                temperature=0.2
            )
            
            response_message = response.choices.message
            tool_calls = response_message.tool_calls
            
            # Kondisi A: Agen memutuskan untuk menggunakan satu atau beberapa alat
            if tool_calls:
                api_messages.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    status_container.caption(f"🛠️ *Agen memutuskan memakai alat: `{function_name}`...*")
                    
                    target_function = AVAILABLE_TOOLS[function_name]
                    if function_name == "tool_cari_di_dokumen":
                        hasil_tool = target_function(query=function_args.get("query"))
                    elif function_name == "tool_kalkulator_akurat":
                        hasil_tool = target_function(ekspresi_matematika=function_args.get("ekspresi_matematika"))
                        
                    api_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": hasil_tool
                    })
                
                status_container.caption("✍️ *Agen sedang menyusun jawaban final dari data alat...*")
                
                final_completion = client.chat.completions.create(
                    model=selected_model,
                    messages=api_messages,
                    stream=True
                )
                
                def stream_agent_response():
                    for chunk in final_completion:
                        if chunk.choices.delta.content:
                            yield chunk.choices.delta.content
                            
                response_text = st.write_stream(stream_agent_response())
                status_container.empty()
                
            # Kondisi B: Agen memberikan jawaban langsung (tanpa alat)
            else:
                status_container.caption("💬 *Memberikan respons langsung...*")
                
                direct_completion = client.chat.completions.create(
                    model=selected_model,
