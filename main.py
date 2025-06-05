import streamlit as st
import sqlite3
from datetime import datetime
from fpdf import FPDF
import os

# === PAGE CONFIG: MUST BE FIRST STREAMLIT COMMAND ===
st.set_page_config(page_title="🩺 Smart Medical Self-Consultation", layout="centered")

# === TRANSLATIONS ===
translations = {
    "en": {
        "app_title": "🩺 Smart Medical Self-Consultation",
        "subtitle": "Follow the steps below to get your diagnosis and treatment plan.",
        "step1": "Step 1: Patient Information",
        "step2": "Step 2: Select Symptoms",
        "step3": "Step 3: Diagnosis",
        "step4": "Step 4: Download Your Report",
        "name": "Full Name",
        "age": "Age",
        "gender": "Gender",
        "next": "Next",
        "symptoms": "Choose your symptoms",
        "diagnosis": "Diagnosis",
        "treatment": "Treatment Plan",
        "finalize": "Finalize and Save",
        "download": "📄 Download Consultation Report",
        "new": "Start New Consultation",
        "history": "📁 Past Consultations",
        "saved": "Consultation saved! Generating PDF...",
        "gender_opts": ["Male", "Female", "Other"],
        "symptoms_list": ["Fever", "Cough", "Headache", "Toothache", "Fatigue", "Shortness of breath"]
    },
    "rw": {
        "app_title": "🩺 Kwisuzumisha kwa Muganga",
        "subtitle": "Kurikirana intambwe zikurikira kugira ngo ubone ibisubizo.",
        "step1": "Intambwe ya 1: Amakuru y’Umurwayi",
        "step2": "Intambwe ya 2: Hitamo Ibimenyetso",
        "step3": "Intambwe ya 3: Isuzuma",
        "step4": "Intambwe ya 4: Kuramo Raporo yawe",
        "name": "Amazina y'umurwayi",
        "age": "Imyaka",
        "gender": "Igitsina",
        "next": "Komeza",
        "symptoms": "Hitamo ibimenyetso",
        "diagnosis": "Isuzuma",
        "treatment": "Uburyo bwo Kuvura",
        "finalize": "Rangiza & Bika",
        "download": "📄 Kuramo Raporo",
        "new": "Tangira Isuzuma Rishya",
        "history": "📁 Amakuru Yabitswe",
        "saved": "Isuzuma ribitswe! Raporo iri gutegurwa...",
        "gender_opts": ["Gabo", "Gore", "Ibindi"],
        "symptoms_list": ["Guh feveri", "Inkoko", "Umutwe", "Kubabara amenyo", "Kunanirwa", "Guhumeka nabi"]
    }
}

# === SELECT LANGUAGE ===
st.sidebar.title("🌐 Language / Ururimi")
lang = st.sidebar.radio("Choose Language", options=["en", "rw"], format_func=lambda l: "English" if l == "en" else "Kinyarwanda")
T = translations[lang]

# === DATABASE SETUP ===
conn = sqlite3.connect('patient_data.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        symptoms TEXT,
        diagnosis TEXT,
        treatment TEXT,
        created_at TEXT
    )
''')
conn.commit()

# === SESSION SETUP ===
st.title(T["app_title"])
st.markdown(T["subtitle"])

if "step" not in st.session_state:
    st.session_state.step = 1

if "form_data" not in st.session_state:
    st.session_state.form_data = {}

# === STEP 1: PATIENT INFO ===
if st.session_state.step == 1:
    st.subheader(T["step1"])
    with st.form("patient_info_form"):
        name = st.text_input(T["name"])
        age = st.number_input(T["age"], 1, 120)
        gender = st.selectbox(T["gender"], T["gender_opts"])
        submitted = st.form_submit_button(T["next"])
        if submitted and name:
            st.session_state.form_data.update({"name": name, "age": age, "gender": gender})
            st.session_state.step = 2

# === STEP 2: SYMPTOMS ===
elif st.session_state.step == 2:
    st.subheader(T["step2"])
    selected_symptoms = st.multiselect(T["symptoms"], T["symptoms_list"])
    if st.button(T["next"]) and selected_symptoms:
        st.session_state.form_data["symptoms"] = selected_symptoms
        st.session_state.step = 3

# === STEP 3: DIAGNOSIS ===
elif st.session_state.step == 3:
    st.subheader(T["step3"])
    symptoms = st.session_state.form_data["symptoms"]
    diagnosis = "General Viral Infection"
    treatment = "Paracetamol and rest"

    if "Toothache" in symptoms or "Kubabara amenyo" in symptoms:
        diagnosis = "Possible Dental Infection"
        treatment = "Ibuprofen + Dental evaluation"
    elif "Shortness of breath" in symptoms or "Guhumeka nabi" in symptoms:
        diagnosis = "Suspected Respiratory Issue"
        treatment = "Immediate clinical exam recommended"

    st.session_state.form_data.update({"diagnosis": diagnosis, "treatment": treatment})
    st.markdown(f"**{T['diagnosis']}:** {diagnosis}")
    st.markdown(f"**{T['treatment']}:** {treatment}")

    if st.button(T["finalize"]):
        data = st.session_state.form_data
        c.execute('''
            INSERT INTO consultations (name, age, gender, symptoms, diagnosis, treatment, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["name"],
            data["age"],
            data["gender"],
            ", ".join(data["symptoms"]),
            data["diagnosis"],
            data["treatment"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        st.success(T["saved"])
        st.session_state.step = 4

# === STEP 4: PDF DOWNLOAD ===
elif st.session_state.step == 4:
    st.subheader(T["step4"])

    def generate_pdf(data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Medical Consultation Report", ln=True, align='C')
        pdf.ln(10)
        for key, value in data.items():
            if isinstance(value, list):
                value = ", ".join(value)
            pdf.cell(200, 10, txt=f"{key.capitalize()}: {value}", ln=True)
        filename = f"consultation_{data['name'].replace(' ', '_')}.pdf"
        path = os.path.join("reports", filename)
        os.makedirs("reports", exist_ok=True)
        pdf.output(path)
        return path

    report_path = generate_pdf(st.session_state.form_data)
    with open(report_path, "rb") as f:
        st.download_button(
            label=T["download"],
            data=f,
            file_name=os.path.basename(report_path),
            mime="application/pdf"
        )

    if st.button(T["new"]):
        st.session_state.step = 1
        st.session_state.form_data = {}

# === SIDEBAR HISTORY ===
with st.sidebar:
    st.header(T["history"])
    results = c.execute("SELECT name, created_at, diagnosis FROM consultations ORDER BY id DESC LIMIT 10").fetchall()
    for row in results:
        st.markdown(f"- **{row[0]}** | {row[1][:16]} | _{row[2]}_")
