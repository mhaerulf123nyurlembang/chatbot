import streamlit as st
from openai import OpenAI

# ⚠️ TEMPELKAN KUNCI GROK API (xAI) ANDA YANG BERAWALAN 'xai-' DI BAWAH INI:
GROK_API_KEY_ANDA = "xai-t6EgbVfke5EH93K9rPHtr2O9jw2Qt92MeE7sao9lOJMni3fUpleeWJAb1zlmILZeUife7ufqIMRFObMB"

st.title("🧠 Chatbot AI Grok (by xAI)")
st.write("Aplikasi live stabil terhubung langsung ke mesin kecerdasan Groq xAI.")

# Inisialisasi Klien OpenAI dengan Base URL resmi dari xAI
try:
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=GROK_API_KEY_ANDA
    )
except Exception as e:
    st.error(f"Gagal memuat sistem: {e}")

# Tombol Bersihkan Chat
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.grok_messages = []
    st.rerun()

# Menginisialisasi riwayat obrolan internal
if "grok_messages" not in st.session_state:
    st.session_state.grok_messages = [
        {"role": "system", "content": "Anda adalah Grok, asisten AI yang cerdas, blak-blakan, dan sangat membantu."}
    ]

# Menampilkan riwayat obrolan di halaman web
for msg in st.session_state.grok_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Menerima ketikan pesan baru dari pengguna
if prompt := st.chat_input("Ketik pesan Anda untuk Grok di sini..."):
    # Tampilkan pesan user ke layar secara instan
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.grok_messages.append({"role": "user", "content": prompt})

    # Mengirim data percakapan ke Server pusat xAI Grok
    try:
        # Menggunakan model default publik aktif yang cepat dan andal
        respons = client.chat.completions.create(
            model="grok-beta", 
            messages=st.session_state.grok_messages
        )
        jawaban_ai = respons.choices.message.content

        # Tampilkan balasan AI di layar web
        with st.chat_message("assistant"):
            st.write(jawaban_ai)
        
        st.session_state.grok_messages.append({"role": "assistant", "content": jawaban_ai})
        
    except Exception as e:
        st.error(f"Gagal memanggil API Grok: {e}")
