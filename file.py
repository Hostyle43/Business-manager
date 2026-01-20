# business_manager.py
# A starting framework for your business management tool

import sys  # For exiting the program

class Employee:
    def __init__(self, name, role, hourly_rate):
        self.name = name
        self.role = role
        self.hourly_rate = hourly_rate
        self.hours_worked = 0  # We'll track time later

    def __str__(self):
        return f"Employee: {self.name} ({self.role}), Rate: ${self.hourly_rate}/hr"

class Project:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.employees = []  # List of assigned employees
        self.expenses = 0.0  # Track costs
        self.status = "Estimate"  # Can change to "Active"

    def add_employee(self, employee):
        self.employees.append(employee)

    def __str__(self):
        return f"Project: {self.name} - {self.description} (Status: {self.status})"

# Global lists to store data (we'll replace with a database later)
employees = []
projects = []

def main_menu():
    while True:
        print("\nBusiness Manager Menu:")
        print("1. Add Employee")
        print("2. Create Project")
        print("3. View Employees")
        print("4. View Projects")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            name = input("Enter employee name: ")
            role = input("Enter role: ")
            rate = float(input("Enter hourly rate: "))
            emp = Employee(name, role, rate)
            employees.append(emp)
            print(f"Added: {emp}")
        elif choice == '2':
            name = input("Enter project name: ")
            desc = input("Enter description: ")
            proj = Project(name, desc)
            projects.append(proj)
            print(f"Created: {proj}")
        elif choice == '3':
            if not employees:
                print("No employees yet.")
            for emp in employees:
                print(emp)
        elif choice == '4':
            if not projects:
                print("No projects yet.")
            for proj in projects:
                print(proj)
        elif choice == '5':
            print("Exiting...")
            sys.exit()
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
