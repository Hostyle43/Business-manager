# Business-manager
Business managing program
# Business Manager App

## Overview
A comprehensive Python-based application for managing business operations, including projects, employees, equipment, finances, and estimates. The goal is to create an efficient tool for internal use that evolves into a multi-platform system with client-facing features.

### Key Features (Planned)
- **Core Management**: Track employee time and location, projects (income, materials purchased, inventory used, project costs, employee time, equipment time, etc.), equipment time and fuel usage, overall income and expenses, vehicle mileage and fuel usage. Accounting and tax preparation. Payroll. Company schedule that draws from project schedules, employee availability, equipment availabitity, and maintenance schedules. Employee daily schedules with automated work descriptions.
- **Estimator**: Complex calculators for project time/cost, material list, and sub contractor report, pulling from equipment, employee, and user input data. Generate project contract and attach to Estimate.
- **Automation**: Dynamic calculations (e.g., hourly equipment costs from maintenance/usage history), project specific invoice generation from project related tracking data. Populated document generation, such as company W-9, 1099 for sub contractors, and paystubs and W-2 for employees.
- **Integrations**:
  - Desktop GUI for internal ops.
  - Website portal for client real-time updates (progress, schedules).
  - Mobile app for field data input, with website extracting/syncing data.
  - Mobile app for vendors and sub contractors to use for scheduling, invoices and payments, and general communications.
- **Future**: Real-time sync, notifications, and Excel data imports.
  - Mobile app for customers to track project progress, view current project schedule, submit change in work order requests, view and sign contracts and change in work orders, store payment information, make payments, send emails, and leave reviews that will post both to the google search landing page and on the website.   

### Architecture Sketch
This diagram shows the high-level flow: Desktop app as the core, with web and mobile extensions sharing a central database via APIs.

```mermaid
graph TD
    A[Desktop App <br> (Python/Tkinter)] -->|Reads/Writes| B[Central Database <br> (e.g., SQLite/PostgreSQL)]
    C[Mobile App <br> (e.g., Flutter)] -->|Pushes Field Data| B
    D[Website Portal <br> (HTML/JS/Flask API)] -->|Pulls Data via API| B
    B -->|Secure Sync| D
    E[Clients] -->|View Updates| D
    F[Admins/Employees] -->|Manage| A
    F -->|Field Input| C
