import tkinter.messagebox
from tkinter import *
from random import randint
from json import dump, load

def submit():
    code = code_input.get()
    if len(code) != 6:
        tkinter.messagebox.showwarning("Input Error", "2FA code should be 6 digits!")
        return
    if not code.isdigit():
        tkinter.messagebox.showwarning("Input Error", "2FA code should be numerical characters!")
        return
    f = open("multifactor.json", "r")
    old = load(f)
    f.close()
    temp = {"check": randint(100, 999), "code": f"{code}"}
    while temp['check'] == old['check']:
        temp = {"check": randint(100, 999), "code": f"{code}"}
    f = open("multifactor.json", "w")
    dump(temp, f)
    f.close()
    mfa_win.destroy()


PURPLE = "#400080"
mfa_win = Tk()
mfa_win.geometry("350x90")
mfa_win.title("Capn 2FA")
icon = PhotoImage(file="icon.ico")
mfa_win.iconphoto(True, icon)
mfa_win.config(background=PURPLE)
mfa_win.resizable(False, False)

left_frame = Frame(mfa_win, bg=PURPLE)
right_frame = Frame(mfa_win, bg=PURPLE)
left_frame.grid(row=0, column=0)
right_frame.grid(row=0, column=1)
label = Label(left_frame, text="2FA Required:", font=("Orbitron", 20), fg="black", bg=PURPLE)
code_input = Entry(left_frame, font=("Orbitron", 20), fg="black", bg="white", width=6)
enter_button = Button(mfa_win, text="Enter", command=submit, font=("Orbitron", 15), bg=PURPLE)
label.grid(row=0, column=0, padx=5)
code_input.grid(row=1, column=0)
enter_button.place(x=245, y=27)

mainloop()
