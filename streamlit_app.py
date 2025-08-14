import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.title("📋 Attendance System - Auth Prototype")

tab1, tab2 = st.tabs(["Register", "Login"])

with tab1:
    st.subheader("Register New User")
    full_name = st.text_input("Full Name", key="reg_full_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_password")
    role = st.selectbox("Role", ["student", "employee", "admin"], key="reg_role")
    matric_number = st.text_input("Matric Number (Optional)", key="reg_matric_number")
    uploaded_image = st.file_uploader("Upload Face Image", type=["jpg", "jpeg", "png"], key="reg_face_image")

    if st.button("Register"):
        if uploaded_image is None:
            st.warning("⚠ Please upload a face image.")
        else:
            try:
                files = {"face_image": (uploaded_image.name, uploaded_image, uploaded_image.type)}
                data = {
                    "full_name": full_name,
                    "email": email,
                    "password": password,
                    "role": role,
                    "matric_number": matric_number if matric_number else ""
                }
                response = requests.post(f"{BASE_URL}/auth/register", data=data, files=files)
                
                if response.status_code == 200:
                    st.success("✅ Registration successful!")
                    st.json(response.json())
                else:
                    st.error(f"❌ {response.json().get('detail', 'Registration failed')}")
            except Exception as e:
                st.error(f"⚠ Error: {e}")

with tab2:
    st.subheader("Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        payload = {
            "email": login_email,
            "password": login_password
        }
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            if response.status_code == 200:
                st.success("✅ Login successful!")
                st.json(response.json())
            else:
                st.error(f"❌ {response.json().get('detail', 'Login failed')}")
        except Exception as e:
            st.error(f"⚠ Error: {e}")
