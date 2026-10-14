# Reflection

## 1. Which issues were the easiest to fix, and which were the hardest?
The Flake8 findings and the Pylint naming/docstring messages were the easiest: they are mechanical, and the tool tells you exactly what to change. The hardest were the Bandit findings, because the fix is a design decision, not a rewrite of one line. For `os.system` I had to decide how to open a file without a shell; for the hardcoded password I had to decide where the secret should live (an environment variable) and what to do when it is missing (reject everything). Removing the `global` was also harder than it looks, since it meant moving the state into a class and updating every caller.

## 2. Did the tools report any false positives?
Not really, but some findings need judgment. Bandit's B105 (hardcoded password) is Low severity and the value is labelled "demo", so in a throwaway demo it is arguably harmless; in a real banking integration it would be serious. Bandit B108 on `/tmp/expense_reports` is similar: it is only dangerous when combined with predictable file names, which is exactly what `mktemp` made worse. Pylint's W0603 (global) is a style warning, not a crash. I treated all of them as real because each one had a safe, cheap fix. The tools also missed problems: nothing flagged that `biggestExpense()["note"]` crashes on an empty ledger, that `nan` passes the `amount <= 0` check, or that `main()` runs on import. Those I found by reading the code.

## 3. How would you integrate static analysis into a real workflow?
Run Flake8 and Pylint in the editor (or as a pre-commit hook) so style and quality problems show up as I type, and run all three in CI on every pull request, failing the build on any Bandit High/Medium finding and on a Pylint score below an agreed threshold. Tune the config (`.pylintrc`, `setup.cfg`, `bandit.yaml`) and use justified `# nosec` or `# pylint: disable` comments sparingly, instead of ignoring the reports. Static analysis complements unit tests and code review; it does not replace them.

## 4. What tangible improvements did you see after the fixes?
Pylint went from 5.27/10 to 10.00/10, Bandit from 4 findings (1 High, 2 Medium, 1 Low) to 0, and Flake8 from 4 findings to 0, with the program's output unchanged. Beyond the numbers: the command-injection hole and the temp-file race are closed, no secret is stored in the source, invalid input is rejected instead of crashing, the code follows PEP 8 naming, every function is documented, and the state lives in a class, so the module can be imported and tested without running the demo.
