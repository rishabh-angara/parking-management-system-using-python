import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime

# ==========================
# Database Connection Function
# ==========================
import os
from dotenv import load_dotenv
import mysql.connector

# Load variables from .env file
load_dotenv()

def connect_db():
    """Connect using credentials from .env file"""
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PWD"),
        database=os.getenv("MYSQL_DB")
    )


# ==========================
# Feature 1: Add Vehicle (Park)
# ==========================
def add_vehicle():
    """
    Park a vehicle by inserting a new record into the database.
    Checks if the slot is already occupied before parking.
    """
    vehicle_no = entry_vehicle.get()
    owner = entry_owner.get()
    slot = entry_slot.get()

    # Validate input fields
    if not vehicle_no or not owner or not slot:
        messagebox.showwarning("Input Error", "All fields are required")
        return

    conn = connect_db()
    cursor = conn.cursor()

    # Check if the chosen slot is already occupied
    cursor.execute("SELECT * FROM parking_slots WHERE slot_number=%s AND status='Parked'", (slot,))
    slot_check = cursor.fetchone()

    if slot_check:
        messagebox.showerror("Slot Occupied", f"Slot {slot} is already taken")
        conn.close()
        return

    # Insert the new vehicle into DB
    try:
        cursor.execute("INSERT INTO parking_slots (vehicle_number, owner_name, slot_number) VALUES (%s, %s, %s)",
                       (vehicle_no, owner, slot))
        conn.commit()
        messagebox.showinfo("Success", f"Vehicle {vehicle_no} parked at slot {slot}")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        conn.close()

# ==========================
# Feature 2: Exit Vehicle + Fee Calculation
# ==========================
def exit_vehicle():
    """
    Exit a parked vehicle, update its exit time, and calculate the fee.
    Fee is calculated as ₹20 per hour, minimum 1 hour.
    """
    vehicle_no = entry_vehicle.get()

    # Validate input
    if not vehicle_no:
        messagebox.showwarning("Input Error", "Enter Vehicle Number to exit")
        return

    conn = connect_db()
    cursor = conn.cursor()

    # Fetch entry time from DB
    cursor.execute("SELECT entry_time FROM parking_slots WHERE vehicle_number=%s AND status='Parked'", (vehicle_no,))
    record = cursor.fetchone()

    if not record:
        messagebox.showwarning("Not Found", f"No active parking found for {vehicle_no}")
        conn.close()
        return

    entry_time = record[0]
    exit_time = datetime.now()

    # Calculate hours and fee (minimum 1 hour)
    parked_hours = (exit_time - entry_time).seconds // 3600 + 1
    fee = parked_hours * 20  # Fee rate ₹20 per hour

    # Update the record with exit time and status
    cursor.execute("UPDATE parking_slots SET exit_time=%s, status=%s WHERE vehicle_number=%s AND status='Parked'",
                   (exit_time, 'Exited', vehicle_no))
    conn.commit()

    # Display fee details
    messagebox.showinfo("Vehicle Exited", f"Vehicle {vehicle_no} exited.\nParked Hours: {parked_hours}\nFee: ₹{fee}")

    conn.close()

# ==========================
# Feature 3: Search Vehicle
# ==========================
def search_vehicle():
    """
    Search for a vehicle by its number and show details.
    """
    vehicle_no = entry_vehicle.get()

    # Validate input
    if not vehicle_no:
        messagebox.showwarning("Input Error", "Enter Vehicle Number to search")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM parking_slots WHERE vehicle_number=%s", (vehicle_no,))
    record = cursor.fetchone()
    conn.close()

    # Show vehicle details if found
    if record:
        status = record[6]  # Status column
        messagebox.showinfo("Search Result",
                            f"Vehicle: {record[1]}\nOwner: {record[2]}\nSlot: {record[3]}\nStatus: {status}")
    else:
        messagebox.showinfo("Search Result", "Vehicle not found")

# ==========================
# Feature 4: Check Slot Availability
# ==========================
def check_availability():
    """
    Display available parking slots (example: total 10 slots).
    """
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT slot_number FROM parking_slots WHERE status='Parked'")
    occupied = [row[0] for row in cursor.fetchall()]
    conn.close()

    all_slots = list(range(1, 11))  # Assuming 10 total slots
    available = [s for s in all_slots if s not in occupied]

    messagebox.showinfo("Slot Availability", f"Available Slots: {available}")

# ==========================
# GUI Setup with Tkinter
# ==========================
root = tk.Tk()
root.title("Parking Management System")
root.geometry("500x400")

# Labels and input fields
tk.Label(root, text="Vehicle Number").pack()
entry_vehicle = tk.Entry(root)
entry_vehicle.pack()

tk.Label(root, text="Owner Name").pack()
entry_owner = tk.Entry(root)
entry_owner.pack()

tk.Label(root, text="Slot Number").pack()
entry_slot = tk.Entry(root)
entry_slot.pack()

# Buttons for features
tk.Button(root, text="Park Vehicle", command=add_vehicle).pack(pady=5)
tk.Button(root, text="Exit Vehicle", command=exit_vehicle).pack(pady=5)
tk.Button(root, text="Search Vehicle", command=search_vehicle).pack(pady=5)
tk.Button(root, text="Check Slot Availability", command=check_availability).pack(pady=5)

# Run the Tkinter main loop
root.mainloop()
