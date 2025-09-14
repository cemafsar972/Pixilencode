import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
from PIL import Image
import string

# -------------------------------------------------
# Color Palette
# -------------------------------------------------
def generate_palette():
    chars = list(string.ascii_uppercase) + list(string.ascii_lowercase) + list(string.digits + string.punctuation)
    palette = {}
    step = 255 // max(1, len(chars) - 1)
    for i, c in enumerate(chars):
        r = (i * step) % 256
        g = (i * step * 2) % 256
        b = (i * step * 3) % 256
        palette[c] = (r, g, b)
    return palette

COLOR_PALETTE = generate_palette()

# -------------------------------------------------
# PIX → PNG
# -------------------------------------------------
def pix_to_png(pix_path, png_path):
    with open(pix_path, "r") as f:
        lines = f.read().splitlines()

    size = int(lines[0].strip())
    grid = lines[1:]
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    img = Image.new("RGB", (width, height), "black")
    pixels = img.load()

    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            color = COLOR_PALETTE.get(char, (0, 0, 0))
            pixels[x, y] = color

    img = img.resize((width * size, height * size), Image.NEAREST)
    img.save(png_path)

# -------------------------------------------------
# PNG → PIX
# -------------------------------------------------
def png_to_pix(png_path, pix_path, size=5):
    img = Image.open(png_path).convert("RGB")
    img_small = img.resize((img.width // size, img.height // size), Image.NEAREST)
    pixels = img_small.load()

    reverse_palette = {}
    for char, color in COLOR_PALETTE.items():
        reverse_palette[color] = char

    def closest_char(rgb):
        min_dist = float("inf")
        best_char = "N"
        for char, color in COLOR_PALETTE.items():
            dist = sum((a - b) ** 2 for a, b in zip(rgb, color))
            if dist < min_dist:
                min_dist = dist
                best_char = char
        return best_char

    lines = [str(size)]
    for y in range(img_small.height):
        row = ""
        for x in range(img_small.width):
            rgb = pixels[x, y]
            row += closest_char(rgb)
        lines.append(row)

    with open(pix_path, "w") as f:
        f.write("\n".join(lines))

# -------------------------------------------------
# Open PIX in Pygame
# -------------------------------------------------
def open_pix(pix_path):
    with open(pix_path, "r") as f:
        lines = f.read().splitlines()

    size = int(lines[0].strip())
    grid = lines[1:]
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0

    pygame.init()
    screen = pygame.display.set_mode((width * size, height * size), pygame.NOFRAME)
    pygame.display.set_caption("PIX Viewer")

    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            color = COLOR_PALETTE.get(char, (0, 0, 0))
            pygame.draw.rect(screen, color, (x * size, y * size, size, size))

    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False
    pygame.quit()

# -------------------------------------------------
# GUI
# -------------------------------------------------
def run_gui():
    def browse_file():
        filepath = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All files", "*.*")]
        )
        if filepath:
            entry_file.delete(0, tk.END)
            entry_file.insert(0, filepath)

    def execute():
        operation = combo_action.get()
        filepath = entry_file.get()
        if not filepath:
            messagebox.showerror("Error", "Please select a file.")
            return

        try:
            if operation == "Open PIX":
                open_pix(filepath)
            elif operation == "Convert PIX to PNG":
                out = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png")]
                )
                if out:
                    pix_to_png(filepath, out)
                    messagebox.showinfo("Success", f"Saved: {out}")
            elif operation == "Convert PNG to PIX":
                out = filedialog.asksaveasfilename(
                    defaultextension=".pix",
                    filetypes=[("PIX files", "*.pix")]
                )
                if out:
                    png_to_pix(filepath, out)
                    messagebox.showinfo("Success", f"Saved: {out}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("PIX Tool")

    # Icon
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        icon_img = tk.PhotoImage(file=icon_path)
        root.iconphoto(False, icon_img)
    except Exception:
        pass

    frm = ttk.Frame(root, padding=20)
    frm.grid()

    ttk.Label(frm, text="Select Operation:").grid(column=0, row=0, sticky="w")
    combo_action = ttk.Combobox(
        frm, values=["Open PIX", "Convert PIX to PNG", "Convert PNG to PIX"], state="readonly"
    )
    combo_action.current(0)
    combo_action.grid(column=1, row=0, padx=5, pady=5)

    ttk.Label(frm, text="File:").grid(column=0, row=1, sticky="w")
    entry_file = ttk.Entry(frm, width=40)
    entry_file.grid(column=1, row=1, padx=5, pady=5)
    ttk.Button(frm, text="Browse", command=browse_file).grid(column=2, row=1, padx=5)

    ttk.Button(frm, text="Execute", command=execute).grid(column=1, row=2, pady=10)

    root.mainloop()

# -------------------------------------------------
# Main
# -------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "extractpng" and len(sys.argv) > 2:
            pix_to_png(sys.argv[2], os.path.splitext(sys.argv[2])[0] + ".png")
        elif sys.argv[1] == "topix" and len(sys.argv) > 2:
            png_to_pix(sys.argv[2], os.path.splitext(sys.argv[2])[0] + ".pix")
        else:
            open_pix(sys.argv[1])
    else:
        run_gui()
