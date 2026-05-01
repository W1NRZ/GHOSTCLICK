# auto_clicker_mac.py
# pip install pynput

import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, Key

mouse = Controller()

clicking = threading.Event()
running = threading.Event()
running.set()

settings_lock = threading.Lock()
cps_value = 20.0
button_name = "left"

button_map = {
    "left": Button.left,
    "right": Button.right,
    "middle": Button.middle,
}


def click_loop():
    global cps_value, button_name

    next_click = time.perf_counter()

    while running.is_set():
        if clicking.is_set():
            with settings_lock:
                cps = cps_value
                chosen_button = button_map.get(button_name, Button.left)

            delay = 1.0 / cps if cps > 0 else 0.02
            now = time.perf_counter()

            if now >= next_click:
                mouse.click(chosen_button, 1)
                next_click += delay
            else:
                time.sleep(0.001)
        else:
            next_click = time.perf_counter()
            time.sleep(0.01)


def apply_settings():
    global cps_value, button_name

    try:
        cps = float(cps_entry.get())
        if cps <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("invalid cps", "enter a number bigger than 0.")
        return

    chosen_button = button_var.get().strip().lower()
    if chosen_button not in button_map:
        messagebox.showerror("invalid button", "choose left, right, or middle.")
        return

    with settings_lock:
        cps_value = cps
        button_name = chosen_button

    settings_status_var.set(f"settings: {cps:g} cps, {chosen_button} click")


def toggle_clicking():
    if clicking.is_set():
        clicking.clear()
        status_var.set("status: stopped")
    else:
        clicking.set()
        status_var.set("status: clicking")


def toggle_topmost():
    current = root.attributes("-topmost")
    root.attributes("-topmost", not current)


def on_press(key):
    # macOS keyboards often require the 'fn' key to trigger actual F-keys
    if key == Key.f6:
        root.after(0, toggle_clicking)
    elif key == Key.f7:
        root.after(0, close_app)
        return False
    elif key == Key.f8:
        root.after(0, toggle_topmost)


def close_app():
    clicking.clear()
    running.clear()
    root.destroy()


root = tk.Tk()
root.title("auto clicker")
# Increased width slightly because Mac system fonts take up a bit more horizontal space
root.geometry("340x260")
root.resizable(False, False)

# This works natively on macOS to keep the window on top
root.attributes("-topmost", True)

main = ttk.Frame(root, padding=16)
main.pack(fill="both", expand=True)

main.columnconfigure(0, weight=1)

# Changed font from "Segoe UI" to standard Mac system font "Helvetica"
title = ttk.Label(main, text="auto clicker", font=("Helvetica", 16, "bold"))
title.grid(row=0, column=0, pady=(0, 12), sticky="w")

ttk.Label(main, text="cps:").grid(row=1, column=0, sticky="w")
cps_entry = ttk.Entry(main)
cps_entry.insert(0, "20")
cps_entry.grid(row=2, column=0, sticky="ew", pady=(0, 10))

ttk.Label(main, text="mouse button:").grid(row=3, column=0, sticky="w")
button_var = tk.StringVar(value="left")
button_menu = ttk.OptionMenu(main, button_var, "left", "left", "right", "middle")
button_menu.grid(row=4, column=0, sticky="ew", pady=(0, 12))

apply_button = ttk.Button(main, text="apply", command=apply_settings)
apply_button.grid(row=5, column=0, sticky="ew", pady=(0, 10))

status_var = tk.StringVar(value="status: stopped")
status_label = ttk.Label(main, textvariable=status_var)
status_label.grid(row=6, column=0, sticky="w", pady=(6, 2))

settings_status_var = tk.StringVar(value="settings: 20 cps, left click")
settings_label = ttk.Label(main, textvariable=settings_status_var)
settings_label.grid(row=7, column=0, sticky="w")

hint = ttk.Label(main, text="f6 = start/stop  |  f7 = exit  |  f8 = top toggle")
hint.grid(row=8, column=0, sticky="w", pady=(14, 0))

threading.Thread(target=click_loop, daemon=True).start()
threading.Thread(target=lambda: Listener(on_press=on_press).run(), daemon=True).start()

root.protocol("WM_DELETE_WINDOW", close_app)
# Force window to the front on Mac specifically 
root.lift()
root.mainloop()
