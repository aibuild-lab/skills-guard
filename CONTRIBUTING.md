# Contributing to skills-guard

Thanks for your interest. A few rules to keep the project sustainable.

## What goes where

`skill_vault/skills_guard.py` is a **verbatim port** of `tools/skills_guard.py` from NousResearch/hermes-agent. We do not modify it locally. If you want to add or improve a threat pattern, submit your change upstream:

- Repo: https://github.com/NousResearch/hermes-agent
- File: `tools/skills_guard.py`

Once your change lands upstream, open an issue here and we will re-port the file. This keeps the regex catalog single-sourced and avoids drift between projects.

`skill_vault/trust_matrix.py`, `skill_vault/cli.py`, the test suite, the example skills, and the docs are all fair game for direct contributions.

## How to contribute

1. Fork and clone.
2. Create a venv: `python -m venv .venv && source .venv/bin/activate`
3. Install in editable mode with dev deps: `pip install -e '.[dev]'`
4. Run tests: `pytest`
5. Make your change. Add a test for any new behavior.
6. Open a pull request with a clear description of what changed and why.

## Adding a new example skill

Examples live under `examples/` and serve as both documentation and test fixtures. If you add one:

- Put it in `examples/<descriptive-name>/SKILL.md`.
- Add a test in `tests/test_patterns.py` or a new test file that asserts the expected verdict.
- If the example is intentionally malicious, mark it clearly in the SKILL body so no one mistakes it for a usable skill.

## Reporting a vulnerability

If you find a real vulnerability in `skills-guard` itself (not a missing threat pattern), please email tyler@aibuildlab.com instead of opening a public issue. Missing or weak threat patterns should be reported to Hermes upstream.

## Code style

- Python 3.10+.
- No external runtime dependencies. Tests can use pytest.
- Type hints on public APIs.
- Docstrings on anything exported from `skill_vault.__init__`.

## License

By contributing you agree your work is released under the same MIT license as the rest of the project.
