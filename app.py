import streamlit as st
import os
from groq import Groq

# 1. Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="Groq AI Chatbot", page_icon="⚡", layout="wide")

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
# 2. KONFIGURASI SIDEBAR
# ==========================================
    # Pilihan Model yang Aktif dan Didukung oleh Groq Terbaru
    st.subheader("1. Pilih Model AI")
    selected_model = st.selectbox(
        "Pilih kecerdasan bot:",
        ["qwen/qwen3.8-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b"],
        index=0,
        help="qwen3.8-27b sangat optimal untuk penalaran bahasa & tool use. gpt-oss-20b merupakan model yang sangat cepat."
    )
    st.markdown("---")
    
    # Pengaturan Peran / Kepribadian Bot
    st.subheader("2. Kepribadian Bot")
    system_instruction = st.text_area(
        "Instruksi Khusus (System Prompt):",
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
st.title("⚡ Chatbot AI Super Cepat (Groq)")

# Menghentikan aplikasi jika API Key benar-benar belum dikonfigurasi di sistem
if not api_key_env:
    st.error("⚠️ API Key tidak ditemukan! Silakan atur 'GROQ_API_KEY' di menu Secrets Streamlit Cloud atau Terminal komputer Anda.")
    st.markdown("[👉 Dapatkan API Key Groq Gratis di Sini](https://console.groq.com/keys)")
    st.stop()

# Inisialisasi Riwayat Obrolan di Session State (Menggunakan format pesan OpenAI/Groq)
if "messages" not in st.session_state:
    # Memasukkan system prompt sebagai pesan awal di latar belakang jika diisi
    st.session_state.messages = []

# Tampilkan Riwayat Obrolan dari Sesi Sebelumnya (Kecuali instruksi sistem)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Logika Utama saat Pengguna Mengirim Pesan
if prompt := st.chat_input("Tanya sesuatu kepada AI..."):
    # Tampilkan pesan pengguna di layar
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim ke Groq API
    try:
        # Menginisialisasi klien Groq secara resmi
        client = Groq(api_key=api_key_env.strip())
        
        # Menyusun paket pesan yang dikirim (Instruksi sistem dimasukkan di awal riwayat)
        api_messages = []
        if system_instruction.strip():
            api_messages.append({"role": "system", "content": system_instruction.strip()})
        
        # Tambahkan riwayat obrolan sebelumnya
        for msg in st.session_state.messages:
            api_messages.append(msg)
            
        # Tambahkan pesan terbaru dari pengguna
        api_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            # Memanggil API Groq dengan metode streaming resmi
            completion = client.chat.completions.create(
                model=selected_model,
                messages=api_messages,
                temperature=0.7,
                stream=True
            )
            
            # Menampilkan potongan teks secara real-time saat selesai dihitung oleh Groq
            def stream_response():
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                        
            response_text = st.write_stream(stream_response())
            
        # Simpan riwayat chat yang baru secara permanen ke memori lokal
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Terjadi kesalahan pada Groq API: {e}")
