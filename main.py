import os
import tkinter as tk
from tkinter import messagebox, scrolledtext

def rename_files():
    prefix = prefix_entry.get().strip()
    if not prefix:
        messagebox.showwarning("Warning", "Prefix tidak boleh kosong!")
        return

    file_paths = text_area.get("1.0", tk.END).strip().splitlines()
    if not file_paths:
        messagebox.showwarning("Warning", "Daftar path file kosong!")
        return

    success, failed = 0, 0
    for i, file_path in enumerate(file_paths, start=1):
        file_path = file_path.strip('"').strip()
        if not os.path.isfile(file_path):
            failed += 1
            continue

        folder = os.path.dirname(file_path)
        ext = os.path.splitext(file_path)[1]
        new_name = f"{prefix}{i}{ext}"
        new_path = os.path.join(folder, new_name)

        try:
            os.rename(file_path, new_path)
            success += 1
        except Exception:
            failed += 1

    messagebox.showinfo("Hasil", f"Berhasil rename: {success}\nGagal: {failed}")

root = tk.Tk()
root.title("Mass File Renamer")
root.geometry("600x400")

tk.Label(root, text="Paste daftar path file di bawah ini:").pack(anchor="w", padx=10, pady=(10,0))

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12)
text_area.pack(fill="both", expand=True, padx=10, pady=5)

frame_prefix = tk.Frame(root)
frame_prefix.pack(fill="x", padx=10, pady=5)

tk.Label(frame_prefix, text="Prefix nama baru:").pack(side="left")
prefix_entry = tk.Entry(frame_prefix)
prefix_entry.insert(0, "MT_") 
prefix_entry.pack(side="left", fill="x", expand=True, padx=5)

rename_button = tk.Button(root, text="Rename Files", command=rename_files, bg="#4CAF50", fg="white")
rename_button.pack(pady=10)

root.mainloop()
