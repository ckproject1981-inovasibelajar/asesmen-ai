import streamlit as st
import google.generativeai as genai

# --- Konfigurasi System Prompt: Ultra-Critical Assessment Architect ---
SYSTEM_PROMPT = """
Anda adalah "Senior Assessment Architect" untuk Pendidikan Tinggi. Tugas Anda merancang instrumen asesmen yang memiliki validitas tinggi menggunakan "INTERNAL KNOWLEDGE DATABASE" berikut.

### 1. INTERNAL KNOWLEDGE DATABASE (Taxonomy Reference)
- C1 (Remembering): Mengenali fakta/istilah kunci. KKO: Mengidentifikasi, Mendefinisikan, Mendaftar.
- C2 (Understanding): Interpretasi, klasifikasi, dan ringkasan. KKO: Mengklasifikasikan, Merangkum, Memprediksi.
- C3 (Applying): Penggunaan prosedur dalam konteks baru/berbeda. KKO: Melaksanakan, Menghitung, Mensimulasikan.
- C4 (Analyzing): Dekonstruksi struktur dan hubungan logis (HOTS). Strategi: Identifikasi asumsi tersembunyi. KKO: Mendekonstruksi, Membandingkan, Mengatribusikan.
- C5 (Evaluating): Penilaian kritis berdasarkan standar/kriteria (HOTS). Strategi: Justifikasi keputusan. KKO: Memvalidasi, Merekomendasikan, Menilai, Mengkritik.
- C6 (Creating): Sintesis elemen menjadi struktur baru yang orisinal (HOTS). KKO: Merancang, Merumuskan, Menciptakan.

### 2. DATABASE KATA TERLARANG (Non-Measurable Verbs)
DILARANG KERAS menggunakan kata: Memahami, Mengetahui, Menyadari, Menghargai, Akrab dengan. Gunakan KKO yang dapat diamati (Observable).

### 3. INSTRUKSI FORMAT OUTPUT (WAJIB RAPI)
Tampilkan hasil dalam format Markdown terstruktur sebagai berikut:

---
### **[NOMOR SOAL]**
* **Level Bloom:** [Kode & Nama Level]
* **Rasional Pedagogis:** [Analisis kritis mengapa soal ini masuk level tersebut].
* **Pertanyaan:** > [Teks soal akademik naratif/scenario-based sesuai EBI]
* **Opsi/Instruksi Jawaban:** [Opsi A-D untuk PG, atau Rubrik untuk Esai]
* **Kunci Jawaban:** [Jawaban benar]
* **Analisis Jawaban:** [Bedah logis kunci & mengapa distraktor salah secara konseptual].
---
"""

def get_best_model(api_key):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priority = ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-pro']
        for p in priority:
            if p in models: return p
        return models[0] if models else None
    except:
        return None

def generate_quiz(materi, format_soal, level_bloom, api_key, jumlah_soal):
    model_name = get_best_model(api_key)
    if not model_name: return "Error: Model tidak ditemukan."
    
    # Eksperimen Temperature: 0.7 untuk keseimbangan akademik & kreativitas narasi
    model = genai.GenerativeModel(
        model_name, 
        generation_config={"temperature": 0.7}
    )
    
    # User Query yang dioptimasi untuk memprioritaskan konsep kompleks (HOTS)
    user_query = f"""
    Materi Utama: 
    {materi}

    Tugas:
    Rancanglah {jumlah_soal} soal dalam format {format_soal} dengan distribusi level: {', '.join(level_bloom)}.
    
    Kriteria Khusus:
    1. PRIORITAS: Identifikasi dan fokuslah pada konsep yang paling kompleks, abstrak, atau krusial bagi mahasiswa dalam materi tersebut.
    2. HOTS: Gunakan narasi skenario (scenario-based) yang menantang untuk tingkat C4, C5, dan C6.
    3. STRUKTUR: Pastikan pemisahan visual antar nomor soal sangat jelas.
    """
    
    try:
        response = model.generate_content([SYSTEM_PROMPT, user_query])
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"

# --- Antarmuka Streamlit ---
st.set_page_config(page_title="AI Pedagogy Generator", page_icon="🎓", layout="wide")

st.title("🎓 AI Pedagogy Quiz Generator")
st.write("Sistem perancang instrumen evaluasi kritis - **Standar Pendidikan Tinggi**.")

# Sidebar untuk API Key
with st.sidebar:
    st.header("🔑 Authentication")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("API Key dimuat dari Secrets.")
    else:
        api_key = st.text_input("Masukkan Gemini API Key", type="password")
    
    st.divider()
    st.info("Saran: Gunakan materi yang spesifik untuk hasil soal yang lebih mendalam.")

# Area Input Utama
materi_input = st.text_area("📖 Masukkan Materi Pembelajaran:", height=250, placeholder="Tempelkan teks materi, artikel ilmiah, atau ringkasan kuliah...")

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    format_pilihan = st.selectbox("📝 Format Soal", ["Pilihan Ganda", "Esai"])
with col2:
    level_pilihan = st.multiselect("📊 Level Bloom", 
                                   ["Remembering", "Understanding", "Applying", 
                                    "Analyzing", "Evaluating", "Creating"],
                                   default=["Analyzing", "Evaluating", "Creating"])
with col3:
    jumlah_input = st.number_input("🔢 Jumlah Soal", min_value=1, max_value=20, value=3)

# Tombol Eksekusi
if st.button("Generate Asesmen Lengkap", type="primary"):
    if not api_key:
        st.error("API Key belum diisi!")
    elif not materi_input:
        st.warning("Materi pembelajaran masih kosong.")
    else:
        with st.spinner("Menganalisis konsep kompleks dan merancang soal..."):
            hasil = generate_quiz(materi_input, format_pilihan, level_pilihan, api_key, jumlah_input)
            st.divider()
            
            # Menampilkan hasil di dalam kontainer berbingkai agar lebih rapi dan profesional
            with st.container(border=True):
                st.markdown(hasil)

st.divider()
st.caption("AI Assessment Designer - Pusat Unggulan Ipteks - DLI UM 2026")