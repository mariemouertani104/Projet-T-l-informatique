from tkinter import *
import socket
import CRC
import tkinter.font as tkFont

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

win = Tk()
win.title("Calculator")
win.geometry('550x510')
win.configure(background=BG_COLOR)
win.resizable(0, 0)

operator = ""
_input = StringVar()

def btnclick(num):
    global operator
    operator = operator + str(num)
    _input.set(operator)

def clear():
    global operator
    operator = ""
    _input.set("")

def send_data():
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
    generated_data = crc.generate(expression.encode())
    addr = ("127.0.0.1", 2999)
    global client
    try:
        client.sendto(generated_data, addr)
        update_text(f"Sending to server: {expression}")
        data, addr = client.recvfrom(1024)
        decoded_data = data.decode()
        if "Error" in decoded_data:
            update_text(f"Received from server: {decoded_data}", "red")
        else:
            update_text(f"Received from server: {decoded_data}", "green")
            _input.set(decoded_data)
        operator = ""
    except OSError as e:
        update_text("Server is Shutdown ", "red")
    except socket.timeout:
        update_text("❌ No response from server.", "red")
    except socket.error as e:
        update_text(f"ERROR: {e}", "red")

def update_text(message, tag=""):
    display_connexion.config(state='normal')
    display_connexion.insert("end", message + "\n", tag)
    display_connexion.config(state='disabled')

# === GUI Elements ===
label_calc = Label(win, font=TITLE_FONT, text='Calculator', bg=BG_COLOR, fg='white')
label_calc.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

label_server = Label(win, font=TITLE_FONT, text='SERVER', bg=BG_COLOR, fg='white')
label_server.grid(row=0, column=4, columnspan=2, padx=10, pady=10)

display = Entry(win, font=('Arial', 20, 'bold'), textvariable=_input, insertwidth=7, bd=5, bg=DISPLAY_BG, fg=DISPLAY_FG, justify='right', state="normal")
display.grid(row=1, columnspan=4, padx=10, pady=10, ipady=5)

display_connexion = Text(win, font=FONT_NORMAL, bg='#2C3E50', fg=FG_COLOR, width=25, height=15)
display_connexion.grid(row=1, column=4, rowspan=6, sticky='nsew', padx=10, pady=10)
display_connexion.tag_configure("red", foreground="#E74C3C")
display_connexion.tag_configure("green", foreground="#2ECC71")
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
    client.settimeout(5)
except socket.error as e:
    update_text(f"Error creating socket: {e}", "red")
    exit(1)

win.mainloop()