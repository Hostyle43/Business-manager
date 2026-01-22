# business_manager.py (suggested rename from file.py)
# Enhanced with Equipment class and GUI integration

import tkinter as tk
from tkinter import messagebox, ttk  # ttk for better widgets like dropdowns
import sys
import json  # For JSON persistence
import os    # For file checks

class BusinessManager:
    def __init__(self, data_file='app_data.json'):
        self.data_file = data_file
        self.employees = []  # List of Employee objects
        self.equipment = []  # List of Equipment objects
        self.projects = []   # List of Project objects
        self.load_data()     # Load on init

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Assuming you have from_dict methods in your classes
                self.employees = [Employee.from_dict(e) for e in data.get('employees', [])]
                self.equipment = [Equipment.from_dict(eq) for eq in data.get('equipment', [])]
                self.projects = [Project.from_dict(p) for p in data.get('projects', [])]
            print("Data loaded successfully.")
        else:
            print("No data file found; starting fresh.")

    def save_data(self):
        data = {
            'employees': [e.to_dict() for e in self.employees],
            'equipment': [eq.to_dict() for eq in self.equipment],
            'projects': [p.to_dict() for p in self.projects]
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved successfully.")


# Existing classes (will add classes as needed)
class Employee:
    def __init__(self, name, role, hourly_rate):
        self.name = name
        self.role = role
        self.hourly_rate = hourly_rate
        self.hours_worked = 0

    def to_dict(self):
        # Converts the Employee object to a dict for JSON saving.
        # Include every attribute you want persisted—matches what you save in BusinessManager.
        return {
            'name': self.name,  # String, saves fine
            'role': self.role,  # String
            'availability': self.availability  # Dict of dates to booleans—JSON handles dicts naturally
        }
    def __str__(self):
        return f"Employee: {self.name} ({self.role}), Rate: ${self.hourly_rate}/hr"


    from datetime import datetime  # If not already imported
class Project:
    def __init__(self, name, estimated_hours, start_date):
        self.name = name
        self.estimated_hours = estimated_hours
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')  # e.g., '2026-01-25'
        self.progress = 0  # 0-100%
        self.schedule = {}  # e.g., {'2026-01-25': {'tasks': '...', 'assigned_employees': [...]}}
        # Assume access to manager.employees for availability
    def to_dict(self):
        return {
            'name': self.name,
            'estimated_hours': self.estimated_hours,  # Number (int/float)
            'start_date': self.start_date.strftime('%Y-%m-%d') if isinstance(self.start_date, datetime) else self.start_date,  # Convert datetime to string for JSON
            'progress': self.progress,  # Number (0-100)
            'schedule': self.schedule  # Dict—saves the entire semi-automated schedule
        }

    def update_progress(self, new_progress):
        self.progress = new_progress
        # Trigger schedule update if needed

    def generate_schedule(self, manager):
        """Semi-automated schedule generation."""
        schedule = {}
        remaining_hours = self.estimated_hours * (1 - self.progress / 100)
        predicted_end = self.start_date + timedelta(hours=remaining_hours)  # Basic prediction

        # Pull employee availability (assume Employee has 'availability' as dict {date: bool})
        available_employees = [e for e in manager.employees if any(avail for date, avail in e.availability.items() if avail)]

        # Simple automation: Assign to first 7 days, suggest employees
        current_date = self.start_date
        for day in range(7):  # Basic: Schedule first week
            date_str = current_date.strftime('%Y-%m-%d')
            assigned = [e.name for e in available_employees[:2]]  # Assign top 2 available
            schedule[date_str] = {
                'tasks': f'Day {day+1} tasks (estimated {remaining_hours / 7:.2f} hours)',
                'assigned_employees': assigned
            }
            current_date += timedelta(days=1)

        self.schedule = schedule
        return schedule  # For GUI display

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

    def to_dict(self):
        return {
            'name': self.name,
            'travel_speed': self.travel_speed,  # Number
            'hourly_cost': self.hourly_cost    # Number
            # Add more if you have them, e.g., 'bucket_volume': self.bucket_volume
        }


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
