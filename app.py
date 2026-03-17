import streamlit as st
import google.generativeai as genai

# --- Konfigurasi System Prompt: Ultra-Critical Higher Education Assessment Architect ---
SYSTEM_PROMPT = """
Anda adalah "Senior Assessment Architect" untuk Pendidikan Tinggi. Tugas Anda adalah merancang instrumen asesmen yang memiliki validitas tinggi menggunakan "INTERNAL KNOWLEDGE DATABASE" berikut.

### 1. INTERNAL KNOWLEDGE DATABASE (Taxonomy Reference)
| Level | Fokus Kognitif | KKO Rekomendasi (Observable) | Strategi Pertanyaan (Stems) |
| :--- | :--- | :--- | :--- |
| **C1: Remembering** | Mengingat fakta mentah. | Mengidentifikasi, Mendefinisikan, Mendaftar, Menunjukkan. | "Apa yang dimaksud...", "Sebutkan komponen..." |
| **C2: Understanding** | Interpretasi & Prediksi. | Mengklasifikasikan, Merangkum, Memprediksi, Menjelaskan. | "Gunakan kata-kata sendiri untuk...", "Apa hasil dari..." |
| **C3: Applying** | Implementasi prosedur. | Mengimplementasikan, Menghitung, Mensimulasikan, Melaksanakan. | "Bagaimana cara menggunakan X untuk...", "Selesaikan..." |
| **C4: Analyzing** | Struktur & Hubungan. | Mendekonstruksi, Membandingkan, Mengatribusikan, Membedakan. | "Bedakan antara X dan Y...", "Apa asumsi di balik..." |
| **C5: Evaluating** | Penilaian & Kritik. | Menjustifikasi, Mengkritik, Memvalidasi, Merekomendasikan. | "Evaluasilah efektivitas...", "Mengapa kriteria X unggul..." |
| **C6: Creating** | Sintesis & Orisinalitas. | Merumuskan, Merancang, Mengonstruksi, Menciptakan. | "Rancanglah solusi untuk...", "Kembangkan rencana..." |

### 2. DATABASE KATA TERLARANG (Non-Measurable Verbs)
Dilarang keras menggunakan kata-kata: Memahami (Understand), Mengetahui (Know), Menyadari (Aware), Menghargai (Appreciate), Mempercayai (Believe), Akrab dengan (Familiar with).

### 3. DATABASE STRATEGI DISTRAKTOR
Gunakan "Plausible Misconceptions": Opsi salah harus terlihat benar bagi mahasiswa yang tidak belajar mendalam.

### 4. INSTRUKSI OUTPUT (FORMAT WAJIB)
[NOMOR SOAL]
- LEVEL BLOOM: [Kode & Nama]
- RASIONAL PEDAGOGIS: [Analisis kritis pemilihan level]
- PERTANYAAN: [Teks soal akademik sesuai EBI]
- OPSI/INSTRUKSI JAWABAN: [Opsi A-D atau panduan esai]
- KUNCI JAWABAN: [Jawaban benar/poin utama]
- ANALISIS JAWABAN: [Bedah kunci & distraktor]
"""

def generate_quiz(materi, format_soal, level_bloom, api_key, jumlah_soal):
    genai.configure(api_key=api_key)
    
    # --- LOGIKA FALLBACK MODEL (Mencegah Error 404) ---
    # Daftar model dari yang paling disarankan hingga alternatif
    model_candidates = [
        'gemini-1.5-flash-latest', 
        'gemini-1.5-flash', 
        'gemini-1.5-pro-latest',
        'gemini-pro'
    ]
    
    selected_model = None
    error_msg = ""
    
    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            # Tes singkat untuk memastikan model merespons (opsional, tapi aman)
            selected_model = model
            break 
        except Exception as e:
            error_msg = str(e)
            continue
            
    if not selected_model:
        return f"Gagal memuat model Gemini. Pastikan API Key aktif. Detail Error: {error_msg}"

    user_query = f"""
    Materi Pembelajaran: {materi}
    Instruksi: Buat {jumlah_soal} soal format {format_soal} pada level: {', '.join(level_bloom)}.
    Patuhi Internal Knowledge Database dalam prompt sistem.
    """
    
    try:
        response = selected_model.generate_content([SYSTEM_PROMPT, user_query])
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan saat pembuatan konten: {str(e)}"

# --- Antarmuka Streamlit ---
st.set_page_config(page_title="AI Pedagogy Generator", page_icon="🎓", layout="wide")

st.title("🎓 AI Pedagogy Quiz Generator")
st.markdown("Pembangun instrumen asesmen berbasis **Higher Order Thinking Skills (HOTS)**.")

# --- Manajemen API Key ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Masukkan Gemini API Key (Manual)", type="password")

# --- Area Input Utama ---
materi_input = st.text_area("📖 Masukkan Materi Pembelajaran:", height=250)

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    format_pilihan = st.selectbox("📝 Format Soal", ["Pilihan Ganda", "Esai"])
with col2:
    level_pilihan = st.multiselect("📊 Level Bloom", 
                                   ["Remembering", "Understanding", "Applying", 
                                    "Analyzing", "Evaluating", "Creating"],
                                   default=["Analyzing", "Evaluating"])
with col3:
    jumlah_input = st.number_input("🔢 Jumlah Soal", min_value=1, max_value=20, value=5)

if st.button("Generate Asesmen Lengkap", type="primary"):
    if not api_key:
        st.error("API Key kosong!")
    elif not materi_input:
        st.warning("Materi kosong!")
    else:
        with st.spinner("AI sedang memproses..."):
            hasil = generate_quiz(materi_input, format_pilihan, level_pilihan, api_key, jumlah_input)
            st.divider()
            st.markdown(hasil)

st.caption("AI Assessment Designer - Higher Education Edition")