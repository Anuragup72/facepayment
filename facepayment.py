import streamlit as st
import cv2
import numpy as np
import face_recognition
import mysql.connector
import time

# **DroidCam Configuration**
DROIDCAM_IP = "192.168.53.196"  # अपना फोन का DroidCam IP डालो
VIDEO_URL = f"http://{DROIDCAM_IP}:4747/video"

# **Connect to MySQL Database**
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Anurag@123",  # अपना MySQL पासवर्ड डालो
        database="face_pay"
    )

# **Register user in database**
def register_user(name, encoding):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, face_encoding) VALUES (%s, %s)", (name, encoding.tobytes()))
    conn.commit()
    conn.close()

# **Fetch registered users**
def fetch_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, face_encoding FROM users")
    users = cursor.fetchall()
    conn.close()
    return [(name, np.frombuffer(enc, dtype=np.float64)) for name, enc in users]

# **Capture and process frame from DroidCam**
def capture_frame():
    cap = cv2.VideoCapture(VIDEO_URL)
    if not cap.isOpened():
        st.error("❌ DroidCam not accessible! Check IP & connection.")
        return None
    
    time.sleep(2)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        st.error("❌ Error capturing image! Try again.")
        return None

    frame = np.array(frame, dtype=np.uint8)  # Ensure image is in uint8 format
    if len(frame.shape) != 3 or frame.shape[2] != 3:
        st.error("❌ Unsupported image format! Ensure camera is working correctly.")
        return None

    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# **Face Registration**
def face_registration():
    st.subheader("🔍 Face Registration")
    name = st.text_input("Enter Your Name")
    if st.button("Register Face"):
        rgb_frame = capture_frame()
        if rgb_frame is None:
            return
        
        face_encodings = face_recognition.face_encodings(rgb_frame)
        if face_encodings:
            register_user(name, face_encodings[0])
            st.success(f"✅ {name} Registered Successfully!")
        else:
            st.warning("⚠️ No face detected. Try Again!")

# **Face Payment**
def face_payment():
    st.subheader("💳 Face Payment System")
    users = fetch_users()
    known_names, known_encodings = zip(*users) if users else ([], [])
    
    if st.button("Scan Face for Payment"):
        rgb_frame = capture_frame()
        if rgb_frame is None:
            return
        
        face_encodings = face_recognition.face_encodings(rgb_frame)
        if face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encodings[0])
            if True in matches:
                matched_index = matches.index(True)
                st.success(f"✅ Payment Successful for {known_names[matched_index]}!")
            else:
                st.warning("⚠️ Face not recognized. Try Again!")
        else:
            st.warning("⚠️ No face detected. Try Again!")

# **Streamlit UI**
st.title("💳 Face Scan Payment System (DroidCam Enabled)")
menu = ["Register Face", "Make Payment"]
choice = st.sidebar.selectbox("Select Option", menu)
if choice == "Register Face":
    face_registration()
elif choice == "Make Payment":
    face_payment()
