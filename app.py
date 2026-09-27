import streamlit as st 
from groq import Groq
import requests
import base64

# ⚠️ TEMPELKAN KUNCI API ANDA DI BAWAH INI:
GROQ_API_KEY_ANDA = "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"
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg"

# Set halaman web agar memiliki tata letak yang bagus
st.set_page_config(page_title="AI Multi-Fungsi: Chat & Foto", layout="wide")

# ==========================================
# 📊 KONFIGURASI SIDEBAR (MENU SAMPING)
# ==========================================
st.sidebar.title("⚙️ Panel Kontrol AI")

# Fitur Pilih Mode Utama Aplikasi
mode_aplikasi = st.sidebar.radio(
    "Pilih Fitur Utama:",
    ["💬 Chat Teks (Groq)", "🖼️ Analisis & Deskripsi Foto (Gemini)"]
)

st.sidebar.markdown("---")

if mode_aplikasi == "💬 Chat Teks (Groq)":
    st.sidebar.subheader("Pengaturan Chat")
    pilihan_model = st.sidebar.selectbox(
        "Pilih Model AI Teks:",
        ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"],
        index=0
    )
    if st.sidebar.button("🗑️ Sapukan / Bersihkan Chat", use_container_width=True):
        st.session_state.groq_messages = []
        st.rerun()
else:
    st.sidebar.subheader("Informasi Fitur Foto")
    st.sidebar.write("Gunakan fitur ini untuk meminta AI menganalisis, membaca teks di dalam foto, atau mendeskripsikan gambar.")

# ==========================================
# 🤖 FITUR 1: CHAT TEKS (GROQ)
# ==========================================
if mode_aplikasi == "💬 Chat Teks (Groq)":
    st.title("⚡ Chatbot AI Super Cepat (Powered by Groq)")
    st.write(f"Mode aktif: Chat teks menggunakan `{pilihan_model}`")

    if GROQ_API_KEY_ANDA == "gsk_TEMPELKAN_KUNCI_GROQ_ASLI_DI_SINI" or not GROQ_API_KEY_ANDA:
        st.error("Silakan ganti kunci Groq API asli Anda di kode GitHub!")
        st.stop()
    else:
        client = Groq(api_key=GROQ_API_KEY_ANDA)

    if "groq_messages" not in st.session_state:
        st.session_state.groq_messages = [
            {"role": "system", "content": "Anda adalah asisten AI yang sangat cerdas, responsif, ramah, dan membantu."}
        ]

    for msg in st.session_state.groq_messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if prompt := st.chat_input("Ketik pesan Anda di sini..."):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.groq_messages.append({"role": "user", "content": prompt})

        try:
            respons = client.chat.completions.create(
                model=pilihan_model,
                messages=st.session_state.groq_messages
            )
            jawaban_ai = respons.choices[0].message.content
            with st.chat_message("assistant"):
                st.write(jawaban_ai)
            st.session_state.groq_messages.append({"role": "assistant", "content": jawaban_ai})
        except Exception as e:
            st.error(f"Gagal memanggil Groq API: {e}")

# ==========================================
# 🖼️ FITUR 2: ANALISIS / EDIT FOTO (GEMINI)
# ==========================================
else:
    st.title("🖼️ Vision AI: Analisis & Olah Foto")
    st.write("Unggah foto Anda dan berikan instruksi kepada AI (misal: 'Jelaskan isi foto ini' atau 'Tuliskan teks yang ada di gambar').")

    # Slot input untuk mengunggah berkas foto
    foto_diunggah = st.file_uploader("Pilih foto Anda (Format: JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])

    if foto_diunggah:
        # Menampilkan foto yang diunggah ke layar web
        st.image(foto_diunggah, caption="Foto yang Anda unggah", width=400)
        
        # Kolom teks untuk memberikan perintah edit/analisis foto
        instruksi_foto = st.text_input("Apa yang ingin Anda tanyakan atau lakukan pada foto ini?", value="Jelaskan objek apa saja yang ada di foto ini secara detail.")
        
        if st.button("🚀 Proses Foto dengan Vision AI"):
            with st.spinner("Sedang memproses foto Anda ke server Google..."):
                try:
                    # Membaca file foto dan mengubahnya menjadi format base64 bytes
                    bytes_foto = foto_diunggah.read()
                    base64_foto = base64.b64encode(bytes_foto).decode('utf-8')
                    tipe_konten = foto_diunggah.type

                    # Endpoint REST API Resmi Google Gemini 2.5 Flash yang mendukung tipe AQ.
                    url = f"https://googleapis.com{GEMINI_API_KEY_ANDA}"
                    
                    headers = {"Content-Type": "application/json"}
                    
                    # Menyusun payload JSON khusus multimodal (Teks + Gambar)
                    payload = {
                        "contents": [{
                            "parts": [
                                {"text": claustruksi_foto if 'instruksi_foto' in locals() else "Deskripsikan gambar ini"},
                                {
                                    "inlineData": {
                                        "mimeType": tipe_konten,
                                        "data": base64_foto
                                    }
                                }
                            ]
                        }]
                    }

                    # Mengirim data langsung ke server pusat Google
                    response = requests.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        hasil_analisis = response_data["candidates"][0]["content"]["parts"][0]["text"]
                        
                        st.success("✨ Hasil Analisis Vision AI:")
                        st.info(hasil_analisis)
                    else:
                        st.error(f"Server Google menolak permintaan (Status {response.status_code}): {response.text}")
                        
                except Exception as e:
                    st.error(f"Terjadi kendala pemrosesan gambar: {e}")
