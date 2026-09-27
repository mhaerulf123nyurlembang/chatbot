import streamlit as st
import requests

# ⚠️ KUNCI GEMINI API BERAWALAN AQ. ANDA SUDAH TERPASANG:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg"

st.title("🤖 Chatbot AI Google Gemini")
st.write("Aplikasi live berhasil terotentikasi menggunakan Kunci Auth API Gemini (AQ).")

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
        # Mengonversi nama role agar sesuai standar REST API Gemini (user/model)
        api_role = "user" if msg["role"] == "user" else "model"
        payload_contents.append({
            "role": api_role,
            "parts": [{"text": msg["text"]}]
        })

    # 💡 URL Endpoint REST API Resmi Google Gemini 2.5 Flash
    url = "https://googleapis.com"
    
    # 💡 Kunci Kelolosan: Melekatkan Kunci AQ lewat Header x-goog-api-key secara manual
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY_ANDA
    }
    
    payload = {
        "contents": payload_contents
    }

    try:
        # Mengirim data langsung layaknya metode cURL manual ke server Google
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            # Mengurai struktur JSON dari balasan resmi Google Gemini
            jawaban_gemini = response_data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Tampilkan balasan AI di layar web
            with st.chat_message("assistant"):
                st.write(jawaban_gemini)
            
            st.session_state.gemini_messages.append({"role": "assistant", "text": jawaban_gemini})
        else:
            error_msg = response_data.get("error", {}).get("message", "Terjadi kesalahan otentikasi.")
            st.error(f"Gagal memanggil Gemini API ({response.status_code}): {error_msg}")
            
    except Exception as e:
        st.error(f"Terjadi kendala penguraian data atau koneksi: {e}")
