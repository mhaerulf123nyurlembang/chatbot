import streamlit as st
from openai import OpenAI

# Mengambil API Key secara aman dari sistem rahasia Streamlit Cloud
try:
    api_key = st.secrets["AQ.Ab8RN6JsQf1MRwetAwt_tazbKKwL7-DqBxlg4RpfBcHKc2lomg"]
    client = OpenAI(api_key=api_key)
except Exception:
    st.error("API Key belum terpasang di Secrets Streamlit Cloud!")
    st.stop()

st.title("🤖 Chatbot AI Terverifikasi")
st.write("Aplikasi live 100% Berhasil.")

# Membuat tombol untuk hapus riwayat chat jika ingin reset
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.messages = []
    st.rerun()

# Menginisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Anda adalah chatbot handal yang selalu memberikan jawaban akurat."}
    ]

# Menampilkan chat yang tersimpan
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Input pesan dari pengguna
if prompt := st.chat_input("Ketik di sini..."):
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Mengirim instruksi ke OpenAI API
    try:
        respons = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages
        )
        jawaban_ai = respons.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.write(jawaban_ai)
        st.session_state.messages.append({"role": "assistant", "content": jawaban_ai})
    except Exception as e:
        st.error(f"Gagal memanggil AI: {e}")
