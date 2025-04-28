import socket
import calculatrice_binaire as calc
import CRC
import threading
import random
import time

# Configuration de la simulation de non-fiabilité côté serveur (pourrait être ajustée)
PERTE_PROBABILITE_RECEPTION = 0.05
DELAI_MAX_RECEPTION = 0.3  # Délai max en secondes pour simuler le désordre à la réception
DUPLICATE_DETECTION_WINDOW = 5 # Nombre de paquets récents à garder en mémoire pour la détection de doublons
RECEIVED_PACKETS = {} # Dictionnaire pour stocker les paquets reçus par client (adresse: [data1, data2, ...])

def reassemble(data):
    result = ""
    for i in range(len(data)):
        result += data[i] + ','
    return result[:-1]

def handle_client(data_bytes_original, addr):
    if random.random() < PERTE_PROBABILITE_RECEPTION:
        print(f"Simulating packet loss from {addr} (server side)...")
        return

    delay = 0
    if random.random() < 0.2:
        delay = random.uniform(0, DELAI_MAX_RECEPTION)
        print(f"Simulating reception delay from {addr}: {delay:.2f} seconds...")
        time.sleep(delay)

    # Détection des doublons
    if addr not in RECEIVED_PACKETS:
        RECEIVED_PACKETS[addr] = []
    if data_bytes_original in RECEIVED_PACKETS[addr][-DUPLICATE_DETECTION_WINDOW:]:
        print(f"Detected duplicate packet from {addr}. Ignoring.")
        return
    RECEIVED_PACKETS[addr].append(data_bytes_original)

    print(f"Handling data from client: {addr}")
    crc = CRC.CRC()
    is_valid = crc.check(data_bytes_original) # Vérification sur les données reçues directement
    if not is_valid:
        print(f"Data corrupted from {addr}")
        result = "erreur_crc"
        server.sendto(result.encode(), addr)
        return

    data = crc.get_data(data_bytes_original)
    try:
        data_str = data.decode().lstrip('\x00').strip()
        if data_str == 'exit':
            print(f"Client {addr} is exiting.")
            server.sendto("Server is shutting down".encode(), addr)
            return

        data_list = data_str.split(',')
        print(f"Received from client {addr}: {data_list}")

        op = data_list[0]
        num1 = int(data_list[1])
        num2 = int(data_list[2])
        result = calc.calcule(op, num1, num2)

        data_list.append(str(result))
        response = reassemble(data_list).encode()
        print(f"Sent to client {addr}: {response}")
        server.sendto(response, addr)

    except UnicodeDecodeError:
        print(f"Error decoding data from {addr}")
        result = "erreur_de_decodage"
        server.sendto(result.encode(), addr)
    except ValueError:
        print(f"Invalid data format from {addr}")
        result = "erreur_de_format"
        server.sendto(result.encode(), addr)
    except IndexError:
        print(f"Incomplete data from {addr}")
        result = "données_incomplètes"
        server.sendto(result.encode(), addr)

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as e:
    print("Error creating socket:", e)
    exit(1)

address = ("127.0.0.1", 2999)
server.bind(address)

print("Server is running and waiting for data...")

while True:
    data, addr = server.recvfrom(1024)
    client_thread = threading.Thread(target=handle_client, args=(data, addr))
    client_thread.start()

print("Server is shutting down...")
server.close()