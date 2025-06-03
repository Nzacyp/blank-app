import streamlit as st

# Initialize session state variables
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

    # Toothache logic
    if complaint == "Toothache":
        severity = answers.get("pain_severity", "Mild")
        duration = answers.get("pain_duration", 0)
        trigger = answers.get("pain_trigger", "None")

        # Severe, prolonged pain with trigger
        if severity == "Severe" and duration > 3 and trigger in ["Cold", "Heat"]:
            diagnosis.append("Irreversible pulpitis or dental caries")
            recommendations.append("Recommend urgent endodontic evaluation and possible root canal therapy.")
        # Moderate pain triggered by chewing
        elif severity in ["Moderate", "Severe"] and trigger == "Chewing":
            diagnosis.append("Possible cracked tooth or pulp inflammation")
            recommendations.append("Clinical examination and bite test recommended.")
        # Mild pain without clear trigger
        elif severity == "Mild" and trigger == "None":
            diagnosis.append("Mild tooth sensitivity")
            recommendations.append("Advise desensitizing toothpaste and monitor symptoms.")
        else:
            diagnosis.append("Unclear toothache etiology")
            recommendations.append("Further clinical and radiographic evaluation needed.")

        # Red flag: severe pain >7 days
        if severity == "Severe" and duration > 7:
            recommendations.append("Consider referral for urgent dental intervention due to prolonged severe pain.")

    # Bleeding gums logic
    elif complaint == "Bleeding gums":
        frequency = answers.get("bleeding_frequency", "Rarely")
        duration = answers.get("bleeding_duration", 0)

        if frequency in ["Often", "Always"] and duration > 7:
            diagnosis.append("Chronic gingivitis or early periodontitis")
            recommendations.append("Recommend scaling and root planing with oral hygiene reinforcement.")
        elif frequency in ["Sometimes", "Often"] and duration <= 7:
            diagnosis.append("Acute gingivitis")
            recommendations.append("Advise improved oral hygiene and possible antimicrobial mouthwash.")
        else:
            diagnosis.append("Minimal gum bleeding")
            recommendations.append("Monitor and maintain good oral hygiene.")

        # Red flag: bleeding gums + swelling or pain
        swelling = answers.get("swelling_location", "")
        pain_with_swelling = answers.get("pain_with_swelling", "No")
        if swelling and pain_with_swelling == "Yes":
            recommendations.append("Possible periodontal abscess; urgent dental assessment needed.")

    # Swelling logic
    elif complaint == "Swelling":
        duration = answers.get("swelling_duration", 0)
        pain = answers.get("pain_with_swelling", "No")
        location = answers.get("swelling_location", "")

        if pain == "Yes" and duration > 1:
            diagnosis.append("Probable dental abscess or cellulitis")
            recommendations.append("Urgent dental intervention and possible antibiotic therapy recommended.")
        elif pain == "No" and duration > 7:
            diagnosis.append("Possibly cyst or benign tumor")
            recommendations.append("Recommend imaging and specialist referral for further evaluation.")
        else:
            diagnosis.append("Mild swelling")
            recommendations.append("Monitor and follow-up as needed.")

    else:
        diagnosis.append("Unspecified complaint")
        recommendations.append("Further clinical assessment required.")

    # Combine lists into readable text
    diagnosis_text = "\n- ".join([""] + diagnosis)  # prepend newline & bullet
    recommendation_text = "\n- ".join([""] + recommendations)

    return f"**Possible Diagnoses:**{diagnosis_text}\n\n**Recommendations:**{recommendation_text}"

