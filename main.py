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

def infer_diagnosis(answers):
    complaint = answers.get("complaint")
    diagnosis = "No diagnosis could be inferred."

    if complaint == "Toothache":
        severity = answers.get("pain_severity", "Mild")
        trigger = answers.get("pain_trigger", "None")
        if severity == "Severe" and trigger in ["Cold", "Heat"]:
            diagnosis = "Likely pulpitis or dental caries. Recommend clinical examination and possible X-ray."
        elif severity in ["Mild", "Moderate"] and trigger == "None":
            diagnosis = "Possible mild tooth sensitivity. Advise patient on oral hygiene and follow-up."
        else:
            diagnosis = "Symptoms unclear, further evaluation needed."

    elif complaint == "Bleeding gums":
        frequency = answers.get("bleeding_frequency", "Rarely")
        if frequency in ["Often", "Always"]:
            diagnosis = "Probable gingivitis or periodontal disease. Recommend professional cleaning and periodontal assessment."
        else:
            diagnosis = "Occasional bleeding; advise improved oral hygiene and monitoring."

    elif complaint == "Swelling":
        pain = answers.get("pain_with_swelling", "No")
        if pain == "Yes":
            diagnosis = "Possible dental abscess; urgent dental treatment recommended."
        else:
            diagnosis = "Swelling without pain; differential diagnosis includes cyst or benign tumor; clinical evaluation needed."

    else:
        diagnosis = "Complaint needs further clinical evaluation."

    return diagnosis

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

    diagnosis = infer_diagnosis(st.session_state.answers)
    st.markdown(f"### Preliminary Diagnosis Suggestion:\n\n{diagnosis}")

    if st.button("Start New Consultation"):
        st.session_state.step = 1
        st.session_state.answers = {}
