import streamlit as st
import google.generativeai as genai

# --- Konfigurasi System Prompt: Ultra-Critical Assessment Architect ---
# Menggabungkan data dari Pitt University & Bloom's Taxonomy Revised
SYSTEM_PROMPT = """
Anda adalah "Senior Assessment Architect" untuk Pendidikan Tinggi. Tugas Anda merancang instrumen asesmen yang memiliki validitas tinggi menggunakan "INTERNAL KNOWLEDGE DATABASE" berikut.

### 1. INTERNAL KNOWLEDGE DATABASE (Taxonomy Reference)
- C1 (Remembering): Mengenali fakta/istilah kunci. Strategi: Fokus pada siapa, apa, kapan, di mana. KKO: Mengidentifikasi, Mendefinisikan, Mendaftar.
- C2 (Understanding): Interpretasi, klasifikasi, dan ringkasan. Strategi: Memprediksi konsekuensi atau menjelaskan dengan kata sendiri. KKO: Mengklasifikasikan, Merangkum, Memprediksi.
- C3 (Applying): Penggunaan prosedur dalam konteks baru/berbeda. Strategi: Simulasi atau implementasi rumus/metode. KKO: Melaksanakan, Menghitung, Mensimulasikan.
- C4 (Analyzing): Dekonstruksi struktur dan hubungan logis (HOTS). Strategi: Perbandingan, kontras, dan identifikasi asumsi tersembunyi. KKO: Mendekonstruksi, Membandingkan, Mengatribusikan.
- C5 (Evaluating): Penilaian kritis berdasarkan standar/kriteria (HOTS). Strategi: Menilai efektivitas atau menjustifikasi keputusan. KKO: Memvalidasi, Merekomendasikan, Menilai, Mengkritik.
- C6 (Creating): Sintesis elemen menjadi struktur baru yang orisinal (HOTS). Strategi: Merumuskan teori baru atau merancang rencana strategis. KKO: Merancang, Merumuskan, Menciptakan.

### 2. DATABASE KATA TERLARANG (Non-Measurable Verbs)
Berdasarkan standar penilaian objektif, DILARANG KERAS menggunakan kata-kata ambigu berikut:
- Memahami (Understand), Mengetahui (Know), Menyadari (Aware), Menghargai (Appreciate), Akrab dengan (Familiar with).
Gunakan hanya Kata Kerja Operasional (KKO) yang dapat diamati (Observable).

### 3. KONTROL KUALITAS DISTRAKTOR (Pilihan Ganda)
- Gunakan "Plausible Misconceptions": Opsi salah harus terlihat logis bagi mahasiswa yang tidak belajar mendalam.
- Pastikan semua opsi memiliki panjang kalimat yang relatif sama untuk menghindari bias.

### 4. INSTRUKSI FORMAT OUTPUT (WAJIB RAPI)
Tampilkan hasil dalam format Markdown yang terstruktur sebagai berikut:

---
### **[NOMOR SOAL]**
* **Level Bloom:** [Kode & Nama Level]
* **Rasional Pedagogis:** [Analisis kritis mengapa soal ini masuk level tersebut berdasarkan aktivitas kognitif yang diminta].
* **Pertanyaan:** > [Teks soal akademik yang naratif dan kritis sesuai EBI]
* **Opsi/Instruksi Jawaban:**
  [List Opsi A-D untuk PG, atau Rubrik Singkat untuk Esai]
* **Kunci Jawaban:** [Jawaban benar]
* **Analisis Jawaban:** [Bedah secara logis mengapa jawaban tersebut benar dan mengapa distraktor lainnya salah secara konseptual].
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
    
    model = genai.GenerativeModel(model_name)
    
    # Memaksa AI memberikan output yang lebih naratif dan terstruktur
    user_query = f"""
    Materi Utama: 
    {materi}

    Tugas:
    Rancanglah {jumlah_soal} soal dalam format {format_soal}.
    Distribusi level kognitif: {', '.join(level_bloom)}.
    
    Kriteria Khusus:
    1. Gunakan narasi yang kaya (scenario-based) untuk tingkat C4-C6.
    2. Pastikan setiap nomor soal memiliki pemisahan visual yang jelas (gunakan garis pemisah).
    3. Fokus pada analisis kritis sesuai standar Pendidikan Tinggi.
    """
    
    try:
        response = model.generate_content([SYSTEM_PROMPT, user_query])
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"

# --- Antarmuka Streamlit ---
st.set_page_config(page_title="AI Pedagogy Generator", page_icon="🎓", layout="wide")

st.title("🎓 AI Pedagogy Quiz Generator")
st.write("Sistem perancang instrumen evaluasi kritis berbasis Standar Taksonomi Bloom Revised.")

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Masukkan Gemini API Key", type="password")

materi_input = st.text_area("📖 Tempelkan Materi Pembelajaran di sini:", height=250, placeholder="Masukkan materi teks atau transkrip kuliah...")

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

if st.button("Generate Asesmen Lengkap", type="primary"):
    if not api_key:
        st.error("Mohon isi API Key di sidebar.")
    elif not materi_input:
        st.warning("Materi tidak boleh kosong.")
    else:
        with st.spinner("Menganalisis materi secara kritis..."):
            hasil = generate_quiz(materi_input, format_pilihan, level_pilihan, api_key, jumlah_input)
            st.divider()
            # Menampilkan hasil dengan tampilan markdown yang lebih rapi
            st.markdown(hasil)

st.divider()
st.caption("AI Assessment Designer - Universitas Negeri Malang Edition")