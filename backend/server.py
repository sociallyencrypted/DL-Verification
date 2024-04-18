# server.py
from flask import Flask, request, jsonify
from models.license import License
from utils.digital_signature import DigitalSignature
import datetime
import random

private_key = open('keys/private.pem').read()
public_key = open('keys/public.pem').read()

digital_signature = DigitalSignature(private_key, public_key)

app = Flask(__name__)

def generate_license_number():
    # generate random number of 10 digits
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

# License issuance route (accessible only to admins)
@app.route('/issue-license', methods=['POST'])
def issue_license():
    data = request.get_json()
    name = data.get('name')
    dob = datetime.datetime.fromparsecode(data.get('dob'))
    photo = data.get('photo')
    validity = datetime.datetime.fromparsecode(data.get('validity'))

    license_number = generate_license_number()
    message = f"{license_number}|{name}|{dob}|{validity}".encode('utf-8')
    digital_signature_str = digital_signature.generate_signature(message)

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

    license = License.find_by_license_number(license_number)
    if not license:
        return jsonify({'message': 'License not found', 'is_valid': False}), 404

    message = f"{license.license_number}|{license.name}|{license.dob}|{license.validity}".encode('utf-8')
    is_valid = digital_signature.verify_signature(message, license.digital_signature)

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