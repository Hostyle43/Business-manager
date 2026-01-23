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
        self.estimates = []
        self.employees = []  # List of Employee objects
        self.equipment = []  # List of Equipment objects
        self.projects = []   # List of Project objects
        self.work_library = {}  # Dict of job_code: description
        self.load_data()     # Load on init

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.estimates = [ExcavatingEstimate.from_dict(d, self) for d in data.get('estimates', [])]  # Use subclass if all are excavating
                self.employees = [Employee.from_dict(e) for e in data.get('employees', [])]
                self.equipment = [Equipment.from_dict(eq) for eq in data.get('equipment', [])]
                self.projects = [Project.from_dict(p) for p in data.get('projects', [])]
                self.work_library = data.get('work_library', {})
            print("Data loaded successfully.")
        else:
            print("No data file found; starting fresh.")

    def save_data(self):
        data = {
            'estimates': [est.to_dict() for est in self.estimates],
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
    def __init__(self, name, role, availability, home, hourly_rate=0.0, hourly_cost=0.0):
        self.name = name
        self.role = role
        self.availability = availability  # From tkcalendar
        self.home = home  # Assuming this is a new field you added
        self.hourly_rate = hourly_rate
        self.hourly_cost = hourly_cost
        # Rest of your __init__ (e.g., hours_worked = 0)

    def to_dict(self):
        return {
            'name': self.name,
            'role': self.role,
            'availability': self.availability,
            'home': self.home,
            'hourly_rate': self.hourly_rate,
            'hourly_cost': self.hourly_cost,
            # Include other fields like hours_worked
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['name'],
            data['role'],
            data.get('availability', {}),
            data.get('home', ''),
            data.get('hourly_rate', 0.0),
            data.get('hourly_cost', 0.0)
        )

    def __str__(self):
        return f"Employee: {self.name} ({self.role}), Rate: ${self.hourly_rate}/hr, Cost: ${self.hourly_cost}/hr"
import math

class Estimate:
    def __init__(self, project_name, work_items=None, assigned_employees=None, estimated_hours=0.0, total_cost=0.0, total_rate=0.0):
        self.project_name = project_name
        self.work_items = work_items or []  # List of dicts, e.g., [{'code': '001', 'description': 'Excavate trench', 'est_hours': 10}]
        self.assigned_employees = assigned_employees or []  # List of Employee objects
        self.estimated_hours = estimated_hours
        self.total_cost = total_cost
        self.total_rate = total_rate

    def calculate_totals(self, manager):
        self.estimated_hours = sum(item.get('est_hours', 0) for item in self.work_items)
        self.total_cost = 0.0
        self.total_rate = 0.0
        for emp in self.assigned_employees:
            if isinstance(emp, str):  # If loaded as names, fetch from manager
                emp = next((e for e in manager.employees if e.name == emp), None)
            if emp:
                self.total_cost += emp.hourly_cost * self.estimated_hours
                self.total_rate += emp.hourly_rate * self.estimated_hours
        # Add markup or other logic as needed

    def to_dict(self):
        return {
            'project_name': self.project_name,
            'work_items': self.work_items,
            'assigned_employees': [emp.name if hasattr(emp, 'name') else emp for emp in self.assigned_employees],
            'estimated_hours': self.estimated_hours,
            'total_cost': self.total_cost,
            'total_rate': self.total_rate
        }

    @classmethod
    def from_dict(cls, data, manager):
        assigned = [next((emp for emp in manager.employees if emp.name == name), name) for name in data.get('assigned_employees', [])]
        return cls(
            data['project_name'],
            data.get('work_items', []),
            assigned,
            data.get('estimated_hours', 0.0),
            data.get('total_cost', 0.0),
            data.get('total_rate', 0.0)
        )


class ExcavatingEstimate(Estimate):
    def __init__(self, project_name, work_items=None, assigned_employees=None, assigned_equipment=None,
                 # Foundation Inputs (from Excel "Foundation" section)
                 footing_width=0.0, footing_length=0.0, footing_thickness=0.0,
                 wall_sections=None,  # List of dicts: [{'width': 0.0, 'length': 0.0, 'depth': 0.0, 'tow': 0.0, 'bof': 0.0}]
                 interior_exc_width=0.0, interior_exc_length=0.0, interior_exc_depth=0.0,
                 piers=None,  # List of dicts: [{'width': 0.0, 'length': 0.0, 'depth': 0.0}]
                 num_piers=0, avg_spoils_distance=0.0, building_corners=0, elevation_steps=0,
                 # Utilities/Trenches (from "Utilities" section)
                 water_depth=7.0, sewer_depth=5.0, power_depth=3.5, trench_linear_ft=0.0, trench_width=0.0,
                 slope_over_ex=0.0, curtain_wall_depth=0.0, curtain_wall_width=0.0, curtain_wall_linear_ft=0.0,
                 perimeter_drain_length=0.0, num_cleanouts=0, num_elbows=0, num_caps=0,
                 # Slabs/Roads (from "Slabs" and "Roads" sections)
                 slab_thickness=0.0, insulation_thickness=0.0, slab_length=0.0, slab_width=0.0, slab_fill_depth=0.0,
                 slab_exc_depth=0.0, road_length=0.0, road_width=0.0, road_thickness=0.0, pitrun_depth=0.0,
                 roadbase_depth=0.0,
                 # Other
                 export_loads=0, haul_truck_hours=0.0, compactor_cost=450.0, fuel_cost=0.0, mobilization_time=0.0,
                 slope_angle=45.0, truck_capacity=10.0, trucking_distance=0.0, bedding_thickness=6.0,  # Inches
                 **kwargs):
        super().__init__(project_name, work_items, assigned_employees, **kwargs)
        self.assigned_equipment = assigned_equipment or []
        # Assign all inputs as attributes (abbreviated for brevity; add all above)
        self.footing_width = footing_width
        self.footing_length = footing_length
        self.footing_thickness = footing_thickness
        self.wall_sections = wall_sections or []
        self.interior_exc_width = interior_exc_width
        self.interior_exc_length = interior_exc_length
        self.interior_exc_depth = interior_exc_depth
        self.piers = piers or []
        self.num_piers = num_piers
        self.avg_spoils_distance = avg_spoils_distance
        self.building_corners = building_corners
        self.elevation_steps = elevation_steps
        self.water_depth = water_depth
        self.sewer_depth = sewer_depth
        self.power_depth = power_depth
        self.trench_linear_ft = trench_linear_ft
        self.trench_width = trench_width
        self.slope_over_ex = slope_over_ex
        self.curtain_wall_depth = curtain_wall_depth
        self.curtain_wall_width = curtain_wall_width
        self.curtain_wall_linear_ft = curtain_wall_linear_ft
        self.perimeter_drain_length = perimeter_drain_length
        self.num_cleanouts = num_cleanouts
        self.num_elbows = num_elbows
        self.num_caps = num_caps
        self.slab_thickness = slab_thickness
        self.insulation_thickness = insulation_thickness
        self.slab_length = slab_length
        self.slab_width = slab_width
        self.slab_fill_depth = slab_fill_depth
        self.slab_exc_depth = slab_exc_depth
        self.road_length = road_length
        self.road_width = road_width
        self.road_thickness = road_thickness
        self.pitrun_depth = pitrun_depth
        self.roadbase_depth = roadbase_depth
        self.export_loads = export_loads
        self.haul_truck_hours = haul_truck_hours
        self.compactor_cost = compactor_cost
        self.fuel_cost = fuel_cost
        self.mobilization_time = mobilization_time
        self.slope_angle = slope_angle
        self.truck_capacity = truck_capacity
        self.trucking_distance = trucking_distance
        self.bedding_thickness = bedding_thickness
        self.utility_materials = {}  # Computed later

        # Rates from Excel
        self.rates = {
            'excavator_hourly': 165.0, 'loader_hourly': 155.0, 'haul_truck_hourly': 160.0, 'labor_hourly': 75.0,
            'margin_general': 1.5, 'margin_trucking': 1.15, 'dump_fee_per_ton': 90.0, 'gravel_density_tons_per_yd': 1.5
        }
        self.productivity = {'excavator': 100.0, 'loader': 80.0}  # Cu yd/hr, inferred from examples

    def calculate_volumes(self):
        # Foundation Volumes (cu yd)
        footing_vol = (self.footing_width * self.footing_length * self.footing_thickness) / 27
        wall_vol = sum((ws['width'] * ws['length'] * ws['depth']) / 27 for ws in self.wall_sections)
        interior_vol = (self.interior_exc_width * self.interior_exc_length * self.interior_exc_depth) / 27
        piers_vol = sum((p['width'] * p['length'] * p['depth']) / 27 for p in self.piers) * self.num_piers
        foundation_total = footing_vol + wall_vol + interior_vol + piers_vol

        # Trench/Utility Volumes with Slope (trapezoidal)
        slope_rad = math.radians(self.slope_angle)
        width_top = self.trench_width + 2 * self.water_depth / math.tan(slope_rad) + self.slope_over_ex
        trench_vol = self.trench_linear_ft * (self.trench_width + width_top) / 2 * self.water_depth / 27  # Using water depth as example; average for others
        curtain_vol = (self.curtain_wall_linear_ft * self.curtain_wall_width * self.curtain_wall_depth) / 27

        # Slabs/Roads
        slab_vol = (self.slab_length * self.slab_width * self.slab_exc_depth) / 27
        road_vol = (self.road_length * self.road_width * (self.pitrun_depth + self.roadbase_depth)) / 27

        total_exc_vol = foundation_total + trench_vol + curtain_vol + slab_vol + road_vol
        backfill_vol = total_exc_vol * 0.8  # Assume 80% backfill, per Excel patterns
        export_vol = total_exc_vol - backfill_vol + (self.export_loads * self.truck_capacity)
        return {'total_exc': total_exc_vol, 'backfill': backfill_vol, 'export': export_vol}

    def calculate_times(self):
        vols = self.calculate_volumes()
        exc_time = vols['total_exc'] / self.productivity['excavator']  # Hours
        load_time = vols['total_exc'] / self.productivity['loader']
        backfill_time = vols['backfill'] / (self.productivity['loader'] * 0.8)
        total_hours = exc_time + load_time + backfill_time + self.haul_truck_hours + self.mobilization_time
        days = total_hours / 8.0  # Assume 8-hour days
        self.estimated_hours = total_hours
        return {'hours': total_hours, 'days': days}

    def calculate_trucking(self):
        vols = self.calculate_volumes()
        num_loads = math.ceil(vols['export'] / self.truck_capacity)
        trip_time = (self.trucking_distance / 30.0) * 2  # Round-trip, 30 mph
        trucking_time = num_loads * trip_time
        trucking_cost = trucking_time * self.rates['haul_truck_hourly'] * self.rates['margin_trucking']
        dump_cost = (vols['export'] * self.rates['gravel_density_tons_per_yd']) * self.rates['dump_fee_per_ton']
        return {'time': trucking_time, 'cost': trucking_cost + dump_cost, 'loads': num_loads}

    def calculate_bedding_and_utilities(self):
        bedding_vol = (self.trench_linear_ft * self.trench_width * (self.bedding_thickness / 12)) / 27  # Inches to ft
        gravel_tons = bedding_vol * self.rates['gravel_density_tons_per_yd']
        self.utility_materials = {
            'perf_pipe_ft': self.perimeter_drain_length,
            'solid_pipe_ft': self.trench_linear_ft * 1.1,  # 10% extra
            'cleanouts': self.num_cleanouts, 'elbows': self.num_elbows, 'caps': self.num_caps
        }
        return {'bedding_vol': bedding_vol, 'gravel_tons': gravel_tons}

    def calculate_totals(self, manager):
        super().calculate_totals(manager)
        times = self.calculate_times()
        trucking = self.calculate_trucking()
        bedding_utils = self.calculate_bedding_and_utilities()

        # Equipment/Labor Costs
        eq_cost = sum(eq.get('hourly_cost', 0.0) * times['hours'] for eq in self.assigned_equipment) * self.rates['margin_general']
        labor_cost = len(self.assigned_employees) * self.rates['labor_hourly'] * times['hours'] * self.rates['margin_general']

        self.total_cost = eq_cost + labor_cost + trucking['cost'] + self.fuel_cost + self.compactor_cost
        self.total_rate = self.total_cost * 1.2  # Placeholder markup; adjust per Excel

    # to_dict and from_dict similar to before, extended for new fields
    def to_dict(self):
        base = super().to_dict()
        base.update({
            'footing_width': self.footing_width,
            # Add all other fields...
        })
        return base

    @classmethod
    def from_dict(cls, data, manager):
        # Extended rehydration
        return cls(data['project_name'], **data)


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
def add_employee_gui(manager, content_frame, nav_history):
    clear_content(content_frame)
    nav_history.append(lambda: add_employee_gui(manager, content_frame, nav_history))

    def submit():
        name = name_entry.get()
        role = role_entry.get()
        try:
            rate = float(rate_entry.get())
            cost = float(cost_entry.get())  # Now reading from the new entry
            # Get selected dates (from your tkcalendar multi-select simulation)
            availability = {date.strftime('%Y-%m-%d'): True for date in selected_dates_list}
            home = home_entry.get()  # Assuming you have a 'home' field
            emp = Employee(name, role, availability, home, rate, cost)
            manager.employees.append(emp)
            messagebox.showinfo("Success", f"Added: {emp}")
            go_back(nav_history, content_frame)
        except ValueError:
            messagebox.showerror("Error", "Invalid input for rates or costs.")

    tk.Label(content_frame, text="Add Employee").pack()
    tk.Label(content_frame, text="Name:").pack()
    name_entry = tk.Entry(content_frame)
    name_entry.pack()

    tk.Label(content_frame, text="Role:").pack()
    role_entry = tk.Entry(content_frame)
    role_entry.pack()

    tk.Label(content_frame, text="Home Address:").pack()  # If this is your 'home' field
    home_entry = tk.Entry(content_frame)
    home_entry.pack()

    tk.Label(content_frame, text="Hourly Rate:").pack()
    rate_entry = tk.Entry(content_frame)
    rate_entry.pack()

    tk.Label(content_frame, text="Hourly Cost:").pack()
    cost_entry = tk.Entry(content_frame)  # This was likely missing or not packed
    cost_entry.pack()  # Ensure it's packed to appear in the GUI

    # Your calendar setup (tkcalendar for availability)
    tk.Label(content_frame, text="Select Available Dates:").pack()
    cal = Calendar(content_frame, selectmode="day", date_pattern="y-mm-dd")
    cal.pack()
    selected_dates_list = []
    def add_date():
        date = cal.get_date()
        dt = datetime.strptime(date, '%Y-%m-%d')
        if dt not in selected_dates_list:
            selected_dates_list.append(dt)
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
        emp.home = home_entry.get()  # If applicable
        try:
            emp.hourly_rate = float(rate_entry.get())
            emp.hourly_cost = float(cost_entry.get())  # Reading from the entry
            # Update availability
            emp.availability = {date.strftime('%Y-%m-%d'): True for date in selected_dates_list}
            messagebox.showinfo("Success", f"Updated: {emp}")
            window.destroy()
            refresh_callback()
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

    tk.Label(window, text="Home Address:").pack()
    home_entry = tk.Entry(window)
    home_entry.insert(0, emp.home)
    home_entry.pack()

    tk.Label(window, text="Hourly Rate:").pack()
    rate_entry = tk.Entry(window)
    rate_entry.insert(0, str(emp.hourly_rate))
    rate_entry.pack()

    tk.Label(window, text="Hourly Cost:").pack()
    cost_entry = tk.Entry(window)  # This was likely missing or not inserted
    cost_entry.insert(0, str(emp.hourly_cost))  # Pre-fill with current value
    cost_entry.pack()

    # Calendar for editing availability (similar to add)
    tk.Label(window, text="Select Available Dates (replaces existing):").pack()
    cal = Calendar(window, selectmode="day", date_pattern="y-mm-dd")
    cal.pack()
    selected_dates_list = [datetime.strptime(date, '%Y-%m-%d') for date in emp.availability if emp.availability.get(date)]
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

    emp_list = ttk.Treeview(content_frame, columns=("Name", "Role", "Rate", "Cost"), show="headings")
    emp_list.heading("Name", text="Name")
    emp_list.heading("Role", text="Role")
    emp_list.heading("Rate", text="Hourly Rate")
    emp_list.heading("Cost", text="Hourly cost")

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
import tkinter as tk
from tkinter import messagebox

def excavating_estimator_gui(manager, content_frame, nav_history):
    clear_content(content_frame)  # Clear existing content
    nav_history.append(lambda: excavating_estimator_gui(manager, content_frame, nav_history))

    def submit():
        try:
            # Collect all inputs
            wall_sections = []
            for i in range(3):  # Up to 3 wall sections; expand as needed
                if wall_width_entries[i].get() and wall_length_entries[i].get() and wall_depth_entries[i].get():
                    wall_sections.append({
                        'width': float(wall_width_entries[i].get()),
                        'length': float(wall_length_entries[i].get()),
                        'depth': float(wall_depth_entries[i].get()),
                        'tow': float(wall_tow_entries[i].get() or 0),  # Optional
                        'bof': float(wall_bof_entries[i].get() or 0)
                    })

            piers = []
            for i in range(3):  # Up to 3 piers
                if pier_width_entries[i].get() and pier_length_entries[i].get() and pier_depth_entries[i].get():
                    piers.append({
                        'width': float(pier_width_entries[i].get()),
                        'length': float(pier_length_entries[i].get()),
                        'depth': float(pier_depth_entries[i].get())
                    })

            est = ExcavatingEstimate(
                project_name=name_entry.get(),
                footing_width=float(footing_width_entry.get() or 0),
                footing_length=float(footing_length_entry.get() or 0),
                footing_thickness=float(footing_thickness_entry.get() or 0),
                wall_sections=wall_sections,
                interior_exc_width=float(interior_width_entry.get() or 0),
                interior_exc_length=float(interior_length_entry.get() or 0),
                interior_exc_depth=float(interior_depth_entry.get() or 0),
                piers=piers,
                num_piers=int(num_piers_entry.get() or 0),
                avg_spoils_distance=float(avg_spoils_entry.get() or 0),
                building_corners=int(corners_entry.get() or 0),
                elevation_steps=int(steps_entry.get() or 0),
                water_depth=float(water_depth_entry.get() or 7.0),
                sewer_depth=float(sewer_depth_entry.get() or 5.0),
                power_depth=float(power_depth_entry.get() or 3.5),
                trench_linear_ft=float(trench_ft_entry.get() or 0),
                trench_width=float(trench_width_entry.get() or 0),
                slope_over_ex=float(slope_over_entry.get() or 0),
                curtain_wall_depth=float(curtain_depth_entry.get() or 0),
                curtain_wall_width=float(curtain_width_entry.get() or 0),
                curtain_wall_linear_ft=float(curtain_ft_entry.get() or 0),
                perimeter_drain_length=float(perimeter_length_entry.get() or 0),
                num_cleanouts=int(cleanouts_entry.get() or 0),
                num_elbows=int(elbows_entry.get() or 0),
                num_caps=int(caps_entry.get() or 0),
                slab_thickness=float(slab_thickness_entry.get() or 0),
                insulation_thickness=float(insulation_entry.get() or 0),
                slab_length=float(slab_length_entry.get() or 0),
                slab_width=float(slab_width_entry.get() or 0),
                slab_fill_depth=float(slab_fill_entry.get() or 0),
                slab_exc_depth=float(slab_exc_entry.get() or 0),
                road_length=float(road_length_entry.get() or 0),
                road_width=float(road_width_entry.get() or 0),
                road_thickness=float(road_thickness_entry.get() or 0),
                pitrun_depth=float(pitrun_entry.get() or 0),
                roadbase_depth=float(roadbase_entry.get() or 0),
                export_loads=int(export_loads_entry.get() or 0),
                haul_truck_hours=float(haul_hours_entry.get() or 0),
                compactor_cost=float(compactor_entry.get() or 450.0),
                fuel_cost=float(fuel_entry.get() or 0),
                mobilization_time=float(mobilization_entry.get() or 0),
                slope_angle=float(slope_angle_entry.get() or 45.0),
                truck_capacity=float(truck_cap_entry.get() or 10.0),
                trucking_distance=float(trucking_dist_entry.get() or 0),
                bedding_thickness=float(bedding_entry.get() or 6.0),
                assigned_employees=[manager.employees[i] for i in emp_listbox.curselection()],
                assigned_equipment=[manager.equipment[i] for i in eq_listbox.curselection()]
            )
            est.calculate_totals(manager)
            vols = est.calculate_volumes()
            times = est.calculate_times()
            trucking = est.calculate_trucking()
            bedding_utils = est.calculate_bedding_and_utilities()

            # Display results (mirroring Excel totals)
            message = (
                f"Estimate for {est.project_name}:\n\n"
                f"**Volumes (cu yd)**:\nTotal Excavation: {vols['total_exc']:.2f}\nBackfill: {vols['backfill']:.2f}\nExport: {vols['export']:.2f}\n\n"
                f"**Times**:\nHours: {times['hours']:.2f} (Days: {times['days']:.2f})\n\n"
                f"**Trucking**:\nLoads: {trucking['loads']}\nTime: {trucking['time']:.2f} hrs\nCost: ${trucking['cost']:.2f}\n\n"
                f"**Bedding & Utilities**:\nBedding Vol: {bedding_utils['bedding_vol']:.2f} cu yd\nGravel Tons: {bedding_utils['gravel_tons']:.2f}\n"
                f"Perf Pipe: {est.utility_materials['perf_pipe_ft']:.2f} ft\nSolid Pipe: {est.utility_materials['solid_pipe_ft']:.2f} ft\n"
                f"Cleanouts/Elbows/Caps: {est.utility_materials['cleanouts']}/{est.utility_materials['elbows']}/{est.utility_materials['caps']}\n\n"
                f"**Totals**:\nEstimated Hours: {est.estimated_hours:.2f}\nTotal Cost: ${est.total_cost:.2f}\nTotal Rate: ${est.total_rate:.2f}"
            )
            messagebox.showinfo("Estimate Results", message)
            manager.estimates.append(est)
            manager.save_data()  # Save immediately
            go_back(nav_history, content_frame)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}. Please check numeric fields.")

    # GUI Layout: Scrollable canvas for many fields
    canvas = tk.Canvas(content_frame)
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    tk.Label(scroll_frame, text="Excavating Estimator").pack()
    tk.Label(scroll_frame, text="Project Name:").pack()
    name_entry = tk.Entry(scroll_frame)
    name_entry.pack()

