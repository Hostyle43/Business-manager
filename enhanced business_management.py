# business_manager.py (suggested rename from file.py)
# Enhanced with Equipment class and GUI integration

import tkinter as tk
from tkinter import messagebox, ttk  # ttk for better widgets like dropdowns
import sys

# Existing classes (assuming from before; adjust as needed)
class Employee:
    def __init__(self, name, role, hourly_rate):
        self.name = name
        self.role = role
        self.hourly_rate = hourly_rate
        self.hours_worked = 0

    def __str__(self):
        return f"Employee: {self.name} ({self.role}), Rate: ${self.hourly_rate}/hr"

class Project:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.employees = []
        self.equipment = []  # New: Link equipment to projects later
        self.expenses = 0.0
        self.status = "Estimate"

    def add_employee(self, employee):
        self.employees.append(employee)

    def add_equipment(self, equipment):
        self.equipment.append(equipment)

    def __str__(self):
        return f"Project: {self.name} - {self.description} (Status: {self.status})"

# New: Equipment class for company profile
class Equipment:
    def __init__(self, name, type_, travel_speed=0.0, bucket_volume=0.0, hourly_cost=0.0):
        self.name = name
        self.type = type_  # e.g., "Excavator", "Truck"
        self.travel_speed = travel_speed  # in mph or km/h
        self.bucket_volume = bucket_volume  # in cubic yards/meters
        self.hourly_cost = hourly_cost  # for expense tracking

    def __str__(self):
        return (f"Equipment: {self.name} ({self.type}), Speed: {self.travel_speed} mph, "
                f"Bucket Vol: {self.bucket_volume} cu yd, Cost: ${self.hourly_cost}/hr")

# Global data (we'll add saving to files next)
employees = []
projects = []
equipment_list = []  # Company-wide equipment inventory

# GUI Functions
def add_equipment_gui():
    def submit():
        name = name_entry.get()
        type_ = type_entry.get()
        try:
            speed = float(speed_entry.get())
            volume = float(volume_entry.get())
            cost = float(cost_entry.get())
            eq = Equipment(name, type_, speed, volume, cost)
            equipment_list.append(eq)
            messagebox.showinfo("Success", f"Added: {eq}")
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input.")

    window = tk.Tk()
    window.title("Add Equipment")

    tk.Label(window, text="Name:").pack()
    name_entry = tk.Entry(window)
    name_entry.pack()

    tk.Label(window, text="Type (e.g., Excavator):").pack()
    type_entry = tk.Entry(window)
    type_entry.pack()

    tk.Label(window, text="Travel Speed (mph):").pack()
    speed_entry = tk.Entry(window)
    speed_entry.pack()

    tk.Label(window, text="Bucket Volume (cu yd):").pack()
    volume_entry = tk.Entry(window)
    volume_entry.pack()

    tk.Label(window, text="Hourly Cost:").pack()
    cost_entry = tk.Entry(window)
    cost_entry.pack()

    tk.Button(window, text="Submit", command=submit).pack()
    window.mainloop()

def view_equipment_gui():
    if not equipment_list:
        messagebox.showinfo("Equipment List", "No equipment added yet.")
        return

    window = tk.Tk()
    window.title("View Equipment")

    tree = ttk.Treeview(window, columns=("Name", "Type", "Speed", "Volume", "Cost"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Type", text="Type")
    tree.heading("Speed", text="Speed (mph)")
    tree.heading("Volume", text="Volume (cu yd)")
    tree.heading("Cost", text="Cost ($/hr)")

    for eq in equipment_list:
        tree.insert("", "end", values=(eq.name, eq.type, eq.travel_speed, eq.bucket_volume, eq.hourly_cost))

    tree.pack()
    window.mainloop()

# Existing add_employee_gui() function here (from previous example)

def main_gui():
    root = tk.Tk()
    root.title("Business Manager")

    tk.Button(root, text="Add Employee", command=add_employee_gui).pack(pady=10)  # Assuming you have this
    tk.Button(root, text="Add Equipment", command=add_equipment_gui).pack(pady=10)
    tk.Button(root, text="View Equipment", command=view_equipment_gui).pack(pady=10)
    tk.Button(root, text="Create Project", command=lambda: messagebox.showinfo("Info", "Project creation coming soon!")).pack(pady=10)
    tk.Button(root, text="View Employees", command=lambda: messagebox.showinfo("Employees", "\n".join(str(e) for e in employees))).pack(pady=10)
    tk.Button(root, text="Exit", command=sys.exit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
