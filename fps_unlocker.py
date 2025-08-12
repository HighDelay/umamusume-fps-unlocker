import tkinter as tk
from tkinter import messagebox
import pymem
import pymem.process
import capstone
import atexit
import webbrowser

# Global variables to store patch information
pm = None
original_bytes = None
patch_address = 0

def apply_patch():
    global pm, original_bytes, patch_address
    try:
        pm = pymem.Pymem("UmamusumePrettyDerby.exe")
        base = pymem.process.module_from_name(pm.process_handle, "UnityPlayer.dll").lpBaseOfDll
        
        # Set FPS
        addr_fps = base + 0x1794EC0
        new_fps = int(fps_entry.get())
        pm.write_int(addr_fps, new_fps)

        # NOP patch
        patch_address = base + 0x556E50
        
        # Read original bytes to determine instruction size
        instruction_bytes = pm.read_bytes(patch_address, 16) # Read 16 bytes
        
        # Disassemble to find the exact instruction length
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
        for i in md.disasm(instruction_bytes, patch_address):
            instruction_size = i.size
            break
        else:
            raise Exception("Failed to disassemble instruction.")
            
        original_bytes = pm.read_bytes(patch_address, instruction_size)
        
        # Write NOPs
        nop_bytes = b'\x90' * instruction_size
        pm.write_bytes(patch_address, nop_bytes, instruction_size)
        
        messagebox.showinfo("Success", f"FPS set to {new_fps} and revert function disabled with a {instruction_size}-byte NOP patch!")
        
    except pymem.exception.ProcessNotFound:
        messagebox.showerror("Error", "Game process (UmamusumePrettyDerby.exe) not found. Please run the game first before running this program!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def restore_patch():
    global pm, original_bytes, patch_address
    if pm and original_bytes and patch_address:
        try:
            pm.write_bytes(patch_address, original_bytes, len(original_bytes))
            print("Original bytes restored.")
        except Exception as e:
            print(f"Could not restore original bytes: {e}")

# Register the restore function to be called on exit
atexit.register(restore_patch)

# Create the main window

def open_web():
    webbrowser.open_new("https://del4yowo.id.vn/")

root = tk.Tk()
root.title("Umamusume FPS Unlocker")

# Create and place the widgets

frame = tk.Frame(root, padx=100, pady=100)
frame.pack()

label = tk.Label(frame, text="Enter desired FPS:")
label.pack(pady=5)

label = tk.Label(text="With 🩷 by HighDel4y", fg="purple", cursor="hand2")
label.bind("<Button-1>", lambda e: open_web())
label.pack(pady=10)

fps_entry = tk.Entry(frame)
fps_entry.pack(pady=5)
fps_entry.insert(0, "120")

set_button = tk.Button(frame, text="Set FPS & Apply Patch", command=apply_patch)
set_button.pack(pady=10)

# Start the GUI event loop
root.mainloop()
