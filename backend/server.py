# server.py
from flask import Flask, request, jsonify
from models.license import License
from utils.digital_signature import DigitalSignature
import datetime
import random
import base64
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

private_key = open('keys/private.pem').read()
public_key = open('keys/public.pem').read()

DSGen = DigitalSignature(private_key, public_key)

app = Flask(__name__)

def generate_license_number():
    # generate random number of 10 digits
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

# License issuance route (accessible only to admins)
@app.route('/issue-license', methods=['POST'])
def issue_license():
    data = request.get_json()
    name = data.get('name')
    dob = data.get('dob')
    photo = data.get('photo')
    # decode photo bytes from base64
    photo = base64.b64decode(photo.encode('utf-8'))
    validity = data.get('validity')

    license_number = generate_license_number()
    message = f"{license_number}|{name}|{dob}|{validity}".encode('utf-8')
    digital_signature_str = DSGen.generate_signature(message)

    license = License(
        license_number=license_number,
        name=name,
        dob=dob,
        photo=photo,
        validity=validity,
        digital_signature=digital_signature_str
    )
    license.save()

    return jsonify({'message': 'License issued successfully', 'license_number': license_number, 'digital_signature': digital_signature_str}), 200


# License verification route
@app.route('/verify-license', methods=['POST'])
def verify_license():
    data = request.get_json()
    license_number = data.get('license_number')
    digital_signature = data.get('digital_signature')
    ticket = data.get('ticket')
    authenticator = data.get('authenticator')

    public_key = (1111,573)
    private_key = (1111,637)

    ticket = ast.literal_eval(decrypt(ast.literal_eval(ticket),private_key))
    session_key_cv = ticket["session_key"]
    print("Ticket: ",ticket)
    authenticator = ast.literal_eval(aes_dec(session_key_cv,ast.literal_eval(authenticator)))
    print("Authenticator: ",authenticator)

    if not authenticator["self_id"] == ticket["self_id"]:
        return jsonify({'message': 'Unauthorized access', 'is_valid': False}), 200
    else:
        print("Authorized access")

    license = License.find_by_license_number(license_number)
    if not license:
        return jsonify({'message': 'License not found', 'is_valid': False}), 200

    print(license.license_number, license.name, license.dob, license.validity)
    message = f"{license.license_number}|{license.name}|{license.dob}|{license.validity}".encode('utf-8')
    is_valid = DSGen.verify_signature(message, digital_signature)
    
    # convert license photo to base64 so it is serializable
    license.photo = base64.b64encode(license.photo).decode('utf-8')
    
    # check if license is valid
    license.validity = datetime.datetime.strptime(license.validity, '%Y-%m-%d')
    date = datetime.datetime.now()
    if date > license.validity:
        is_valid = False
        

    if is_valid:
        return jsonify({
            'message': 'License is valid',
            'is_valid': True,
            'license_details': {
                'name': license.name,
                'dob': license.dob,
                'photo': license.photo,
                'validity': license.validity
            }
        }), 200
    else:
        return jsonify({'message': 'License is invalid', 'is_valid': False}), 200

if __name__ == '__main__':
    app.run(port=8000)