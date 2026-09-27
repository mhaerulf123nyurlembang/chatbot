import streamlit as st
from groq import Groq

# 💡 HACKTIV8 BEST PRACTICES: Membaca API Key dari brankas Secrets Streamlit Cloud
try:
    GROQ_API_KEY_ANDA = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Gagal membaca API Key! Pastikan Anda sudah mengisi menu Secrets di Streamlit Cloud dengan label 'GROQ_API_KEY'.")
    st.stop()

# Set halaman web agar memiliki tata letak yang bagus
st.set_page_config(page_title="Chatbot AI Groq", layout="centered", page_icon="🤖")

st.title("🤖 Chatbot AI Super Cepat")
st.write("Aplikasi chatbot live menggunakan infrastruktur LPU Groq Cloud.")

# Tombol Bersihkan Chat
if st.button("🗑️ Bersihkan Riwayat Chat"):
    st.session_state.groq_messages = [
        {"role": "system", "content": "Anda adalah asisten AI yang sangat cerdas, responsif, ramah, dan membantu."}
    ]
    st.rerun()

# Menginisialisasi riwayat obrolan internal (Mengikuti standar OpenAI/Groq)
if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = [
        {"role": "system", "content": "Anda adalah asisten AI yang sangat cerdas, responsif, ramah, dan membantu."}
    ]

# Menampilkan riwayat obrolan di layar web
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

    # Mengirim data ke server Groq menggunakan model gratis aktif terbaru
    try:
        client = Groq(api_key=GROQ_API_KEY_ANDA)
        
        with st.spinner("AI sedang berpikir..."):
            respons = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=st.session_state.groq_messages
            )
            
            # 💡 FIX UTAMA: Menambahkan indeks [0] untuk mengambil elemen pertama dari list choices
            jawaban_ai = respons.choices[0].message.content

        # Tampilkan balasan AI di layar web
        with st.chat_message("assistant"):
            st.write(jawaban_ai)
        
        st.session_state.groq_messages.append({"role": "assistant", "content": jawaban_ai})
        st.rerun()
        
    except Exception as e:
        st.error(f"Gagal memanggil Groq API: {e}")
