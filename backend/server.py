# server.py
from flask import Flask, request, jsonify
from models.license import License
from utils.digital_signature import DigitalSignature
import datetime
import random
import base64

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

    license = License.find_by_license_number(license_number)
    if not license:
        return jsonify({'message': 'License not found', 'is_valid': False}), 404

    print(license.license_number, license.name, license.dob, license.validity)
    message = f"{license.license_number}|{license.name}|{license.dob}|{license.validity}".encode('utf-8')
    is_valid = DSGen.verify_signature(message, digital_signature)
    
    # convert license photo to base64 so it is serializable
    license.photo = base64.b64encode(license.photo).decode('utf-8')

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
        return jsonify({'message': 'License is invalid', 'is_valid': False}), 400

if __name__ == '__main__':
    app.run(port=8000)