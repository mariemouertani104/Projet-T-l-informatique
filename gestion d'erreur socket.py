import socket
import sys

HOST = '127.0.0.1'
PORT = 65432

try:
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
                conn.sendall(data)
except socket.error as e:
    print(f"Erreur de socket : {e}")
    sys.exit(1)
