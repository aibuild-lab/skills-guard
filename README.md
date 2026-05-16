# skills-guard

Threat scanner and trust matrix for AI skill files.

> Renamed from `skill-vault` on 2026-05-16 because "vault" implied storage; the tool is a scanner/guard. The PyPI package is still published as `skill-vault` for compatibility (see Quick start).

## What it is

`skills-guard` is a static analysis tool that scans AI skill files (the YAML-frontmatter + Markdown bundles that Claude Code, Hermes, and OpenClaw load to teach an agent a new capability) for known threat patterns before installation. It pairs the regex catalog from NousResearch's `hermes-agent` with a 3-level trust matrix so you can decide what gets installed automatically, what needs human review, and what gets blocked outright.

This is the first deliverable in AI Build Lab's "agents that have governance" line of open-source tooling. Bounded, inspectable agents need bounded, inspectable skills. If your agent will execute whatever Markdown file you hand it, you have already lost.

## Why it exists

Skills are a form of code. They land in your agent's prompt, instruct it to run shell commands, and often pre-approve tool access. A malicious or compromised skill can exfiltrate credentials, plant persistence, or hijack the agent's role with a single line of YAML or a hidden Unicode character. Most ecosystems treat skills like static documentation. They are not.

`skills-guard` exists so the same care you apply to a `pip install` from a stranger applies to a `skills-guard --check` before it touches your agent.

## Quick start

```bash
pip install skill-vault

# Scan a skill directory you cloned from somewhere
skills-guard --check ./some-skill

# Scan against a specific source for trust resolution
skills-guard --check ./some-skill --source openai/skills

# JSON output for CI pipelines
skills-guard --check ./some-skill --json

# Add your own trusted source
skills-guard --check ./some-skill --source aibuild-lab/curated --trusted aibuild-lab/curated
```

Exit codes: `0` allowed, `1` blocked, `2` needs confirmation, `3` bad arguments.

## The 3-level trust matrix

| Level | What it means | Default behavior |
|---|---|---|
| **TRUSTED** | Source you have explicitly vetted (e.g. `openai/skills`, `anthropics/skills`, your own curated registry). | Caution verdicts allowed. Dangerous verdicts blocked. |
| **REVIEW_REQUIRED** | Anything you have not explicitly trusted. The default for community skills. | Caution and dangerous verdicts both block. Clean scans pass. |
| **BLOCKED** | Sources you have explicitly denied. | All verdicts blocked, regardless of scan result. |

The verdict itself comes from the underlying scan:

| Verdict | Triggered by |
|---|---|
| `safe` | No findings. |
| `caution` | Only medium or high severity findings. |
| `dangerous` | At least one critical finding. |

The scanner covers prompt injection (DAN, role hijack, deception, restriction bypass), exfiltration (curl/wget with secrets, credential-store reads, DNS tunnelling, markdown image exfil), destructive ops (`rm -rf /`, `dd`, `mkfs`), persistence (cron, shell rc, `authorized_keys`, launchd, sudoers), reverse shells, obfuscation (base64-pipe-shell, hex strings, `eval`), supply-chain risks (unpinned `pip install`, curl-pipe-bash), credential leaks (GitHub PATs, OpenAI keys, AWS keys, private keys), and invisible Unicode characters used for hidden text.

## Library usage

```python
from pathlib import Path
from skill_vault import TrustMatrix

matrix = TrustMatrix.from_lists(
    trusted=["aibuild-lab/curated"],
    blocked=["known-bad-author/skills"],
)

allowed, reason, result = matrix.evaluate(
    Path("./incoming-skill"),
    source="aibuild-lab/curated",
)

if allowed is True:
    print(f"Install OK: {reason}")
elif allowed is None:
    print(f"Needs human review: {reason}")
else:
    print(f"Blocked: {reason}")
    for finding in result.findings:
        print(f"  [{finding.severity}] {finding.file}:{finding.line} -- {finding.description}")
```

## Attribution

`skill_vault/skills_guard.py` is a verbatim port of `tools/skills_guard.py` from [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), used under its MIT license. The full original copyright and license are preserved in the file header and in `LICENSE`.

The threat-pattern catalog, `INSTALL_POLICY` matrix, structural checks, and invisible-Unicode detector are all upstream work. The `trust_matrix.py` wrapper, the `skills-guard` CLI, the example skills, and the test suite are AI Build Lab additions.

If you find a new threat pattern, please submit it upstream to Hermes first. We will re-port the file when it lands.

## Roadmap

- **Phase 1 (now)**: Verbatim port of `skills_guard.py` plus a thin trust-matrix wrapper and CLI. CI runs the threat patterns against a fixture suite on every push.
- **Phase 2**: A clean-room examiner that does semantic analysis on top of the regex layer (does a skill that touches `~/.aws` actually justify it in its description? does it declare `allowed-tools` it does not need?).
- **Phase 3**: A community skill registry with cryptographically-signed publishers, automated scanning on submission, and a curated `aibuild-lab/curated` trusted source.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Threat-pattern improvements should go to Hermes upstream first; trust-matrix and CLI improvements land here.

## License

MIT. See [LICENSE](./LICENSE) for full terms including the upstream Hermes notice.
