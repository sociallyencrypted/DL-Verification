import hashlib

# Prompt the user for a password
# password = input("Enter a password: ")
password = "password"

# Hash the password using SHA-256
hashed_password = hashlib.sha256(password.encode()).hexdigest()

# Store the hashed password in a file
with open("keys/admin_pass.txt", "w") as file:
    file.write(hashed_password)

def read_admin_pass():
    with open("keys/admin_pass.txt", "r") as file:
        return file.read()
    
print("Stored Hash is", read_admin_pass(), "for password", password, "in keys/admin_pass.txt")

# Make sure the password is hashed and stored successfully
if read_admin_pass() == hashlib.sha256(password.encode()).hexdigest():
    print("Stored Hash is correct.")

print("Password hashed and stored successfully.")