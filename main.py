import streamlit as st
import pandas as pd
import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}

def next_step():
    st.session_state.step += 1

def prev_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1

def infer_diagnosis_refined(answers):
    complaint = answers.get("complaint")
    diagnosis = []
    recommendations = []
    treatment_plan = []

    if complaint == "Toothache":
        severity = answers.get("pain_severity", "Mild")
        duration = answers.get("pain_duration", 0)
        trigger = answers.get("pain_trigger", "None")

        if severity == "Severe" and duration > 3 and trigger in ["Cold", "Heat"]:
            diagnosis.append("Irreversible pulpitis or deep dental caries")
            recommendations.append("Urgent endodontic evaluation needed.")
            treatment_plan.append("Root canal therapy or extraction.")
        else:
            diagnosis.append("General tooth sensitivity")
            recommendations.append("Monitor with desensitizing toothpaste.")
            treatment_plan.append("Topical fluoride.")

    return f"""**Possible Diagnoses:**  
- {'; '.join(diagnosis)}

**Recommendations:**  
- {'; '.join(recommendations)}

**Treatment Plan:**  
- {'; '.join(treatment_plan)}"""

def save_consultation_to_csv(answers, diagnosis_output):
    file_path = "consultations.csv"
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patient_name": answers.get("patient_name"),
        "age": answers.get("age"),
        "gender": answers.get("gender"),
        "complaint": answers.get("complaint"),
        "summary": diagnosis_output.replace("\n", " "),
    }
    df_new = pd.DataFrame([data])

    if os.path.exists(file_path):
        df_existing = pd.read_csv(file_path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(file_path, index=False)

def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    # Add logo
    logo_path = "static/logo.png"  # Adjust path to your logo file
    try:
        logo = ImageReader(logo_path)
        c.drawImage(logo, 50, 680, width=300, height=150)  # Position and size
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Add consultation details
    c.drawString(100, 700, "Patient Consultation Report")
    for index, (key, value) in enumerate(st.session_state.answers.items()):
        c.drawString(100, 680 - (index * 20), f"{key.capitalize()}: {value}")

    c.save()
    buffer.seek(0)
    return buffer

# Step 1: Patient Info
if st.session_state.step == 1:
    st.title("🦷 Elite Dental Consultation")
    st.header("Step 1: Patient Info")
    st.session_state.answers["patient_name"] = st.text_input("Patient Name", value=st.session_state.answers.get("patient_name", ""))
    st.session_state.answers["age"] = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.answers.get("age", 0))
    st.session_state.answers["gender"] = st.radio("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.answers.get("gender", "Male")))

    if st.button("Next"):
        if not st.session_state.answers["patient_name"] or st.session_state.answers["age"] == 0:
            st.error("Please fill patient name and age.")
        else:
            next_step()

# Step 2: Complaint
elif st.session_state.step == 2:
    st.header("Step 2: Presenting Complaint")
    st.session_state.answers["complaint"] = st.selectbox("What is the main complaint?", ["Toothache", "Bleeding gums", "Swelling", "Other"],
        index=["Toothache", "Bleeding gums", "Swelling", "Other"].index(st.session_state.answers.get("complaint", "Toothache")))

    if st.button("Back"):
        prev_step()
    if st.button("Next"):
        next_step()

# Step 3: Diagnosis Summary & PDF Generation
elif st.session_state.step == 3:
    st.header("Step 3: Diagnosis & Report")
    diagnosis_text = infer_diagnosis_refined(st.session_state.answers)
    st.markdown(diagnosis_text)

    if st.button("💾 Save Consultation"):
        save_consultation_to_csv(st.session_state.answers, diagnosis_text)
        st.success("Consultation saved to consultations.csv")

    if st.button("📄 Download PDF Report"):
        pdf_buffer = generate_pdf()
        st.download_button("Download Report", pdf_buffer, "report.pdf", "application/pdf")

    if st.button("🔁 New Consultation"):
        st.session_state.step = 1
        st.session_state.answers = {}