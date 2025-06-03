import streamlit as st

st.set_page_config(page_title="Smart Medical Assistant", layout="wide")

st.title("🤖 Medical Self-Consultation Tool")
st.write("Welcome! Please answer the following to receive suggestions.")

# Add fields
name = st.text_input("Patient Name")
age = st.number_input("Age", min_value=0)
symptoms = st.text_area("Describe symptoms")

if st.button("Get Diagnosis"):
    if symptoms:
        st.success(f"Possible diagnosis for {name}: [Example Output]")
    else:
        st.warning("Please describe your symptoms first.")
