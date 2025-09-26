import os
import tkinter as tk
from tkinter import filedialog, messagebox

def rename_files_in_folder():
    folder = filedialog.askdirectory(title="Pilih Folder Gambar")
    if not folder:
        return

    prefix = prefix_entry.get().strip()
    if not prefix:
        messagebox.showwarning("Warning", "Prefix tidak boleh kosong!")
        return

    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files.sort()  

    success, failed = 0, 0
    for i, filename in enumerate(files, start=1):
        old_path = os.path.join(folder, filename)
        ext = os.path.splitext(filename)[1]
        new_name = f"{prefix}{i}{ext}"
        new_path = os.path.join(folder, new_name)

        try:
            os.rename(old_path, new_path)
            success += 1
        except Exception as e:
            failed += 1
            print(f"Gagal rename {old_path} → {e}")

    messagebox.showinfo("Hasil", f"Berhasil rename: {success}\nGagal: {failed}")

root = tk.Tk()
root.title("Mass File Renamer")
root.geometry("400x150")

tk.Label(root, text="Prefix nama baru:").pack(pady=5)
prefix_entry = tk.Entry(root)
prefix_entry.insert(0, "MT_")
prefix_entry.pack(fill="x", padx=20)

rename_button = tk.Button(root, text="Pilih Folder & Rename", command=rename_files_in_folder, bg="#4CAF50", fg="white")
rename_button.pack(pady=20)

root.mainloop()
