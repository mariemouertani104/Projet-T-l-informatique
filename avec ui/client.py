from tkinter import *
import socket
import CRC
import tkinter.font as tkFont
import random
import time

# === Style ===
BG_COLOR = '#34495E'
FG_COLOR = '#FFFFFF'
BUTTON_BG = 'white'
BUTTON_FG = 'black'
BUTTON_ACTIVE_BG = '#D3D3D3'
DISPLAY_BG = '#2C3E50'
DISPLAY_FG = '#FFFFFF'
FONT_NORMAL = ('Arial', 12)
FONT_BOLD = ('Arial', 14, 'bold')
TITLE_FONT = ('Arial', 20, 'bold')

# === Non-Reliability Simulation (Client Side) ===
PERTE_PROBABILITE_ENVOI = 0.05
DUPLICATION_PROBABILITE_ENVOI = 0.03
DELAI_MAX_ENVOI = 0.2
BIT_ERROR_PROBABILITY_CLIENT = 0.02
MAX_RETRIES = 3
TIMEOUT_SEC = 2

win = Tk()
win.title("Calculator")
win.geometry('550x510')
win.configure(background=BG_COLOR)
win.resizable(0, 0)

operator = ""
_input = StringVar()
client = None

def introduce_bit_error(data_bytes):
    """Introduit aléatoirement une erreur sur un bit des données."""
    if random.random() < BIT_ERROR_PROBABILITY_CLIENT:
        byte_index = random.randint(0, len(data_bytes) - 1)
        bit_index = random.randint(0, 7)
        byte_list = list(data_bytes)
        original_byte = byte_list[byte_index]
        modified_byte = original_byte ^ (1 << bit_index)
        byte_list[byte_index] = modified_byte
        update_text(f"⚠️ Simulating a bit error in sent data (byte {byte_index}, bit {bit_index}).")
        return bytes(byte_list)
    return data_bytes

def btnclick(num):
    global operator
    operator = operator + str(num)
    _input.set(operator)

def clear():
    global operator
    operator = ""
    _input.set("")

def send_data():
    global operator, client
    error = False
    expression = _input.get()
    if not expression or any(c.isalpha() for c in expression) or expression in "+-*/()" or all(c in "+-*/.()" for c in expression):
        update_text("Can't send nothing or only operations to the server !! ", "red")
        _input.set("")
        return
    while expression.startswith("0") and len(expression) > 1 and expression[1] != '.':
        expression = expression[1:]
        _input.set(expression)

    crc = CRC.CRC()
    encoded_data = expression.encode()
    addr = ("127.0.0.1", 3007)
    retries = 0

    while retries < MAX_RETRIES:
        update_text(f"Attempting to send: {expression} (Attempt {retries + 1})...")

        # Simulate packet loss
        if random.random() < PERTE_PROBABILITE_ENVOI:
            update_text("💨 Simulating packet loss (client side)...")
        else:
            # Introduce bit error
            data_with_potential_bit_error = introduce_bit_error(encoded_data)
            encoded_data_with_crc = crc.generate(data_with_potential_bit_error)

            num_envois = 1
            # Simulate duplication
            if random.random() < DUPLICATION_PROBABILITE_ENVOI:
                num_envois = random.randint(2, 3)
                update_text(f"👯 Simulating {num_envois} duplicate packets...")

            # Simulate delay
            delay = 0
            if random.random() < 0.3:
                delay = random.uniform(0, DELAI_MAX_ENVOI)
                update_text(f"⏳ Simulating send delay of {delay:.2f} seconds...")
                time.sleep(delay)

            for _ in range(num_envois):
                try:
                    client.sendto(encoded_data_with_crc, addr)
                    update_text(f"Sent to server (with potential bit error and CRC): {encoded_data_with_crc}")
                except OSError as e:
                    update_text("Server is Shutdown ", "red")
                    return

            client.settimeout(TIMEOUT_SEC)
            try:
                data, server_addr = client.recvfrom(1024)
                decoded_data = data.decode()
                if "Error" in decoded_data:
                    update_text(f"Received from server: {decoded_data}", "red")
                else:
                    update_text(f"Received from server: {decoded_data}", "green")
                    _input.set(decoded_data)
                operator = ""
                break # Exit retry loop on successful reception
            except socket.timeout:
                update_text(f"❌ Timeout: No response from server after {TIMEOUT_SEC} seconds.")
                retries += 1
            except socket.error as e:
                update_text(f"ERROR receiving: {e}", "red")
                break

    if retries == MAX_RETRIES:
        update_text("❌ No response from server after multiple attempts.", "red")

def update_text(message, tag=""):
    display_connexion.config(state='normal')
    display_connexion.insert("end", message + "\n", tag)
    display_connexion.config(state='disabled')

# === GUI Elements ===
label_calc = Label(win, font=TITLE_FONT, text='Calculator', bg=BG_COLOR, fg='white')
label_calc.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

label_server = Label(win, font=TITLE_FONT, text='SERVER LOG', bg=BG_COLOR, fg='white')
label_server.grid(row=0, column=4, columnspan=2, padx=10, pady=10)

display = Entry(win, font=('Arial', 20, 'bold'), textvariable=_input, insertwidth=7, bd=5, bg=DISPLAY_BG, fg=DISPLAY_FG, justify='right', state="normal")
display.grid(row=1, columnspan=4, padx=10, pady=10, ipady=5)

display_connexion = Text(win, font=FONT_NORMAL, bg='#2C3E50', fg=FG_COLOR, width=25, height=15)
display_connexion.grid(row=1, column=4, rowspan=6, sticky='nsew', padx=10, pady=10)
display_connexion.tag_configure("red", foreground="#E74C3C")
display_connexion.tag_configure("green", foreground="#2ECC71")
display_connexion.tag_configure("orange", foreground="#FFA500")
display_connexion.config(state="disabled")

button_font = tkFont.Font(family="Arial", size=16, weight="bold")
buttons = [
    ('C', 2, 0), ('(', 2, 1), (')', 2, 2), ('+', 2, 3),
    ('7', 3, 0), ('8', 3, 1), ('9', 3, 2), ('-', 3, 3),
    ('4', 4, 0), ('5', 4, 1), ('6', 4, 2), ('*', 4, 3),
    ('1', 5, 0), ('2', 5, 1), ('3', 5, 2), ('/', 5, 3),
    ('0', 6, 0, 3), ('=', 6, 3)
]

for (text, row, col, *colspan) in buttons:
    sticky = 'ew'
    grid_config = {'row': row, 'column': col, 'padx': 5, 'pady': 5, 'sticky': sticky}
    if colspan:
        grid_config['columnspan'] = colspan[0]

    command = lambda t=text: btnclick(t) if t.isdigit() or t in '+-*/().' else clear() if t == 'C' else send_data() if t == '=' else None
    bg = BUTTON_BG
    fg = BUTTON_FG
    activebg = BUTTON_ACTIVE_BG

    button = Button(win, text=text, padx=16, pady=16, bd=4, fg=fg, bg=bg, activebackground=activebg, font=button_font, command=command, relief=FLAT)
    button.grid(**grid_config)

win.columnconfigure(4, weight=1)
for i in range(7):
    win.rowconfigure(i, weight=1)

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    update_text("Socket created successfully", "green")
except socket.error as e:
    update_text(f"Error creating socket: {e}", "red")
    exit(1)

win.mainloop()