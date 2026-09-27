import streamlit as st
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="AI Chatbot Pro", page_icon="🤖", layout="wide")

# ==========================================
# 2. KONFIGURASI SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Pengaturan Chatbot")
    
    # Input API Key baru (Format AQ.)
    api_key_input = st.text_input(
        "1. Google Gemini API Key:", 
        type="password", 
        help="Masukkan API Key baru Anda (biasanya diawali dengan AQ.)"
    )
    st.markdown("[👉 Dapatkan API Key Gratis di Sini](https://aistudio.google.com/)")
    st.markdown("---")
    
    # Pilihan Model Gemini
    st.subheader("2. Pilih Model AI")
    selected_model = st.selectbox(
        "Pilih kecerdasan bot:",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0
    )
    st.markdown("---")
    
    # Pengaturan Peran / Kepribadian Bot
    st.subheader("3. Kepribadian Bot")
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

# Inisialisasi Riwayat Obrolan di Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan Riwayat Obrolan dari Sesi Sebelumnya
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Logika Utama saat Pengguna Mengirim Pesan
if prompt := st.chat_input("Tanya sesuatu kepada AI..."):
    # Validasi API Key kosong
    if not api_key_input:
        st.error("⚠️ Silakan masukkan Gemini API Key terlebih dahulu di sidebar kiri!")
        st.stop()

    # Tampilkan pesan pengguna di layar
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim ke Google Gemini API dengan konfigurasi dari sidebar
    try:
        # PERBAIKAN UTAMA: Memaksa inisialisasi langsung menggunakan string API Key Anda
        client = genai.Client(api_key=api_key_input.strip())
        
        with st.chat_message("assistant"):
            # Konfigurasi instansiasi instruksi sistem yang aman
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
        # Menampilkan detail error yang lebih mudah dipahami jika terjadi masalah jaringan
        st.error(f"Terjadi kesalahan pada API: {e}")
        st.info("💡 Tips: Pastikan tidak ada spasi kosong yang ikut tersalin di depan atau belakang API Key Anda.")