# Step 1: Patient info input
if st.session_state.step == 1:
    st.title("🦷 Elite Dental Consultation")
    st.header("Step 1: Patient Information")

    st.session_state.answers["patient_name"] = st.text_input(
        "Patient Name", value=st.session_state.answers.get("patient_name", "")
    )
    st.session_state.answers["age"] = st.number_input(
        "Age", min_value=0, max_value=120, value=st.session_state.answers.get("age", 0)
    )
    st.session_state.answers["gender"] = st.radio(
        "Gender", ("Male", "Female", "Other"),
        index=["Male", "Female", "Other"].index(st.session_state.answers.get("gender", "Male"))
    )

    if st.button("Next"):
        if not st.session_state.answers["patient_name"] or st.session_state.answers["age"] == 0:
            st.error("Please enter a valid patient name and age.")
        else:
            next_step()

# Step 2: Presenting complaint
elif st.session_state.step == 2:
    st.header("Step 2: Presenting Complaint")

    st.session_state.answers["complaint"] = st.selectbox(
        "What is the main complaint?",
        ["Toothache", "Bleeding gums", "Swelling", "Other"],
        index=["Toothache", "Bleeding gums", "Swelling", "Other"].index(
            st.session_state.answers.get("complaint", "Toothache")
        )
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            prev_step()
    with col2:
        if st.button("Next"):
            next_step()

# Step 3: Symptom details
elif st.session_state.step == 3:
    st.header("Step 3: Symptom Details")

    complaint = st.session_state.answers.get("complaint")

    if complaint == "Toothache":
        st.session_state.answers["pain_duration"] = st.slider(
            "How many days have you had the toothache?", 0, 30, st.session_state.answers.get("pain_duration", 1)
        )
        st.session_state.answers["pain_severity"] = st.selectbox(
            "Pain severity", ["Mild", "Moderate", "Severe"],
            index=["Mild", "Moderate", "Severe"].index(st.session_state.answers.get("pain_severity", "Mild"))
        )
        st.session_state.answers["pain_trigger"] = st.radio(
            "Is the pain triggered by:", ["Cold", "Heat", "Sweet foods", "Chewing", "None"],
            index=["Cold", "Heat", "Sweet foods", "Chewing", "None"].index(st.session_state.answers.get("pain_trigger", "None"))
        )

    elif complaint == "Bleeding gums":
        st.session_state.answers["bleeding_frequency"] = st.selectbox(
            "How often do your gums bleed?", ["Rarely", "Sometimes", "Often", "Always"],
            index=["Rarely", "Sometimes", "Often", "Always"].index(st.session_state.answers.get("bleeding_frequency", "Rarely"))
        )
        st.session_state.answers["bleeding_duration"] = st.slider(
            "Duration of bleeding (days)", 0, 30, st.session_state.answers.get("bleeding_duration", 1)
        )

    elif complaint == "Swelling":
        st.session_state.answers["swelling_location"] = st.text_input(
            "Where is the swelling located?", value=st.session_state.answers.get("swelling_location", "")
        )
        st.session_state.answers["swelling_duration"] = st.slider(
            "Duration of swelling (days)", 0, 30, st.session_state.answers.get("swelling_duration", 1)
        )
        st.session_state.answers["pain_with_swelling"] = st.radio(
            "Is the swelling painful?", ["Yes", "No"],
            index=["Yes", "No"].index(st.session_state.answers.get("pain_with_swelling", "No"))
        )

    else:  # Other complaint
        st.session_state.answers["other_complaint"] = st.text_area(
            "Please describe your complaint:", value=st.session_state.answers.get("other_complaint", "")
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            prev_step()
    with col2:
        if st.button("Next"):
            next_step()

# Step 4: Summary with diagnosis
elif st.session_state.step == 4:
    st.header("Step 4: Consultation Summary")
    st.write("Here are the details you provided:")

    for key, value in st.session_state.answers.items():
        st.write(f"**{key.replace('_', ' ').capitalize()}:** {value}")

    diagnosis_text = infer_diagnosis_refined(st.session_state.answers)
    st.markdown(diagnosis_text)

    if st.button("Start New Consultation"):
        st.session_state.step = 1
        st.session_state.answers = {}
