import streamlit as st
import os
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="AI Chatbot Pro", page_icon="🤖", layout="wide")

# ==========================================
# KONEKSI API OTOMATIS (Membaca dari Sistem)
# ==========================================
if "GEMINI_API_KEY" in st.secrets:
    api_key_env = st.secrets["GEMINI_API_KEY"]
elif os.environ.get("GEMINI_API_KEY"):
    api_key_env = os.environ.get("GEMINI_API_KEY")
else:
    api_key_env = None

# ==========================================
# 2. KONFIGURASI SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Pengaturan Chatbot")
    st.write("Status API: ✅ Terhubung Otomatis" if api_key_env else "❌ API Key Belum Dikonfigurasi")
    st.markdown("---")
    
    # Pilihan Model Gemini
    st.subheader("1. Pilih Model AI")
    selected_model = st.selectbox(
        "Pilih kecerdasan bot:",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
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
st.title("🤖 Chatbot AI Interaktif")

# Menghentikan aplikasi jika API Key benar-benar belum dikonfigurasi di sistem
if not api_key_env:
    st.error("⚠️ API Key tidak ditemukan! Silakan atur 'GEMINI_API_KEY' di menu Secrets Streamlit Cloud atau Terminal komputer Anda.")
    st.stop()

# Inisialisasi Riwayat Obrolan di Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan Riwayat Obrolan dari Sesi Sebelumnya
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Logika Utama saat Pengguna Mengirim Pesan
if prompt := st.chat_input("Tanya sesuatu kepada AI..."):
    # Tampilkan pesan pengguna di layar
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim ke Google Gemini API (Struktur Indentasi yang Benar)
    try:
        # Menginisialisasi klien dengan menyuntikkan header khusus agar format AQ. terbaca sebagai API Key murni
        client = genai.Client(
            api_key=api_key_env.strip(),
            http_options={'headers': {'x-goog-api-key': api_key_env.strip()}}
        )
        
        with st.chat_message("assistant"):
            config_params = {}
            if system_instruction.strip():
                config_params["system_instruction"] = system_instruction.strip()

            # Menggunakan stream agar teks muncul mengetik secara real-time
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=prompt,
                config=types.GenerateContentConfig(**config_params) if config_params else None
            )
            response_text = st.write_stream(response_stream)
            
        # Simpan respons AI ke riwayat
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Terjadi kesalahan pada API: {e}")
