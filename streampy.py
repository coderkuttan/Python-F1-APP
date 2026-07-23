import streamlit as st

# Title
st.title("🔐 User Login Page")

# User Role
role = st.selectbox(
    "Select User Role",
    ["Student", "Faculty", "Admin"]
)

# Username
username = st.text_input("Username")

# Password
password = st.text_input("Password", type="password")

# Remember Me
remember = st.checkbox("Remember Me")

# Login Button
if st.button("Login"):

    if username == "alan" and password == "1234":
        st.success(f"Welcome {username}!")
        st.write("Role :", role)

        if remember:
            st.info("Your login will be remembered.")
        else:
            st.write("Remember Me is OFF")

    else:
        st.error("Invalid Username or Password")