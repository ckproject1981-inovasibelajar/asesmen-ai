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
1. Level Bloom: Sebutkan kode (C1-C6) dan nama tingkatannya.
2. Rasional Level Bloom: Jelaskan alasan mengapa pertanyaan tersebut dikategorikan ke dalam level tersebut berdasarkan aktivitas kognitif yang diminta.
3. Pertanyaan: Teks soal yang jelas dan akademis.
4. Pilihan Jawaban/Instruksi Jawaban: (Opsi A-D untuk Pilihan Ganda, atau batasan jawaban untuk Esai).
5. Kunci Jawaban: Jawaban yang benar atau poin utama yang diharapkan.
6. Penjelasan Kunci Jawaban: Alasan logis mengapa jawaban tersebut benar berdasarkan materi pembelajaran.

Gunakan bahasa Indonesia yang formal dan akademis (sesuai EBI).
"""

def generate_quiz(materi, format_soal, level_bloom, api_key, model_choice):
    # Konfigurasi API
    genai.configure(api_key=api_key)
    
    # Logika Pemilihan Model
    if model_choice == "Gemini 1.5 Flash (Cepat)":
        selected_model = "gemini-1.5-flash"
    else:
        selected_model = "gemini-1.5-pro"
        
    model = genai.GenerativeModel(selected_model)
    
    user_query = f"""
    Materi Pembelajaran: 
    {materi}

    Instruksi Tugas:
    Buatlah soal dalam format {format_soal} untuk tingkat kognitif berikut: {', '.join(level_bloom)}.
    Terapkan instruksi khusus mengenai Rasional Bloom dan Penjelasan Jawaban secara mendetail.
    """
    
    try:
        response = model.generate_content([SYSTEM_PROMPT, user_query])
        return response.text
    except Exception as e:
        return f"Terjadi kesalahan pada model: {str(e)}"

# --- Antarmuka Streamlit ---
st.set_page_config(page_title="AI Pedagogy Generator", page_icon="🎓", layout="wide")

st.title("🎓 AI Pedagogy Quiz Generator")
st.markdown("Pembangun instrumen asesmen berbasis **Higher Order Thinking Skills (HOTS)**.")

# --- Manajemen API Key (Streamlit Secrets) ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = st.sidebar.text_input("Masukkan Gemini API Key (Manual)", type="password")
    st.sidebar.warning("Tips: Simpan API Key di `.streamlit/secrets.toml` untuk penggunaan otomatis.")

# --- Sidebar Pengaturan ---
with st.sidebar:
    st.header("⚙️ Pengaturan Model")
    model_option = st.radio(
        "Pilih Otak AI:",
        ("Gemini 1.5 Flash (Cepat)", "Gemini 1.5 Pro (Lebih Akurat/HOTS)")
    )
    st.divider()
    st.info("Model Pro sangat disarankan untuk menghasilkan 'Rasional Pedagogis' dan 'Penjelasan Jawaban' yang lebih mendalam.")

# --- Area Input ---
materi_input = st.text_area("📖 Masukkan Materi Pembelajaran:", height=250, placeholder="Tempelkan teks materi atau ringkasan kuliah di sini...")

col1, col2 = st.columns(2)
with col1:
    format_pilihan = st.selectbox("📝 Format Soal", ["Pilihan Ganda", "Esai"])
with col2:
    level_pilihan = st.multiselect("📊 Level Bloom", 
                                   ["Remembering", "Understanding", "Applying", 
                                    "Analyzing", "Evaluating", "Creating"],
                                   default=["Analyzing", "Evaluating"])

# --- Eksekusi ---
if st.button("Generate Asesmen Lengkap", type="primary"):
    if not api_key:
        st.error("API Key tidak ditemukan! Masukkan di sidebar atau st.secrets.")
    elif not materi_input:
        st.warning("Mohon masukkan materi pembelajaran terlebih dahulu.")
    elif not level_pilihan:
        st.warning("Pilih setidaknya satu Level Bloom.")
    else:
        with st.spinner(f"AI sedang menganalisis materi dan merancang soal menggunakan {model_option}..."):
            hasil_soal = generate_quiz(materi_input, format_pilihan, level_pilihan, api_key, model_option)
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
st.caption("Dikembangkan untuk mendukung Standar Penilaian Perguruan Tinggi (OBE).")