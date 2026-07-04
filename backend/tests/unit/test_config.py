"""Definition-of-Done item: .env.example must cover exactly the environment
variables config.py reads — no more, no less."""
from __future__ import annotations

import re
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _env_vars_read_by_config() -> set[str]:
    source = (_PROJECT_ROOT / "backend" / "app" / "config.py").read_text(encoding="utf-8")
    return set(re.findall(r'os\.environ\.get\(\s*"([A-Z_]+)"', source)) | set(
        re.findall(r'os\.environ\[\s*"([A-Z_]+)"\s*\]', source)
    )


def _env_vars_documented_in_example() -> set[str]:
    example = (_PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")
    return {
        line.split("=", 1)[0].strip()
        for line in example.splitlines()
        if line.strip() and not line.strip().startswith("#") and "=" in line
    }


def test_env_example_covers_exactly_the_variables_config_reads():
    assert _env_vars_read_by_config() == _env_vars_documented_in_example()
