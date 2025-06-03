import streamlit as st
import pandas as pd
import os
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

    # Toothache logic
    if complaint == "Toothache":
        severity = answers.get("pain_severity", "Mild")
        duration = answers.get("pain_duration", 0)
        trigger = answers.get("pain_trigger", "None")

        if severity == "Severe" and duration > 3 and trigger in ["Cold", "Heat"]:
            diagnosis.append("Irreversible pulpitis or deep dental caries")
            recommendations.append("Urgent endodontic evaluation needed.")
            treatment_plan.append("Root canal therapy or extraction.")
        elif severity in ["Moderate", "Severe"] and trigger == "Chewing":
            diagnosis.append("Possible cracked tooth or pulp inflammation")
            recommendations.append("Clinical exam and bite test recommended.")
            treatment_plan.append("Crown or root canal depending on severity.")
        elif severity == "Mild" and trigger == "None":
            diagnosis.append("Tooth sensitivity")
            recommendations.append("Use desensitizing toothpaste.")
            treatment_plan.append("Topical fluoride, monitor progress.")
        else:
            diagnosis.append("Unclear etiology")
            recommendations.append("Further evaluation needed.")
            treatment_plan.append("Clinical and radiographic exam.")

        if severity == "Severe" and duration > 7:
            recommendations.append("Urgent dental intervention.")

    elif complaint == "Bleeding gums":
        freq = answers.get("bleeding_frequency", "Rarely")
        duration = answers.get("bleeding_duration", 0)

        if freq in ["Often", "Always"] and duration > 7:
            diagnosis.append("Chronic gingivitis or early periodontitis")
            recommendations.append("Scaling and improved hygiene.")
            treatment_plan.append("Full-mouth scaling + oral hygiene instructions.")
        elif freq in ["Sometimes", "Often"] and duration <= 7:
            diagnosis.append("Acute gingivitis")
            recommendations.append("Temporary inflammation; review hygiene.")
            treatment_plan.append("Scaling and chlorhexidine mouthwash.")
        else:
            diagnosis.append("Minimal inflammation")
            recommendations.append("Monitor; advise good brushing.")
            treatment_plan.append("Routine cleaning.")

        swelling = answers.get("swelling_location", "")
        pain_swelling = answers.get("pain_with_swelling", "No")
        if swelling and pain_swelling == "Yes":
            recommendations.append("Possible periodontal abscess.")
            treatment_plan.append("Drainage and antibiotic therapy.")

    elif complaint == "Swelling":
        duration = answers.get("swelling_duration", 0)
        pain = answers.get("pain_with_swelling", "No")
        location = answers.get("swelling_location", "")

        if pain == "Yes" and duration > 1:
            diagnosis.append("Dental abscess or facial cellulitis")
            recommendations.append("Urgent treatment needed.")
            treatment_plan.append("Incision, drainage, antibiotics.")
        elif pain == "No" and duration > 7:
            diagnosis.append("Cyst or benign tumor")
            recommendations.append("Refer for biopsy or imaging.")
            treatment_plan.append("Specialist referral.")
        else:
            diagnosis.append("Inflammatory swelling")
            recommendations.append("Monitor and re-evaluate.")
            treatment_plan.append("Warm compress and review.")

    else:
        diagnosis.append("Other/unspecified complaint")
        recommendations.append("Manual assessment required.")
        treatment_plan.append("Refer to general dentist.")

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

# Step 1: Patient info
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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"): prev_step()
    with col2:
        if st.button("Next"): next_step()

# Step 3: Symptoms
elif st.session_state.step == 3:
    st.header("Step 3: Symptom Details")
    complaint = st.session_state.answers.get("complaint")

    if complaint == "Toothache":
        st.session_state.answers["pain_duration"] = st.slider("Pain duration (days)", 0, 30, st.session_state.answers.get("pain_duration", 1))
        st.session_state.answers["pain_severity"] = st.selectbox("Pain severity", ["Mild", "Moderate", "Severe"], index=["Mild", "Moderate", "Severe"].index(st.session_state.answers.get("pain_severity", "Mild")))
        st.session_state.answers["pain_trigger"] = st.radio("Pain triggered by?", ["Cold", "Heat", "Sweet", "Chewing", "None"], index=["Cold", "Heat", "Sweet", "Chewing", "None"].index(st.session_state.answers.get("pain_trigger", "None")))

    elif complaint == "Bleeding gums":
        st.session_state.answers["bleeding_frequency"] = st.selectbox("Frequency of bleeding?", ["Rarely", "Sometimes", "Often", "Always"],
            index=["Rarely", "Sometimes", "Often", "Always"].index(st.session_state.answers.get("bleeding_frequency", "Rarely")))
        st.session_state.answers["bleeding_duration"] = st.slider("Duration of bleeding (days)", 0, 30, st.session_state.answers.get("bleeding_duration", 1))

    elif complaint == "Swelling":
        st.session_state.answers["swelling_location"] = st.text_input("Swelling location", value=st.session_state.answers.get("swelling_location", ""))
        st.session_state.answers["swelling_duration"] = st.slider("Swelling duration (days)", 0, 30, st.session_state.answers.get("swelling_duration", 1))
        st.session_state.answers["pain_with_swelling"] = st.radio("Is the swelling painful?", ["Yes", "No"], index=["Yes", "No"].index(st.session_state.answers.get("pain_with_swelling", "No")))

    else:
        st.session_state.answers["other_complaint"] = st.text_area("Describe the issue", value=st.session_state.answers.get("other_complaint", ""))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"): prev_step()
    with col2:
        if st.button("Next"): next_step()

# Step 4: Summary
elif st.session_state.step == 4:
    st.header("Step 4: Consultation Summary")
    st.subheader("Patient Info")
    for key, value in st.session_state.answers.items():
        st.write(f"**{key.replace('_', ' ').capitalize()}**: {value}")

    st.subheader("🩺 Diagnosis & Plan")
    diagnosis_text = infer_diagnosis_refined(st.session_state.answers)
    st.markdown(diagnosis_text)

    if st.button("💾 Save Consultation"):
        save_consultation_to_csv(st.session_state.answers, diagnosis_text)
        st.success("Consultation saved to consultations.csv")

    if st.button("🔁 New Consultation"):
        st.session_state.step = 1
        st.session_state.answers = {}
