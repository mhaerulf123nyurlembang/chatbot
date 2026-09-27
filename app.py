import streamlit as st
from groq import Groq

# ⚠️ TEMPELKAN KUNCI GROQ API ANDA (Wajib Diawali gsk_) DI BAWAH INI:
GROQ_API_KEY_ANDA = "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"

st.title("⚡ Chatbot AI Super Cepat (Powered by Groq)")
st.write("Aplikasi live gratis menggunakan infrastruktur Groq LPU.")

# Inisialisasi Klien Groq Resmi
if GROQ_API_KEY_ANDA == "gsk_TEMPELKAN_KUNCI_GROQ_ASLI_DI_SINI" or not GROQ_API_KEY_ANDA:
    st.error("Silakan ganti teks 'gsk_...' di kode GitHub dengan Groq API Key asli Anda!")
    st.stop()
else:
    client = Groq(api_key=GROQ_API_KEY_ANDA)

# Tombol Bersihkan Chat
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.groq_messages = []
    st.rerun()

# Menginisialisasi riwayat obrolan internal sesuai standar Groq SDK
if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = [
        {"role": "system", "content": "Anda adalah asisten AI yang sangat cerdas, responsif, ramah, dan membantu."}
    ]

# Menampilkan riwayat obrolan di halaman web Streamlit
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

    # Mengirim data percakapan ke server Groq
    try:
        respons = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Model gratis, super cepat, dan aktif saat ini
            messages=st.session_state.groq_messages
        )
        
        # 💡 FIX UTAMA: Menambahkan [0] untuk mengambil elemen pertama dari list choices
        jawaban_ai = respons.choices[0].message.content

        # Tampilkan balasan AI di layar web
        with st.chat_message("assistant"):
            st.write(jawaban_ai)
        
        st.session_state.groq_messages.append({"role": "assistant", "content": jawaban_ai})
        
    except Exception as e:
        st.error(f"Gagal memanggil Groq API: {e}")
