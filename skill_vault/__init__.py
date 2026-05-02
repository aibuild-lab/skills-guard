"""skill-vault — Threat scanner and trust matrix for AI skill files.

Public API:
    scan_skill(path, source) -> ScanResult
    should_allow_install(result, force=False) -> (allowed, reason)
    format_scan_report(result) -> str
    content_hash(path) -> str

    TrustMatrix — convenience wrapper around the 3-level install policy.
"""

from skill_vault.skills_guard import (
    Finding,
    ScanResult,
    THREAT_PATTERNS,
    INSTALL_POLICY,
    TRUSTED_REPOS,
    INVISIBLE_CHARS,
    scan_file,
    scan_skill,
    should_allow_install,
    format_scan_report,
    content_hash,
)
from skill_vault.trust_matrix import TrustMatrix, TrustLevel

__version__ = "0.1.0"

__all__ = [
    "Finding",
    "ScanResult",
    "THREAT_PATTERNS",
    "INSTALL_POLICY",
    "TRUSTED_REPOS",
    "INVISIBLE_CHARS",
    "TrustMatrix",
    "TrustLevel",
    "scan_file",
    "scan_skill",
    "should_allow_install",
    "format_scan_report",
    "content_hash",
    "__version__",
]
