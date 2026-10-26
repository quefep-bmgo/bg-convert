# Contributing

Bug reports and small fixes are welcome. Open an issue first if the change is
more than a small cleanup.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Before a pull request

```powershell
python -m pytest
ruff check .
```

Both commands should pass. The GitHub workflow runs the same checks on Linux and
Windows.

## Rules

- Keep a pull request to one topic.
- Add a test when behavior changes.
- Do not commit world saves, pulled APKs, or the Chunker jar. Those are large and
  easy to download again.
- Keep comments and docs short. Explain the reason, not every line.
- Use plain wording in issues and pull requests. A short example is better than a
  long summary.
