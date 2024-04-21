import socket
from rsa import *
from datetime import datetime
import json

def gen_ticket(session_key, self_id, network_address, rid, timestamp, duration):
    ticket = {"session_key": session_key,
             "self_id": self_id,
             "address": network_address,
             "id": rid,
             "timestamp": timestamp,
             "duration": duration}
    ticket = json.dumps(ticket)
    enc_tkt = (str(encrypt(ticket,TGS_public_key)).encode()) #tkt encrypted with public key of tgs for only tgs
    return enc_tkt.decode() #tkt is in byte string

def req_handler(data_recv,sock):
    request_recv = json.loads(data_recv)
    timestamp = str(datetime.now())
    duration = 5
    sess_key = "secretkey1234567"
    resp = {"session_key": sess_key,
          "id":request_recv["id"],
          "timestamp":timestamp,
          "duration":duration,
          "TGS_ticket":gen_ticket(
              sess_key,
              request_recv['self_id'],
              "network_addr",
              request_recv['id'],
              timestamp,
              duration)
        }
    response = encrypt(json.dumps(resp),server_pub_keys[request_recv["self_id"]]) #enc with public key of client
    sock.send(str(response).encode())

TGS_public_key = (6283,4663)
public_key = (1313,289)
private_key = (1313,1009)
keys_dict = {'B':'(1111,573)','A':'(6077,3437)'}
server_pub_keys = {'A':(6077,3437),'B':(1111,573)}
server = socket.socket()
server.bind((socket.gethostname(),2000))
server.listen(10)

while(1):
    print("Waiting for connection")
    sock, conn_from = server.accept()
    data_recv = sock.recv(1024).decode()
    print("Data received " + str(data_recv))
    req_handler(data_recv,sock)
    sock.close()

