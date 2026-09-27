import streamlit as st 
from groq import Groq
import os
from datetime import datetime

# Mengimpor SDK Resmi Google GenAI terbaru
try:
    from google import genai
    from google.genai import types
except ImportError:
    import google.genai as genai
    from google.genai import types

# 💡 HACKTIV8 BEST PRACTICES: Mengambil API Key dari brankas rahasia (Secrets) Streamlit Cloud
try:
    GROQ_API_KEY_ANDA = st.secrets["GROQ_API_KEY"]
    GEMINI_API_KEY_ANDA = st.secrets["GEMINI_API_KEY"]
    
    # 🔥 SOLUSI KUNCI MUTLAK: Daftarkan kunci AQ. langsung ke lingkungan sistem
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY_ANDA
except Exception:
    st.error("Gagal membaca API Key! Pastikan Anda sudah mengisi menu Secrets di Streamlit Cloud dengan benar.")
    st.stop()

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
    log_teks = f"RIWAYAT OBROLAN CHATBOT\n"
    log_teks += "="*50 + "\n\n"
    for msg in st.session_state.groq_messages:
        if msg["role"] != "system":
            role_label = "PENGGUNA" if msg["role"] == "user" else "ASISTEN AI"
            log_teks += f"[{role_label}]:\n{msg['content']}\n\n"
    
    st.sidebar.download_button(
        label="📥 Unduh Riwayat Obrolan (.txt)",
        data=log_teks,
        file_name="riwayat_chat.txt",
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
    st.write("Aplikasi live dengan fitur input teks dan transkripsi suara.")

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
                
                if st.session_state.last_processed_audio != audio_id and len(audio_bytes) > 100:
                    with st.spinner("🎙️ Menerjemahkan suara via Groq Whisper..."):
                        try:
                            transkripsi = client.audio.transcriptions.create(
                                model="whisper-large-v3",
                                file=("rekaman_asli.wav", audio_bytes, "audio/wav"),
                                response_format="verbose_json"
                            )
                            prompt_final = transkripsi.text.strip()
                            st.session_state.last_processed_audio = audio_id
                            st.info(f"🗣️ Terdeteksi: \"{prompt_final}\"")
                        except Exception as audio_err:
                            st.error(f"Gagal memproses audio lewat Whisper: {audio_err}")

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
    st.write("Unggah foto kuitansi, tulisan tangan, atau gambar apa saja untuk diekstrak teksnya.")

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
                    try:
                        bytes_foto = foto_diunggah.read()
                        tipe_konten = foto_diunggah.type

                        # 💡 FIX 401 UTAMA: Kosongkan inisialisasi Client() agar SDK membaca variabel lingkungan 'GEMINI_API_KEY'
                        # Cara ini memaksa SDK mengirimkan kunci bertipe AQ. murni lewat header x-goog-api-key bawaan
                        client_gemini = genai.Client()
                        
                        response = client_gemini.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[
                                prompt_perintah,
                                types.Part.from_bytes(
                                    data=bytes_foto,
                                    mime_type=tipe_konten,
                                )
                            ]
                        )
                        hasil_ekstraksi = response.text
                        
                        st.success("✨ Hasil Pemrosesan Vision AI:")
                        st.text_area("Salin Hasil Teks Di Sini:", value=hasil_ekstraksi, height=300)
                        st.download_button(label="💾 Unduh Hasil Teks Ekstraksi (.txt)", data=hasil_ekstraksi, file_name="hasil_ocr.txt", mime="text/plain")
                    except Exception as vision_err:
                        st.error(f"Terjadi kendala pemrosesan gambar via SDK: {vision_err}")
