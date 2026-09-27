import streamlit as st
import google.generativeai as genai

# ⚠️ TEMPELKAN API KEY GEMINI ANDA LANGSUNG DI BAWAH INI:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg" 

# Validasi dan Inisialisasi API Key
if GEMINI_API_KEY_ANDA == "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg" or not GEMINI_API_KEY_ANDA:
    st.error("Ganti teks 'AIzaSy...' di dalam kode dengan Gemini API Key asli Anda!")
    st.stop()
else:
    genai.configure(api_key=GEMINI_API_KEY_ANDA)

st.title("🤖 Chatbot AI Google Gemini")
st.write("Aplikasi live stabil menggunakan Gemini API secara Gratis.")

# Tombol Bersihkan Chat
if st.button("Sapukan / Bersihkan Chat"):
    st.session_state.chat_history = []
    st.rerun()

# Menginisialisasi riwayat obrolan dalam format bawaan model Gemini
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Menampilkan riwayat pesan ke layar halaman web
for msg in st.session_state.chat_history:
    # Mengonversi nama role agar sesuai ikon standar Streamlit
    display_role = "user" if msg.role == "user" else "assistant"
    with st.chat_message(display_role):
        st.write(msg.parts[0].text)

# Menerima ketikan input dari pengguna
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # Tampilkan pesan user secara instan di layar
    with st.chat_message("user"):
        st.write(prompt)
    
    try:
        # Memanggil mesin model Gemini 1.5 Flash yang sangat stabil
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Memulai atau melanjutkan sesi chat dengan menyertakan riwayat lama
        chat_session = model.start_chat(history=st.session_state.chat_history)
        
        # Mengirim pesan baru ke Google server
        response = chat_session.send_message(prompt)
        
        # Tampilkan jawaban AI ke layar
        with st.chat_message("assistant"):
            st.write(response.text)
            
        # Simpan otomatis riwayat obrolan terbaru ke session state
        st.session_state.chat_history = chat_session.history
        
    except Exception as e:
        st.error(f"Gagal memanggil Gemini API: {e}")
