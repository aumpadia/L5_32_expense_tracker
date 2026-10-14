# Reflection: Lab 5 Static Code Analysis

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the style issues: the camelCase names, missing docstrings, blank lines (E302), the long line and the `range(len(...))` loop. They are mechanical, they don't change behaviour, and the tools tell you exactly what to change. Renaming functions only needed me to update every call site.

The hardest were the security issues, mainly the `os.system` shell injection and the hardcoded password. Fixing them means understanding why the code is unsafe, then choosing a replacement that still does the same job. For `os.system` I had to switch to `subprocess.run` with an argument list and add a check that the path exists. For the password I had to decide where the secret should live (an environment variable), keep the demo output the same, and use a constant-time comparison. The `global` statement was also slightly tricky because removing it meant changing how the budget is stored (a `settings` dict).

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes. After I moved the password into an environment variable, Bandit still reported B105 (hardcoded password) on the line that only stores the *name* of that variable, for example `SYNC_SECRET_VAR = "BANK_SYNC_PASSWORD"`. That string is not a password. Bandit matches on words like "password" or "secret" in a string or variable name, so it flagged it anyway. It stopped only after I renamed the variable to `SYNC_ENV_NAME` and the value to `BANK_SYNC_KEY`. The `import subprocess` warning (B404) is similar: the module is flagged even when it is used safely, so I documented that with a `# nosec` comment and a reason.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- Run Flake8 and Pylint in the editor (VS Code or PyCharm) so problems show up as I type.
- Add a pre-commit hook that runs Flake8, Pylint and Bandit, so bad code can't be committed.
- Run all three in a CI pipeline (for example GitHub Actions) on every pull request, and fail the build on High or Medium Bandit findings or a Pylint score below a set threshold (e.g. 9.5).
- Keep the tool configuration (`.pylintrc`, `setup.cfg`, `bandit.yaml`) in the repo so the whole team gets the same results.
- Treat `# nosec` or `# pylint: disable` comments as something that needs a written reason and a review.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Scores:** Pylint went from 5.27/10 to 10.00/10, Bandit from 4 findings (1 High, 2 Medium, 1 Low) to 0, and Flake8 from 4 warnings to none.
- **Security:** The code no longer allows shell injection through a file path, no longer has the temp-file race condition, and no longer stores a password in the repo.
- **Robustness:** `biggest_expense` no longer hides unrelated errors behind `except Exception`. `main()` no longer runs when the file is imported, so the functions can be reused and tested.
- **Readability:** Consistent snake_case names, docstrings on every function, and `enumerate` make the code easier to read and to explain. Removing the `global` makes it clearer where the budget state lives.
- **Behaviour preserved:** The demo prints exactly the same output as before, which showed the fixes did not change what the program does.
