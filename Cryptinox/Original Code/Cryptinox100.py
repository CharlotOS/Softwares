import os
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_file(file_path, password):
    with open(file_path, "rb") as f:
        data = f.read()
    
    salt = os.urandom(16)  
    key = derive_key(password, salt)
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data)
    
    with open(file_path + ".enc", "wb") as f:
        f.write(salt + encrypted_data)  
    
    os.remove(file_path)  


def decrypt_file(file_path, password):
    with open(file_path, "rb") as f:
        data = f.read()
    
    salt, encrypted_data = data[:16], data[16:]  
    key = derive_key(password, salt)
    cipher = Fernet(key)
    
    try:
        decrypted_data = cipher.decrypt(encrypted_data)
        original_path = file_path[:-4]  
        
        with open(original_path, "wb") as f:
            f.write(decrypted_data)
        
        os.remove(file_path)  
        messagebox.showinfo("Success", "File decrypted successfully!")
    except:
        messagebox.showerror("Error", "Wrong password or corrupted file!")


def encrypt_folder():
    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        return
    
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password!")
        return
    
    for file in os.listdir(folder_selected):
        file_path = os.path.join(folder_selected, file)
        if os.path.isfile(file_path):
            encrypt_file(file_path, password)
    
    messagebox.showinfo("Success", "All files encrypted successfully!")


def decrypt_single_file():
    file_selected = filedialog.askopenfilename(filetypes=[("Encrypted Files", "*.enc")])
    if not file_selected:
        return
    
    password = password_entry.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password!")
        return
    
    decrypt_file(file_selected, password)


root = tk.Tk()
root.title("File Encryptor & Decryptor")
root.geometry("400x200")

tk.Label(root, text="Enter Password:").pack()
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack()

tk.Button(root, text="Encrypt Folder", command=encrypt_folder).pack(pady=5)
tk.Button(root, text="Decrypt File", command=decrypt_single_file).pack(pady=5)

root.mainloop()
