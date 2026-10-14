# Lab 5: Static Code Analysis — Reflection

## 1. What is static code analysis?

Static code analysis is the automated evaluation of software source code performed without executing the program. By parsing the code into an Abstract Syntax Tree (AST) and applying predefined rule sets, static analysis tools detect syntax errors, security vulnerabilities, adherence to coding standards, performance bottlenecks, and anti-patterns early in the development lifecycle.

In this lab, static analysis served as a multi-layered automated review pipeline. Rather than waiting for runtime crashes, data corruption, or external security breaches in production, static analysis provided immediate feedback directly in the development environment.

## 2. What issues did you identify and fix?

Through a combination of static analysis reports and manual code review, I identified and resolved eight key issues across security, reliability, data integrity, and style:

1. **Security Vulnerability (Bandit B605):** In `logConflicts`, `os.system("cat " + file)` posed a command injection vulnerability and broke Windows cross-platform compatibility. I replaced it with secure, native Python file reading using `with open(...)`.
2. **Silent Failure & Bare Exception (Bandit B110, Flake8 E722, Pylint W0702):** In `cancel_reservation`, a bare `try...except: pass` swallowed unexpected runtime errors. I replaced it with an explicit check (`if reservation_id not in reservations: return False`) and returned boolean status indicators.
3. **Overlapping Time-Slot Room Conflicts (Manual / Unit Test):** The original code only checked exact string equality (`slot == time_slot`), permitting overlapping bookings like `09-11` and `10-12` on the same room. I implemented interval overlap detection (`max(start_hour, res_start) < min(end_hour, res_end)`) and rejected conflicting requests.
4. **Equipment Stock Exhaustion & Negative Inventory (Manual / Unit Test):** Equipment deductions did not validate requested counts against available stock, allowing duplicate item requests to drive inventory negative. I added pre-validation across all requested items before decrementing any stock.
5. **Mutable Default Argument (Pylint W0102):** `schedule_room` had `equipment_list=[]`, which shared state across calls. I changed the default to `None` and initialized a fresh list inside the function.
6. **Unmanaged File Handles and Missing Encoding (Pylint R1732, W1514):** File operations lacked context managers and explicit encodings. I wrapped all file reads and writes in `with open(..., encoding="utf-8")` blocks.
7. **Unused Variables and Non-Standard Naming (Flake8 F841, Pylint C0103, W0612):** Unused variables (`a`, `a_more`, `c`) were eliminated in `main()`, `logConflicts` was renamed to snake_case `log_conflicts`, and monotonic reservation tracking was moved to `itertools.count(1)`.
8. **PEP 8 Formatting and Line Length (Flake8 E302, E305, E501, Pylint C0301):** Corrected blank line spacing (2 blank lines between top-level functions) and wrapped lines and docstrings to strictly respect the 79-character limit.

## 3. How did Pylint, Bandit, and Flake8 help?

Each tool played a specialized, complementary role:

- **Bandit ("Security Guard"):** Bandit scanned for common Python security weaknesses and CWEs. It immediately flagged the high-severity shell execution in `os.system` (B605) and the low-severity swallowed exception pattern (B110), directing attention to defensive coding and input sanitization.
- **Pylint ("Strict Code Reviewer"):** Pylint analyzed overall code structure, design patterns, and potential runtime bugs. It caught the mutable default argument (`dangerous-default-value`), unclosed file handles (`consider-using-with`), unspecified file encodings, and missing docstrings. Its scoring metric (raising our code from 5.60/10 to 10.00/10) provided an objective benchmark of code quality.
- **Flake8 ("Grammar & Style Checker"):** Flake8 enforced PEP 8 stylistic consistency, catching excess line lengths, missing blank lines, bare exception syntax, and unused variable assignments. It ensured the codebase is clean, readable, and idiomatic.

Importantly, the lab demonstrated the boundary of static analysis: while the tools caught dangerous syntax, security anti-patterns, and bad practices, they did not detect domain-specific logic bugs like interval overlap or inventory exhaustion. Automated unit testing was essential to complement static analysis.

## 4. What did you learn from this lab?

1. **Working Code Is Not Necessarily Quality Code:** A script can run without throwing an unhandled exception while harboring severe security flaws, resource leaks, and logic errors. Static analysis exposes hidden technical debt before deployment.
2. **Tool Specialization Matters:** No single tool covers every facet of software engineering. Bandit excels at security, Flake8 at PEP 8 style adherence, and Pylint at architectural and semantic code quality. Using them together forms a comprehensive quality assurance gate.
3. **Iterative Verification (Red-Green-Refactor):** Generating baseline before-reports, methodically applying targeted fixes, and rerunning tools to generate clean after-reports provided verified proof that each issue was eliminated without introducing regressions.
4. **Static Analysis Complements, but Does Not Replace, Unit Testing:** Static analysis ensures the code is written correctly according to language rules; automated tests verify the code solves the actual business problem correctly.
