import streamlit as st
import requests

# ⚠️ KUNCI GEMINI API BERAWALAN AQ. ANDA SUDAH TERPASANG:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg"

st.title("🤖 Chatbot AI Google Gemini")
st.write("Aplikasi live berhasil terotentikasi menggunakan rute interaksi global Google.")

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
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.gemini_messages.append({"role": "user", "text": prompt})

    # 💡 FIX UTAMA: Menggunakan endpoint rute interaksi global yang diwajibkan untuk kunci AQ.
    url = "https://generativelanguage.googleapis.com/v1beta/interactions"
    
    # Otentikasi header yang presisi untuk tipe kunci terbaru
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY_ANDA
    }
    
    # Skema pengiriman interaksi tunggal berbasis model cloud global aktif
    payload = {
        "model": "gemini-2.5-flash",
        "input": prompt
    }

    try:
        # Mengirim data langsung ke gerbang interaksi Google
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            response_data = response.json()
            try:
                # Mengambil teks balasan dari struktur interaksi resmi Google
                jawaban_gemini = response_data["interaction"]["outputText"]
                
                with st.chat_message("assistant"):
                    st.write(jawaban_gemini)
                
                st.session_state.gemini_messages.append({"role": "assistant", "text": jawaban_gemini})
            except (KeyError, TypeError):
                st.error(f"Format data respons tidak sesuai. Data: {response_data}")
        else:
            try:
                error_msg = response.json().get("error", {}).get("message", "Terjadi kesalahan sistem.")
            except Exception:
                error_msg = response.text
            st.error(f"Server Google menolak permintaan (Status {response.status_code}): {error_msg}")
            
    except Exception as e:
        st.error(f"Terjadi kendala koneksi internet: {e}")
