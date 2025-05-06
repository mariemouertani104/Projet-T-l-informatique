import socket
import threading
from tkinter import *
import tkinter.font as tkFont
import CRC
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
    if random.random() < BIT_ERROR_PROBABILITE_SERVER:
        byte_index = random.randint(0, len(data_bytes) - 1)
        bit_index = random.randint(0, 7)
        byte_list = list(data_bytes)
        original_byte = byte_list[byte_index]
        modified_byte = original_byte ^ (1 << bit_index)
        byte_list[byte_index] = modified_byte
        update_text(f"⚠️ Simulating a bit error in received data (server side).", "orange")
        return bytes(byte_list)
    return data_bytes

def reassemble(data_list):
    return ','.join(map(str, data_list))

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
        result = "erreur_crc"
        server.sendto(result.encode(), addr)
        return

    data = crc.get_data(data_with_potential_bit_error)
    try:
        data_str = data.decode().lstrip('\x00').strip()
        if data_str == 'exit':
            update_text(f"Client {addr} is exiting.")
            server.sendto("Server is shutting down".encode(), addr)
            return

        data_list = data_str.split(',')
        update_text(f"Received from client {addr}: {data_list}")

        if len(data_list) == 3:
            op = data_list[0]
            num1 = int(data_list[1])
            num2 = int(data_list[2])
            result = calc.calcule(op, num1, num2)
            response = reassemble([op, num1, num2, result]).encode()
            update_text(f"Sent to client {addr}: {response.decode()}", ACCENT_COLOR)
            server.sendto(response, addr)
        else:
            update_text(f"⚠️ Invalid data format from {addr}: {data_str}", "red")
            server.sendto("erreur_de_format".encode(), addr)

    except UnicodeDecodeError:
        update_text(f"Error decoding data from {addr}", "red")
        server.sendto("erreur_de_decodage".encode(), addr)
    except ValueError as e:
        update_text(f"Invalid value in data from {addr}: {e}", "red")
        server.sendto("erreur_de_format".encode(), addr)
    except IndexError:
        update_text(f"Incomplete data from {addr}", "red")
        server.sendto("données_incomplètes".encode(), addr)

def start_server():
    global running, server
    if running:
        update_text("Server already running", "red")
        return
    running = True
    run_button.config(state="disabled")
    threading.Thread(target=run_server_thread, daemon=True).start()

def shutdown_server():
    global running, server
    running = False
    if server:
        server.close()
        server = None
        update_text("Server shutdown requested", "orange")
    run_button.config(state="normal")

def run_server_thread():
    global server, running
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(('127.0.0.1', 2999)) # Use the same port as the client
        update_text(f"🚀 Server started on 127.0.0.1:2999", ACCENT_COLOR)
        while running:
            try:
                data, addr = server.recvfrom(1024)
                threading.Thread(target=handle_client, args=(data, addr), daemon=True).start()
            except socket.timeout:
                pass
            except Exception as e:
                update_text(f"⚠️ Error in server loop: {e}", "red")
                break
    except Exception as e:
        update_text(f"❌ Server startup error: {e}", "red")
    finally:
        if server:
            server.close()
            server = None
            update_text("🛑 Server socket closed.")
        running = False
        run_button.config(state="normal")

# === GUI Setup ===
win = Tk()
win.title("Calculator SERVER")
win.geometry(WINDOW_SIZE)
center_window(win, WINDOW_SIZE)
win.configure(background=BG_COLOR)
win.resizable(0, 0)

# Configure grid layout
win.grid_rowconfigure(0, weight=1)
win.grid_rowconfigure(1, weight=1)
win.grid_rowconfigure(2, weight=0) # Buttons row should not expand
win.grid_columnconfigure(0, weight=1)
win.grid_columnconfigure(1, weight=1)

label = Label(win, font=TITLE_FONT, text="I'm a Server Calculator", bg=BG_COLOR, fg=FG_COLOR)
label.grid(row=0, column=0, columnspan=2, sticky="n") # Align title to the top

display = Text(win, width=48, height=15, bg='#2C3E50', fg=FG_COLOR, font=FONT_NORMAL, padx=5, pady=5)
display.grid(row=1, column=0, columnspan=2, sticky="nsew") # Make text area expand

button_font = tkFont.Font(family="Arial", size=14, weight="bold")
run_button = Button(win, text="RUN", bg=ACCENT_COLOR, fg=FG_COLOR, font=button_font, command=start_server, relief=FLAT, bd=0, padx=20, pady=10)
run_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 10)) # Buttons at the bottom

shutdown_button = Button(win, text="SHUTDOWN", bg="#E74C3C", fg=FG_COLOR, font=button_font, command=shutdown_server, relief=FLAT, bd=0, padx=20, pady=10)
shutdown_button.grid(row=2, column=1, sticky="ew", padx=10, pady=(10, 10)) # Buttons at the bottom

win.mainloop()