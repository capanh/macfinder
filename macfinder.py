import tkinter as tk
from tkinter import ttk,messagebox
import requests
import re

api_key = "b252e856f1b276399e79e7fc907ee05ede716f74"
org_id = "187186"
BASE_URL = 'https://dashboard.meraki.com'

def safe_request(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to fetch data: {e}")
        return None

def get_meraki_networks(api_key, organization_id):
    url = f"https://api.meraki.com/api/v1/organizations/{organization_id}/networks"
    headers = {
        'Accept': 'application/json',
        'X-Cisco-Meraki-API-Key': api_key
    }
    return safe_request(url, headers)

def get_meraki_client_info(api_key, network_id, client_mac):
    url = f"https://api.meraki.com/api/v1/networks/{network_id}/clients?mac={client_mac}"
    headers = {
        'Accept': 'application/json',
        'X-Cisco-Meraki-API-Key': api_key
    }
    return safe_request(url, headers)

def check_connectivity():
    # Simplified connectivity check to just Meraki API
    try:
        response = requests.get("https://api.meraki.com/api/v1", timeout=5)
        status_label.config(image=connected_icon)
    except requests.RequestException:
        status_label.config(image=disconnected_icon)
    root.after(30000, check_connectivity)  # Check every 30 seconds

def validate_mac_address(action, mac_address):
    if action == '1':  # Insert
        if not re.match(r'^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$', mac_address):
            return False
    return True


def get_network_name_by_id(networks, network_id):
    # Iterate through the networks list to find the matching network name
    for network in networks:
        if network['id'] == network_id:
            return network['name']
    return None

def search_mac():
    mac_address = entry_mac.get().lower()
    if not validate_mac_address('1', mac_address):
        messagebox.showerror("Error", "Invalid MAC address format!")
        return
    
    networks = get_meraki_networks(api_key, org_id)
    if not networks:
        output_field.insert(tk.END, "Failed to fetch networks.\n")
        return

    output_field.config(state=tk.NORMAL)
    output_field.delete(1.0, tk.END)
    output_field.insert(tk.END, f"Searching for MAC address: {mac_address}\n")
    output_field.insert(tk.END, "Loading...\n")
    output_field.update_idletasks()  # Update GUI to show loading message

    for network in networks:
        network_id = network['id']
        client_info = get_meraki_client_info(api_key, network_id, mac_address)
        if client_info:
            output_message = f"Found in network {network_id}: {client_info}\n"
            network_name = get_network_name_by_id(networks,network['id'])
            clickable_output_message = f"Found in network {network_id} \n Network name:{network_name} \n Link:"
        else:
            output_message = f"Not found in network {network_id}.\n"
        
        output_field.insert(tk.END, output_message)
        
        output_field.update_idletasks()  # Update GUI for each iteration
    
    clickable_output_field.insert(tk.END,clickable_output_message)
    output_field.config(state=tk.DISABLED)

def reset():
    entry_mac.delete(0, tk.END)
    output_field.config(state=tk.NORMAL)
    output_field.delete(1.0, tk.END)
    output_field.config(state=tk.DISABLED)
    clickable_output_field.config(state=tk.NORMAL)
    clickable_output_field.delete(1.0, tk.END)
    clickable_output_field.config(state=tk.DISABLED)
    
root = tk.Tk()
root.title("Meraki Dashboard - MAC Address Search")
root.geometry("800x700")  # Set the window size

# Load icons
# Note: Update these paths to your actual icon files
connected_icon = tk.PhotoImage(file="green_light.png").subsample(3)
disconnected_icon = tk.PhotoImage(file="red_light.png").subsample(3)

# Create and place widgets
frame = ttk.Frame(root, padding="20")
frame.place(x=0, y=0, width=700, height=500)

connectivity_status = ttk.Label(frame, text="Meraki API Connectivity:")
connectivity_status.place(x=5, y=5, width=200, height=30)

status_label = ttk.Label(frame, width=30)
status_label.place(x=210, y=5, width=200, height=30)

label_mac = ttk.Label(frame, text="Enter MAC Address:")
label_mac.place(x=5, y=35, width=200, height=30)

entry_mac = ttk.Entry(frame, width=30,)
entry_mac.place(x=210, y=35, width=200, height=30)
entry_mac['validatecommand'] = (entry_mac.register(validate_mac_address), '%d', '%P')

button_search = ttk.Button(frame, text="Search", command=search_mac)
button_search.place(x=5, y=65, width=100, height=35)

button_reset = ttk.Button(frame, text="Reset", command=reset)  # Add reset button
button_reset.place(x=110, y=65, width=100, height=35)

output_label = ttk.Label(frame, text="Progress:")
output_label.place(x=5, y=95, width=200, height=30)

output_frame = ttk.Frame(frame)
output_frame.place(x=5, y=125, width=350, height=350)

output_label = ttk.Label(frame, text="Output:")
output_label.place(x=375, y=95, width=200, height=30)

clickable_output_frame = ttk.Frame(frame)
clickable_output_frame.place(x=375,y=125,width=300,height=100)

output_field = tk.Text(output_frame, wrap=tk.WORD, height=5, width=100)
output_field.pack(expand=True, fill=tk.BOTH)

clickable_output_field = tk.Text(clickable_output_frame, height=5, width=200,bg='grey')
clickable_output_field.pack(expand=True, fill=tk.BOTH)

# Check connectivity initially and schedule periodic checks
check_connectivity()

root.mainloop()