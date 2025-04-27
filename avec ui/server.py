import CRC
import socket
import threading
from tkinter import *
import tkinter.font as tkFont
import random
import time

# === Globals ===
server = None
running = False
RECEIVED_PACKETS = {}
DUPLICATE_DETECTION_WINDOW = 5

# === Non-Reliability Simulation (Server Side) ===
PERTE_PROBABILITE_RECEPTION = 0.05
DELAI_MAX_RECEPTION = 0.3
BIT_ERROR_PROBABILITY_SERVER = 0.01

# === Style ===
BG_COLOR = '#34495E'
FG_COLOR = '#FFFFFF'
ACCENT_COLOR = '#2ECC71'
FONT_NORMAL = ('Arial', 12)
FONT_BOLD = ('Arial', 12, 'bold')
TITLE_FONT = ('Arial', 20, 'bold')
WINDOW_SIZE = '600x510'

def center_window(window, size):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    width, height = map(int, size.split('x'))
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def update_text(message, tag=""):
    display.config(state='normal')
    display.insert("end", message + "\n", tag)
    display.see("end")  # auto-scroll to bottom
    display.config(state='disabled')

def introduce_bit_error_server(data_bytes):
    """Introduit aléatoirement une erreur sur un bit des données côté serveur."""
    if random.random() < BIT_ERROR_PROBABILITY_SERVER:
        byte_index = random.randint(0, len(data_bytes) - 1)
        bit_index = random.randint(0, 7)
        byte_list = list(data_bytes)
        original_byte = byte_list[byte_index]
        modified_byte = original_byte ^ (1 << bit_index)
        byte_list[byte_index] = modified_byte
        update_text(f"⚠️ Simulating a bit error in received data from {addr} (server side).", "orange")
        return bytes(byte_list)
    return data_bytes

def start():
    global running, server
    if running:
        update_text("Server already running", "red")
        return
    running = True
    run_button.config(state="disabled")  # Disable RUN button
    threading.Thread(target=run_server, daemon=True).start()

def shutdown():
    global running, server
    running = False
    try:
        if server:
            server.close()
        update_text("Server shutdown requested", "orange")
    except Exception as e:
        update_text(f"Shutdown error: {e}", "red")
    run_button.config(state="normal")  # Re-enable RUN
    server=None

def handle_client(data_bytes_original, addr):
    if random.random() < PERTE_PROBABILITE_RECEPTION:
        update_text(f"💨 Simulating packet loss from {addr} (server side)...", "orange")
        return

    delay = 0
    if random.random() < 0.2:
        delay = random.uniform(0, DELAI_MAX_RECEPTION)
        update_text(f"⏳ Simulating reception delay from {addr}: {delay:.2f} seconds...", "orange")
        time.sleep(delay)

    # Duplicate detection
    if addr not in RECEIVED_PACKETS:
        RECEIVED_PACKETS[addr] = []
    if data_bytes_original in RECEIVED_PACKETS[addr][-DUPLICATE_DETECTION_WINDOW:]:
        update_text(f"👯 Detected duplicate packet from {addr}. Ignoring.", "orange")
        return
    RECEIVED_PACKETS[addr].append(data_bytes_original)

    update_text(f"Handling data from client: {addr}")
    crc = CRC.CRC()

    # Simulate bit error on server side before checking CRC
    data_with_potential_bit_error = introduce_bit_error_server(data_bytes_original)

    if not crc.check(data_with_potential_bit_error):
        update_text(f"❌ Data corrupted from {addr}", "red")
        result = "Error: CRC check failed"
        server.send