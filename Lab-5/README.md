# Lab 5: Static Code Analysis — Conference Room & Equipment Scheduler

## Project Overview

The **Conference Room & Equipment Scheduler** is a Python application designed to manage room reservations and equipment allocations (such as projectors, microphones, and webcams). The system tracks bookings, detects room scheduling conflicts (including overlapping time intervals), validates equipment availability, safely cancels bookings with complete resource restoration, logs double-booking incidents, and exports the active schedule to JSON.

This repository serves as a practical implementation and demonstration of static code analysis utilizing **Pylint**, **Bandit**, and **Flake8** to identify, rectify, and verify code quality, security vulnerabilities, and PEP 8 style standards.

---

## Environment Setup (Windows)

The project runs on **Python 3.13** inside a dedicated virtual environment (`venv`).

### 1. Activate the Virtual Environment
In Windows Command Prompt (`cmd.exe`):
```cmd
..\venv\Scripts\activate.bat
```
Or in Windows PowerShell:
```powershell
..\venv\Scripts\Activate.ps1
```

### 2. Verify Tool Installation
Confirm all required static analysis tools are installed and available:
```cmd
python --version
pylint --version
bandit --version
flake8 --version
```

---

## How to Run the Application & Tests

### Run the Scheduler
Execute the demonstration script:
```cmd
python scheduler_system.py
```
When prompted for an optional time slot for `Board-2`, press **Enter** to accept the default (`10-12`) or input an hour range in `HH-HH` format.

### Run Automated Unit Tests
Run the complete unit test suite (13 test cases):
```cmd
python -m unittest test_scheduler_system.py -v
```

---

## How to Run Static Analysis Tools

To re-run the static analysis tools and generate reports, execute the following commands from the `room_scheduler` directory:

### 1. Pylint (Code Quality & Metrics)
```cmd
pylint scheduler_system.py > pylint_after.txt
```
*Current Rating: **10.00 / 10** (Target: > 9.50 / 10).*

### 2. Bandit (Security Vulnerabilities)
```cmd
bandit -r scheduler_system.py > bandit_after.txt
```
*Current Status: **0 issues identified** (No high, medium, or low severity issues).*

### 3. Flake8 (PEP 8 Style & Formatting)
```cmd
flake8 scheduler_system.py > flake8_after.txt
```
*Current Status: **0 violations** (Empty file indicates clean exit).*

---

## Deliverables & Documentation Index

| Deliverable File | Description | Status |
|---|---|---|
| `scheduler_system.py` | Refactored, secure, PEP 8-compliant room scheduler source code | Completed (10.00/10) |
| `test_scheduler_system.py` | Automated test suite covering all 12+ functional requirements | Completed (13/13 Pass) |
| `issues.md` | Detailed table of 8 verified security, reliability, logic, and style findings | Completed |
| `reflection.md` | Academic reflection answering the 4 required static analysis questions | Completed |
| `pylint_before.txt` | Initial Pylint report showing baseline score of 5.60/10 | Preserved unchanged |
| `pylint_after.txt` | Final Pylint report demonstrating perfect score of 10.00/10 | Generated & verified |
| `bandit_before.txt` | Initial Bandit report showing High (B605) and Low (B110) vulnerabilities | Preserved unchanged |
| `bandit_after.txt` | Final Bandit report confirming 0 security vulnerabilities | Generated & verified |
| `flake8_before.txt` | Initial Flake8 report showing 13 PEP 8 formatting/syntax violations | Preserved unchanged |
| `flake8_after.txt` | Final Flake8 report showing 0 style violations | Generated & verified |
| `.gitignore` | Configured to ignore caches, virtual environments, and generated artifacts | Configured |
