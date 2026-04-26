# tests/test_skill_creator_quick_validate.py
# Where: repository tests for the bundled skill validator.
# What: Checks that quick_validate works without optional YAML dependencies.
# Why: Keep skill creation validation usable in this minimal project environment.

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    ROOT
    / ".agents"
    / "skills"
    / "skill-creator"
    / "scripts"
    / "quick_validate.py"
)


def _load_validator():
    spec = importlib.util.spec_from_file_location("quick_validate", VALIDATOR)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_quick_validate_accepts_minimal_skill_without_pyyaml(tmp_path: Path) -> None:
    skill_dir = tmp_path / "sample-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: sample-skill\n"
        "description: 日本語の説明を含むサンプルskill。\n"
        "---\n"
        "\n"
        "# Sample Skill\n",
        encoding="utf-8",
    )

    valid, message = _load_validator().validate_skill(skill_dir)

    assert valid, message
