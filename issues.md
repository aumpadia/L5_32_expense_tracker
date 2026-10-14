# Issues Found (Pylint / Bandit / Flake8)

Original file: Pylint **5.27/10**, Bandit 4 issues (1 High, 2 Medium, 1 Low), Flake8 4 warnings.
Fixed file: Pylint **10.00/10**, Bandit **0 issues**, Flake8 **clean**.

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| Shell command injection (B605, High) | Security | 61 | `os.system("xdg-open " + path)` builds a shell command from a string. A path like `x; rm -rf ~` would run arbitrary commands (CWE-78). | Replaced with `subprocess.run(["xdg-open", path], check=False)` (argument list, no shell) and check that the path is an existing file first. |
| Insecure temp file creation (B306, Medium) | Security | 55 | `tempfile.mktemp()` only returns a name and does not create the file, so another process can create or symlink that name first (race condition, CWE-377). | Used `tempfile.mkstemp()`, which creates the file atomically with safe permissions, and closed the returned descriptor. |
| Hardcoded temp directory (B108, Medium) | Security | 8 | `REPORT_DIR = "/tmp/expense_reports"` is a predictable, shared, world-writable location. | Built the path from `tempfile.gettempdir()` and create it with `os.makedirs(..., mode=0o700)`. |
| Hardcoded password (B105, Low) | Security | 5 (also compared on 50) | `BANK_SYNC_PASSWORD = "demo-sync-pass"` is stored in source code and visible to anyone with the repo (CWE-259). The `==` comparison also leaks timing information. | Read the credential from an environment variable. Compare with `hmac.compare_digest`. Reject everything if the variable is not set. |
| Broad exception hides errors (W0718) | Code quality / bug risk | 41 | `except Exception` around `max()` would also swallow unrelated bugs (e.g. a missing `"amount"` key) and return `None`. | Removed the try/except and used `max(..., default=None)`, which only handles the real case: empty list. |
| Global statement (W0603) | Design | 29 | `global monthly_budget` makes state hard to track and test. | Stored the budget in a `settings` dict and updated it in place. No `global` needed. |
| Naming: not snake_case (C0103) | Style | 11, 20, 28, 33, 38, 44, 49, 53, 59 (+ arg on 28, variable on 55) | `addExpense`, `totalByCategory`, `newBudget`, `reportPath`, etc. use camelCase, against PEP 8. | Renamed to `add_expense`, `total_by_category`, `new_budget`, `report_path`, and so on. Updated every call. |
| Constant name (C0103) | Style | 7 | `monthly_budget` is a module-level variable that Pylint treats as a constant (should be UPPER_CASE), yet the program reassigns it with `global`. | Added a `DEFAULT_BUDGET` constant and kept the changing value in a `settings` dict. |
| Missing docstrings (C0114, C0116) | Documentation | 1, 11, 20, 28, 33, 38, 44, 49, 53, 59, 64 | Module and all functions lack docstrings. | Added a module docstring and a one-line docstring to every function. |
| Range/len loop (C0200) | Style / readability | 45 | `for i in range(len(expenses))` is unidiomatic and error-prone. | Replaced with `for number, expense in enumerate(expenses, start=1)`. |
| Code runs on import (design) | Bug risk | 80 | `main()` is called at module level, so importing the file prints output and mutates state. | Wrapped the call in `if __name__ == "__main__":`. |
| Blank lines / whitespace (E302, E203, E261) | Style (Flake8) | 44, 15, 74 | Only 1 blank line before `printLedger` (needs 2), a space before `:` in a dict literal, and only one space before an inline comment (needs 2). | Reformatted per PEP 8. |
| Line too long (E501) | Style (Flake8) | 77 | Line is 93 characters, over the 79 limit. | Wrapped the `print` call across two lines. |

## Behaviour check

Output of the demo is identical before and after the fixes (same ledger, totals, remaining budget 2051, biggest expense "Cab to airport", sync password rejected).
