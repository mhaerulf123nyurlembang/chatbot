import streamlit as st
from openai import OpenAI

# ⚠️ TEMPELKAN KUNCI GEMINI API BERAWALAN AQ. ANDA DI BAWAH INI:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg"

st.title("🤖 Chatbot AI Google Gemini 3.6")
st.write("Aplikasi live menggunakan model terbaru Gemini 3.6 Flash secara gratis.")

# Menginisialisasi Klien dengan Base URL khusus kompatibilitas Google Gemini
try:
    client = OpenAI(
        base_url="https://googleapis.com",
        api_key=GEMINI_API_KEY_ANDA
    )
except Exception as e:
    st.error(f"Gagal memuatan sistem: {e}")

# Tombol Bersihkan Chat
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.gemini_messages = []
    st.rerun()

# Menginisialisasi riwayat obrolan internal
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = [
        {"role": "system", "content": "Anda adalah chatbot handal berbasis Gemini 3.6 yang menjawab dengan sangat ramah."}
    ]

# Menampilkan riwayat obrolan di halaman web
for msg in st.session_state.gemini_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Menerima ketikan pesan baru dari pengguna
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # Tampilkan pesan user ke layar secara instan
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.gemini_messages.append({"role": "user", "content": prompt})

    # Mengirim data ke server Google menggunakan model resmi gemini-3.6-flash
    try:
        respons = client.chat.completions.create(
            model="gemini-3.6-flash", # 💡 Model telah diganti ke versi 3.6 Flash
            messages=st.session_state.gemini_messages
        )
        jawaban_ai = respons.choices.message.content

        # Tampilkan balasan AI di layar web
        with st.chat_message("assistant"):
            st.write(jawaban_ai)
        
        st.session_state.gemini_messages.append({"role": "assistant", "content": jawaban_ai})
        
    except Exception as e:
        st.error(f"Gagal memanggil API Gemini 3.6: {e}")
