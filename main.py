import streamlit as st

st.title("🦷 Elite Dental Consultation")
st.write("Welcome, Dr. Cyprien!")

name = st.text_input("Patient name:")
age = st.number_input("Age:", min_value=0, max_value=120)

if st.button("Submit"):
    st.success(f"Saved info for {name}, aged {age}.")
