import streamlit as st
import sqlite3
import bcrypt
import io
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

# **Generate Consultation PDF**
def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    logo_path = "static/logo.png"
    try:
        logo = ImageReader(logo_path)
        c.drawImage(logo, 50, 720, width=250, height=100)
    except:
        pass

    c.drawString(100, 700, f"Consultation Report for {st.session_state.username}")
    
    for index, (key, value) in enumerate(st.session_state.answers.items()):
        c.drawString(100, 680 - (index * 20), f"{key.capitalize()}: {value}")

    c.save()
    buffer.seek(0)
    return buffer

# **Session Initialization**
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}

# **Authentication System**
def authenticate(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result and bcrypt.checkpw(password.encode("utf-8"), result[0].encode("utf-8"))

# **Login UI**
st.title("🔐 Login to Self-Consultation")
if not st.session_state.user_logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.user_logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}! ✅")
        else:
            st.error("Invalid username or password!")
    st.stop()

# **Logout Button**
st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
if st.sidebar.button("Logout"):
    st.session_state.user_logged_in = False
    st.session_state.username = None
    st.rerun()

# **Step Navigation**
def next_step(): st.session_state.step += 1
def prev_step(): 
    if st.session_state.step > 1: st.session_state.step -= 1

# **Step 1: Basic Patient Info**
if st.session_state.step == 1:
    st.title("🩺 Self-Consultation")
    st.header("Step 1: Patient Info")
    st.session_state.answers["patient_name"] = st.text_input("Patient Name", value=st.session_state.answers.get("patient_name", ""))
    st.session_state.answers["age"] = st.number_input("Age", min_value=0, max_value=120, value=st.session_state.answers.get("age", 0))
    st.session_state.answers["gender"] = st.radio("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.answers.get("gender", "Male")))

    if st.button("Next"):
        if not st.session_state.answers["patient_name"] or st.session_state.answers["age"] == 0:
            st.error("Please enter patient name and age.")
        else:
            next_step()

# **Step 2: General Symptoms**
elif st.session_state.step == 2:
    st.header("Step 2: Select Primary Symptom")
    st.session_state.answers["complaint"] = st.selectbox("Which symptom best describes your condition?", 
        ["Toothache", "Bleeding Gums", "Jaw Swelling", "Sensitivity", "Other"], 
        index=["Toothache", "Bleeding Gums", "Jaw Swelling", "Sensitivity", "Other"].index(st.session_state.answers.get("complaint", "Toothache"))
    )
    if st.button("Back"): prev_step()
    if st.button("Next"): next_step()

# **Step 3: Detailed Questions**
elif st.session_state.step == 3:
    st.header("Step 3: Describe Your Symptoms")

    if st.session_state.answers["complaint"] == "Toothache":
        st.session_state.answers["pain_severity"] = st.selectbox("Pain Severity:", ["Mild", "Moderate", "Severe"])
        st.session_state.answers["pain_duration"] = st.slider("How long have you had the pain?", 0, 30, 3)
        st.session_state.answers["pain_trigger"] = st.radio("Is the pain triggered by cold, heat, or biting?", ["Yes", "No"])

    elif st.session_state.answers["complaint"] == "Bleeding Gums":
        st.session_state.answers["bleeding_occurrence"] = st.selectbox("When does bleeding occur?", ["Brushing", "Eating", "Randomly"])
        st.session_state.answers["gum_swelling"] = st.radio("Do your gums feel swollen or tender?", ["Yes", "No"])

    elif st.session_state.answers["complaint"] == "Jaw Swelling":
        st.session_state.answers["swelling_size"] = st.selectbox("How large is the swelling?", ["Small", "Moderate", "Severe"])
        st.session_state.answers["difficulty_opening_mouth"] = st.radio("Do you have difficulty opening your mouth?", ["Yes", "No"])

    if st.button("Back"): prev_step()
    if st.button("Next"): next_step()

# **Step 4: Diagnosis Summary & PDF Generation**
elif st.session_state.step == 4:
    st.header("Step 4: Diagnosis & Recommendations")

    # Generate possible diagnosis based on responses
    diagnosis = []
    recommendations = []
    urgency_level = "Routine Consultation"

    if st.session_state.answers.get("pain_severity") == "Severe" and st.session_state.answers.get("pain_duration", 0) > 3 and st.session_state.answers.get("pain_trigger") == "Yes":
        diagnosis.append("Irreversible pulpitis or deep dental caries")
        recommendations.append("Urgent endodontic evaluation needed.")
        urgency_level = "Urgent Consultation"

    if st.session_state.answers.get("high_fever") == "Yes" or st.session_state.answers.get("difficulty_swallowing") == "Yes":
        urgency_level = "Emergency Consultation"
        recommendations.append("Seek immediate medical attention.")

    st.markdown(f"### **Possible Diagnosis:** {', '.join(diagnosis)}")
    st.markdown(f"### **Recommendations:** {', '.join(recommendations)}")
    st.markdown(f"### **Urgency Level:** 🔥 {urgency_level}")

    if st.button("📄 Download PDF Report"):
        pdf_buffer = generate_pdf()
        st.download_button("Download Report", pdf_buffer, "consultation_report.pdf", "application/pdf")

    if st.button("🔁 New Consultation"):
        st.session_state.step = 1
        st.session_state.answers = {}