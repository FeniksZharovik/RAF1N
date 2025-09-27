import os
import uuid
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

root = tk.Tk()
root.title("Mass File Renamer")

# Tambahkan icon (gunakan ico agar kompatibel Windows)
icon_path = os.path.join("assets", "ic-card-file-box.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path) 

def normalize_path(p: str) -> str:
    p = p.strip()
    if not p:
        return ""
    if (p[0] == p[-1]) and p[0] in ('"', "'"):
        p = p[1:-1]
    p = p.strip().strip('"').strip("'")
    return os.path.normpath(p)

def add_files():
    paths = filedialog.askopenfilenames(title="Pilih file (multi-select)")
    for p in paths:
        text_area.insert(tk.END, normalize_path(p) + "\n")

def add_folder():
    folder = filedialog.askdirectory(title="Pilih folder (akan memasukkan semua file di folder)")
    if not folder:
        return
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files.sort()
    for f in files:
        text_area.insert(tk.END, normalize_path(f) + "\n")

def clear_list():
    text_area.delete("1.0", tk.END)

def get_file_list_from_text():
    raw = text_area.get("1.0", tk.END).splitlines()
    seen = set()
    out = []
    for line in raw:
        p = normalize_path(line)
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out

def build_mappings():
    files = get_file_list_from_text()
    existing = [f for f in files if os.path.isfile(f)]
    missing = [f for f in files if not os.path.isfile(f)]
    if missing:
        msg = f"Ada {len(missing)} path yang tidak ditemukan dan akan diabaikan.\nContoh: {missing[:3]}"
        print(msg)

    if not existing:
        messagebox.showwarning("Tidak ada file valid", "Tidak ada file yang valid di daftar. Pastikan path benar.")
        return None, None

    prefix = prefix_entry.get().strip()
    if not prefix:
        messagebox.showwarning("Prefix kosong", "Isi prefix (misal: MT_) terlebih dahulu.")
        return None, None

    try:
        start_index = int(start_entry.get().strip())
        if start_index < 0:
            raise ValueError
    except Exception:
        messagebox.showwarning("Index salah", "Start index harus berupa bilangan bulat (contoh: 1).")
        return None, None

    total = len(existing)
    auto_pad = pad_var.get()
    pad = len(str(total + start_index - 1)) if auto_pad else 0

    mappings = []
    for i, old in enumerate(existing, start=start_index):
        folder = os.path.dirname(old)
        ext = os.path.splitext(old)[1]
        if pad:
            new_basename = f"{prefix}{i:0{pad}d}"
        else:
            new_basename = f"{prefix}{i}"
        new_name = new_basename + ext
        new_path = os.path.join(folder, new_name)
        mappings.append((old, new_path))
    return mappings, missing

def preview():
    result = build_mappings()
    if result is None:
        return
    mappings, missing = result
    top = tk.Toplevel(root)
    top.title("Preview rename")
    top.geometry("700x400")
    lbl = tk.Label(top, text=f"Preview ({len(mappings)} file). Perhatikan daftar sebelum menekan Rename.")
    lbl.pack(anchor="w", padx=8, pady=6)
    st = scrolledtext.ScrolledText(top, wrap=tk.NONE)
    st.pack(fill="both", expand=True, padx=8, pady=6)
    for old, new in mappings:
        st.insert(tk.END, f"{old}  →  {new}\n")
    st.configure(state="disabled")

def unique_path(path):
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    counter = 1
    while True:
        candidate = f"{base}_{counter}{ext}"
        if not os.path.exists(candidate):
            return candidate
        counter += 1

def rename_files():
    result = build_mappings()
    if result is None:
        return
    mappings, missing = result
    if not mappings:
        messagebox.showinfo("Info", "Tidak ada file yang akan di-rename.")
        return

    if missing:
        cont = messagebox.askyesno("Beberapa file tidak ditemukan",
                                   f"Ada {len(missing)} path yang tidak ditemukan dan akan diabaikan.\nLanjutkan rename untuk {len(mappings)} file yang valid?")
        if not cont:
            return

    cont = messagebox.askyesno("Konfirmasi", f"Akan merename {len(mappings)} file.\nApakah Anda yakin?")
    if not cont:
        return

    temp_list = [] 
    failed_stage1 = []
    for old, final in mappings:
        try:
            ext = os.path.splitext(old)[1]
            temp_name = f"__tmp__{uuid.uuid4().hex}{ext}"
            temp_path = os.path.join(os.path.dirname(old), temp_name)
            while os.path.exists(temp_path):
                temp_name = f"__tmp__{uuid.uuid4().hex}{ext}"
                temp_path = os.path.join(os.path.dirname(old), temp_name)
            os.rename(old, temp_path)
            temp_list.append((temp_path, final))
        except Exception as e:
            failed_stage1.append((old, str(e)))
            print(f"[ERROR] Stage1 rename {old} -> temp: {e}")

    success = []
    failed_stage2 = []
    for temp_path, desired_final in temp_list:
        try:
            final_path = desired_final
            final_path = unique_path(final_path)
            os.replace(temp_path, final_path)
            success.append((temp_path, final_path))
        except Exception as e:
            failed_stage2.append((temp_path, desired_final, str(e)))
            print(f"[ERROR] Stage2 rename {temp_path} -> {desired_final}: {e}")

    msg_lines = [
        f"Total diminta rename: {len(mappings)}",
        f"Berhasil: {len(success)}",
        f"Gagal stage1 (tidak bisa rename ke temp): {len(failed_stage1)}",
        f"Gagal stage2 (tidak bisa rename ke final): {len(failed_stage2)}"
    ]
    
    if failed_stage1:
        msg_lines.append("\nContoh gagal stage1:")
        for old, err in failed_stage1[:5]:
            msg_lines.append(f"- {old} -> {err}")
    if failed_stage2:
        msg_lines.append("\nContoh gagal stage2:")
        for temp, final, err in failed_stage2[:5]:
            msg_lines.append(f"- {temp} -> {final} -> {err}")

    messagebox.showinfo("Hasil Rename", "\n".join(msg_lines))
    current = get_file_list_from_text()
    succeeded_old = [os.path.abspath(old_path) for old_path, _ in mappings if os.path.exists(_)] 

# === GUI ===
root = tk.Tk()
root.title("Mass File Renamer")
root.geometry("800x520")

top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=8, pady=6)

