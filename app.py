import streamlit as st
from google import genai

# ⚠️ TEMPELKAN API KEY GEMINI ANDA LANGSUNG DI BAWAH INI:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg" 

# Inisialisasi Klien Google GenAI secara langsung
if GEMINI_API_KEY_ANDA == "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg" or not GEMINI_API_KEY_ANDA:
    st.error("Ganti teks 'AIzaSy...' di dalam kode dengan Gemini API Key asli Anda!")
    st.stop()
else:
    client = genai.Client(api_key=GEMINI_API_KEY_ANDA)

st.title("🤖 Chatbot AI Google Gemini")
st.write("Aplikasi live menggunakan Gemini API secara Gratis.")

# Tombol Bersihkan Chat
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.gemini_messages = []
    st.rerun()

# Menginisialisasi riwayat obrolan
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = []

# Menampilkan riwayat pesan
for msg in st.session_state.gemini_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# Menerima input dari pengguna
if prompt := st.chat_input("Ketik pesan Anda untuk Gemini di sini..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.gemini_messages.append({"role": "user", "text": prompt})

    # Menyusun riwayat agar dipahami oleh API Gemini
    contents_for_api = []
    for msg in st.session_state.gemini_messages:
        contents_for_api.append(
            genai.types.Content(
                role=msg["role"],
                parts=[genai.types.Part.from_text(text=msg["text"])]
            )
        )

    # Mengirim data ke Model AI Google Gemini
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=contents_for_api,
        )
        jawaban_gemini = response.text

        with st.chat_message("assistant"):
            st.write(jawaban_gemini)
        
        st.session_state.gemini_messages.append({"role": "assistant", "text": jawaban_gemini})
        
    except Exception as e:
        st.error(f"Gagal memanggil Gemini API: {e}")
