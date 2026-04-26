# tests/test_kaggle_fetch_competition_skill.py
# Where: repository tests for the Kaggle competition fetch skill.
# What: Checks that the shared skill keeps required MCP workflow anchors.
# Why: Prevent accidental edits from breaking skill discovery or README workflow.

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills" / "kaggle-fetch-competition"


def test_kaggle_fetch_competition_skill_mentions_required_kaggle_mcp_tools() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "name: kaggle-fetch-competition" in skill_text
    assert "search_content" in skill_text
    assert "list_competition_pages" in skill_text
    assert "list_competition_data_files" in skill_text
    assert "README" in skill_text


def test_kaggle_fetch_competition_openai_prompt_keeps_skill_trigger() -> None:
    openai_yaml = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert "Kaggle Fetch Competition" in openai_yaml
    assert "$kaggle-fetch-competition" in openai_yaml
