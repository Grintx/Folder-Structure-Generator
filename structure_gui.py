import os
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext

def parse_tree_structure(tree_string, base_folder):
    lines = tree_string.strip().splitlines()
    stack = []

    for line in lines:
        if not line.strip() or re.fullmatch(r'[│\s]+', line):
            continue

        depth = line.count("    ") 
        clean_line = re.sub(r"[├└─│]+", "", line).strip()
        clean_line = clean_line.split("#")[0].strip()

        if not clean_line:
            continue

        while len(stack) > depth:
            stack.pop()

        current_path = os.path.join(stack[-1] if stack else base_folder, clean_line)
        stack.append(current_path)

        if clean_line.endswith('/'):
            os.makedirs(current_path, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            with open(current_path, 'w') as f:
                f.write('')

def on_create_clicked():
    folder_name = entry.get().strip()
    structure_input = text.get("1.0", tk.END).strip()

    if not folder_name or not structure_input:
        messagebox.showerror("Missing Information", "Please provide both folder name and structure.")
        return

    base_path = os.path.join(os.getcwd(), folder_name)
    os.makedirs(base_path, exist_ok=True)

    try:
        parse_tree_structure(structure_input, base_path)
        messagebox.showinfo("Success", f"Structure created inside: {base_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create structure:\n{str(e)}")

window = tk.Tk()
window.title("📁 Folder Structure Generator")
window.geometry("700x600")
window.resizable(False, False)

tk.Label(window, text="Enter Top-Level Folder Name:", font=("Arial", 12, "bold")).pack(pady=10)
entry = tk.Entry(window, width=50, font=("Arial", 12))
entry.pack(pady=5)

tk.Label(window, text="Paste Folder/File Structure Below:", font=("Arial", 12, "bold")).pack(pady=10)
text = scrolledtext.ScrolledText(window, width=80, height=20, font=("Courier New", 10))
text.pack()

# Create button
tk.Button(window, text="Create", font=("Arial", 12, "bold"), bg="green", fg="white", command=on_create_clicked).pack(pady=20)

window.mainloop()
