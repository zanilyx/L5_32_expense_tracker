# Issues found in `expense_tracker.py`

Line numbers refer to the **original** file. Baseline: Pylint 5.27/10, Bandit 4 findings (1 High, 2 Medium, 1 Low), Flake8 4 findings.
After fixes: Pylint 10.00/10, Bandit 0 findings, Flake8 0 findings. Demo output is byte-for-byte identical to before.

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| Shell command injection via `os.system` (Bandit B605, **High**) | Security | 61 | `os.system("xdg-open " + path)` builds a shell command from a string, so a path like `x; rm -rf ~` would run arbitrary commands. | Removed the shell. Validate that `path` is an existing file, then open it with `webbrowser.open(Path(path).resolve().as_uri())`. |
| Insecure `tempfile.mktemp` (Bandit B306, **Medium**) | Security | 55 | `mktemp` only returns a name; another process can create or symlink that name before it is used (race condition). | Replaced with `tempfile.mkstemp`, which atomically creates the file, and close the descriptor. |
| Hardcoded `/tmp` directory (Bandit B108, **Medium**) | Security | 8 | `"/tmp/expense_reports"` is a predictable, world-writable location. | Built the path from `tempfile.gettempdir()` and created it with `os.makedirs(..., mode=0o700)` so only the owner can use it. |
| Hardcoded password (Bandit B105, Low) | Security | 5 | `BANK_SYNC_PASSWORD = "demo-sync-pass"` is a secret committed to source control. | Read the secret from the `BANK_SYNC_PASSWORD` environment variable; reject everything if unset. Compare with `hmac.compare_digest` (constant time). |
| Overly broad `except Exception` (Pylint W0718) | Bug / Style | 41 | Catches every error in `biggestExpense` and hides real bugs (e.g. a missing `"amount"` key). It only existed to handle an empty list. | Removed the try/except and used `max(..., default=None)`. |
| Mutable module-level state + `global` (Pylint W0603) | Design | 6-7, 29 | `expenses` and `monthly_budget` are global; `setBudget` mutates a global, so the code is hard to test and reuse. | Moved state into an `ExpenseTracker` class (`self.expenses`, `self.monthly_budget`). `main()` creates an instance. |
| No input validation | Bug | 11-17, 28-30 | Only `amount <= 0` was checked. A string amount raised `TypeError`; `nan` slipped through; `True` counted as 1; budgets were never checked. | Added `_is_valid_amount` (numeric, finite, positive, not bool). `set_budget` raises `ValueError` for non-numeric or negative values. |
| Unsafe `biggestExpense()["note"]` | Bug | 75 | Returns `None` when there are no expenses, so indexing it crashes with `TypeError`. | Check for `None` first in `main()`. |
| Non-snake_case names (Pylint C0103) | Style | 7, 11, 20, 28, 33, 38, 44, 49, 53, 55, 59 | `addExpense`, `totalByCategory`, `newBudget`, `reportPath`, etc. break PEP 8; `monthly_budget` is a module constant but not UPPER_CASE. | Renamed to `add_expense`, `total_by_category`, `new_budget`, `report_path`, ... and the default budget to `DEFAULT_MONTHLY_BUDGET`. |
| Missing docstrings (Pylint C0114, C0116) | Style | 1, 11, 20, 28, 33, 38, 44, 49, 53, 59, 64 | Module and all functions undocumented. | Added a module docstring and a docstring on every function/method. |
| `range(len(...))` loop (Pylint C0200) | Style | 45-46 | Indexing by position is verbose and error-prone. | Replaced with `enumerate(self.expenses, start=1)`. |
| Whitespace before `:` (Flake8 E203) | Style | 15 | `{"amount" : amount` | Reformatted the dict literal. |
| Expected 2 blank lines (Flake8 E302) | Style | 44 | Only one blank line before `def printLedger`. | Two blank lines between top-level definitions. |
| Inline comment spacing (Flake8 E261) | Style | 74 | Only one space before `# after setBudget`. | Two spaces before the comment. |
| Line too long, 93 > 79 (Flake8 E501) | Style | 77 | The summary `print` was over the limit. | Split into an f-string across two lines. |
| `main()` runs on import | Design | 80 | Importing the module executes the demo. Not flagged by the tools. | Added `if __name__ == "__main__":` guard. |

## Notes
- `exportReport` now **creates** an empty file (that is what `mkstemp` does) rather than only returning a name. That is the point of the fix, and the function is not called by the demo.
- `open_statement` now uses `webbrowser.open` instead of `xdg-open`, so it is no longer Linux-only. Using `subprocess` instead would have triggered Bandit's low-severity B404/B603 warnings.
