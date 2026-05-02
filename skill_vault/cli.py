"""skills-guard — CLI entry point for skill-vault.

Usage:
    skills-guard --check ./path/to/skill
    skills-guard --check ./path/to/skill --source openai/skills
    skills-guard --check ./path/to/skill --json
    skills-guard --check ./path/to/skill --force

Exit codes:
    0  ALLOWED
    1  BLOCKED
    2  NEEDS CONFIRMATION (trust matrix asks)
    3  Bad arguments / file not found
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from skill_vault import (
    TrustMatrix,
    format_scan_report,
)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="skills-guard",
        description=(
            "Threat scanner and install gate for AI skill files. Wraps the "
            "Hermes skills_guard regex catalog with a 3-level trust matrix."
        ),
    )
    p.add_argument(
        "--check",
        metavar="PATH",
        required=True,
        help="Path to a skill directory (or a single SKILL.md file).",
    )
    p.add_argument(
        "--source",
        default="community",
        help=(
            "Source identifier for trust resolution. "
            "Defaults to 'community'. Examples: 'openai/skills', "
            "'anthropics/skills', 'aibuild-lab/skill-vault', 'agent-created'."
        ),
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Override blocked verdicts (useful for testing).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit the scan result as JSON instead of human-readable text.",
    )
    p.add_argument(
        "--trusted",
        action="append",
        default=[],
        metavar="SOURCE",
        help=(
            "Add a source to the trusted list (repeatable). Caution verdicts "
            "from these sources will be allowed."
        ),
    )
    p.add_argument(
        "--blocked",
        action="append",
        default=[],
        metavar="SOURCE",
        help="Add a source to the blocked list (repeatable). Always denied.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    target = Path(args.check).expanduser()
    if not target.exists():
        print(f"error: path not found: {target}", file=sys.stderr)
        return 3

    matrix = TrustMatrix.from_lists(trusted=args.trusted, blocked=args.blocked)
    allowed, reason, result = matrix.evaluate(target, source=args.source, force=args.force)

    if args.json:
        payload = {
            "skill": result.skill_name,
            "source": result.source,
            "trust_level": result.trust_level,
            "verdict": result.verdict,
            "allowed": allowed,
            "reason": reason,
            "scanned_at": result.scanned_at,
            "summary": result.summary,
            "findings": [asdict(f) for f in result.findings],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(format_scan_report(result))
        print(f"Trust matrix: {matrix.classify_source(args.source).value}")
        if allowed is True:
            print(f"Final decision: ALLOWED -- {reason}")
        elif allowed is None:
            print(f"Final decision: NEEDS CONFIRMATION -- {reason}")
        else:
            print(f"Final decision: BLOCKED -- {reason}")

    if allowed is True:
        return 0
    if allowed is None:
        return 2
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