# Add mouse wheel support (works on Windows/Mac/Linux)
def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")  # Adjust for wheel direction/sensitivity

canvas.bind_all("<MouseWheel>", on_mouse_wheel)  # Bind to all widgets for global wheel capture

    # Foundation Section
    foundation_frame = tk.LabelFrame(scroll_frame, text="Foundation")
    foundation_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    tk.Label(foundation_frame, text="Footing Width (ft):").pack()
    footing_width_entry = tk.Entry(foundation_frame)
    footing_width_entry.pack()
    tk.Label(foundation_frame, text="Footing Length (ft):").pack()
    footing_length_entry = tk.Entry(foundation_frame)
    footing_length_entry.pack()
    tk.Label(foundation_frame, text="Footing Thickness (ft):").pack()
    footing_thickness_entry = tk.Entry(foundation_frame)
    footing_thickness_entry.pack()
    tk.Label(foundation_frame, text="Interior Exc. Width (ft):").pack()
    interior_width_entry = tk.Entry(foundation_frame)
    interior_width_entry.pack()
    tk.Label(foundation_frame, text="Interior Exc. Length (ft):").pack()
    interior_length_entry = tk.Entry(foundation_frame)
    interior_length_entry.pack()
    tk.Label(foundation_frame, text="Interior Exc. Depth (ft):").pack()
    interior_depth_entry = tk.Entry(foundation_frame)
    interior_depth_entry.pack()
    tk.Label(foundation_frame, text="Avg Spoils Distance (ft):").pack()
    avg_spoils_entry = tk.Entry(foundation_frame)
    avg_spoils_entry.pack()
    tk.Label(foundation_frame, text="Building Corners:").pack()
    corners_entry = tk.Entry(foundation_frame)
    corners_entry.pack()
    tk.Label(foundation_frame, text="Elevation Steps:").pack()
    steps_entry = tk.Entry(foundation_frame)
    steps_entry.pack()
    tk.Label(foundation_frame, text="Number of Piers:").pack()
    num_piers_entry = tk.Entry(foundation_frame)
    num_piers_entry.pack()

    # Wall Sections (up to 3)
    wall_width_entries, wall_length_entries, wall_depth_entries, wall_tow_entries, wall_bof_entries = [], [], [], [], []
    for i in range(3):
        tk.Label(foundation_frame, text=f"Wall {i+1} Width (ft):").pack()
        entry = tk.Entry(foundation_frame)
        entry.pack()
        wall_width_entries.append(entry)
        tk.Label(foundation_frame, text=f"Wall {i+1} Length (ft):").pack()
        entry = tk.Entry(foundation_frame)
        entry.pack()
        wall_length_entries.append(entry)
        tk.Label(foundation_frame, text=f"Wall {i+1} Depth (ft):").pack()
        entry = tk.Entry(foundation_frame)
        entry.pack()
        wall_depth_entries.append(entry)
        tk.Label(foundation_frame, text=f"Wall {i+1} T.O.W. (ft):").pack()
        entry = tk.Entry(foundation_frame)
        entry.pack()
        wall_tow_entries.append(entry)
        tk.Label(foundation_frame, text=f"Wall {i+1} B.O.F. (ft):").pack()
        entry = tk.Entry(foundation_frame)
        entry.pack()
        wall_bof_entries.append(entry)

    # Piers (up to 3)
    pier_width_entries, pier_length_entries, pier_depth_entries = [], [], []
    for i in range(3):
        tk.Label(foundation_frame, text=f"Pier {i+1} Width (ft):").pack()
        entry = tk.Entry(foundation_frame)
        entry.pack()
        pier_width_entries.append(entry)
        tk.Label(foundation_frame, text=f"Pier {i+1} Length (ft):").pack()
        entry = tk.Entry(foundation_frame)
        entry.pack()
        pier_length_entries.append(entry)
        tk.Label(foundation_frame, text=f"Pier {i+1} Depth (ft):").pack()
        entry = tk.Entry(foundation_frame)
        entry.pack()
        pier_depth_entries.append(entry)

    # Utilities Section
    utilities_frame = tk.LabelFrame(scroll_frame, text="Utilities/Trenches")
    utilities_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    tk.Label(utilities_frame, text="Water Depth (ft):").pack()
    water_depth_entry = tk.Entry(utilities_frame)
    water_depth_entry.insert(0, "7.0")
    water_depth_entry.pack()
    tk.Label(utilities_frame, text="Sewer Depth (ft):").pack()
    sewer_depth_entry = tk.Entry(utilities_frame)
    sewer_depth_entry.insert(0, "5.0")
    sewer_depth_entry.pack()
    tk.Label(utilities_frame, text="Power Depth (ft):").pack()
    power_depth_entry = tk.Entry(utilities_frame)
    power_depth_entry.insert(0, "3.5")
    power_depth_entry.pack()
    tk.Label(utilities_frame, text="Trench Linear Ft:").pack()
    trench_ft_entry = tk.Entry(utilities_frame)
    trench_ft_entry.pack()
    tk.Label(utilities_frame, text="Trench Width (ft):").pack()
    trench_width_entry = tk.Entry(utilities_frame)
    trench_width_entry.pack()
    tk.Label(utilities_frame, text="Slope & Over Ex (ft):").pack()
    slope_over_entry = tk.Entry(utilities_frame)
    slope_over_entry.pack()
    tk.Label(utilities_frame, text="Curtain Wall Depth (ft):").pack()
    curtain_depth_entry = tk.Entry(utilities_frame)
    curtain_depth_entry.pack()
    tk.Label(utilities_frame, text="Curtain Wall Width (ft):").pack()
    curtain_width_entry = tk.Entry(utilities_frame)
    curtain_width_entry.pack()
    tk.Label(utilities_frame, text="Curtain Wall Linear Ft:").pack()
    curtain_ft_entry = tk.Entry(utilities_frame)
    curtain_ft_entry.pack()
    tk.Label(utilities_frame, text="Perimeter Drain Length (ft):").pack()
    perimeter_length_entry = tk.Entry(utilities_frame)
    perimeter_length_entry.pack()
    tk.Label(utilities_frame, text="# Cleanouts:").pack()
    cleanouts_entry = tk.Entry(utilities_frame)
    cleanouts_entry.pack()
    tk.Label(utilities_frame, text="# Elbows:").pack()
    elbows_entry = tk.Entry(utilities_frame)
    elbows_entry.pack()
    tk.Label(utilities_frame, text="# Caps:").pack()
    caps_entry = tk.Entry(utilities_frame)
    caps_entry.pack()

    # Slabs/Roads Section
    slabs_frame = tk.LabelFrame(scroll_frame, text="Slabs/Roads")
    slabs_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    tk.Label(slabs_frame, text="Slab Thickness (ft):").pack()
    slab_thickness_entry = tk.Entry(slabs_frame)
    slab_thickness_entry.pack()
    tk.Label(slabs_frame, text="Insulation Thickness (in):").pack()
    insulation_entry = tk.Entry(slabs_frame)
    insulation_entry.pack()
    tk.Label(slabs_frame, text="Slab Length (ft):").pack()
    slab_length_entry = tk.Entry(slabs_frame)
    slab_length_entry.pack()
    tk.Label(slabs_frame, text="Slab Width (ft):").pack()
    slab_width_entry = tk.Entry(slabs_frame)
    slab_width_entry.pack()
    tk.Label(slabs_frame, text="Slab Fill Depth (ft):").pack()
    slab_fill_entry = tk.Entry(slabs_frame)
    slab_fill_entry.pack()
    tk.Label(slabs_frame, text="Slab Exc. Depth (ft):").pack()
    slab_exc_entry = tk.Entry(slabs_frame)
    slab_exc_entry.pack()
    tk.Label(slabs_frame, text="Road Length (ft):").pack()
    road_length_entry = tk.Entry(slabs_frame)
    road_length_entry.pack()
    tk.Label(slabs_frame, text="Road Width (ft):").pack()
    road_width_entry = tk.Entry(slabs_frame)
    road_width_entry.pack()
    tk.Label(slabs_frame, text="Road Thickness (ft):").pack()
    road_thickness_entry = tk.Entry(slabs_frame)
    road_thickness_entry.pack()
    tk.Label(slabs_frame, text="Pitrun Depth (ft):").pack()
    pitrun_entry = tk.Entry(slabs_frame)
    pitrun_entry.pack()
    tk.Label(slabs_frame, text="Roadbase Depth (ft):").pack()
    roadbase_entry = tk.Entry(slabs_frame)
    roadbase_entry.pack()

    # Other Section
    other_frame = tk.LabelFrame(scroll_frame, text="Other")
    other_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    tk.Label(other_frame, text="Export Loads:").pack()
    export_loads_entry = tk.Entry(other_frame)
    export_loads_entry.pack()
    tk.Label(other_frame, text="Haul Truck Hours:").pack()
    haul_hours_entry = tk.Entry(other_frame)
    haul_hours_entry.pack()
    tk.Label(other_frame, text="Compactor Cost ($):").pack()
    compactor_entry = tk.Entry(other_frame)
    compactor_entry.insert(0, "450.0")
    compactor_entry.pack()
    tk.Label(other_frame, text="Fuel Cost ($):").pack()
    fuel_entry = tk.Entry(other_frame)
    fuel_entry.pack()
    tk.Label(other_frame, text="Mobilization Time (hrs):").pack()
    mobilization_entry = tk.Entry(other_frame)
    mobilization_entry.pack()
    tk.Label(other_frame, text="Slope Angle (deg):").pack()
    slope_angle_entry = tk.Entry(other_frame)
    slope_angle_entry.insert(0, "45.0")
    slope_angle_entry.pack()
    tk.Label(other_frame, text="Truck Capacity (cu yd):").pack()
    truck_cap_entry = tk.Entry(other_frame)
    truck_cap_entry.insert(0, "10.0")
    truck_cap_entry.pack()
    tk.Label(other_frame, text="Trucking Distance (mi):").pack()
    trucking_dist_entry = tk.Entry(other_frame)
    trucking_dist_entry.pack()
    tk.Label(other_frame, text="Bedding Thickness (in):").pack()
    bedding_entry = tk.Entry(other_frame)
    bedding_entry.insert(0, "6.0")
    bedding_entry.pack()

    # Employee and Equipment Selection
    tk.Label(scroll_frame, text="Assign Employees:").pack()
    emp_listbox = tk.Listbox(scroll_frame, selectmode="multiple")
    for i, emp in enumerate(manager.employees):
        emp_listbox.insert(tk.END, emp.name)
    emp_listbox.pack()

    tk.Label(scroll_frame, text="Assign Equipment:").pack()
    eq_listbox = tk.Listbox(scroll_frame, selectmode="multiple")
    for i, eq in enumerate(manager.equipment):
        eq_listbox.insert(tk.END, eq.get('name', 'Unknown'))  # Assuming equipment is list of dicts with 'name'
    eq_listbox.pack()

    tk.Button(scroll_frame, text="Calculate & Submit", command=submit).pack(pady=10)
    tk.Button(scroll_frame, text="Back", command=lambda: go_back(nav_history, content_frame)).pack()


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

    tk.Button(sidebar, text="Excavating Estimator", command=lambda: excavating_estimator_gui(manager, content_frame, nav_history)).pack(fill=tk.X)
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
