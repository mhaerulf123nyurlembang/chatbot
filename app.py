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

    # 💡 FIX UTAMA: Alamat URL dibuat bersih tanpa ada variabel yang menempel langsung
    url = "https://googleapis.com"
    
    # Kunci API dikirimkan secara terpisah melalui parameter data, bukan digabung ke teks URL
    query_params = {
        "key": GEMINI_API_KEY_ANDA
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": payload_contents
    }

    try:
        # Mengirim data dengan memisahkan url dan params agar tidak memicu NameResolutionError
        response = requests.post(url, headers=headers, params=query_params, json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            try:
                # Mengambil teks balasan dari struktur data Google Gemini
                jawaban_gemini = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                # Tampilkan balasan AI di layar web
                with st.chat_message("assistant"):
                    st.write(jawaban_gemini)
                
                st.session_state.gemini_messages.append({"role": "assistant", "text": jawaban_gemini})
            except (KeyError, IndexError):
                st.error(f"Format data respons tidak sesuai. Data: {response_data}")
        else:
            try:
                error_msg = response.json().get("error", {}).get("message", "Terjadi kesalahan otentikasi.")
            except Exception:
                error_msg = response.text
            st.error(f"Server Google menolak permintaan (Status {response.status_code}): {error_msg}")
            
    except Exception as e:
        st.error(f"Terjadi kendala koneksi internet: {e}")
