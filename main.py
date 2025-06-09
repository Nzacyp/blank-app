# Enhanced Elite Dental Consultation App with Clinical Features

import streamlit as st
import pandas as pd
import os
import io
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
from PIL import Image
import hashlib

# --- Secure User Database (Simulated Hashing) ---
USER_CREDENTIALS = {
    "doctor1": hashlib.sha256("password123".encode()).hexdigest(),
    "admin": hashlib.sha256("securepass".encode()).hexdigest()
}

def authenticate(username, password):
    return USER_CREDENTIALS.get(username) == hashlib.sha256(password.encode()).hexdigest()

# --- Session Initialization ---
for key, default in {
    "user_logged_in": False,
    "username": None,
    "step": 1,
    "answers": {}
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Login Interface ---
if not st.session_state.user_logged_in:
    st.title("🔐 Login to Elite Dental Consultation")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.user_logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}! ✅")
            st.rerun()
        else:
            st.error("Invalid username or password!")
    st.stop()

# --- Sidebar Info ---
st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# --- Step Navigation ---
def next_step(): st.session_state.step += 1

def prev_step():
    if st.session_state.step > 1: st.session_state.step -= 1

# --- Diagnosis Logic ---
def infer_diagnosis_refined(answers):
    complaint = answers.get("complaint")
    diagnosis, recommendations, treatment_plan = [], [], []

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

    elif complaint == "Bleeding gums":
        diagnosis.append("Gingivitis or Periodontitis")
        recommendations.append("Professional cleaning and oral hygiene instruction.")
        treatment_plan.append("Scaling and root planing, chlorhexidine rinse.")

    elif complaint == "Swelling":
        diagnosis.append("Dental abscess or soft tissue infection")
        recommendations.append("Immediate evaluation. May require drainage.")
        treatment_plan.append("Antibiotics and possible extraction or root canal.")

    elif complaint == "Mouth ulcer":
        diagnosis.append("Aphthous ulcer or traumatic ulcer")
        recommendations.append("Avoid spicy foods, apply topical analgesic.")
        treatment_plan.append("Topical corticosteroids if severe.")

    elif complaint == "Broken tooth":
        diagnosis.append("Fractured tooth")
        recommendations.append("Radiographic assessment and restoration planning.")
        treatment_plan.append("Composite restoration, crown, or extraction.")

    elif complaint == "Discoloration":
        diagnosis.append("Extrinsic/intrinsic tooth staining")
        recommendations.append("Evaluate etiology, advise on oral hygiene.")
        treatment_plan.append("Scaling/polishing or bleaching.")

    elif complaint == "Other":
        diagnosis.append("Needs further evaluation.")
        recommendations.append("Complete dental exam recommended.")
        treatment_plan.append("Pending clinical findings.")

    return f"""**Possible Diagnoses:**  \n- {'; '.join(diagnosis)}\n\n**Recommendations:**  \n- {'; '.join(recommendations)}\n\n**Treatment Plan:**  \n- {'; '.join(treatment_plan)}"""

# --- Save to CSV ---
def save_consultation_to_csv(answers, diagnosis_output):
    file_path = "consultations.csv"
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": st.session_state.username,
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

