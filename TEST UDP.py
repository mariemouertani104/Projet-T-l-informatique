# Serveur UDP Simple :

import socket

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"Serveur UDP en écoute sur {HOST}:{PORT}")
    while True:
        data, addr = s.recvfrom(1024)
        print(f"Reçu de {addr}: {data.decode()}")
        s.sendto(data, addr)  # Renvoie les données à l'expéditeur
# Client UDP Simple :

import socket

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    message = b"Salut le serveur UDP!"
    s.sendto(message, (HOST, PORT))
    data, addr = s.recvfrom(1024)
    print(f"Reçu du serveur : {data.decode()} de {addr}")