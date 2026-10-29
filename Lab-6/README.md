# Lab 6: Code and Branch Coverage Analysis

**Student Identifier:** PES1UG24CS676  
**Course:** Software Engineering Lab (SE_LAB)  
**Module:** Cloud Storage Tier (`cloud_storage_tier.py`)

---

## 1. Overview & Objectives
This lab focuses on measuring, analyzing, and improving code coverage and branch coverage for the `cloud_storage_tier.py` module. The module computes tenant storage charges, network egress costs across hot, cool, and archive tiers, and monitors cluster nodes for replication latency anomalies.

The objectives achieved:
- Executed the initial starter test suite and analyzed baseline statement and branch coverage.
- Designed comprehensive test cases to achieve 100% statement (line) coverage (exceeding the ≥90% threshold).
- Designed targeted branch test cases covering all control decisions (True/False outcomes, boundary values, exception paths, and loop iterations) to achieve 100% branch-specific coverage.
- Captured terminal output screenshots verifying the coverage metrics.

---

## 2. File Structure

| File | Description |
|---|---|
| `cloud_storage_tier.py` | Production module under test implementing `process_storage_tenants` and `monitor_replication_latency`. |
| `test_cloud_storage.py` | Initial starter test file provided with the assignment. |
| `CodeCoverageTest_PES1UG24CS676_application.py` | Part A test suite focused on full statement/line coverage across all functions and paths. |
| `BranchCoverageTest_PES1UG24CS676_application.py` | Part B test suite focused on exercising all decision points and branch directions. |
| `screenshots/CodeCoverage_Report.png` | Terminal screenshot demonstrating 100% line coverage and test run output for Part A. |
| `screenshots/BranchCoverage_Report.png` | Terminal screenshot demonstrating 100% branch coverage (40/40 branches) for Part B. |
| `Lab_6_Code&BranchCoverage_Student_Handout.docx (1).pdf` | Student lab handout and specification. |

---

## 3. Dependencies & Installation

This project requires **Python 3.10+** (tested on Python 3.13) along with `pytest` and `coverage`.

Install dependencies:
```powershell
python -m pip install coverage pytest
```

---

## 4. Running the Test Suite

### Running All Tests Explicitly
Run the starter test along with both coverage test suites:
```powershell
python -m pytest -q test_cloud_storage.py CodeCoverageTest_PES1UG24CS676_application.py BranchCoverageTest_PES1UG24CS676_application.py
```
*Result:* **48 passed**

### Running the Default Starter Test
```powershell
python -m pytest -q
```
*Result:* **1 passed**

---

## 5. Coverage Analysis Commands & Results

### Part A: Code Coverage (Statement / Line Coverage)
Measure line coverage using `CodeCoverageTest_PES1UG24CS676_application.py`:
```powershell
python -m coverage erase
python -m coverage run --source=cloud_storage_tier -m pytest -q CodeCoverageTest_PES1UG24CS676_application.py
python -m coverage report -m
```

#### Results:
- **Tests Passed:** 18 passed
- **Total Statements:** 57
- **Missed Statements:** 0
- **Statement Coverage:** **100%**

---

### Part B: Branch Coverage
Measure branch coverage using `BranchCoverageTest_PES1UG24CS676_application.py`:
```powershell
python -m coverage erase
python -m coverage run --branch --source=cloud_storage_tier -m pytest -q BranchCoverageTest_PES1UG24CS676_application.py
python -m coverage report -m
```

#### Results:
- **Tests Passed:** 29 passed
- **Total Statements:** 57 (0 missed)
- **Total Branches:** 40
- **Covered Branches:** 40
- **Partial Branches:** 0
- **Branch-Specific Coverage:** **100.0%**
- **Overall Coverage (Statements + Branches):** **100%**

---

## 6. Screenshots & Purpose

1. **`screenshots/CodeCoverage_Report.png`**:
   - Demonstrates the execution of `python -m coverage run --source=cloud_storage_tier -m pytest -q CodeCoverageTest_PES1UG24CS676_application.py` followed by `python -m coverage report -m`.
   - Confirms all 18 unit tests passed and reports 100% line coverage (57/57 statements, 0 missing).

2. **`screenshots/BranchCoverage_Report.png`**:
   - Demonstrates the execution of `python -m coverage run --branch --source=cloud_storage_tier -m pytest -q BranchCoverageTest_PES1UG24CS676_application.py` followed by `python -m coverage report -m`.
   - Confirms all 29 branch tests passed, showing 40 total branches, 0 partial branches, and 100% branch-specific coverage.
