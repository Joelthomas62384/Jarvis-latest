import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Set up the destination folder
destination_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(destination_folder, exist_ok=True)

def save_to_local(file_path):
    """Save the selected file to the 'data' folder."""
    try:
        file_name = os.path.basename(file_path)
        destination_path = os.path.join(destination_folder, file_name)

        shutil.copy(file_path, destination_path)

        messagebox.showinfo("Success", f"File '{file_name}' saved to 'data/' folder successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")

def select_file():
    """Open file dialog to select images or PDFs and close the app after selection."""
    file_path = filedialog.askopenfilename(filetypes=[
        ("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
        ("PDF Files", "*.pdf"),
        ("All Files", "*.*")
    ])
    if file_path:
        save_to_local(file_path)
    
    # Close the window after selection (whether file is selected or not)
    root.destroy()

# GUI Setup
root = tk.Tk()
root.title("Local File Uploader")
root.geometry("350x200")

tk.Label(root, text="Select an image or PDF to save locally").pack(pady=10)
btn_upload = tk.Button(root, text="Save File", command=select_file)
btn_upload.pack(pady=20)

root.mainloop()
