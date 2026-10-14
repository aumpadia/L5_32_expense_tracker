"""Monthly personal expense tracker.

Records expenses by category, rejects invalid amounts, totals spending per
category, tracks the remaining budget and finds the biggest expense.
"""

import hmac
import os
import subprocess  # nosec B404 - fixed argument list, no shell
import tempfile
from datetime import datetime

# Name of the env variable holding the sync credential (not in source).
SYNC_ENV_NAME = "BANK_SYNC_KEY"

expenses = []

DEFAULT_BUDGET = 20000
settings = {"monthly_budget": DEFAULT_BUDGET}

# Platform temp dir instead of a hardcoded /tmp path.
REPORT_DIR = os.path.join(tempfile.gettempdir(), "expense_reports")


def add_expense(amount, category="Misc", note=""):
    """Record an expense; return False if the amount is not positive."""
    if amount <= 0:
        print("Ignoring invalid amount", amount)
        return False
    expenses.append({"amount": amount, "category": category,
                     "note": note, "time": datetime.now().isoformat()})
    return True


def total_by_category():
    """Return a dict mapping each category to its total spend."""
    totals = {}
    for expense in expenses:
        category = expense["category"]
        totals[category] = totals.get(category, 0) + expense["amount"]
    return totals


def set_budget(new_budget):
    """Set the monthly budget."""
    settings["monthly_budget"] = new_budget


def remaining_budget():
    """Return the monthly budget minus everything spent so far."""
    spent = sum(expense["amount"] for expense in expenses)
    return settings["monthly_budget"] - spent


def biggest_expense():
    """Return the largest expense, or None if nothing has been recorded."""
    return max(expenses, key=lambda expense: expense["amount"], default=None)


def print_ledger():
    """Print every expense with a running number."""
    for number, expense in enumerate(expenses, start=1):
        print(number, expense["category"], expense["amount"])


def check_sync_password(password):
    """Check the bank-sync password using a constant-time comparison."""
    expected = os.environ.get(SYNC_ENV_NAME)
    if not expected:
        return False
    return hmac.compare_digest(password.encode(), expected.encode())


def export_report():
    """Create an empty report file safely and return its path."""
    os.makedirs(REPORT_DIR, mode=0o700, exist_ok=True)
    file_descriptor, report_path = tempfile.mkstemp(suffix=".txt",
                                                    dir=REPORT_DIR)
    os.close(file_descriptor)
    return report_path


def open_statement(path):
    """Open a statement file with the desktop's default viewer."""
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    # Argument list + no shell, so the path cannot inject commands.
    subprocess.run(["xdg-open", path], check=False)  # nosec B603 B607


def main():
    """Run a short demonstration of the tracker."""
    print("Biggest expense before any entries:", biggest_expense())
    add_expense(450, "Food", "Lunch with team")
    add_expense(1200, "Travel", "Cab to airport")
    add_expense(-50, "Food")
    add_expense(300, "Food", "Groceries")
    add_expense(999, "Bills", "Internet")
    set_budget(5000)
    print_ledger()
    print("Totals:", total_by_category())
    print("Remaining budget:", remaining_budget())  # after set_budget
    print("Biggest expense:", biggest_expense()["note"])
    print("Sync password accepted:", check_sync_password("guess"))
    print("Summary:", len(expenses), "expenses recorded against a budget of",
          settings["monthly_budget"])


if __name__ == "__main__":
    main()
