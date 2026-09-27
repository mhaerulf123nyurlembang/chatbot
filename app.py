import streamlit as st
from google import genai

# 1. Konfigurasi Halaman Web Streamlit
st.set_page_config(page_title="AI Chatbot Pro", page_icon="🤖", layout="wide")

# ==========================================
# 2. KONFIGURASI SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚙️ Pengaturan Chatbot")
    
    # Input API Key secara aman
    api_key_input = st.text_input("1. Google Gemini API Key:", type="password", help="Masukkan API Key Anda dari Google AI Studio.")
    st.markdown("[👉 Dapatkan API Key Gratis di Sini](https://google.com)")
    st.markdown("---")
    
    # Pilihan Model Gemini
    st.subheader("2. Pilih Model AI")
    selected_model = st.selectbox(
        "Pilih kecerdasan bot:",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
        help="Gemini 2.5 Flash lebih cepat & hemat. Pro lebih cerdas untuk penalaran rumit."
    )
    st.markdown("---")
    
    # Pengaturan Peran / Kepribadian Bot (System Instruction)
    st.subheader("3. Kepribadian Bot")
    system_instruction = st.text_area(
        "Instruksi Khusus (System Prompt):",
        value="Anda adalah asisten AI yang ramah, sopan, dan membantu menjawab dalam bahasa Indonesia.",
        help="Tulis instruksi di sini untuk mengatur bagaimana cara bot merespons. Contoh: 'Jawablah seperti seorang guru matematika' atau 'Gunakan gaya bahasa santai'."
    )
    st.markdown("---")
    
    # Tombol Kontrol (Hapus Chat)
    st.subheader("4. Kontrol Sesi")
    if st.button("🔄 Hapus Riwayat Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Dibuat dengan ❤️ menggunakan Streamlit & Gemini API")

# ==========================================
# 3. KONTEN UTAMA CHATBOT
# ==========================================
st.title("🤖 Chatbot AI Interaktif")
st.write("Silakan sesuaikan pengaturan kepribadian atau model AI di menu sidebar kiri sebelum memulai percakapan.")

# Inisialisasi Riwayat Obrolan di Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan Riwayat Obrolan dari Sesi Sebelumnya
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Logika Utama saat Pengguna Mengirim Pesan
if prompt := st.chat_input("Tanya sesuatu kepada AI..."):
    # Validasi API Key
    if not api_key_input:
        st.error("⚠️ Silakan masukkan Gemini API Key terlebih dahulu di sidebar kiri!")
        st.stop()

    # Tampilkan pesan pengguna di layar
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kirim ke Google Gemini API dengan konfigurasi dari sidebar
    try:
        client = genai.Client(api_key=api_key_input)
        
        with st.chat_message("assistant"):
            # Menggunakan stream agar teks muncul mengetik secara real-time
            response_stream = client.models.generate_content_stream(
                model=selected_model,
                contents=prompt,
                # Memasukkan kepribadian bot dari sidebar ke dalam konfigurasi API
                config={"system_instruction": system_instruction} if system_instruction else None
            )
            response_text = st.write_stream(response_stream)
            
        # Simpan respons AI ke riwayat
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"Terjadi kesalahan pada API: {e}")
