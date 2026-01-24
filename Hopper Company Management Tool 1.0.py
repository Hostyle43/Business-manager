import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from tkcalendar import Calendar
import math

# --- Data Management ---

DATA_FILE = "business_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"employees": {}, "work_library": {}}
    return {"employees": {}, "work_library": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Classes ---

class Employee:
    def __init__(self, name, role, contact):
        self.name = name
        self.role = role
        self.contact = contact
        self.availability = {}  # date_string: status

# --- Excavating Estimator Classes ---

class Estimate:
    def __init__(self, project_name):
        self.project_name = project_name
        self.date = datetime.now().strftime("%Y-%m-%d")

class ExcavatingEstimate(Estimate):
    def __init__(self, project_name):
        super().__init__(project_name)
        # Initialize all fields with default values
        self.footing_length = 0.0
        self.footing_width = 0.0
        self.footing_depth = 0.0
        self.wall_height = 0.0
        self.wall_thickness = 0.0
        self.excavation_depth = 0.0
        self.slope_ratio = 1.0  # 1:1 default
        self.working_space = 2.0  # 2ft default
        # ... other fields ...

# --- GUI (Wrapped in Class to Fix 'self' Issues) ---

class BusinessManagerApp:
    def __init__(self):
        self.data = load_data()
        self.root = tk.Tk()
        self.root.title("Business Manager Pro")
        self.root.geometry("1200x800")
        self.main_gui()  # Build the GUI
        self.root.mainloop()

    def main_gui(self):
        # Main Container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        # Sidebar (Fixed: Now uses 'self' properly, with enhanced scrolling)
        self.sidebar_container = tk.Frame(self.main_container, width=200, bg='gray')
        self.sidebar_container.pack(side='left', fill='y')

        self.sidebar_canvas = tk.Canvas(self.sidebar_container, width=200, bg='gray', highlightthickness=0)
        self.sidebar_scrollbar = tk.Scrollbar(self.sidebar_container, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar = tk.Frame(self.sidebar_canvas, bg='gray')

        # Enhanced binding for dynamic content and scrolling
        def update_scrollregion(event=None):
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))

        self.sidebar.bind("<Configure>", update_scrollregion)
        self.root.after(100, update_scrollregion)  # Force initial update

        # Mouse wheel support
        def on_mousewheel(event):
            self.sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.root.bind_all("<MouseWheel>", on_mousewheel)

        self.sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw")
        self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)

        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        self.sidebar_scrollbar.pack(side="right", fill="y")

        # Viewer Pane
        self.viewer_pane = tk.Frame(self.main_container, bg="white")
        self.viewer_pane.pack(side="right", fill="both", expand=True)

        # ... Add your existing menu buttons here (e.g., for Excavating Estimator) ...
        # Example placeholder buttons to test scrolling (add enough to force scroll)
        for i in range(20):  # Placeholder to test scrollbar
            tk.Button(self.sidebar, text=f"Menu Item {i+1}", command=lambda: print(f"Item {i+1} clicked")).pack(fill='x', pady=2)

if __name__ == "__main__":
    app = BusinessManagerApp()
