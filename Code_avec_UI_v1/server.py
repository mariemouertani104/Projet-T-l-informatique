import CRC
import socket
import threading
from tkinter import *
import tkinter.font as tkFont

# === Globals ===
server = None
running = False

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

def run_server():
    global server, running
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.settimeout(1.0)  # Timeout every 1 second to check running
        update_text("Socket created successfully", ACCENT_COLOR)
    except socket.error as e:
        update_text("Error creating socket: " + str(e), "red")
        return

    address = ("127.0.0.1", 2999) 
    try:
        server.bind(address)
    except Exception as e:
        update_text(f"Bind failed: {e}", "red")
        return

    update_text("Server is running and waiting for data...", ACCENT_COLOR)

    while running:
        try:
            data, addr = server.recvfrom(1024)

            crc = CRC.CRC()
            if not crc.check(data):
                update_text("Data is corrupted", "red")
                result = "erreur"
                server.sendto(result.encode(), addr)
                continue

            data = crc.get_data(data)
            data = data.decode().lstrip('\x00').strip()

            if data == 'exit':
                update_text("Client requested shutdown", "orange")
                server.sendto("Server is shutting down".encode(), addr)
                break

            update_text(f"Received from client: {data}")
            try:
                result = str(eval(data))
                update_text(f"Sending to client: {result}", ACCENT_COLOR)
                server.sendto(result.encode(), addr)
            except Exception as e:
                update_text(f"Error processing data: {e}", "red")
                server.sendto(("Error: "+str(e)).encode(),addr)

        except socket.timeout:
            continue  # Re-check the running flag
        except OSError as e:
            continue
        except Exception as e:
            update_text(f"Error: {e}", "red")
            server.sendto(("Error: "+str(e)).encode(),addr)

    if server:
        server.close()
        server = None
    update_text("Server is shutting down...", "orange")
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
run_button = Button(win, text="RUN", bg=ACCENT_COLOR, fg=FG_COLOR, font=button_font, command=start, relief=FLAT, bd=0, padx=20, pady=10)
run_button.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 10)) # Buttons at the bottom

shutdown_button = Button(win, text="SHUTDOWN", bg="#E74C3C", fg=FG_COLOR, font=button_font, command=shutdown, relief=FLAT, bd=0, padx=20, pady=10)
shutdown_button.grid(row=2, column=1, sticky="ew", padx=10, pady=(10, 10)) # Buttons at the bottom

win.mainloop()