import socket
from rsa import *
from datetime import datetime
import json
import ast
import random
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

def gen_ticket(sess_key,self_id,network_address,rid,ts,dur):
    ticket={"session_key":sess_key,"self_id":self_id,"address":network_address,"id":rid,"timestamp":ts,"duration":dur}
    ticket=json.dumps(ticket)
    enc_tkt=(str(encrypt(ticket,public_key_B)).encode())#tkt encrypted with public key of tgs for only tgs
    return enc_tkt.decode()#tkt is in byte string

AS_public_key = (1313,289)
public_key_B = (1111,573)

public_key=(6283,4663)
private_key=(6283,4087)

server = socket.socket()

server.bind((socket.gethostname(),2001))

server.listen(1)

print("Waiting for connection")

sock, conn_from = server.accept()

data_recv = ast.literal_eval(sock.recv(10240).decode())
data_recv = json.loads(data_recv)


recv_tkt=data_recv["ticket"]
recv_auth=data_recv["authenticator"]
recv = ast.literal_eval(decrypt(ast.literal_eval(recv_tkt),private_key))

ts=str(datetime.now())
dur=5
sess_key="secretkey123458V"
ret_tkt=gen_ticket(sess_key,recv["self_id"],"net",data_recv['id'],ts,dur)

session_key_C=recv["session_key"]
authn=ast.literal_eval(aes_dec(session_key_C,data_recv["authenticator"][2:-1]))
# print(authn)
if(authn["self_id"]==recv["self_id"]):
    resp={"session_key":sess_key,"id":data_recv['id'],"timestamp":str(datetime.now()),"ticket":ret_tkt}#resp ticket
    resp=json.dumps(resp)
    sock.send(str(aes_enc(session_key_C,resp)).encode())
    print("Ticket Sent!")

sock.close()