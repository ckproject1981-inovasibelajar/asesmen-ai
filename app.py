import streamlit as st
import google.generativeai as genai

# --- Konfigurasi System Prompt: Higher Education Assessment Designer ---
SYSTEM_PROMPT = """
Anda adalah "Expert Instructional Designer" untuk Perguruan Tinggi. Tugas Anda adalah merancang soal asesmen (Esai atau Pilihan Ganda) yang berbasis pada Bloom's Taxonomy Revised dan materi pembelajaran yang diberikan.

PEDOMAN KKO UNTUK LEVEL PERGURUAN TINGGI:

1. C1 - Remembering (Mengingat): Fokus pada rekognisi fakta mentah.
   - KKO: Mengidentifikasi, menyebutkan, mendaftar, menunjukkan, mendefinisikan, menyatakan kembali.
   - Question Stem: "Sebutkan komponen utama dari...", "Definisikan istilah...".

2. C2 - Understanding (Memahami): Fokus pada interpretasi dan ekstrapolasi makna.
   - KKO: Mengklasifikasikan, mengilustrasikan, merangkum, mengonversi, membedakan (secara konseptual), mengestimasi.
   - Question Stem: "Gunakan kata-kata Anda sendiri untuk menjelaskan...", "Rangkum poin utama dari...".

3. C3 - Applying (Menerapkan): Fokus pada implementasi prosedur dalam konteks baru.
   - KKO: Mengimplementasikan, mendemonstrasikan, mengoperasikan, menghitung, memodifikasi, mensimulasikan.
   - Question Stem: "Bagaimana Anda akan menerapkan konsep X untuk menyelesaikan...", "Demonstrasikan penggunaan...".

4. C4 - Analyzing (Menganalisis): Fokus pada dekonstruksi struktur dan hubungan logis (HOTS).
   - KKO: Mendekonstruksi, mengorganisasikan, mengatribusikan, membedakan (secara struktural), menguji, menyurvei.
   - Question Stem: "Identifikasi asumsi di balik...", "Analisislah hubungan antara X dan Y...", "Apa bukti yang mendukung...".

5. C5 - Evaluating (Mengevaluasi): Fokus pada penilaian kritis berdasarkan standar/kriteria (HOTS).
   - KKO: Mengkritik, menilai (appraise), menjustifikasi, memvalidasi, memprioritaskan, merekomendasikan.
   - Question Stem: "Evaluasilah efektivitas dari...", "Justifikasikan mengapa prosedur X lebih baik daripada Y...", "Kritiklah argumen berikut berdasarkan...".

6. C6 - Creating (Menciptakan): Fokus pada sintesis elemen menjadi struktur baru yang orisinal (HOTS).
   - KKO: Merumuskan (formulate), merancang (design), mengonstruksi, menciptakan, mengembangkan, menyusun rencana.
   - Question Stem: "Rancanglah sebuah prototipe/model untuk...", "Rumuskan sebuah teori atau hipotesis yang menjelaskan...", "Kembangkan sebuah rencana strategis untuk...".

INSTRUKSI KHUSUS UNTUK FORMAT OUTPUT:
Untuk setiap butir soal yang dihasilkan, Anda WAJIB menyertakan elemen berikut:
1. Level Bloom: Kode (C1-C6) dan nama tingkatannya.
2. Rasional Level Bloom: Penjelasan aktivitas kognitif mengapa soal masuk level tersebut.
3. Pertanyaan: Teks soal akademis.
4. Pilihan Jawaban/Instruksi Jawaban: (Opsi A-D untuk Pilihan Ganda, atau batasan jawaban untuk Esai).
5. Kunci Jawaban: Jawaban benar atau poin utama.
6. Penjelasan Kunci Jawaban: Alasan logis berdasarkan materi.

Gunakan bahasa Indonesia yang formal dan akademis (sesuai EBI).
"""

def generate_quiz(materi, format_soal, level_bloom, api_key, jumlah_soal):
    # Konfigurasi API
    genai.configure(api_key=api_key)
    
    # Menggunakan model gemini-1.5-flash untuk stabilitas dan kecepatan
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    user_query = f"""
    Materi Pembelajaran: 
    {materi}

    Instruksi Tugas:
    Buatlah sebanyak {jumlah_soal} soal dalam format {format_soal}.
    Distribusikan soal tersebut pada tingkat kognitif berikut: {', '.join(level_bloom)}.
    Pastikan setiap nomor soal memiliki Rasional Bloom dan Penjelasan Jawaban secara mendetail.
    """
    
    try:
        response = model.generate_content([SYSTEM_PROMPT, user_query])
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan pada sistem: {str(e)}"

# --- Antarmuka Streamlit ---
st.set_page_config(page_title="AI Pedagogy Generator", page_icon="🎓", layout="wide")

st.title("🎓 AI Pedagogy Quiz Generator")
st.markdown("Pembangun instrumen asesmen berbasis **Higher Order Thinking Skills (HOTS)** untuk Perguruan Tinggi.")

# --- Manajemen API Key ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Masukkan Gemini API Key (Manual)", type="password")
    st.sidebar.warning("Dapatkan API Key di Google AI Studio.")

# --- Sidebar Info ---
with st.sidebar:
    st.header("📌 Info Aplikasi")
    st.write("Aplikasi ini menggunakan model **Gemini 1.5 Flash** untuk kecepatan pemrosesan data materi secara instan.")
    st.divider()
    st.caption("Dikembangkan untuk mendukung Standar OBE (Outcome-Based Education).")

# --- Area Input ---
materi_input = st.text_area("📖 Masukkan Materi Pembelajaran:", height=200, placeholder="Tempelkan teks materi atau ringkasan kuliah di sini...")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    format_pilihan = st.selectbox("📝 Format Soal", ["Pilihan Ganda", "Esai"])
with col2:
    level_pilihan = st.multiselect("📊 Level Bloom", 
                                   ["Remembering", "Understanding", "Applying", 
                                    "Analyzing", "Evaluating", "Creating"],
                                   default=["Analyzing", "Evaluating"])
with col3:
    jumlah_soal = st.number_input("🔢 Jumlah Soal", min_value=1, max_value=20, value=5)

# --- Eksekusi ---
if st.button("Generate Asesmen Lengkap", type="primary"):
    if not api_key:
        st.error("API Key tidak ditemukan! Masukkan di sidebar atau st.secrets.")
    elif not materi_input:
        st.warning("Mohon masukkan materi pembelajaran terlebih dahulu.")
    elif not level_pilihan:
        st.warning("Pilih setidaknya satu Level Bloom.")
    else:
        with st.spinner("AI sedang merancang soal berdasarkan standar pedagogi..."):
            hasil_soal = generate_quiz(materi_input, format_pilihan, level_pilihan, api_key, jumlah_soal)
            st.divider()
            st.markdown(hasil_soal)
            
            # Tombol Unduh
            st.download_button(
                label="📥 Unduh Hasil Asesmen",
                data=hasil_soal,
                file_name="asesmen_bloom_lengkap.txt",
                mime="text/plain"
            )

st.markdown("---")
st.caption("© 2026 AI Assessment Designer - Higher Education Edition")