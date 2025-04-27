#Serveur TCP Simple :

import socket

HOST = '127.0.0.1'  # Adresse IP de l'interface d'écoute
PORT = 65432        # Port d'écoute

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Serveur TCP en écoute sur {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        print(f"Connecté par {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Reçu : {data.decode()}")
            conn.sendall(data)  # Renvoie les données reçues au client
            
# Client TCP Simple :

import socket

HOST = '127.0.0.1'  # Adresse IP du serveur
PORT = 65432        # Port du serveur

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    message = b"Bonjour, serveur!"
    s.sendall(message)
    data = s.recv(1024)
    print(f"Reçu du serveur : {data.decode()}")