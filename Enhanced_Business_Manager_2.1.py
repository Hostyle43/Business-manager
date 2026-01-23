# business_manager.py
# Enhanced with employee availability (via tkcalendar), scheduling GUI, work library, employee editing/deletion (edits in pop-up),
# sidebar + dynamic viewer GUI, and back navigation in viewer

import tkinter as tk
from tkinter import messagebox, ttk  # ttk for better widgets like Treeview
import sys
import json  # For JSON persistence
import os    # For file checks
from datetime import datetime, timedelta  # For date handling
import random  # For demo: Randomly assign work codes to tasks
from tkcalendar import Calendar  # For calendar widget (pip install tkcalendar)

class BusinessManager:
    def __init__(self, data_file='app_data.json'):
        self.data_file = data_file
        self.employees = []  # List of Employee objects
        self.equipment = []  # List of Equipment objects
        self.projects = []   # List of Project objects
        self.work_library = {}  # Dict of job_code: description
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
    def __init__(self, name, role, hourly_rate=0.0, hourly_cost=0.0, availability=None):
        self.name = name
        self.role = role
        self.hourly_rate = hourly_rate
        self.hourly_cost = hourly_cost
        self.hours_worked = 0
        self.availability = availability or {}  # e.g., {'2026-01-25': True}
        
    def to_dict(self):
        return {
            'name': self.name,
            'role': self.role,
            'hourly_rate': self.hourly_rate,
            'hours_worked': self.hours_worked,
            'availability': self.availability,
            'hourly_cost': self.hourly_cost,
        }

    @classmethod
    def from_dict(cls, data):
        emp = cls(data['name'], data['role'], data['hourly_rate'], data.get('availability', {}))
        emp.hours_worked = data.get('hours_worked', 0)
        return emp

    def __str__(self):
        return f"Employee: {self.name} ({self.role}), Rate: ${self.hourly_rate}/hr, Cost: ${self.hourly_cost}/hr"

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

