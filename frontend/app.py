import streamlit as st
import requests

def main():
    st.title("Driver's License Verification")
    license_number = st.text_input("Enter License Number")
    if st.button("Verify"):
        url = "https://localhost:31337/verify"
        data = {"license_number": license_number}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            verified_data = response.json()
            st.write(verified_data)
        else:
            st.write("Error verifying license")

if __name__ == "__main__":
    main()