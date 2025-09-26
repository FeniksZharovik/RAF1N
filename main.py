import os

def rename_files(file_paths, prefix="MT_"):
    """
    Rename banyak file sekaligus menjadi prefix_1, prefix_2, dst.
    """
    for i, file_path in enumerate(file_paths, start=1):
        folder = os.path.dirname(file_path)
        ext = os.path.splitext(file_path)[1]
        new_name = f"{prefix}{i}{ext}"
        new_path = os.path.join(folder, new_name)

        try:
            os.rename(file_path, new_path)
            print(f"Berhasil: {file_path} → {new_path}")
        except Exception as e:
            print(f"Gagal: {file_path} → {e}")


if __name__ == "__main__":
    print("=== Mass Rename Files ===")
    print("Paste semua path file, satu per baris. Jika selesai, tekan Enter 2x.\n")

    file_paths = []
    while True:
        line = input().strip('"')
        if not line:
            break
        file_paths.append(line)

    if not file_paths:
        print("Tidak ada file yang dimasukkan.")
    else:
        rename_files(file_paths, prefix="MT_")
        print("\nSelesai rename!")
