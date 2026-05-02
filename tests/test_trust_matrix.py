"""Tests for the 3-level TrustMatrix wrapper."""

from __future__ import annotations

from pathlib import Path

import pytest

from skill_vault import TrustMatrix, TrustLevel


REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = REPO_ROOT / "examples"


def test_default_classifies_unknown_as_review_required():
    matrix = TrustMatrix.default()
    assert matrix.classify_source("random/author") is TrustLevel.REVIEW_REQUIRED


def test_default_classifies_anthropics_skills_as_trusted():
    matrix = TrustMatrix.default()
    assert matrix.classify_source("anthropics/skills") is TrustLevel.TRUSTED
    assert matrix.classify_source("anthropics/skills/foo") is TrustLevel.TRUSTED


def test_default_classifies_openai_skills_as_trusted():
    matrix = TrustMatrix.default()
    assert matrix.classify_source("openai/skills") is TrustLevel.TRUSTED


def test_explicit_trusted_source_overrides_default():
    matrix = TrustMatrix.from_lists(trusted=["aibuild-lab/curated"])
    assert matrix.classify_source("aibuild-lab/curated") is TrustLevel.TRUSTED


def test_blocked_source_is_classified_blocked():
    matrix = TrustMatrix.from_lists(blocked=["evil-corp/skills"])
    assert matrix.classify_source("evil-corp/skills") is TrustLevel.BLOCKED


def test_blocked_source_always_denied_even_for_clean_skill():
    matrix = TrustMatrix.from_lists(blocked=["evil-corp/skills"])
    allowed, reason, result = matrix.evaluate(
        EXAMPLES / "trusted-example",
        source="evil-corp/skills",
    )
    assert allowed is False
    assert "deny list" in reason.lower()
    assert result.verdict == "safe"  # the scan itself was clean


def test_clean_skill_from_unknown_source_is_allowed():
    matrix = TrustMatrix.default()
    allowed, _, result = matrix.evaluate(
        EXAMPLES / "trusted-example",
        source="random/author",
    )
    assert allowed is True
    assert result.verdict == "safe"


def test_malicious_skill_blocked_from_community_source():
    matrix = TrustMatrix.default()
    allowed, _, result = matrix.evaluate(
        EXAMPLES / "malicious-example",
        source="random/author",
    )
    assert allowed is False
    assert result.verdict == "dangerous"


def test_force_overrides_block_for_malicious_skill():
    matrix = TrustMatrix.default()
    allowed, reason, _ = matrix.evaluate(
        EXAMPLES / "malicious-example",
        source="random/author",
        force=True,
    )
    assert allowed is True
    assert "force" in reason.lower()


def test_force_does_not_override_blocked_source():
    """Source-level BLOCKED is stronger than --force on the verdict."""
    matrix = TrustMatrix.from_lists(blocked=["evil-corp/skills"])
    allowed, _, _ = matrix.evaluate(
        EXAMPLES / "trusted-example",
        source="evil-corp/skills",
        force=True,
    )
    assert allowed is False
