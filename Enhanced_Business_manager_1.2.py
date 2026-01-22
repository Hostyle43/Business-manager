# business_manager.py
# Enhanced with employee availability, scheduling GUI, and work library

import tkinter as tk
from tkinter import messagebox, ttk  # ttk for better widgets like Treeview
import sys
import json  # For JSON persistence
import os    # For file checks
from datetime import datetime, timedelta  # For date handling
import random  # For demo: Randomly assign work codes to tasks

class BusinessManager:
    def __init__(self, data_file='app_data.json'):
        self.data_file = data_file
        self.employees = []  # List of Employee objects
        self.equipment = []  # List of Equipment objects
        self.projects = []   # List of Project objects
        self.work_library = {}  # New: Dict of job_code: description
        self.load_data()     # Load on init

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.employees = [Employee.from_dict(e) for e in data.get('employees', [])]
                self.equipment = [Equipment.from_dict(eq) for eq in data.get('equipment', [])]
                self.projects = [Project.from_dict(p) for p in data.get('projects', [])]
                self.work_library = data.get('work_library', {})
            print("Data loaded successfully.")
        else:
            print("No data file found; starting fresh.")

    def save_data(self):
        data = {
            'employees': [e.to_dict() for e in self.employees],
            'equipment': [eq.to_dict() for eq in self.equipment],
            'projects': [p.to_dict() for p in self.projects],
            'work_library': self.work_library
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved successfully.")

    def add_work_item(self, code, description):
        self.work_library[code] = description

# Employee class (with availability added)
class Employee:
    def __init__(self, name, role, hourly_rate, availability=None):
        self.name = name
        self.role = role
        self.hourly_rate = hourly_rate
        self.hours_worked = 0
        self.availability = availability or {}  # e.g., {'2026-01-25': True}

    def to_dict(self):
        return {
            'name': self.name,
            'role': self.role,
            'hourly_rate': self.hourly_rate,
            'hours_worked': self.hours_worked,
            'availability': self.availability
        }

    @classmethod
    def from_dict(cls, data):
        emp = cls(data['name'], data['role'], data['hourly_rate'], data.get('availability', {}))
        emp.hours_worked = data.get('hours_worked', 0)
        return emp

    def __str__(self):
        return f"Employee: {self.name} ({self.role}), Rate: ${self.hourly_rate}/hr"

# Project class (enhanced scheduling with availability and work codes)
class Project:
    def __init__(self, name, description, estimated_hours, start_date, status='Pending'):
        self.name = name
        self.description = description
        self.estimated_hours = estimated_hours
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.progress = 0
        self.schedule = {}
        self.status = status
        self.employees = []
        self.equipment = []

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'estimated_hours': self.estimated_hours,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'progress': self.progress,
            'schedule': self.schedule,
            'status': self.status,
            'employees': [e.to_dict() for e in self.employees],
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

    def generate_schedule(self, manager):
        schedule = {}
        remaining_hours = self.estimated_hours * (1 - self.progress / 100)
        current_date = self.start_date

        # Get work codes for auto-populating tasks
        work_codes = list(manager.work_library.keys())

        for day in range(7):  # Weekly schedule
            date_str = current_date.strftime('%Y-%m-%d')

            # Filter available employees for this date
            available_employees = [e for e in manager.employees if e.availability.get(date_str, False)]
            assigned = [e.name for e in available_employees[:2]] or ['No one available']

            # Auto-populate task with a random work code/description (for demo; customize later)
            task_code = random.choice(work_codes) if work_codes else 'TASK-001'
            task_desc = manager.work_library.get(task_code, 'General tasks') + f' (estimated {remaining_hours / 7:.2f} hours)'

            schedule[date_str] = {
                'tasks': task_desc,
                'assigned_employees': assigned,
                'completed': False  # For future timecard integration
            }
            current_date += timedelta(days=1)

        self.schedule = schedule
        return schedule

    def add_employee(self, employee):
        self.employees.append(employee)

    def add_equipment(self, equipment):
        self.equipment.append(equipment)

    def __str__(self):
        return f"Project: {self.name} - {self.description} (Status: {self.status})"

# Equipment class (unchanged)
class Equipment:
    def __init__(self, name, type_, travel_speed=0.0, bucket_volume=0.0, hourly_cost=0.0):
        self.name = name
        self.type = type_
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
            # Parse availability (e.g., input as "2026-01-25:True,2026-01-26:False")
            avail_str = avail_entry.get()
            availability = {}
            if avail_str:
                pairs = avail_str.split(',')
                for pair in pairs:
                    date, avail = pair.split(':')
                    availability[date.strip()] = avail.strip().lower() == 'true'
            emp = Employee(name, role, rate, availability)
            manager.employees.append(emp)
            messagebox.showinfo("Success", f"Added: {emp}")
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")

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

    tk.Label(window, text="Availability (e.g., 2026-01-25:True,2026-01-26:False):").pack()
    avail_entry = tk.Entry(window)
    avail_entry.pack()

    tk.Button(window, text="Submit", command=submit).pack()
    window.mainloop()

def add_equipment_gui(manager):
    # (Unchanged from previous; omitted for brevity)
    pass  # Replace with your existing code

def view_equipment_gui(manager):
    # (Unchanged; omitted for brevity)
    pass

def create_project_gui(manager):
    def submit():
        name = name_entry.get()
        desc = desc_entry.get()
        try:
            hours = float(hours_entry.get())
            start = start_entry.get()
            proj = Project(name, desc, hours, start)
            manager.projects.append(proj)
            proj.generate_schedule(manager)  # Auto-generate on creation
            messagebox.showinfo("Success", f"Added: {proj} (Schedule generated)")
            window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")

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

def add_work_item_gui(manager):
    def submit():
        code = code_entry.get()
        desc = desc_entry.get()
        if code and desc:
            manager.add_work_item(code, desc)
            messagebox.showinfo("Success", f"Added: {code} - {desc}")
            window.destroy()
        else:
            messagebox.showerror("Error", "Fill in both fields.")

    window = tk.Tk()
    window.title("Add Work Item")

    tk.Label(window, text="Job Code (e.g., EXC-001):").pack()
    code_entry = tk.Entry(window)
    code_entry.pack()

    tk.Label(window, text="Description:").pack()
    desc_entry = tk.Entry(window)
    desc_entry.pack()

    tk.Button(window, text="Submit", command=submit).pack()
    window.mainloop()

def view_projects_schedules_gui(manager):
    if not manager.projects:
        messagebox.showinfo("Projects", "No projects yet.")
        return

    window = tk.Tk()
    window.title("View Projects & Schedules")

    # List of projects
    proj_list = ttk.Treeview(window, columns=("Name",), show="headings")
    proj_list.heading("Name", text="Project Name")
    for proj in manager.projects:
        proj_list.insert("", "end", values=(proj.name,))
    proj_list.pack()

    def show_schedule(event):
        selected = proj_list.selection()
        if selected:
            proj_name = proj_list.item(selected[0])['values'][0]
            proj = next(p for p in manager.projects if p.name == proj_name)
            if not proj.schedule:
                proj.generate_schedule(manager)

            # Weekly calendar grid
            cal_window = tk.Toplevel()
            cal_window.title(f"Schedule for {proj.name} (Weekly View)")

            days = list(proj.schedule.keys())
            for i, date in enumerate(days):
                day_data = proj.schedule[date]
                summary = f"{date}\nTasks: {day_data['tasks'][:20]}...\nAssigned: {', '.join(day_data['assigned_employees'])}"

                btn = tk.Button(cal_window, text=summary, command=lambda d=date: show_day_detail(proj, d))
                btn.grid(row=0, column=i, padx=5, pady=5)

    proj_list.bind("<<TreeviewSelect>>", show_schedule)
    window.mainloop()

def show_day_detail(proj, date):
    day_data = proj.schedule.get(date, {})
    detail_window = tk.Toplevel()
    detail_window.title(f"Details for {date}")

    tk.Label(detail_window, text=f"Tasks: {day_data.get('tasks', 'N/A')}").pack()
    tk.Label(detail_window, text=f"Assigned: {', '.join(day_data.get('assigned_employees', []))}").pack()
    tk.Label(detail_window, text=f"Completed: {day_data.get('completed', False)}").pack()
    # Future: Add checkboxes for task completion, edit buttons for mobile-like functionality

    # Placeholder for timecard preview
    tk.Button(detail_window, text="Mark Completed (Simulate Timecard)", command=lambda: mark_completed(proj, date)).pack()

def mark_completed(proj, date):
    if date in proj.schedule:
        proj.schedule[date]['completed'] = True
        messagebox.showinfo("Updated", f"Marked {date} as completed. (In mobile: This would populate timecard.)")

def main_gui():
    manager = BusinessManager()

    root = tk.Tk()
    root.title("Business Manager")

    tk.Button(root, text="Add Employee", command=lambda: add_employee_gui(manager)).pack(pady=10)
    tk.Button(root, text="Add Equipment", command=lambda: add_equipment_gui(manager)).pack(pady=10)
    tk.Button(root, text="View Equipment", command=lambda: view_equipment_gui(manager)).pack(pady=10)
    tk.Button(root, text="Create Project", command=lambda: create_project_gui(manager)).pack(pady=10)
    tk.Button(root, text="Add Work Item", command=lambda: add_work_item_gui(manager)).pack(pady=10)
    tk.Button(root, text="View Projects & Schedules", command=lambda: view_projects_schedules_gui(manager)).pack(pady=10)
    tk.Button(root, text="View Employees", command=lambda: messagebox.showinfo("Employees", "\n".join(str(e) for e in manager.employees))).pack(pady=10)
    tk.Button(root, text="Save Data", command=manager.save_data).pack(pady=10)
    tk.Button(root, text="Exit", command=sys.exit).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
