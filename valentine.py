import tkinter as tk
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk
import random
import math
import time

# ================== CUSTOMIZE HERE ==================
WIFE_NAME = "My Love"  # or her actual name/pet name
QUESTION = f"Will you be my Valentine... again, {WIFE_NAME}? ❤️"
YES_TEXT = "YES! 😍"
NO_TEXT = "NO 😢"

PHOTO_PATHS = [
    "photos/1.jpg",   # replace with your real paths
    "photos/2.jpg",
    "photos/3.jpg",
    "photos/4.jpg",
    "photos/5.jpg",
    # add more!
]

FINAL_MESSAGE = f"Happy Valentine's Day, {WIFE_NAME}!\nI love you more every beat of my heart 💕"
# ====================================================

root = tk.Tk()
root.title("For You ❤️")
root.attributes('-fullscreen', True)  # fullscreen for impact; comment out for windowed testing
root.configure(bg="black")

# Keep references to avoid garbage collection
photo_refs = []

# ── Phase 1: Yes/No Question ──
question_frame = tk.Frame(root, bg="black")
question_frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(question_frame, text=QUESTION, font=("Arial", 32, "bold"),
         fg="pink", bg="black").pack(pady=40)

def yes_clicked():
    question_frame.destroy()
    start_slideshow()

def no_enter(event):
    # Move "No" button to random position when hovered
    new_x = random.randint(100, root.winfo_screenwidth() - 200)
    new_y = random.randint(200, root.winfo_screenheight() - 200)
    btn_no.place(x=new_x, y=new_y)

btn_yes = tk.Button(question_frame, text=YES_TEXT, font=("Arial", 28, "bold"),
                    bg="#ff4d4d", fg="white", width=10,
                    command=yes_clicked)
btn_yes.pack(side="left", padx=80)

btn_no = tk.Button(question_frame, text=NO_TEXT, font=("Arial", 28, "bold"),
                   bg="gray", fg="white", width=10)
btn_no.pack(side="right", padx=80)
btn_no.bind("<Enter>", no_enter)  # hover → run away!

# Optional: Make "No" even harder — change text on hover
def no_leave(event):
    btn_no.config(text=NO_TEXT)
btn_no.bind("<Leave>", no_leave)

# ── Phase 2: Slideshow ──
canvas = Canvas(root, bg="black", highlightthickness=0)
# We'll place it later

current_photo_idx = 0
fade_step = 0.1  # alpha increment for fade

def start_slideshow():
    global canvas
    canvas.pack(fill="both", expand=True)
    show_photo(current_photo_idx)

def show_photo(idx):
    global current_photo_idx
    if idx >= len(PHOTO_PATHS):
        show_beating_heart()
        return

    try:
        img = Image.open(PHOTO_PATHS[idx])
        # Resize to fit screen (keep aspect ratio)
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        img.thumbnail((screen_w, screen_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        photo_refs.append(photo)  # keep ref

        # Center image
        x = (screen_w - img.width) // 2
        y = (screen_h - img.height) // 2
        canvas.create_image(x, y, image=photo, anchor="nw", tags="photo")

        # Caption (optional per photo)
        caption = f"Remember this? ❤️" if idx == 0 else ""
        canvas.create_text(screen_w//2, screen_h - 100,
                           text=caption, fill="white",
                           font=("Arial", 24, "italic"))

        # Schedule next
        root.after(5000, lambda: fade_to_next(idx))  # show 5 sec

    except Exception as e:
        messagebox.showerror("Oops", f"Couldn't load photo: {e}")
        show_beating_heart()

def fade_to_next(current_idx):
    # Simple fade: clear old, show new (for smoother, we'd blend layers, but keep simple)
    canvas.delete("photo")
    global current_photo_idx
    current_photo_idx = current_idx + 1
    show_photo(current_photo_idx)

# ── Phase 3: Beating Heart ──
def show_beating_heart():
    canvas.delete("all")  # clear slideshow

    heart_size_base = 150
    pulse = 0
    pulse_dir = 0.8

    def draw_heart(size):
        points = []
        cx, cy = root.winfo_screenwidth()//2, root.winfo_screenheight()//2 - 50
        for t in range(0, 360, 2):
            rad = math.radians(t)
            # Classic heart parametric (from math sources)
            x = size * 16 * math.sin(rad)**3
            y = size * -(13 * math.cos(rad) - 5 * math.cos(2*rad) -
                         2 * math.cos(3*rad) - math.cos(4*rad))
            points.append((cx + x, cy + y))
        canvas.create_polygon(points, fill="red", outline="pink", width=4, tags="heart")

    def beat():
        nonlocal pulse, pulse_dir
        canvas.delete("heart")
        current_size = heart_size_base + pulse
        draw_heart(current_size)
        pulse += pulse_dir
        if pulse > 30 or pulse < -10:
            pulse_dir *= -1
        root.after(60, beat)  # fast heartbeat feel

    beat()

    # Final text
    canvas.create_text(root.winfo_screenwidth()//2, root.winfo_screenheight() - 150,
                       text=FINAL_MESSAGE,
                       fill="pink", font=("Arial", 40, "bold"), justify="center")

    # Exit hint
    canvas.create_text(root.winfo_screenwidth()//2, root.winfo_screenheight() - 50,
                       text="(Press ESC to close)",
                       fill="gray", font=("Arial", 16))

    root.bind("<Escape>", lambda e: root.destroy())

# Start with question screen
root.mainloop()
