import streamlit as st
import speech_recognition as sr
import sqlite3
import bcrypt
import io
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

# Initialize Speech Recognizer
recognizer = sr.Recognizer()

def capture_voice_input():
    with sr.Microphone() as source:
        st.info("🎤 Speak your symptoms now...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            st.success(f"🗣 Recognized: {text}")
            return text
        except sr.UnknownValueError:
            st.error("❌ Could not understand audio.")
            return None
        except sr.RequestError:
            st.error("⚠️ Could not request results; check your internet connection.")
            return None

# **Authentication System**
def create_users_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password.encode("utf-8"))

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result and check_password(result[0], password)

create_users_table()

# **Session Initialization**
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}

# **Login & Registration UI**
st.title("🔐 Login to Elite Dental Consultation")

menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Register":
    st.subheader("🆕 Create a New Account")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")

    if st.button("Register"):
        if register_user(new_username, new_password):
            st.success("Account created successfully! ✅ Please log in.")
        else:
            st.error("Username already exists. Try a different one.")

if menu == "Login":
    st.subheader("🔑 User Login")
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

# **Consultation Form**
def next_step():
    st.session_state.step += 1

def prev_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1

def save_consultation_to_csv(answers):
    file_path = "consultations.csv"
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": st.session_state.username,
        "patient_name": answers.get("patient_name"),
        "age": answers.get("age"),
        "gender": answers.get("gender"),
        "complaint": answers.get("complaint"),
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

# **Step 1: Patient Info**
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

# **Step 2: Complaint (Voice Input Enabled)**
elif st.session_state.step == 2:
    st.header("Step 2: Presenting Complaint")

    if st.button("🎤 Speak Your Symptoms"):
        voice_text = capture_voice_input()
        if voice_text:
            st.session_state.answers["complaint"] = voice_text
    
    st.session_state.answers["complaint"] = st.text_input("Or Type Your Complaint", value=st.session_state.answers.get("complaint", ""))

    if st.button("Back"): prev_step()
    if st.button("Next"): next_step()