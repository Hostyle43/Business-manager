# business_manager.py
# Enhanced with Equipment class, GUI integration, and full persistence

import tkinter as tk
from tkinter import messagebox, ttk  # ttk for better widgets like Treeview
import sys
import json  # For JSON persistence
import os    # For file checks
from datetime import datetime, timedelta  # For date handling in Project

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

# Employee class
class Employee:
    def __init__(self, name, role, hourly_rate):
        self.name = name
        self.role = role
        self.hourly_rate = hourly_rate
        self.hours_worked = 0
        # Note: 'availability' not yet implemented; add later if needed (e.g., self.availability = {})

    def to_dict(self):
        return {
            'name': self.name,
            'role': self.role,
            'hourly_rate': self.hourly_rate,
            'hours_worked': self.hours_worked
            # Add 'availability': self.availability if implemented
        }

    @classmethod
    def from_dict(cls, data):
        emp = cls(data['name'], data['role'], data['hourly_rate'])
        emp.hours_worked = data.get('hours_worked', 0)
        # If adding availability: emp.availability = data.get('availability', {})
        return emp

    def __str__(self):
        return f"Employee: {self.name} ({self.role}), Rate: ${self.hourly_rate}/hr"

# Project class
class Project:
    def __init__(self, name, description, estimated_hours, start_date, status='Pending'):
        self.name = name
        self.description = description  # Added based on __str__
        self.estimated_hours = estimated_hours
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.progress = 0  # 0-100%
        self.schedule = {}  # For generated schedule
        self.status = status  # Added based on __str__
        self.employees = []   # List for assigned employees
        self.equipment = []   # List for assigned equipment

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'estimated_hours': self.estimated_hours,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'progress': self.progress,
            'schedule': self.schedule,
            'status': self.status,
            'employees': [e.to_dict() for e in self.employees],  # Nested serialization
            'equipment': [eq.to_dict() for eq in self.equipment]
        }

    @classmethod
    def from_dict(cls, data):
        proj = cls(
            data['name'],
            data.get('description', ''),
            data['estimated_hours'],
            data['start_date'],
            data.get('status', 'Pending')
        )
        proj.progress = data.get('progress', 0)
        proj.schedule = data.get('schedule', {})
        proj.employees = [Employee.from_dict(e) for e in data.get('employees', [])]
        proj.equipment = [Equipment.from_dict(eq) for eq in data.get('equipment', [])]
        return proj

    def update_progress(self, new_progress):
        self.progress = new_progress
        # Trigger schedule update if needed

    def generate_schedule(self, manager):
        """Semi-automated schedule generation."""
        schedule = {}
        remaining_hours = self.estimated_hours * (1 - self.progress / 100)
        predicted_end = self.start_date + timedelta(hours=remaining_hours)  # Basic prediction

        # Pull employee availability (placeholder; assumes 'availability' dict on Employee)
        # If not implemented, use all employees for now
        available_employees = manager.employees  # Fallback; update when availability is added
        # available_employees = [e for e in manager.employees if any(avail for date, avail in e.availability.items() if avail)]

        # Simple automation: Assign to first 7 days, suggest employees
        current_date = self.start_date
        for day in range(7):  # Basic: Schedule first week
            date_str = current_date.strftime('%Y-%m-%d')
            assigned = [e.name for e in available_employees[:2]]  # Assign top 2
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

# Equipment class
class Equipment:
    def __init__(self, name, type_, travel_speed=0.0, bucket_volume=0.0, hourly_cost=0.0):
        self.name = name
        self.type = type_  # e.g., "Excavator", "Truck"
        self.travel_speed = travel_speed
        self.bucket_volume = bucket_volume
        self.hourly_cost = hourly_cost

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'travel_speed': self.travel_speed,
            'bucket_volume': self.bucket_volume,
            'hourly_cost': self.hourly_cost
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['name'],
            data['type'],
            data.get('travel_speed', 0.0),
            data.get('bucket_volume', 0.0),
            data.get('hourly_cost', 0.0)
        )

    def __str__(self):
        return (f"Equipment: {self.name} ({self.type}), Speed: {self.travel_speed} mph, "
                f"Bucket Vol: {self.bucket_volume} cu yd, Cost: ${self.hourly_cost}/hr")

# GUI Functions
def add_employee_gui(manager):
    def submit():
        name = name_entry.get()
        role = role_entry.get()
        try:
            rate = float(rate_entry.get())
            emp = Employee(name, role, rate)
            manager.employees.append(emp)
            messagebox.showinfo("Success", f"Added: {emp}")
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input.")

    window = tk.Tk()
    window.title("Add Employee")

    tk.Label(window, text="Name:").pack()
    name_entry = tk.Entry(window)
    name_entry.pack()

    tk.Label(window, text="Role:").pack()
    role_entry = tk.Entry(window)
    role_entry.pack()

    tk.Label(window, text="Hourly Rate:").pack()
    rate_entry = tk.Entry(window)
    rate_entry.pack()

    tk.Button(window, text="Submit", command=submit).pack()
    window.mainloop()

def add_equipment_gui(manager):
    def submit():
        name = name_entry.get()
        type_ = type_entry.get()
        try:
            speed = float(speed_entry.get())
            volume = float(volume_entry.get())
            cost = float(cost_entry.get())
            eq = Equipment(name, type_, speed, volume, cost)
            manager.equipment.append(eq)
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

def view_equipment_gui(manager):
    if not manager.equipment:
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

    for eq in manager.equipment:
        tree.insert("", "end", values=(eq.name, eq.type, eq.travel_speed, eq.bucket_volume, eq.hourly_cost))

    tree.pack()
    window.mainloop()

def create_project_gui(manager):
    def submit():
        name = name_entry.get()
        desc = desc_entry.get()
        try:
            hours = float(hours_entry.get())
            start = start_entry.get()  # e.g., '2026-01-25'
            proj = Project(name, desc, hours, start)
            manager.projects.append(proj)
            messagebox.showinfo("Success", f"Added: {proj}")
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input (check numbers/date format).")

    window = tk.Tk()
    window.title("Create Project")

    tk.Label(window, text="Name:").pack()
    name_entry = tk.Entry(window)
    name_entry.pack()

    tk.Label(window, text="Description:").pack()
    desc_entry = tk.Entry(window)
    desc_entry.pack()

    tk.Label(window, text="Estimated Hours:").pack()
    hours_entry = tk.Entry(window)
    hours_entry.pack()

    tk.Label(window, text="Start Date (YYYY-MM-DD):").pack()
    start_entry = tk.Entry(window)
    start_entry.pack()

    tk.Button(window, text="Submit", command=submit).pack()
    window.mainloop()

def main_gui():
    manager = BusinessManager()  # Create instance here (loads data automatically)

    root = tk.Tk()
    root.title("Business Manager")

    tk.Button(root, text="Add Employee", command=lambda: add_employee_gui(manager)).pack(pady=10)
    tk.Button(root, text="Add Equipment", command=lambda: add_equipment_gui(manager)).pack(pady=10)
    tk.Button(root, text="View Equipment", command=lambda: view_equipment_gui(manager)).pack(pady=10)
    tk.Button(root, text="Create Project", command=lambda: create_project_gui(manager)).pack(pady=10)
    tk.Button(root, text="View Employees", command=lambda: messagebox.showinfo("Employees", "\n".join(str(e) for e in manager.employees))).pack(pady=10)
    tk.Button(root, text="Save Data", command=manager.save_data).pack(pady=10)  # New: Save button
    tk.Button(root, text="Exit", command=sys.exit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
