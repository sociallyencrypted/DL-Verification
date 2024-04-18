from Crypto.PublicKey import RSA

# Generate a new RSA key pair
key = RSA.generate(2048)

# Export the private key as PEM format
private_key = key.export_key().decode('utf-8')
# save it to keys folder
with open('keys/private.pem', 'w') as f:
    f.write(private_key)

# Export the public key as PEM format
public_key = key.publickey().export_key().decode('utf-8')
# save it to keys folder
with open('keys/public.pem', 'w') as f:
    f.write(public_key)