"""Tests for the skills-guard CLI entry point."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import pytest

from skill_vault.cli import main


REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"


def _run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


def test_cli_clean_skill_returns_zero():
    rc, out, _ = _run(["--check", str(EXAMPLES / "trusted-example")])
    assert rc == 0
    assert "ALLOWED" in out


def test_cli_malicious_skill_returns_one():
    rc, out, _ = _run(["--check", str(EXAMPLES / "malicious-example")])
    assert rc == 1
    assert "BLOCKED" in out


def test_cli_force_overrides_block():
    rc, out, _ = _run([
        "--check", str(EXAMPLES / "malicious-example"),
        "--force",
    ])
    assert rc == 0
    assert "ALLOWED" in out or "Force" in out


def test_cli_missing_path_returns_three():
    rc, _, err = _run(["--check", "/nonexistent/path/to/skill"])
    assert rc == 3
    assert "not found" in err.lower()


def test_cli_json_output_is_valid_json():
    rc, out, _ = _run([
        "--check", str(EXAMPLES / "malicious-example"),
        "--json",
    ])
    assert rc == 1
    payload = json.loads(out)
    assert payload["skill"] == "malicious-example"
    assert payload["verdict"] == "dangerous"
    assert payload["allowed"] is False
    assert isinstance(payload["findings"], list)
    assert len(payload["findings"]) > 0
    # Spot-check a finding has the expected shape
    f0 = payload["findings"][0]
    for key in ("pattern_id", "severity", "category", "file", "line", "match", "description"):
        assert key in f0


def test_cli_blocked_source_via_flag():
    rc, out, _ = _run([
        "--check", str(EXAMPLES / "trusted-example"),
        "--source", "evil-corp/skills",
        "--blocked", "evil-corp/skills",
    ])
    # Source-level block, regardless of clean scan
    assert rc == 1


def test_cli_trusted_source_via_flag():
    rc, _, _ = _run([
        "--check", str(EXAMPLES / "trusted-example"),
        "--source", "my-org/curated",
        "--trusted", "my-org/curated",
    ])
    assert rc == 0
