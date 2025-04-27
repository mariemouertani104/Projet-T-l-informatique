import socket
import menu
import CRC
import random
import time

# Configuration du serveur
SERVER_ADDRESS = ('127.0.0.1', 2999)
TIMEOUT_SEC = 5
MAX_RETRIES = 2

# Probabilités de non-fiabilité
PERTE_PROBABILITE = 0.1
DUPLICATION_PROBABILITE = 0.05
DELAI_MAX = 0.5  # Délai max en secondes pour simuler le désordre
BIT_ERROR_PROBABILITY = 0.1  # Probabilité d'introduire une erreur sur un bit

def introduce_bit_error(data_bytes):
    """Introduit aléatoirement une erreur sur un bit des données."""
    if random.random() < BIT_ERROR_PROBABILITY:
        byte_index = random.randint(0, len(data_bytes) - 1)
        bit_index = random.randint(0, 7)
        byte_list = list(data_bytes)
        original_byte = byte_list[byte_index]
        modified_byte = original_byte ^ (1 << bit_index)
        byte_list[byte_index] = modified_byte
        print(f"Simulating a bit error in byte {byte_index}, bit {bit_index}.")
        return bytes(byte_list)
    return data_bytes

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as e:
    print("Error creating socket:", e)
    exit(1)

data_to_send = menu.menu()
print("Data to be sent to server:", data_to_send)

if data_to_send != "exit":
    data_str = ",".join(data_to_send)
    crc = CRC.CRC()
    encoded_data = data_str.encode()

    retries = 0
    while retries < MAX_RETRIES:
        print(f"Attempting to send data to server (Attempt {retries + 1})...")

        # Simulation de la non-fiabilité (perte)
        if random.random() < PERTE_PROBABILITE:
            print("Simulating packet loss...")
        else:
            # Préparation des données avec potentielle erreur de bit et CRC
            data_with_potential_bit_error = introduce_bit_error(encoded_data)
            encoded_data_with_crc = crc.generate(data_with_potential_bit_error)

            # Simulation de duplication
            num_envois = 1
            if random.random() < DUPLICATION_PROBABILITE:
                num_envois = random.randint(2, 3)
                print(f"Simulating {num_envois} duplicate packets...")

            # Simulation de délai (désordre potentiel)
            delay = 0
            if random.random() < 0.3:  # Probabilité d'introduire un délai
                delay = random.uniform(0, DELAI_MAX)
                print(f"Simulating delay of {delay:.2f} seconds...")
                time.sleep(delay)

            for _ in range(num_envois):
                client.sendto(encoded_data_with_crc, SERVER_ADDRESS)
                print("Sent to server (with potential bit error and CRC):", encoded_data_with_crc)

        client.settimeout(TIMEOUT_SEC)
        try:
            received_data, addr = client.recvfrom(1024)
            result = received_data.decode().split(',')
            print("Received response from server:", result)
            break  # Sortir de la boucle de tentatives si une réponse est reçue
        except socket.timeout:
            print(f"Timeout: No response from server after {TIMEOUT_SEC} seconds.")
            retries += 1

    if retries == MAX_RETRIES:
        print("No response from server after multiple attempts. Exiting and will try again later.")
else:
    print("Exiting client.")

client.close()