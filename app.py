import streamlit as st 
from groq import Groq
import requests
import base64
from datetime import datetime

# ⚠️ TEMPELKAN KUNCI API ANDA DI BAWAH INI:
GROQ_API_KEY_ANDA = "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"
GEMINI_API_KEY_ANDA = "AQ.Ab8RN6JyeYM9pBnmYGztS53vaUYkoLa9N7GlzWroMyHbNIzDWg"

# Set halaman web agar memiliki tata letak yang bagus dan profesional
st.set_page_config(page_title="AI Multi-Fungsi Platform", layout="wide", page_icon="🤖")

# Custom CSS untuk memosisikan input area agar selalu berada di bawah layar ala ChatGPT
st.markdown("""
    <style>
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 📊 KONFIGURASI SIDEBAR (PANEL KONTROL)
# ==========================================
st.sidebar.title("⚙️ Panel Kontrol AI")

mode_aplikasi = st.sidebar.radio(
    "Pilih Fitur Utama:",
    ["💬 Chat Teks & Suara (Groq)", "🖼️ Vision AI & OCR (Gemini)"]
)

st.sidebar.markdown("---")

# Menginisialisasi session state untuk riwayat chat teks
if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = [
        {"role": "system", "content": "Anda adalah asisten AI yang sangat cerdas, responsif, ramah, dan membantu."}
    ]

# Inisialisasi pelacak audio agar tidak terjadi double processing / looping bug
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# FITUR TAMBAHAN 1: EKSPOR CHAT (DOWNLOAD TXT)
st.sidebar.subheader("💾 Manajemen Data")
if len(st.session_state.groq_messages) > 1:
    log_teks = f"RIWAYAT OBROLAN CHATBOT - Dibuat pada {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    log_teks += "="*50 + "\n\n"
    for msg in st.session_state.groq_messages:
        if msg["role"] != "system":
            role_label = "PENGGUNA" if msg["role"] == "user" else "ASISTEN AI"
            log_teks += f"[{role_label}]:\n{msg['content']}\n\n"
    
    st.sidebar.download_button(
        label="📥 Unduh Riwayat Obrolan (.txt)",
        data=log_teks,
        file_name=f"riwayat_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# Tombol bersihkan chat
if st.sidebar.button("🗑️ Sapukan / Bersihkan Chat", use_container_width=True):
    st.session_state.groq_messages = [
        {"role": "system", "content": "Anda adalah asisten AI yang sangat cerdas, responsif, ramah, dan membantu."}
    ]
    st.session_state.last_processed_audio = None
    st.rerun()

# ==========================================
# 🤖 MODUL 1: CHAT TEKS & SUARA (GROQ)
# ==========================================
if mode_aplikasi == "💬 Chat Teks & Suara (Groq)":
    st.title("⚡ Chatbot AI Super Cepat (Powered by Groq)")
    st.write("Aplikasi live dengan fitur input teks dan transkripsi suara yang menyatu di bagian bawah.")

    if GROQ_API_KEY_ANDA == "gsk_TEMPELKAN_KUNCI_GROQ_ASLI_DI_SINI" or not GROQ_API_KEY_ANDA:
        st.error("Silakan ganti kunci Groq API asli Anda di kode GitHub!")
        st.stop()
    else:
        client = Groq(api_key=GROQ_API_KEY_ANDA)

    for msg in st.session_state.groq_messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Container Kolom untuk Menyatukan Input Teks & Perekam Suara
    input_container = st.container()
    prompt_final = ""

    with input_container:
        col_teks, col_suara = st.columns([6, 2], gap="small")
        
        with col_teks:
            prompt_teks = st.chat_input("Ketik pesan Anda di sini...")
            if prompt_teks:
                prompt_final = prompt_teks

        with col_suara:
            input_suara = st.audio_input("Klik untuk rekam suara:", label_visibility="collapsed", key="uploader_suara_unik")
            
            if input_suara:
                audio_bytes = input_suara.read()
                audio_id = hash(audio_bytes)
                
                if st.session_state.last_processed_audio != audio_id:
                    with st.spinner("🎙️ Menerjemahkan suara via Gemini..."):
                        try:
                            base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
                            
                            # 💡 FIX URL AUDIO: Menyisipkan rute v1beta secara utuh ke dalam endpoint resmi Google
                            url_audio = "https://googleapis.com"
                            
                            query_params = {
                                "key": GEMINI_API_KEY_ANDA
                            }
                            
                            headers = {"Content-Type": "application/json"}
                            payload = {
                                "contents": [{
                                    "parts": [
                                        {"text": "Tolong dengarkan rekaman audio ini dengan seksama dan tulis ulang ucapan/kata-kata di dalamnya menjadi teks bersih (transkripsi bahasa Indonesia murni) tanpa tambahan penjelasan dari Anda."},
                                        {
                                            "inlineData": {
                                                "mimeType": "audio/wav",
                                                "data": base64_audio
                                            }
                                        }
                                    ]
                                }]
                            }
                            
                            response = requests.post(url_audio, headers=headers, params=query_params, json=payload)
                            
                            if response.status_code == 200:
                                response_data = response.json()
                                prompt_final = response_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                                st.session_state.last_processed_audio = audio_id
                            else:
                                st.error(f"Gagal memproses audio (Status {response.status_code}): {response.text}")
                        except Exception as audio_err:
                            st.error(f"Kendala audio: {audio_err}")

    # Eksekusi pengiriman pesan ke model utama (Groq Llama)
    if prompt_final:
        with st.chat_message("user"):
            st.write(prompt_final)
        st.session_state.groq_messages.append({"role": "user", "content": prompt_final})

        try:
            with st.spinner("AI sedang berpikir..."):
                respons = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=st.session_state.groq_messages
                )
                
                jawaban_ai = respons.choices[0].message.content
                
                with st.chat_message("assistant"):
                    st.write(jawaban_ai)
                st.session_state.groq_messages.append({"role": "assistant", "content": jawaban_ai})
                st.rerun()
                
        except Exception as e:
            st.error(f"Gagal memanggil Groq API: {e}")

# ==========================================
# 🖼️ MODUL 2: VISION AI & OCR EKSTRAKTOR (GEMINI)
# ==========================================
else:
    st.title("🖼️ Vision AI & OCR Ekstraktor Dokumen")
    st.write("Unggah foto kuitansi, tulisan tangan, atau gambar apa saja untuk dianalisis dan diekstrak teksnya.")

    foto_diunggah = st.file_uploader("Pilih berkas gambar Anda (Format: JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])

    if foto_diunggah:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(foto_diunggah, caption="Foto Yang Diunggah", use_container_width=True)
            
        with col2:
            st.subheader("💡 Opsi Pengolahan Gambar")
            opsi_tugas = st.selectbox(
                "Pilih Tindakan Khusus AI:",
                [
                    "📝 OCR Murni: Ekstrak semua teks di dalam gambar kata demi kata",
                    "🔍 Analisis Gambar Secara Umum & Detail",
                    "📊 Pahami & Rangkum data Kuitansi / Faktur belanja"
                ]
            )
            
            instruksi_tambahan = st.text_input("Tuliskan instruksi tambahan (Opsional):")
            
            if "OCR Murni" in opsi_tugas:
                prompt_perintah = "Lakukan OCR tingkat tinggi. Tolong baca gambar ini dan salin ulang setiap baris teks, huruf, angka, atau simbol yang Anda lihat di dalam gambar ini tanpa menambahkan opini atau kesimpulan Anda. Tulis dalam format teks bersih."
            elif "Kuitansi" in opsi_tugas:
                prompt_perintah = "Analisislah gambar kuitansi/faktur ini. Identifikasi dan buatkan rangkuman terstruktur yang mencakup nama toko, tanggal transaksi, daftar barang yang dibeli beserta harga masing-masing, serta total biaya akhir."
            else:
                prompt_perintah = "Analisislah gambar ini secara mendalam dan deskripsikan objek-objek penting di dalamnya secara detail."
                
            if instruksi_tambahan:
                prompt_perintah += f" Catatan tambahan dari pengguna: {instruksi_tambahan}"

            if st.button("🚀 Ekstrak & Jalankan Vision AI", use_container_width=True):
                with st.spinner("Mengirimkan file gambar ke server Google Vision API..."):
                    bytes_foto = foto_diunggah.read()
                    base64_foto = base64.b64encode(bytes_foto).decode('utf-8')
                    tipe_konten = foto_diunggah.type

                    url = "https://googleapis.com"
                    
                    query_params_vision = {
                        "key": GEMINI_API_KEY_ANDA
                    }
