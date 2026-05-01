print("FILE LOADED")

try:
    print("Trying import...")
    from parking_lot import park_vehicle, remove_parked_vehicle
    print("Imported parking_lot successfully")
except Exception as e:
    print("Error importing parking_lot:", e)

print("MAIN GUI STARTED")

import tkinter as tk
from tkinter import messagebox

def park_action():
    try:
        vehicle_number = entry_number.get()
        vehicle_type = entry_type.get()
        slot_number = entry_slot.get()
        vehicle_id = park_vehicle(vehicle_number, vehicle_type, slot_number)
        if vehicle_id:
            messagebox.showinfo("Success", f"Vehicle parked. ID: {vehicle_id}")
    except Exception as e:
        print("Error in park_action:", e)

def remove_action():
    try:
        vehicle_id = int(entry_remove.get())
        hours = int(entry_hours.get())
        remove_parked_vehicle(vehicle_id, hours)
        messagebox.showinfo("Removed", f"Vehicle {vehicle_id} removed.")
    except Exception as e:
        print("Error in remove_action:", e)

root = tk.Tk()
root.title("Parking Lot Management")

# Park vehicle
tk.Label(root, text="Vehicle Number:").grid(row=0, column=0)
entry_number = tk.Entry(root)
entry_number.grid(row=0, column=1)

tk.Label(root, text="Vehicle Type:").grid(row=1, column=0)
entry_type = tk.Entry(root)
entry_type.grid(row=1, column=1)

tk.Label(root, text="Slot Number:").grid(row=2, column=0)
entry_slot = tk.Entry(root)
entry_slot.grid(row=2, column=1)

tk.Button(root, text="Park Vehicle", command=park_action).grid(row=3, column=0, columnspan=2)

# Remove vehicle
tk.Label(root, text="Vehicle ID to remove:").grid(row=4, column=0)
entry_remove = tk.Entry(root)
entry_remove.grid(row=4, column=1)

tk.Label(root, text="Hours Parked:").grid(row=5, column=0)
entry_hours = tk.Entry(root)
entry_hours.grid(row=5, column=1)

tk.Button(root, text="Remove Vehicle", command=remove_action).grid(row=6, column=0, columnspan=2)

print("Starting mainloop...")
root.mainloop()

