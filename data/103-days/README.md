# 103 days in numbers — the data

`repo-stats.csv` holds the counts behind our "103 days" report, taken from the `main` branch of each of our repositories on 19 November 2026 (Dhaka time). The source code itself stays private; these are only the counts.

| Section | What it counts |
|---|---|
| `by_month`, `repo_total` | Commits on `main`, and pull requests named in those commits, per month and per repository |
| `lines`, `lines_by_area` | Lines of code and lines of tests (physical and non-blank) |
| `structure` | API route handlers, pages, data models, migrations, CI workflows, test files, declared test cases |
| `ai_marker` | Commits whose message carries a Claude co-author or session line |
| `span` | First and last commit, and the number of days with a commit |

**How lines are counted** — see `count_lines.py`: only programming-language files (not JSON, Markdown, YAML, images or lockfiles); dependency, build and generated folders, minified files, built copies and documentation folders are left out. A file is a test when its name contains `.test.` or `.spec.`, or it sits in a test folder.

**Read with care**
- `ai_marker` counts a line in a commit message. It shows which commits name Claude; it is not proof of who typed each line.
- `declared_test_cases` is a static count of `it`/`test` blocks, not a count of tests that passed.
- November covers 1–19 November only.
