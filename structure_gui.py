import os
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from pathlib import Path


# ============================================================
# ADVANCED FOLDER STRUCTURE GENERATOR
# ============================================================

class FolderStructureGenerator:

    INVALID_CHARS = r'<>:"|?*'

    def __init__(self, root):

        self.root = root
        self.root.title("📁 Advanced Folder Structure Generator")
        self.root.geometry("900x720")
        self.root.minsize(850, 650)

        self.build_ui()

    # ============================================================
    # UI
    # ============================================================

    def build_ui(self):

        title = tk.Label(
            self.root,
            text="Folder Structure Generator",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)

        # Folder Name
        tk.Label(
            self.root,
            text="Top-Level Folder Name",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=20)

        self.folder_entry = tk.Entry(
            self.root,
            font=("Arial", 11)
        )
        self.folder_entry.pack(
            fill="x",
            padx=20,
            pady=5
        )

        # Destination
        tk.Label(
            self.root,
            text="Destination Path",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=20)

        path_frame = tk.Frame(self.root)
        path_frame.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.path_entry = tk.Entry(
            path_frame,
            font=("Arial", 11)
        )
        self.path_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        browse_btn = tk.Button(
            path_frame,
            text="Browse",
            command=self.browse_directory
        )
        browse_btn.pack(side="left", padx=5)

        # Structure Input
        tk.Label(
            self.root,
            text="Paste Folder/File Tree Structure",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=20, pady=(10, 0))

        self.text_area = scrolledtext.ScrolledText(
            self.root,
            font=("Courier New", 10),
            wrap=tk.NONE
        )
        self.text_area.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        # Example
        example = """
project/
├── src/
│   ├── main.py
│   ├── utils/
│   │   └── helper.py
│   └── config.py
├── requirements.txt
└── README.md
"""

        self.text_area.insert("1.0", example.strip())

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        create_btn = tk.Button(
            btn_frame,
            text="Create Structure",
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=5,
            command=self.create_structure
        )
        create_btn.pack(side="left", padx=10)

        clear_btn = tk.Button(
            btn_frame,
            text="Clear",
            font=("Arial", 12),
            padx=20,
            pady=5,
            command=self.clear_text
        )
        clear_btn.pack(side="left")

    # ============================================================
    # UTILITIES
    # ============================================================

    def browse_directory(self):

        folder = filedialog.askdirectory()

        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)

    def clear_text(self):

        self.text_area.delete("1.0", tk.END)

    def sanitize_name(self, name):

        for char in self.INVALID_CHARS:
            name = name.replace(char, "_")

        return name.strip()

    # ============================================================
    # CORE PARSER
    # ============================================================

    def parse_tree(self, tree_text, base_path):

        # Normalize tabs
        lines = tree_text.replace("\t", "    ").splitlines()

        stack = [Path(base_path)]

        for raw_line in lines:

            line = raw_line.rstrip()

            # Skip empty lines
            if not line.strip():
                continue

            # Skip pure tree symbol lines
            if re.fullmatch(r'[\s│├└─]+', line):
                continue

            # Match tree structure
            match = re.match(
                r'^(?P<prefix>(?:│   |    )*)(?:├── |└── )?(?P<name>.+)$',
                line
            )

            if not match:
                continue

            prefix = match.group("prefix")
            name = match.group("name").strip()

            # Remove inline comments
            name = name.split("#")[0].strip()

            # Remove accidental symbols
            name = re.sub(r'^[│├└─\s]+', '', name)
            name = re.sub(r'[│├└─]+$', '', name)

            name = name.strip()

            # Skip invalid entries
            if not name:
                continue

            # Prevent "|" folder bug
            if name in ["|", "│"]:
                continue

            # Prevent malformed nodes
            if all(ch in "│├└─" for ch in name):
                continue

            # Prevent dangerous paths
            if name in ["..", "."]:
                continue

            # Sanitize
            name = self.sanitize_name(name)

            # Calculate depth
            depth = prefix.count("│   ") + prefix.count("    ")

            # Maintain stack
            while len(stack) > depth + 1:
                stack.pop()

            parent = stack[-1]

            cleaned_name = name.rstrip("/")

            current_path = parent / cleaned_name

            # Determine if folder
            is_folder = (
                name.endswith("/")
                or "." not in cleaned_name.split("/")[-1]
            )

            try:

                if is_folder:

                    current_path.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                else:

                    current_path.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    current_path.touch(
                        exist_ok=True
                    )

                stack.append(current_path)

            except Exception as e:

                print(f"Skipping invalid path: {current_path}")
                print(e)

    # ============================================================
    # CREATE STRUCTURE
    # ============================================================

    def create_structure(self):

        folder_name = self.folder_entry.get().strip()

        destination = self.path_entry.get().strip()

        tree_text = self.text_area.get(
            "1.0",
            tk.END
        ).strip()

        # Validation
        if not folder_name:

            messagebox.showerror(
                "Error",
                "Folder name is required."
            )
            return

        if not destination:

            messagebox.showerror(
                "Error",
                "Destination path is required."
            )
            return

        if not tree_text:

            messagebox.showerror(
                "Error",
                "Tree structure is empty."
            )
            return

        try:

            folder_name = self.sanitize_name(folder_name)

            base_path = Path(destination) / folder_name

            base_path.mkdir(
                parents=True,
                exist_ok=True
            )

            self.parse_tree(
                tree_text,
                base_path
            )

            messagebox.showinfo(
                "Success",
                f"Folder structure created successfully.\n\nLocation:\n{base_path}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"Failed to create structure.\n\n{str(e)}"
            )


# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = FolderStructureGenerator(root)

    root.mainloop()