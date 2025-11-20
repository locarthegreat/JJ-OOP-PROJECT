import ipaddress
import tkinter as tk
from tkinter import messagebox

def calculate_subnet():
    ip_input = ip_entry.get()
    subnet_input = subnet_entry.get()

    try:
        # Combine IP and subnet mask
        network = ipaddress.IPv4Network(f"{ip_input}/{subnet_input}", strict=False)
        
        network_address_var.set(str(network.network_address))
        broadcast_address_var.set(str(network.broadcast_address))
        total_hosts_var.set(str(network.num_addresses - 2 if network.num_addresses > 2 else network.num_addresses))
        first_host_var.set(str(list(network.hosts())[0]) if network.num_addresses > 2 else 'N/A')
        last_host_var.set(str(list(network.hosts())[-1]) if network.num_addresses > 2 else 'N/A')
        
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

# GUI setup
root = tk.Tk()
root.title("Subnet Calculator")
root.geometry("400x400")

tk.Label(root, text="IP Address").pack(pady=5)
ip_entry = tk.Entry(root)
ip_entry.pack()

tk.Label(root, text="Subnet Mask or Prefix (e.g., 255.255.255.0 or 24)").pack(pady=5)
subnet_entry = tk.Entry(root)
subnet_entry.pack()

tk.Button(root, text="Calculate", command=calculate_subnet).pack(pady=20)

# Output fields
network_address_var = tk.StringVar()
broadcast_address_var = tk.StringVar()
total_hosts_var = tk.StringVar()
first_host_var = tk.StringVar()
last_host_var = tk.StringVar()

tk.Label(root, text="Network Address:").pack()
tk.Label(root, textvariable=network_address_var).pack()

tk.Label(root, text="Broadcast Address:").pack()
tk.Label(root, textvariable=broadcast_address_var).pack()

tk.Label(root, text="Total Hosts:").pack()
tk.Label(root, textvariable=total_hosts_var).pack()

tk.Label(root, text="First Host:").pack()
tk.Label(root, textvariable=first_host_var).pack()

tk.Label(root, text="Last Host:").pack()
tk.Label(root, textvariable=last_host_var).pack()

root.mainloop()
