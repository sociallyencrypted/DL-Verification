import streamlit as st
import requests
import qrcode
from PIL import Image
import io
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import base64
import json
from datetime import datetime
import socket
from rsa import *
import ast

from Crypto.Cipher import AES
import base64

# Key and IV should be generated with a secure random generator
def aes_enc(session_key,plaintext):
    key = session_key.encode()#b'secretkey1234567' # 16, 24, or 32 bytes long
    iv = b'1234567890123456' # 16 bytes long

    # The message you want to encrypt
    message = plaintext.encode()
    # Pad the message to be a multiple of 16 bytes
    pad = b' ' * (16 - len(message) % 16)
    message += pad

    # Create the AES cipher object
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Encrypt the message
    encrypted_message = cipher.encrypt(message)

    # Encode the encrypted message in base64 for transmission/storage
    encoded_message = base64.b64encode(encrypted_message)
    return encoded_message

def aes_dec(session_key,encoded_message):

    key = session_key.encode()#b'secretkey1234567' # 16, 24, or 32 bytes long
    iv = b'1234567890123456' # 16 bytes long
    # Decode the base64-encoded message
    decoded_message = base64.b64decode(encoded_message)
    
    # Create a new AES cipher object for decryption
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the message
    decrypted_message = cipher.decrypt(decoded_message)

    # Remove the padding from the decrypted message
    decrypted_message = decrypted_message.rstrip()

    return decrypted_message.decode()

backend_url = "http://localhost:8000"

# Config
st.set_page_config(page_title="Driver's License Verification", layout="centered")

# Admin credentials: NEED TO BE SECURED
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

def get_auth(self_id,network_address,ts,session_key):
    auth={"self_id":self_id,"address":network_address,"timestamp":ts}
    auth=json.dumps(auth)
    enc_auth=(str(aes_enc(session_key,auth)).encode()) #tkt encrypted with public key of tgs for only tgs
    return enc_auth.decode() #tkt is in byte string

# Frontend sections
def police_verification():

    public_key = (6077,3437)
    private_key = (6077,4613)

    if "session_key" not in st.session_state or "ticket" not in st.session_state or "ts" not in st.session_state:
        request = {'self_id':'A','id':'TGS','time':str(datetime.now()),"Duration":5}
        request = json.dumps(request)

        client = socket.socket() 
        client.connect((socket.gethostname(), 2000)) #port 2000 for AS 
        client.send(request.encode())
        data_recv = client.recv(10240).decode()
        data_recv = decrypt(ast.literal_eval(data_recv),private_key)
        data_recv = json.loads(data_recv)
        session_key_TGS = data_recv["session_key"]
        client.close()

        print("Session key with TGS: ",session_key_TGS)

        client = socket.socket() 
        client.connect((socket.gethostname(), 2001))  
        ts = str(datetime.now())
        request = {'id':'B','ticket':data_recv["TGS_ticket"],"authenticator":get_auth("A","network_address",ts,session_key_TGS)}
        request_to_send = json.dumps(request)
        client.send(str(json.dumps(request_to_send)).encode())
        data_recv = client.recv(10240).decode()
        data_recv = ast.literal_eval(aes_dec(session_key_TGS,ast.literal_eval(data_recv)))
        client.close()

        print("Session key received from TGS to communicate with B: ",data_recv["session_key"])
        print("Ticket received from TGS to communicate with B: ",data_recv["ticket"])
        print("Current timestamp: ",ts)

        st.session_state.session_key = data_recv["session_key"]
        st.session_state.ticket = data_recv["ticket"]
        st.session_state.ts = ts
    
    else:
        session_key = st.session_state.session_key
        ticket = st.session_state.ticket
        ts = st.session_state.ts
        print("Session key: ",session_key)
        print("Ticket: ",ticket)
        print("Timestamp: ",ts)

    session_key_V = st.session_state.session_key
    ticket = st.session_state.ticket
    authenticator = get_auth("A","network_address", ts, session_key_V)

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
                response = requests.post(f"{backend_url}/verify-license", json={"license_number": license_number, 
                                                                                "digital_signature": digital_signature,
                                                                                "ticket":ticket,
                                                                                "authenticator":authenticator
                                                                                })
                response.raise_for_status()
                data = response.json()

                if data["is_valid"]:
                    st.success(data["message"])
                    st.subheader("License Details")
                    st.write(f"Name: {data['license_details']['name']}")
                    st.write(f"Date of Birth: {data['license_details']['dob']}")
                    data["license_details"]["photo"] = base64.b64decode(data["license_details"]["photo"])
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
    elif username or password:
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