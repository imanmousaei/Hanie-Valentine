import tkinter as tk
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk
import random
import math
from pathlib import Path


# configs
QUESTION = f"Will you be my Valentine... again, My Love?"
YES_TEXT = "YES :)"
NO_TEXT = "NO :("

SLIDESHOW_DELAY_MS = 5000

FINAL_MESSAGE = (f"Happy Valentine's Day, My Love!\n"
                 f"I love you Hanie. \n"
                 f"You are my best friend, my home, my everything. \n"
                 f"Thank you for making me the happiest man in the world <3")


# photo paths
folder = Path("./photos")

PHOTO_PATHS = [f for f in folder.iterdir()
          if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg'}]

PHOTO_COUNT_LIMIT = 3
PHOTO_PATHS = PHOTO_PATHS[:PHOTO_COUNT_LIMIT]

# ====================================================

root = tk.Tk()
root.title("For You ❤")
root.attributes('-fullscreen', True)
root.configure(bg="black")

def exit_app(event=None):
    root.destroy()

root.bind("<Escape>", exit_app)

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

def random_point():
    margin = 40
    frame_w = question_frame.winfo_width()
    frame_h = question_frame.winfo_height()
    if frame_w < 100 or frame_h < 100:  # not yet laid out
        frame_w, frame_h = 600, 300  # fallback guess

    new_x = random.randint(margin, frame_w - margin - 180)
    new_y = random.randint(margin, frame_h - margin - 80)
    return new_x, new_y

last_x=0
last_y=0

def no_enter(event):
    global last_x, last_y
    min_distance = 300

    new_x, new_y = random_point()
    distance = ((new_x - last_x) ** 2 + (new_y - last_y) ** 2) ** 0.5

    # while distance < min_distance:
    #     new_x, new_y = random_point()
    #
    # last_x, last_y = new_x, new_y
    btn_no.place(x=new_x, y=new_y, anchor="center")



btn_yes = tk.Button(question_frame, text=YES_TEXT, font=("Arial", 28, "bold"),
                    bg="#ff4d4d", fg="white", width=10,
                    command=yes_clicked)
btn_yes.pack(side="left", padx=80)

btn_no = tk.Button(question_frame, text=NO_TEXT, font=("Arial", 28, "bold"),
                   bg="gray", fg="white", width=10)
btn_no.pack(side="right", padx=80)
btn_no.bind("<Enter>", no_enter)  # hover → run away!


# ── Phase 2: Slideshow ──
canvas = Canvas(root, bg="black", highlightthickness=0)

current_photo_idx = 0
fade_step = 0.5  # alpha increment for fade

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
        caption = f"Remember this?" if idx == 0 else ""
        canvas.create_text(screen_w//2, screen_h - 100,
                           text=caption, fill="white",
                           font=("Arial", 24, "italic"))

        # Schedule next
        root.after(SLIDESHOW_DELAY_MS, lambda: fade_to_next(idx))  # show 5 sec

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
    canvas.delete("all")  # clear slideshow etc.

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    # Start with a reasonable base size (adjust multiplier if needed)
    base_size = min(screen_w, screen_h) // 8  # e.g. 200–300 px on most screens
    pulse_offset = 0
    pulse_direction = 2.0

    def draw_heart(current_size):
        points = []
        # Center position (slightly above vertical center)
        cx = screen_w // 2
        cy = screen_h // 2 - base_size // 3

        scale = current_size / 16.0  # normalize so multiplier ≈1 gives ~reasonable size

        for t in range(0, 361, 4):  # coarser step = faster + less points
            rad = math.radians(t)
            # Standard heart parametric – values roughly -16 to 16 range
            x = 16 * (math.sin(rad) ** 3)
            y = 13 * math.cos(rad) - 5 * math.cos(2 * rad) \
                - 2 * math.cos(3 * rad) - math.cos(4 * rad)

            px = cx + x * scale
            py = cy - y * scale  # negate y (canvas y grows down)

            # Safety clamp (prevents insane off-screen values)
            px = max(0, min(screen_w, px))
            py = max(0, min(screen_h, py))

            points.append((px, py))

        if len(points) > 10:
            canvas.create_polygon(points, fill="#ff3366", outline="#ff6699",
                                  width=4, smooth=True, tags="heart")
        else:
            # Fallback if something broke
            canvas.create_oval(cx - current_size, cy - current_size,
                               cx + current_size, cy + current_size,
                               fill="red", tags="heart")
            canvas.create_text(cx, cy, text="Fallback circle", fill="white", font=("Arial", 16))

        # Debug label (remove later if you want)
        # canvas.create_text(100, 50, text=f"Size: {current_size:.1f} | Points: {len(points)}",
        #                    fill="yellow", font=("Arial", 14), anchor="nw", tags="debug")

    def pulse():
        nonlocal pulse_offset, pulse_direction
        canvas.delete("heart")
        current_size = base_size + pulse_offset
        draw_heart(current_size)
        pulse_offset += pulse_direction
        if pulse_offset > 35 or pulse_offset < -15:
            pulse_direction *= -1
        root.after(80, pulse)

    pulse()

    # Final message
    canvas.create_text(screen_w // 2, screen_h - 160,
                       text=FINAL_MESSAGE,
                       fill="pink", font=("Arial", 38, "bold"), justify="center")

    # Exit instructions
    # canvas.create_text(screen_w // 2, screen_h - 60,
    #                    text="Press ESC or click anywhere to close",
    #                    fill="gray", font=("Arial", 18))

    root.bind("<Escape>", lambda e: root.destroy())
    canvas.bind("<Button-1>", lambda e: root.destroy())

# Start with question screen
root.mainloop()
