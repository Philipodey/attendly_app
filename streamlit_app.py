import streamlit as st
import requests
import jwt  # pip install pyjwt

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Attendance System", page_icon="📋")
st.title("📋 Attendance System")

# Helper to initialize session_state keys once
def _init_state():
    for k, v in {
        "user_id": None,
        "role": None,
        "token": None,
        "logged_in": False
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Register", "Login", "Create Session", "Mark Attendance"])

# ---------------- Register Tab ----------------
with tab1:
    st.subheader("Register New User")
    full_name = st.text_input("Full Name", key="reg_full_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_password")
    role = st.selectbox("Role", ["student", "employee", "admin"], key="reg_role")
    matric_number = st.text_input("Matric Number (Optional)", key="reg_matric_number")
    uploaded_image = st.file_uploader("Upload Face Image", type=["jpg", "jpeg", "png"], key="reg_face_image")

    if st.button("Register"):
        if role in ["student", "employee"] and uploaded_image is None:
            st.warning("⚠ Please upload a face image.")
        else:
            try:
                files = None
                if uploaded_image is not None:
                    files = {"face_image": (uploaded_image.name, uploaded_image, uploaded_image.type)}
                data = {
                    "full_name": full_name,
                    "email": email,
                    "password": password,
                    "role": role,
                    "matric_number": matric_number if matric_number else ""
                }
                resp = requests.post(f"{BASE_URL}/auth/register", data=data, files=files)
                if resp.status_code == 200:
                    st.success("✅ Registration successful!")
                    st.json(resp.json())
                else:
                    st.error(f"❌ {resp.json().get('detail', 'Registration failed')}")
            except Exception as e:
                st.error(f"⚠ Error: {e}")

# ---------------- Login Tab ----------------
with tab2:
    st.subheader("Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")

    cols = st.columns(2)
    with cols[0]:
        if st.button("Login"):
            payload = {"email": login_email, "password": login_password}
            try:
                resp = requests.post(f"{BASE_URL}/auth/login", json=payload)
                if resp.status_code == 200:
                    user_data = resp.json()
                    # Prefer explicit fields if present
                    st.session_state["token"] = user_data.get("access_token")
                    st.session_state["role"] = user_data.get("role")

                    # Get user_id reliably:
                    uid = user_data.get("user_id")
                    if uid is None and st.session_state["token"]:
                        try:
                            decoded = jwt.decode(st.session_state["token"], options={"verify_signature": False})
                            uid = decoded.get("user_id") or decoded.get("sub")
                            if isinstance(uid, str) and uid.isdigit():
                                uid = int(uid)
                        except Exception:
                            uid = None
                    st.session_state["user_id"] = uid
                    st.session_state["logged_in"] = st.session_state["user_id"] is not None

                    if st.session_state["logged_in"]:
                        st.success("✅ Login successful!")
                        st.json(user_data)
                    else:
                        st.warning("Logged in but could not extract user_id. Check backend token payload.")
                else:
                    st.error(f"❌ {resp.json().get('detail', 'Login failed')}")
            except Exception as e:
                st.error(f"⚠ Error: {e}")

    with cols[1]:
        if st.button("Logout"):
            _init_state()  # reset
            st.success("Logged out.")

# ---------------- Create Session Tab (Admins Only) ----------------
with tab3:
    st.subheader("Create Attendance Session (Admins Only)")
    if not st.session_state["logged_in"] or not st.session_state["token"]:
        st.warning("⚠ You must be logged in to create a session.")
    else:
        session_name = st.text_input("Session Name")
        duration_minutes = st.number_input("Duration (minutes)", min_value=1, value=10)

        if st.button("Generate QR Code"):
            try:
                headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                params = {
                    "name": session_name,
                    "duration_minutes": duration_minutes
                }
                resp = requests.post(
                    f"{BASE_URL}/sessions/create-session",
                    params=params,
                    headers=headers,
                    stream=True
                )
                if resp.status_code == 200:
                    st.image(resp.content, caption="📸 Scan to mark attendance", use_column_width=True)
                else:
                    # show best error we can
                    try:
                        err_msg = resp.json().get("detail", "Failed to create session")
                    except Exception:
                        err_msg = "Failed to create session"
                    st.error(f"❌ {err_msg}")
            except Exception as e:
                st.error(f"⚠ Error: {e}")

# ---------------- Mark Attendance Tab ----------------
with tab4:
    st.subheader("Mark Attendance")

    if not st.session_state["logged_in"] or st.session_state["user_id"] is None:
        st.warning("⚠ You must be logged in to mark attendance.")
    else:
        session_id = st.number_input("Session ID", min_value=1)
        use_dummy = st.checkbox("Use dummy location (for quick test)", value=True)
        if use_dummy:
            latitude = st.number_input("Latitude", value=6.5244, format="%.6f")   # Lagos-ish
            longitude = st.number_input("Longitude", value=3.3792, format="%.6f")
        else:
            latitude = st.number_input("Latitude", format="%.6f")
            longitude = st.number_input("Longitude", format="%.6f")

        st.write("Upload a face image OR capture from camera:")
        cam_img = st.camera_input("Camera (optional)")
        face_file = st.file_uploader("Or upload face image", type=["jpg", "jpeg", "png"], key="mark_face_image")

        the_file = None
        if cam_img is not None:
            the_file = ("camera.jpg", cam_img.getvalue(), "image/jpeg")
        elif face_file is not None:
            the_file = (face_file.name, face_file, face_file.type)

        if st.button("Submit Attendance"):
            if the_file is None:
                st.warning("⚠ Please provide a face image (camera or upload).")
            else:
                try:
                    files = {"image": the_file}
                    # Form data values can be strings; FastAPI will coerce types for Form(...)
                    data = {
                        "session_id": str(int(session_id)),
                        "user_id": str(int(st.session_state["user_id"])),
                        "latitude": str(float(latitude)),
                        "longitude": str(float(longitude))
                    }
                    resp = requests.post(
                        f"{BASE_URL}/attendance/mark_attendance",
                        data=data,
                        files=files
                    )
                    if resp.status_code == 200:
                        st.success("✅ Attendance marked successfully!")
                        st.json(resp.json())
                    else:
                        # show best error from backend
                        try:
                            err_msg = resp.json().get("detail", "Failed to mark attendance")
                        except Exception:
                            err_msg = "Failed to mark attendance"
                        st.error(f"❌ {err_msg}")
                except Exception as e:
                    st.error(f"⚠ Error: {e}")
