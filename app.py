import streamlit as st
from openai import OpenAI

# ⚠️ TEMPELKAN KUNCI GEMINI API BERAWALAN AQ. ANDA DI BAWAH INI:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg"

st.title("🤖 Chatbot AI Google Gemini")
st.write("Aplikasi live berhasil menggunakan model Gemini 2.5 Flash secara gratis.")

# Menginisialisasi Klien OpenAI dengan menghilangkan kata 'openai/' agar tidak memicu 404
try:
    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/",
        api_key=GEMINI_API_KEY_ANDA
    )
except Exception as e:
    st.error(f"Gagal memuat sistem: {e}")

# Tombol Bersihkan Chat
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.gemini_messages = []
    st.rerun()

# Menginisialisasi riwayat obrolan internal
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = [
        {"role": "system", "content": "Anda adalah chatbot handal berbasis Gemini yang menjawab dengan ramah."}
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

    # Mengirim data ke server Google menggunakan model resmi gemini-2.5-flash
    try:
        respons = client.chat.completions.create(
            model="gemini-2.5-flash", # Menggunakan penamaan model global yang valid
            messages=st.session_state.gemini_messages
        )
        jawaban_ai = respons.choices[0].message.content

        # Tampilkan balasan AI di layar web
        with st.chat_message("assistant"):
            st.write(jawaban_ai)
        
        st.session_state.gemini_messages.append({"role": "assistant", "content": jawaban_ai})
        
    except Exception as e:
        st.error(f"Gagal memanggil API Gemini: {e}")
