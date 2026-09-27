import streamlit as st
from groq import Groq

# ⚠️ TEMPELKAN KUNCI GROQ API ANDA (Diawali dengan gsk_) DI BAWAH INI:
GROQ_API_KEY_ANDA = "gsk_TEMPELKAN_KUNCI_GROQ_ASLI_DI_SINI"

st.title("⚡ Chatbot AI Super Cepat (Powered by Groq)")
st.write("Aplikasi live stabil menggunakan Groq API Key secara gratis.")

# Inisialisasi Klien Groq Resmi
if GROQ_API_KEY_ANDA == "gsk_TEMPELKAN_KUNCI_GROQ_ASLI_DI_SINI" or not GROQ_API_KEY_ANDA:
    st.error("Silakan masukkan Groq API Key asli Anda terlebih dahulu!")
    st.stop()
else:
    client = Groq(api_key=GROQ_API_KEY_ANDA)

# Tombol Bersihkan Chat
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.groq_messages = []
    st.rerun()

# Menginisialisasi riwayat obrolan internal (Mengikuti standar OpenAI/Groq)
if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = [
        {"role": "system", "content": "Anda adalah asisten AI yang sangat cerdas, responsif, dan membantu."}
    ]

# Menampilkan riwayat obrolan di halaman web
for msg in st.session_state.groq_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Menerima ketikan pesan baru dari pengguna
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # Tampilkan pesan user ke layar secara instan
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.groq_messages.append({"role": "user", "content": prompt})

    # Mengirim data ke server Groq
    try:
        respons = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Model andalan gratis yang sangat cerdas
            messages=st.session_state.groq_messages
        )
        jawaban_ai = respons.choices.message.content

        # Tampilkan balasan AI di layar web
        with st.chat_message("assistant"):
            st.write(jawaban_ai)
        
        st.session_state.groq_messages.append({"role": "assistant", "content": jawaban_ai})
        
    except Exception as e:
        st.error(f"Gagal memanggil Groq API: {e}")
