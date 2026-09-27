import streamlit as st
import requests

# ⚠️ TEMPELKAN KUNCI GEMINI API BERAWALAN AQ. ANDA DI BAWAH INI:
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg"

st.title("🤖 Chatbot AI Google Gemini")
st.write("Aplikasi live stabil menggunakan Kunci Auth API Gemini.")

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

    # Menyusun struktur percakapan agar dipahami endpoint REST API Google
    payload_contents = []
    for msg in st.session_state.gemini_messages:
        api_role = "user" if msg["role"] == "user" else "model"
        payload_contents.append({
            "role": api_role,
            "parts": [{"text": msg["text"]}]
        })

    # 💡 FIX URL: Alamat web dipisah secara sempurna dari API Key Anda menggunakan parameter resmi (?key=)
    url = "https://googleapis.com"
    
    params = {
        "key": GEMINI_API_KEY_ANDA
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": payload_contents
    }

    try:
        # Mengirim data langsung ke server Google dengan memisahkan params URL
        response = requests.post(url, headers=headers, params=params, json=payload)
        
        # Pengaman: Cek jika respons bukan JSON
        try:
            response_data = response.json()
        except Exception:
            st.error(f"Server Google memberikan respons mentah: {response.text}")
            st.stop()

        if response.status_code == 200:
            # Mengambil teks jawaban dari struktur JSON resmi Google Gemini
            try:
                jawaban_gemini = response_data["candidates"][0]["content"]["parts"][0]["text"]
                
                with st.chat_message("assistant"):
                    st.write(jawaban_gemini)
                
                st.session_state.gemini_messages.append({"role": "assistant", "text": jawaban_gemini})
            except (KeyError, IndexError):
                st.error(f"Format JSON Google berubah atau tidak sesuai. Respons: {response_data}")
        else:
            error_msg = response_data.get("error", {}).get("message", "Terjadi kesalahan otentikasi.")
            st.error(f"Gagal memanggil Gemini API ({response.status_code}): {error_msg}")
            
    except Exception as e:
        st.error(f"Terjadi kendala koneksi: {e}")