btn_add_files = tk.Button(top_frame, text="Add Files", command=add_files)
btn_add_files.pack(side="left", padx=4)

btn_add_folder = tk.Button(top_frame, text="Add Folder", command=add_folder)
btn_add_folder.pack(side="left", padx=4)

btn_clear = tk.Button(top_frame, text="Clear List", command=clear_list)
btn_clear.pack(side="left", padx=4)

btn_preview = tk.Button(top_frame, text="Preview", command=preview)
btn_preview.pack(side="right", padx=4)

btn_rename = tk.Button(top_frame, text="Rename", command=rename_files, bg="#4CAF50", fg="white")
btn_rename.pack(side="right", padx=4)

lbl_instructions = tk.Label(root, text="Paste path satu per baris atau gunakan tombol Add Files / Add Folder. Path yang mengandung spasi & kutip akan dibersihkan.")
lbl_instructions.pack(anchor="w", padx=8)

text_area = scrolledtext.ScrolledText(root, wrap=tk.NONE, height=20)
text_area.pack(fill="both", expand=True, padx=8, pady=6)

bottom_frame = tk.Frame(root)
bottom_frame.pack(fill="x", padx=8, pady=6)

tk.Label(bottom_frame, text="Prefix:").pack(side="left")
prefix_entry = tk.Entry(bottom_frame, width=12)
prefix_entry.insert(0, "MT_")
prefix_entry.pack(side="left", padx=4)

tk.Label(bottom_frame, text="Start index:").pack(side="left")
start_entry = tk.Entry(bottom_frame, width=6)
start_entry.insert(0, "1")
start_entry.pack(side="left", padx=4)

pad_var = tk.BooleanVar(value=True)
pad_cb = tk.Checkbutton(bottom_frame, text="Zero-pad otomatis", variable=pad_var)
pad_cb.pack(side="left", padx=8)

root.mainloop()
