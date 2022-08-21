import tkinter.messagebox
from tkinter import *
from random import randint
import tkinter.font as TkFont
from pyglet import font
from configparser import ConfigParser

def submit():
    code = code_input.get()
    if len(code) != 6:
        tkinter.messagebox.showwarning("Input Error", "2FA code should be 6 digits!")
        return
    if not code.isdigit():
        tkinter.messagebox.showwarning("Input Error", "2FA code should be 6 numerical characters!")
        return
    old = settings['DEFAULT']['check']
    settings['DEFAULT']['code'] = code
    settings['DEFAULT']['check'] = str(randint(100, 999))
    while settings['DEFAULT']['check'] == old:
        settings['DEFAULT']['check'] = str(randint(100, 999))
    f = open("settings.ini", "w")
    settings.write(f)
    mfa_win.destroy()


settings = ConfigParser()
settings.read('settings.ini')
PURPLE = settings['DEFAULT']['bg']
BLACK = settings['DEFAULT']['fg']
mfa_win = Tk()
mfa_win.geometry("350x90")
mfa_win.title("Capn 2FA")
icon = PhotoImage(file="icon.ico")
mfa_win.iconphoto(True, icon)
mfa_win.config(background=PURPLE)
mfa_win.resizable(False, False)

if not ('Orbitron' in TkFont.families()):
    font.add_file('Orbitron-Bold.ttf')

left_frame = Frame(mfa_win, bg=PURPLE)
right_frame = Frame(mfa_win, bg=PURPLE)
left_frame.grid(row=0, column=0)
right_frame.grid(row=0, column=1)
label = Label(left_frame, text="2FA Required:", font=("Orbitron", 20), fg=BLACK, bg=PURPLE)
code_input = Entry(left_frame, font=("Orbitron", 20), fg=BLACK, bg=PURPLE, width=6)
enter_button = Button(mfa_win, text="Enter", command=submit, font=("Orbitron", 15), bg=PURPLE, fg=BLACK)
label.grid(row=0, column=0, padx=5)
code_input.grid(row=1, column=0)
enter_button.place(x=245, y=27)

mainloop()