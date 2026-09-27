import streamlit as st
import requests

# ⚠️ KUNCI GEMINI API BERAWALAN AQ. ANDA SUDAH TERPASANG:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg"

st.title("🤖 Chatbot AI Google Gemini")
st.write("Aplikasi live berhasil terotentikasi menggunakan Kunci Auth API Gemini.")

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

    # Menyusun struktur percakapan agar dipahami endpoint REST API Google
    payload_contents = []
    for msg in st.session_state.gemini_messages:
        api_role = "user" if msg["role"] == "user" else "model"
        payload_contents.append({
            "role": api_role,
            "parts": [{"text": msg["text"]}]
        })

    # 💡 Perbaikan Endpoint URL: Menyematkan API Key langsung via parameter URL (?key=)
    # Ini adalah format paling stabil dan diizinkan Google untuk kunci auth bertipe AQ.
    url = f"https://googleapis.com{GEMINI_API_KEY_ANDA}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": payload_contents
    }

    try:
        # Mengirim data langsung layaknya metode cURL manual ke server Google
        response = requests.post(url, headers=headers, json=payload)
        
        # Pengaman Lanjutan: Cek status kode sebelum memproses JSON
        if response.status_code == 200:
            response_data = response.json()
            # Mengurai struktur JSON dari balasan resmi Google Gemini
            try:
                jawaban_gemini = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Tampilkan balasan AI di layar web
                with st.chat_message("assistant"):
                    st.write(jawaban_gemini)
                
                st.session_state.gemini_messages.append({"role": "assistant", "text": jawaban_gemini})
            except (KeyError, IndexError):
                st.error(f"Format JSON respons tidak sesuai. Data: {response_data}")
        else:
            # Jika Google mengembalikan error teks biasa / HTML
            st.error(f"Server Google menolak permintaan (Status {response.status_code}).")
            st.warning("Periksa apakah API Key Anda aktif atau coba buat API Key baru di Google AI Studio.")
            
    except Exception as e:
        st.error(f"Terjadi kendala koneksi internet: {e}")
