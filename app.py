import streamlit as st
import os

# Memanggil modul SDK Google GenAI Modern (Mendukung penuh Kunci API berformat AQ.)
try:
    from google import genai
except ImportError:
    import google.genai as genai

# ⚠️ TEMPELKAN KUNCI GEMINI API BERAWALAN AQ. ANDA DI BAWAH INI:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6Ke92i7KazkWK82P4ea_XQsqHYNKCzCzvbUULSTuRFpJg" 

# Daftarkan API Key langsung ke environment variabel sistem agar dibaca SDK dengan benar
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY_ANDA

if not GEMINI_API_KEY_ANDA:
    st.error("Silakan masukkan Gemini API Key asli Anda!")
    st.stop()
else:
    # Menginisialisasi klien GenAI resmi sesuai dokumentasi terbaru
    client = genai.Client(api_key=GEMINI_API_KEY_ANDA)

st.title("🤖 Chatbot AI Google Gemini")
st.write("Aplikasi live stabil menggunakan Kunci Auth API Gemini secara Gratis.")

# Tombol Bersihkan Chat
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.gemini_messages = []
    st.rerun()

# Menginisialisasi riwayat obrolan internal
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = []

# Menampilkan riwayat obrolan di halaman web
for msg in st.session_state.gemini_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# Menerima ketikan pesan baru dari pengguna
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # Tampilkan pesan user ke layar secara instan
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.gemini_messages.append({"role": "user", "text": prompt})

    # Mengonversi format riwayat agar dipatuhi oleh mesin Gemini SDK terbaru
    contents_for_api = []
    for msg in st.session_state.gemini_messages:
        contents_for_api.append(
            genai.types.Content(
                role=msg["role"],
                parts=[genai.types.Part.from_text(text=msg["text"])]
            )
        )

    # Mengirim data percakapan ke Model Cerdas Gemini 2.5 Flash
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=contents_for_api,
        )
        jawaban_gemini = response.text

        # Tampilkan balasan AI di layar web
        with st.chat_message("assistant"):
            st.write(jawaban_gemini)
        
        st.session_state.gemini_messages.append({"role": "assistant", "text": jawaban_gemini})
        
    except Exception as e:
        st.error(f"Gagal memanggil Gemini API: {e}")
