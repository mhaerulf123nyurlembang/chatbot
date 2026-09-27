import streamlit as st 
from groq import Groq

# ⚠️ TEMPELKAN KUNCI GROQ API ANDA (Wajib Diawali gsk_) DI BAWAH INI:
GROQ_API_KEY_ANDA = "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"

# Set halaman web agar memiliki tata letak yang bagus
st.set_page_config(page_title="Chatbot AI Groq", layout="wide")

# ==========================================
# 📊 KONFIGURASI SIDEBAR (MENU SAMPING)
# ==========================================
st.sidebar.title("⚙️ Pengaturan Sistem")
st.sidebar.write("Sesuaikan performa mesin AI Anda di bawah ini:")

# 1. Fitur Pemilih Model (Model Switcher)
pilihan_model = st.sidebar.selectbox(
    "Pilih Model AI:",
    ["openai/gpt-oss-120b", "llama-3.3-70b-versatile", "llama3-70b-8192"],
    index=0,
    help="openai/gpt-oss-120b sangat cerdas, sedangkan Llama sangat cepat."
)

# 2. Fitur Pengatur Kreativitas (Temperature Slider)
suhu_ai = st.sidebar.slider(
    "Tingkat Kreativitas (Temperature):",
    min_value=0.0,
    max_value=1.0,
    value=0.7,
    step=0.1,
    help="Makin tinggi angkanya, jawaban AI akan makin kreatif dan bervariasi."
)

st.sidebar.markdown("---")

# Tombol Bersihkan Chat dipindahkan ke sidebar agar tampilan utama bersih
if st.sidebar.button("🗑️ Sapukan / Bersihkan Chat", use_container_width=True):
    st.session_state.groq_messages = []
    st.rerun()

# ==========================================
# 🤖 HALAMAN UTAMA CHATBOT
# ==========================================
st.title("⚡ Chatbot AI Super Cepat (Powered by Groq)")
st.write(f"Aplikasi live menggunakan model: `{pilihan_model}`")

# Inisialisasi Klien Groq Resmi
if GROQ_API_KEY_ANDA == "gsk_TEMPELKAN_KUNCI_GROQ_ASLI_DI_SINI" or not GROQ_API_KEY_ANDA:
    st.error("Silakan ganti teks 'gsk_...' di kode GitHub dengan Groq API Key asli Anda!")
    st.stop()
else:
    client = Groq(api_key=GROQ_API_KEY_ANDA)

# Menginisialisasi riwayat obrolan internal
if "groq_messages" not in st.session_state:
    st.session_state.groq_messages = [
        {"role": "system", "content": "Anda adalah asisten AI yang sangat cerdas, responsif, ramah, dan membantu."}
    ]

# 3. Fitur Statistik Riwayat Pesan di Sidebar
# Menghitung jumlah chat (dikurangi 1 karena indeks 0 adalah system prompt rahasia)
jumlah_pesan = max(0, len(st.session_state.groq_messages) - 1)
st.sidebar.metric(label="Jumlah Percakapan", value=f"{jumlah_pesan} Pesan")

# Menampilkan riwayat obrolan di halaman web Streamlit
for msg in st.session_state.groq_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Menerima ketikan pesan baru dari pengguna
if prompt := st.chat_input("Ketik pesan Anda di sini..."):
    # Tampilkan pesan user ke layar secara instan
    with st.chat_message("user"):
        st.write(prompt)
    
    st.session_state.groq_messages.append({"role": "user", "content": prompt})

    # Mengirim data percakapan ke server Groq
    try:
        respons = client.chat.completions.create(
            model=pilihan_model, # 💡 Variabel dinamis mengambil pilihan dari sidebar
            messages=st.session_state.groq_messages,
            temperature=suhu_ai   # 💡 Variabel dinamis mengambil angka slider dari sidebar
        )
        
        # Mengambil balasan teks dari list choices objek pertama secara presisi
        jawaban_ai = respons.choices[0].message.content

        # Tampilkan balasan AI di layar web
        with st.chat_message("assistant"):
            st.write(jawaban_ai)
        
        st.session_state.groq_messages.append({"role": "assistant", "content": jawaban_ai})
        
        # Memperbarui halaman agar jumlah counter pesan di sidebar langsung berubah
        st.rerun()
        
    except Exception as e:
        st.error(f"Gagal memanggil Groq API: {e}")