# GUI Functions (views in content_frame, edits in pop-up Toplevel, with back navigation)
def clear_content(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def add_employee_gui(manager, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: add_employee_gui(manager, content_frame, nav_history))  # Push self to history

    def submit():
        name = name_entry.get()
        role = role_entry.get()
        try:
            rate = float(rate_entry.get())
            # Get selected dates from calendar and mark as available
            selected_dates = cal.selection_get() if cal.selection_get() else []  # tkcalendar allows multi-select? Wait, default is single; for multi, use list
            # Note: tkcalendar default is single select; for multi, we'll simulate with a list and button
            availability = {date.strftime('%Y-%m-%d'): True for date in selected_dates_list}
            emp = Employee(name, role, rate, availability)
            manager.employees.append(emp)
            messagebox.showinfo("Success", f"Added: {emp}")
            go_back(nav_history, content_frame)  # Back after submit
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")

    tk.Label(content_frame, text="Add Employee").pack()

    tk.Label(content_frame, text="Name:").pack()
    name_entry = tk.Entry(content_frame)
    name_entry.pack()

    tk.Label(content_frame, text="Role:").pack()
    role_entry = tk.Entry(content_frame)
    role_entry.pack()

    tk.Label(content_frame, text="Hourly Rate:").pack()
    rate_entry = tk.Entry(content_frame)
    rate_entry.pack()

    tk.Label(content_frame, text="Select Available Dates:").pack()
    cal = Calendar(content_frame, selectmode="day", date_pattern="y-mm-dd")
    cal.pack()

    # For multi-select simulation (tkcalendar doesn't support native multi, so use a list and button)
    selected_dates_list = []
    def add_date():
        date = cal.get_date()
        if date not in selected_dates_list:
            selected_dates_list.append(datetime.strptime(date, '%Y-%m-%d'))
            avail_label.config(text=f"Selected: {', '.join(d.strftime('%Y-%m-%d') for d in selected_dates_list)}")

    tk.Button(content_frame, text="Add Selected Date", command=add_date).pack()
    avail_label = tk.Label(content_frame, text="Selected: None")
    avail_label.pack()

    tk.Button(content_frame, text="Submit", command=submit).pack()

def edit_employee_gui(manager, emp_index, refresh_callback):
    emp = manager.employees[emp_index]

    window = tk.Toplevel()
    window.title("Edit Employee")

    def submit():
        emp.name = name_entry.get()
        emp.role = role_entry.get()
        try:
            emp.hourly_rate = float(rate_entry.get())
            # Update availability from selected dates
            emp.availability = {date.strftime('%Y-%m-%d'): True for date in selected_dates_list}
            messagebox.showinfo("Success", f"Updated: {emp}")
            window.destroy()
            refresh_callback()  # Refresh the viewer list after edit
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")

    tk.Label(window, text="Name:").pack()
    name_entry = tk.Entry(window)
    name_entry.insert(0, emp.name)
    name_entry.pack()

    tk.Label(window, text="Role:").pack()
    role_entry = tk.Entry(window)
    role_entry.insert(0, emp.role)
    role_entry.pack()

    tk.Label(window, text="Hourly Rate:").pack()
    rate_entry = tk.Entry(window)
    rate_entry.insert(0, str(emp.hourly_rate))
    rate_entry.pack()

    tk.Label(window, text="Select Available Dates (replaces existing):").pack()
    cal = Calendar(window, selectmode="day", date_pattern="y-mm-dd")
    cal.pack()

    selected_dates_list = [datetime.strptime(date, '%Y-%m-%d') for date in emp.availability if emp.availability[date]]
    def add_date():
        date = cal.get_date()
        dt = datetime.strptime(date, '%Y-%m-%d')
        if dt not in selected_dates_list:
            selected_dates_list.append(dt)
            avail_label.config(text=f"Selected: {', '.join(d.strftime('%Y-%m-%d') for d in selected_dates_list)}")

    tk.Button(window, text="Add Selected Date", command=add_date).pack()
    avail_label = tk.Label(window, text=f"Selected: {', '.join(d.strftime('%Y-%m-%d') for d in selected_dates_list)}")
    avail_label.pack()

    tk.Button(window, text="Submit", command=submit).pack()

def view_employees_gui(manager, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: view_employees_gui(manager, content_frame, nav_history))  # Push self

    if not manager.employees:
        tk.Label(content_frame, text="No employees yet.").pack()
        return

    tk.Label(content_frame, text="View Employees").pack()

    emp_list = ttk.Treeview(content_frame, columns=("Name", "Role", "Rate"), show="headings")
    emp_list.heading("Name", text="Name")
    emp_list.heading("Role", text="Role")
    emp_list.heading("Rate", text="Hourly Rate")

    def refresh_list():
        emp_list.delete(*emp_list.get_children())
        for i, emp in enumerate(manager.employees):
            emp_list.insert("", "end", values=(emp.name, emp.role, emp.hourly_rate), iid=i)

    refresh_list()
    emp_list.pack()

    def edit_selected(event):
        selected = emp_list.selection()
        if selected:
            emp_index = int(selected[0])
            edit_employee_gui(manager, emp_index, refresh_list)

    emp_list.bind("<<TreeviewSelect>>", edit_selected)

    def delete_selected():
        selected = emp_list.selection()
        if selected:
            emp_index = int(selected[0])
            emp_name = manager.employees[emp_index].name
            if messagebox.askyesno("Confirm Delete", f"Delete {emp_name}?"):
                del manager.employees[emp_index]
                messagebox.showinfo("Deleted", f"{emp_name} has been removed.")
                refresh_list()
        else:
            messagebox.showwarning("No Selection", "Select an employee to delete.")

    tk.Button(content_frame, text="Delete Selected", command=delete_selected).pack(pady=10)

# Placeholder for add_equipment_gui
def add_equipment_gui(manager, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: add_equipment_gui(manager, content_frame, nav_history))
    tk.Label(content_frame, text="Add Equipment (Placeholder)").pack()
    # Implement your equipment form here, similar to add_employee_gui

# Placeholder for view_equipment_gui
def view_equipment_gui(manager, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: view_equipment_gui(manager, content_frame, nav_history))
    tk.Label(content_frame, text="View Equipment (Placeholder)").pack()
    # Implement your equipment view here

def create_project_gui(manager, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: create_project_gui(manager, content_frame, nav_history))

    def submit():
        name = name_entry.get()
        desc = desc_entry.get()
        try:
            hours = float(hours_entry.get())
            start = start_entry.get()
            proj = Project(name, desc, hours, start)
            manager.projects.append(proj)
            proj.generate_schedule(manager)
            messagebox.showinfo("Success", f"Added: {proj} (Schedule generated)")
            go_back(nav_history, content_frame)
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")

    tk.Label(content_frame, text="Create Project").pack()
    tk.Label(content_frame, text="Name:").pack()
    name_entry = tk.Entry(content_frame)
    name_entry.pack()

    tk.Label(content_frame, text="Description:").pack()
    desc_entry = tk.Entry(content_frame)
    desc_entry.pack()

    tk.Label(content_frame, text="Estimated Hours:").pack()
    hours_entry = tk.Entry(content_frame)
    hours_entry.pack()

    tk.Label(content_frame, text="Start Date (YYYY-MM-DD):").pack()
    start_entry = tk.Entry(content_frame)
    start_entry.pack()

    tk.Button(content_frame, text="Submit", command=submit).pack()

def add_work_item_gui(manager, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: add_work_item_gui(manager, content_frame, nav_history))

    def submit():
        code = code_entry.get()
        desc = desc_entry.get()
        if code and desc:
            manager.add_work_item(code, desc)
            messagebox.showinfo("Success", f"Added: {code} - {desc}")
            go_back(nav_history, content_frame)
        else:
            messagebox.showerror("Error", "Fill in both fields.")

    tk.Label(content_frame, text="Add Work Item").pack()
    tk.Label(content_frame, text="Job Code (e.g., EXC-001):").pack()
    code_entry = tk.Entry(content_frame)
    code_entry.pack()

    tk.Label(content_frame, text="Description:").pack()
    desc_entry = tk.Entry(content_frame)
    desc_entry.pack()

    tk.Button(content_frame, text="Submit", command=submit).pack()

def view_projects_schedules_gui(manager, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: view_projects_schedules_gui(manager, content_frame, nav_history))

    if not manager.projects:
        tk.Label(content_frame, text="No projects yet.").pack()
        return

    tk.Label(content_frame, text="View Projects & Schedules").pack()

    proj_list = ttk.Treeview(content_frame, columns=("Name",), show="headings")
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
            show_schedule_view(proj, content_frame, nav_history)  # Push to new view

    proj_list.bind("<<TreeviewSelect>>", show_schedule)

def show_schedule_view(proj, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: show_schedule_view(proj, content_frame, nav_history))

    tk.Label(content_frame, text=f"Schedule for {proj.name} (Weekly View)").pack()

    days = list(proj.schedule.keys())
    cal_frame = tk.Frame(content_frame)
    cal_frame.pack()
    for i, date in enumerate(days):
        day_data = proj.schedule[date]
        summary = f"{date}\nTasks: {day_data['tasks'][:20]}...\nAssigned: {', '.join(day_data['assigned_employees'])}"
        btn = tk.Button(cal_frame, text=summary, command=lambda d=date: show_day_detail(proj, d, content_frame, nav_history))
        btn.grid(row=0, column=i, padx=5, pady=5)

def show_day_detail(proj, date, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: show_day_detail(proj, date, content_frame, nav_history))

    day_data = proj.schedule.get(date, {})
    tk.Label(content_frame, text=f"Details for {date}").pack()
    tk.Label(content_frame, text=f"Tasks: {day_data.get('tasks', 'N/A')}").pack()
    tk.Label(content_frame, text=f"Assigned: {', '.join(day_data.get('assigned_employees', []))}").pack()
    tk.Label(content_frame, text=f"Completed: {day_data.get('completed', False)}").pack()

    def mark_completed():
        if date in proj.schedule:
            proj.schedule[date]['completed'] = True
            messagebox.showinfo("Updated", f"Marked {date} as completed.")
            show_day_detail(proj, date, content_frame, nav_history)  # Refresh (re-pushes self)

    tk.Button(content_frame, text="Mark Completed (Simulate Timecard)", command=mark_completed).pack()

def go_back(nav_history, content_frame):
    if len(nav_history) > 1:
        nav_history.pop()  # Remove current
        previous = nav_history[-1]  # Get previous
        previous()  # Call to reload
    else:
        clear_content(content_frame)
        tk.Label(content_frame, text="Welcome! Select an option from the menu.").pack(pady=20)

def main_gui():
    manager = BusinessManager()

    root = tk.Tk()
    root.title("Business Manager")
    root.geometry("800x600")  # Initial size for sidebar + viewer

    # Navigation history stack
    nav_history = []

    # Sidebar frame (left menu)
    sidebar = tk.Frame(root, width=200, bg="lightgray")
    sidebar.pack(side="left", fill="y")

    tk.Button(sidebar, text="Add Employee", command=lambda: add_employee_gui(manager, content_frame, nav_history)).pack(pady=10, fill="x")
    tk.Button(sidebar, text="Add Equipment", command=lambda: add_equipment_gui(manager, content_frame, nav_history)).pack(pady=10, fill="x")
    tk.Button(sidebar, text="View Equipment", command=lambda: view_equipment_gui(manager, content_frame, nav_history)).pack(pady=10, fill="x")
    tk.Button(sidebar, text="Create Project", command=lambda: create_project_gui(manager, content_frame, nav_history)).pack(pady=10, fill="x")
    tk.Button(sidebar, text="Add Work Item", command=lambda: add_work_item_gui(manager, content_frame, nav_history)).pack(pady=10, fill="x")
    tk.Button(sidebar, text="View Projects & Schedules", command=lambda: view_projects_schedules_gui(manager, content_frame, nav_history)).pack(pady=10, fill="x")
    tk.Button(sidebar, text="View Employees", command=lambda: view_employees_gui(manager, content_frame, nav_history)).pack(pady=10, fill="x")
    tk.Button(sidebar, text="Save Data", command=manager.save_data).pack(pady=10, fill="x")
    tk.Button(sidebar, text="Exit", command=sys.exit).pack(pady=10, fill="x")

    # Main content frame (viewer)
    content_frame = tk.Frame(root, bg="white")
    content_frame.pack(side="right", fill="both", expand=True)

    # Back button (persistent at top of content_frame)
    back_button = tk.Button(content_frame, text="Back", command=lambda: go_back(nav_history, content_frame))
    back_button.pack(anchor="nw", pady=5)  # Always visible, but we can hide if at root

    # Initial welcome message (no history push)
    tk.Label(content_frame, text="Welcome! Select an option from the menu.").pack(pady=20)

    # Hide back button initially
    back_button.pack_forget()

    # Modify clear_content to show back button if history exists
    global clear_content
    def clear_content(frame):
        for widget in frame.winfo_children():
            if widget != back_button:  # Preserve back button
                widget.destroy()
        if len(nav_history) > 0:
            back_button.pack(anchor="nw", pady=5)
        else:
            back_button.pack_forget()

    root.mainloop()

if __name__ == "__main__":
    main_gui()