# --- PDF Generation ---
def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    y = 800

    try:
        logo = ImageReader("static/logo.png")
        c.drawImage(logo, 50, y - 80, width=150, height=80)
        y -= 100
    except:
        pass

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, f"Consultation Report")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Generated by: {st.session_state.username}")
    y -= 20
    c.drawString(50, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 30

    c.setFont("Helvetica", 10)
    for key, value in st.session_state.answers.items():
        if key in ["image", "image_bytes"]:
            continue
        elif key == "dental_chart":
            c.drawString(50, y, "Dental Chart:")
            y -= 15
            for tooth, status in value.items():
                c.drawString(70, y, f"Tooth {tooth}: {status}")
                y -= 12
                if y < 50:
                    c.showPage()
                    y = 800
        else:
            c.drawString(50, y, f"{key.replace('_', ' ').capitalize()}: {value}")
            y -= 15
            if y < 50:
                c.showPage()
                y = 800

    if st.session_state.answers.get("image_bytes"):
        try:
            c.showPage()
            image_reader = ImageReader(io.BytesIO(st.session_state.answers["image_bytes"]))
            c.drawImage(image_reader, 100, 400, width=200, height=200)
        except Exception as e:
            print("Error adding image to PDF:", e)

    c.save()
    buffer.seek(0)
    return buffer

# --- Step 1: Patient Info ---
if st.session_state.step == 1:
    st.title("🦷 Elite Dental Consultation")
    st.header("Step 1: Patient Information")

    st.session_state.answers["patient_name"] = st.text_input("Patient Name", value=st.session_state.answers.get("patient_name", ""))
    st.session_state.answers["age"] = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.answers.get("age", 0))
    st.session_state.answers["gender"] = st.radio("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.answers.get("gender", "Male")))

    st.subheader("Optional Medical History")
    st.session_state.answers["diabetes"] = st.checkbox("Diabetic")
    st.session_state.answers["smoking"] = st.checkbox("Smoker")
    st.session_state.answers["bleeding_disorder"] = st.checkbox("Bleeding Disorder")
    st.session_state.answers["allergies"] = st.text_input("Known Allergies", value=st.session_state.answers.get("allergies", ""))
    st.session_state.answers["dental_visit"] = st.selectbox("Last dental visit?", ["<6 months", "6-12 months", ">1 year", "Never"], index=0)

    st.subheader("Vital Signs")
    st.session_state.answers["blood_pressure"] = st.text_input("Blood Pressure (e.g., 120/80)", value=st.session_state.answers.get("blood_pressure", ""))
    st.session_state.answers["temperature"] = st.number_input("Temperature (°C)", min_value=30.0, max_value=45.0, value=st.session_state.answers.get("temperature", 36.5))
    st.session_state.answers["pulse"] = st.number_input("Pulse (bpm)", min_value=30, max_value=180, value=st.session_state.answers.get("pulse", 72))

    uploaded_image = st.file_uploader("Upload Lesion or Clinical Photo (optional)", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        st.session_state.answers["image"] = uploaded_image.name
        st.session_state.answers["image_bytes"] = uploaded_image.read()
        st.image(st.session_state.answers["image_bytes"], caption="Uploaded Image", use_column_width=True)
    else:
        st.session_state.answers["image"] = None
        st.session_state.answers["image_bytes"] = None

    st.subheader("Dental Chart (Tooth Status)")
    teeth_quadrants = {
        "Upper Right": range(18, 10, -1),
        "Upper Left": range(21, 29),
        "Lower Left": range(38, 30, -1),
        "Lower Right": range(41, 49)
    }
    teeth_status = {}
    for quadrant, teeth in teeth_quadrants.items():
        st.write(quadrant)
        cols = st.columns(len(teeth))
        for i, tooth in enumerate(teeth):
            teeth_status[str(tooth)] = cols[i].selectbox(f"{tooth}", ["Normal", "Caries", "Missing", "Restored"], key=f"tooth_{tooth}")
    st.session_state.answers["dental_chart"] = teeth_status

    if st.button("Next"):
        if not st.session_state.answers["patient_name"] or st.session_state.answers["age"] == 0:
            st.error("Please fill patient name and age.")
        else:
            next_step()

# --- Step 2: Complaint ---
elif st.session_state.step == 2:
    st.header("Step 2: Presenting Complaint")
    complaint = st.selectbox("What is the main complaint?", ["Toothache", "Bleeding gums", "Swelling", "Mouth ulcer", "Broken tooth", "Discoloration", "Other"])
    st.session_state.answers["complaint"] = complaint

    if complaint == "Toothache":
        st.session_state.answers["pain_severity"] = st.radio("Pain severity", ["Mild", "Moderate", "Severe"])
        st.session_state.answers["pain_duration"] = st.number_input("Duration of pain (days)", min_value=0)
        st.session_state.answers["pain_trigger"] = st.radio("Pain trigger", ["None", "Cold", "Heat", "Chewing"])

    if st.button("Back"): prev_step()
    if st.button("Next"): next_step()

# --- Step 3: Diagnosis Summary ---
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

# --- Admin Panel --- 
if st.session_state.username == "admin":
    st.sidebar.title("📊 Admin Panel")
    if st.sidebar.button("View All Consultations"):
        if os.path.exists("consultations.csv"):
            df = pd.read_csv("consultations.csv")
            st.write("### All Consultation Records")
            st.dataframe(df)
        else:
            st.warning("No consultation data found.")
