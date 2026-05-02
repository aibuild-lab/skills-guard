"""
trust_matrix.py — Three-level trust model for AI skill installation.

Wraps the INSTALL_POLICY matrix from skills_guard.py with a friendlier API
and explicit enums. The underlying policy is unchanged from the upstream
Hermes implementation; this module just makes it easier to reason about.

Trust Levels
------------
TRUSTED          Skills from anthropics/skills, openai/skills, or sources
                 you have explicitly added to trusted_sources. Caution
                 verdicts are allowed; only dangerous verdicts get blocked.

REVIEW_REQUIRED  Default for community sources. Caution and dangerous
                 verdicts both block — the skill must be reviewed by a
                 human before install.

BLOCKED          Sources you have explicitly denied. All verdicts block.
                 Mostly used for known-bad authors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional, Set, Tuple

from skill_vault.skills_guard import (
    ScanResult,
    scan_skill,
    should_allow_install as _hermes_should_allow_install,
)


class TrustLevel(str, Enum):
    """Three-level trust model for skill sources."""

    TRUSTED = "trusted"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"


@dataclass
class TrustMatrix:
    """A trust matrix used to gate skill installation.

    The matrix layers source-level allow/deny on top of the underlying
    Hermes scan policy.

    Attributes:
        trusted_sources:  Source identifiers (e.g. "openai/skills",
                          "aibuild-lab/curated-skills") considered TRUSTED.
        blocked_sources:  Source identifiers always denied regardless of
                          scan verdict.
        default_level:    Trust level applied to anything not in the above
                          sets. Defaults to REVIEW_REQUIRED.
    """

    trusted_sources: Set[str] = field(default_factory=set)
    blocked_sources: Set[str] = field(default_factory=set)
    default_level: TrustLevel = TrustLevel.REVIEW_REQUIRED

    def classify_source(self, source: str) -> TrustLevel:
        """Return the trust level for a given source identifier."""
        if source in self.blocked_sources:
            return TrustLevel.BLOCKED
        if source in self.trusted_sources:
            return TrustLevel.TRUSTED
        # Honour upstream Hermes hardcoded trust list as a fallback.
        # openai/skills and anthropics/skills are TRUSTED by default.
        for prefix in ("openai/skills", "anthropics/skills"):
            if source == prefix or source.startswith(prefix + "/"):
                return TrustLevel.TRUSTED
        return self.default_level

    def evaluate(
        self,
        skill_path: Path,
        source: str,
        force: bool = False,
    ) -> Tuple[Optional[bool], str, ScanResult]:
        """Scan a skill and decide whether it should be installed.

        Returns:
            (allowed, reason, scan_result)
            - allowed=True  -> install
            - allowed=False -> block
            - allowed=None  -> needs human confirmation
        """
        level = self.classify_source(source)
        result = scan_skill(skill_path, source=source)

        # Source-level BLOCKED always wins.
        if level is TrustLevel.BLOCKED:
            return (
                False,
                f"Blocked by trust matrix: source '{source}' is on the deny list.",
                result,
            )

        # Force flag honoured for everything except BLOCKED sources.
        allowed, reason = _hermes_should_allow_install(result, force=force)

        # When level is TRUSTED, upgrade community-default decisions.
        if level is TrustLevel.TRUSTED and allowed is False and not force:
            # Re-scan policy: trusted sources allow caution but not dangerous.
            if result.verdict == "caution":
                return (
                    True,
                    f"Allowed (trusted source override, {result.verdict} verdict).",
                    result,
                )

        return allowed, reason, result

    @classmethod
    def default(cls) -> "TrustMatrix":
        """Return a default trust matrix.

        TRUSTED:         openai/skills, anthropics/skills (via classify_source).
        REVIEW_REQUIRED: everything else.
        BLOCKED:         empty.
        """
        return cls()

    @classmethod
    def from_lists(
        cls,
        trusted: Optional[Iterable[str]] = None,
        blocked: Optional[Iterable[str]] = None,
    ) -> "TrustMatrix":
        """Construct a trust matrix from explicit source lists."""
        return cls(
            trusted_sources=set(trusted or ()),
            blocked_sources=set(blocked or ()),
        )
