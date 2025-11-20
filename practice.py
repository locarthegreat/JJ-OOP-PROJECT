import tkinter as tk
from tkinter import Toplevel, Label, Button

def open_custom_dialog():
    dialog = Toplevel(root)
    dialog.title("Hardware Alert")
    dialog.geometry("300x180")

    # --- Color Scheme ---
    bg_color = "#2E2E2E"      # dark steel gray
    text_color = "#F5F5F5"    # light gray/white
    accent_color = "#FBC02D"  # construction yellow
    button_hover = "#F9A825"  # darker yellow

    # --- Apply Styles ---
    dialog.config(bg=bg_color)

    Label(dialog, text="Item successfully added to inventory!", 
          bg=bg_color, fg=text_color, font=("Segoe UI", 11, "bold")).pack(pady=20)

    def on_enter(e): btn.config(bg=button_hover)
    def on_leave(e): btn.config(bg=accent_color)

    btn = Button(dialog, text="Close", command=dialog.destroy,
                 bg=accent_color, fg="black", activebackground=button_hover,
                 font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=5)
    btn.pack(pady=10)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

root = tk.Tk()
Button(root, text="Open Dialog", command=open_custom_dialog, bg="#FBC02D", fg="black",
       font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=40)
root.mainloop()
