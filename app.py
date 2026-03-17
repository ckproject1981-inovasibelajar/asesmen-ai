import streamlit as st
import google.generativeai as genai

# --- Konfigurasi System Prompt: Ultra-Critical Assessment Architect ---
# Menggabungkan data dari Pitt University & Bloom's Taxonomy Revised
SYSTEM_PROMPT = """
Anda adalah "Senior Assessment Architect" untuk Pendidikan Tinggi. Tugas Anda merancang instrumen asesmen menggunakan "INTERNAL KNOWLEDGE DATABASE" berikut.

### 1. INTERNAL KNOWLEDGE DATABASE
- C1 (Remembering): Fokus pada rekognisi fakta. KKO: Mengidentifikasi, Mendefinisikan.
- C2 (Understanding): Fokus pada interpretasi. KKO: Klasifikasi, Memprediksi, Menjelaskan.
- C3 (Applying): Fokus pada prosedur. KKO: Melaksanakan, Menghitung, Mensimulasikan.
- C4 (Analyzing): Fokus pada struktur/hubungan. KKO: Mendekonstruksi, Membedakan, Mengatribusikan.
- C5 (Evaluating): Fokus pada kritik/justifikasi. KKO: Memvalidasi, Merekomendasikan, Menilai.
- C6 (Creating): Fokus pada sintesis/orisinalitas. KKO: Merancang, Merumuskan, Menciptakan.

### 2. DATABASE KATA TERLARANG (Non-Measurable)
Dilarang keras menggunakan: Memahami (Understand), Mengetahui (Know), Menyadari (Aware), Menghargai (Appreciate), Akrab dengan (Familiar with).

### 3. INSTRUKSI OUTPUT (FORMAT WAJIB)
[NOMOR SOAL]
- LEVEL BLOOM: [Kode & Nama]
- RASIONAL PEDAGOGIS: [Analisis kritis mengapa soal ini masuk level tersebut]
- PERTANYAAN: [Teks soal akademik sesuai EBI]
- OPSI/INSTRUKSI JAWABAN: [Opsi A-D atau panduan esai]
- KUNCI JAWABAN: [Jawaban benar/poin utama]
- ANALISIS JAWABAN: [Bedah kunci & mengapa distraktor salah secara konseptual]
"""

def get_best_model(api_key):
    """Mencari model yang tersedia secara dinamis untuk menghindari Error 404"""
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prioritas model: Flash 1.5 -> Flash terbaru -> Pro -> Apa saja yang ada
        priority = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-pro', 'models/gemini-pro']
        
        for p in priority:
            if p in models:
                return p
        return models[0] if models else None
    except:
        return None

def generate_quiz(materi, format_soal, level_bloom, api_key, jumlah_soal):
    model_name = get_best_model(api_key)
    
    if not model_name:
        return "Error: Tidak dapat menemukan model Gemini yang kompatibel di akun Anda."
    
    model = genai.GenerativeModel(model_name)
    
    user_query = f"""
    Materi: {materi}
    Instruksi: Buat {jumlah_soal} soal {format_soal} untuk level: {', '.join(level_bloom)}.
    Patuhi Internal Database dalam prompt sistem. Sertakan Analisis Jawaban yang kritis.
    """
    
    try:
        response = model.generate_content([SYSTEM_PROMPT, user_query])
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan saat pembuatan konten: {str(e)}"

# --- Antarmuka Streamlit ---
st.set_page_config(page_title="AI Pedagogy Generator", page_icon="🎓", layout="wide")

st.title("🎓 AI Pedagogy Quiz Generator")
st.markdown("Pembangun asesmen berbasis **Higher Order Thinking Skills (HOTS)**.")

# --- Manajemen API Key ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Masukkan Gemini API Key", type="password")

# --- Area Input ---
materi_input = st.text_area("📖 Masukkan Materi Pembelajaran:", height=200)

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
        st.error("API Key belum diisi!")
    elif not materi_input:
        st.warning("Silakan masukkan materi.")
    else:
        with st.spinner("Mencari model terbaik dan merancang soal..."):
            hasil = generate_quiz(materi_input, format_pilihan, level_pilihan, api_key, jumlah_input)
            st.divider()
            st.markdown(hasil)

st.caption("AI Assessment Designer - Higher Education Edition")