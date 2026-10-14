"""Monthly personal expense tracker.

Records expenses by category, totals spending, tracks the remaining budget,
finds the biggest expense and checks a bank-sync password.
"""

import hmac
import math
import os
import tempfile
import webbrowser
from datetime import datetime
from pathlib import Path

DEFAULT_MONTHLY_BUDGET = 20000
REPORT_DIR = os.path.join(tempfile.gettempdir(), "expense_reports")


def _is_valid_amount(amount):
    """Return True if amount is a finite, positive number (bool excluded)."""
    return (
        isinstance(amount, (int, float))
        and not isinstance(amount, bool)
        and math.isfinite(amount)
        and amount > 0
    )


class ExpenseTracker:
    """Holds the expenses and the monthly budget for one tracker."""

    def __init__(self, monthly_budget=DEFAULT_MONTHLY_BUDGET):
        self.expenses = []
        self.monthly_budget = monthly_budget

    def add_expense(self, amount, category="Misc", note=""):
        """Record an expense. Return False if the amount is invalid."""
        if not _is_valid_amount(amount):
            print("Ignoring invalid amount", amount)
            return False
        self.expenses.append({
            "amount": amount,
            "category": category,
            "note": note,
            "time": datetime.now().isoformat(),
        })
        return True

    def total_by_category(self):
        """Return a dict of total spending per category."""
        totals = {}
        for expense in self.expenses:
            category = expense["category"]
            totals[category] = totals.get(category, 0) + expense["amount"]
        return totals

    def set_budget(self, new_budget):
        """Set the monthly budget (must be a non-negative number)."""
        if not isinstance(new_budget, (int, float)) or new_budget < 0:
            raise ValueError(f"Invalid budget: {new_budget!r}")
        self.monthly_budget = new_budget

    def remaining_budget(self):
        """Return the budget left after all recorded expenses."""
        spent = sum(expense["amount"] for expense in self.expenses)
        return self.monthly_budget - spent

    def biggest_expense(self):
        """Return the largest expense, or None if nothing is recorded."""
        return max(self.expenses, key=lambda e: e["amount"], default=None)

    def print_ledger(self):
        """Print a numbered list of all expenses."""
        for i, expense in enumerate(self.expenses, start=1):
            print(i, expense["category"], expense["amount"])


def check_sync_password(password):
    """Compare password to the one in BANK_SYNC_PASSWORD (env variable).

    Returns False if the variable is not set, so nothing is accepted by
    default. Uses a constant-time comparison.
    """
    expected = os.environ.get("BANK_SYNC_PASSWORD")
    if not expected:
        return False
    return hmac.compare_digest(password.encode(), expected.encode())


def export_report():
    """Create an empty, uniquely named report file and return its path."""
    os.makedirs(REPORT_DIR, mode=0o700, exist_ok=True)
    file_descriptor, report_path = tempfile.mkstemp(
        suffix=".txt", dir=REPORT_DIR
    )
    os.close(file_descriptor)
    return report_path


def open_statement(path):
    """Open a statement file in the default viewer (no shell involved)."""
    statement = Path(path).resolve()
    if not statement.is_file():
        raise FileNotFoundError(f"No such statement: {path}")
    return webbrowser.open(statement.as_uri())


def main():
    """Run a short demonstration."""
    tracker = ExpenseTracker()
    print("Biggest expense before any entries:", tracker.biggest_expense())
    tracker.add_expense(450, "Food", "Lunch with team")
    tracker.add_expense(1200, "Travel", "Cab to airport")
    tracker.add_expense(-50, "Food")
    tracker.add_expense(300, "Food", "Groceries")
    tracker.add_expense(999, "Bills", "Internet")
    tracker.set_budget(5000)
    tracker.print_ledger()
    print("Totals:", tracker.total_by_category())
    print("Remaining budget:", tracker.remaining_budget())  # after set_budget
    biggest = tracker.biggest_expense()
    print("Biggest expense:", biggest["note"] if biggest else "none")
    print("Sync password accepted:", check_sync_password("guess"))
    print(
        f"Summary: {len(tracker.expenses)} expenses recorded "
        f"against a budget of {tracker.monthly_budget}"
    )


if __name__ == "__main__":
    main()
