import streamlit as st

st.title("My First Streamlit App")

st.write("Hello, Welcome to Streamlit!")

name = st.text_input("Enter your name")

if st.button("Submit"):
    st.success(f"Hello, {name}! Have a great day.")
