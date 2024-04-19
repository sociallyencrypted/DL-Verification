import streamlit as st
import requests
import qrcode
from PIL import Image
import io
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import base64

backend_url = "http://localhost:8000"

# Config
st.set_page_config(page_title="Driver's License Verification", layout="centered")

# Admin credentials: NEED TO BE SECURED
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

# Frontend sections
def police_verification():
    st.title("Police Verification")
    
    st.subheader("Enter License Number")
    license_number = st.text_input("License Number")

    # QR Code Scanning
    st.subheader("Scan QR Code")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Decode QR code
        decoded_info = decode(image)
        if decoded_info:
            digital_signature = decoded_info[0].data.decode("utf-8")

            try:
                response = requests.post(f"{backend_url}/verify-license", json={"license_number": license_number, "digital_signature": digital_signature})
                response.raise_for_status()
                data = response.json()
                data["license_details"]["photo"] = base64.b64decode(data["license_details"]["photo"])

                if data["is_valid"]:
                    st.success(data["message"])
                    st.subheader("License Details")
                    st.write(f"Name: {data['license_details']['name']}")
                    st.write(f"Date of Birth: {data['license_details']['dob']}")
                    st.image(Image.open(io.BytesIO(data['license_details']['photo'])), caption="Photo")
                    st.write(f"Validity: {data['license_details']['validity']}")
                else:
                    st.error(data["message"])
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
        else:
            st.error("QR code not detected in the image")

def admin_portal():
    st.title("Admin Portal")

    # Admin authentication
    username = st.text_input("Username", type="default")
    password = st.text_input("Password", type="password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        name = st.text_input("Name")
        dob = st.date_input("Date of Birth")
        photo = st.file_uploader("Upload Photo", type=["jpg", "png"])
        validity = st.date_input("Validity")

        if st.button("Issue License"):
            try:
                photo_bytes = photo.getvalue()
                #encode photo to base64
                photo_bytes = base64.b64encode(photo_bytes).decode('utf-8')
                json={
                    "name": name,
                    "dob": str(dob),
                    "photo": photo_bytes,
                    "validity": str(validity)
                }
                response = requests.post(f"{backend_url}/issue-license", json=json)
                response.raise_for_status()
                data = response.json()
                st.success(data["message"])
                st.subheader("License Details")
                st.write(f"License Number: {data['license_number']}")
                qr_img = qrcode.make(data["digital_signature"])
                # convert from PILImage to bytes
                img_byte_arr = io.BytesIO()
                qr_img.save(img_byte_arr, format='PNG')
                qr_img = Image.open(img_byte_arr)
                st.image(qr_img, caption="Digital Signature (QR Code)")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
    else:
        st.error("Invalid username or password")

# Sidebar navigation
pages = {
    "Police Verification": police_verification,
    "Admin Portal": admin_portal,
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(pages.keys()))

# Call the selected page function
pages[selection]()