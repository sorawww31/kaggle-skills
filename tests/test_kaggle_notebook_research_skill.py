# tests/test_kaggle_notebook_research_skill.py
# Where: repository tests for the Kaggle notebook research skill.
# What: Checks that the shared skill keeps required MCP workflow anchors.
# Why: Prevent accidental edits from dropping fork-aware notebook research steps.

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills" / "kaggle-notebook-research"


def test_kaggle_notebook_research_skill_mentions_required_kaggle_mcp_tools() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "name: kaggle-notebook-research" in skill_text
    assert "search_notebooks" in skill_text
    assert "search_content" in skill_text
    assert "get_notebook_info" in skill_text
    assert "list_notebook_files" in skill_text
    assert "docs/notebooks/" in skill_text


def test_kaggle_notebook_research_skill_requires_fork_and_duplicate_tracking() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "fork_parent_kernel_url" in skill_text
    assert "copy-or-near-copy" in skill_text
    assert "small-mod" in skill_text
    assert "substantial-mod" in skill_text
    assert "Notebookファミリー" in skill_text
    assert "Source Index" in skill_text


def test_kaggle_notebook_research_reference_records_observed_tool_usage() -> None:
    reference_text = (
        SKILL_DIR / "references" / "kaggle_mcp_notebook_tools.md"
    ).read_text(encoding="utf-8")

    assert "birdclef-2026" in reference_text
    assert "search_notebooks" in reference_text
    assert "search_content" in reference_text
    assert "best_public_score" in reference_text
    assert "Family Mapping Checklist" in reference_text


def test_kaggle_notebook_research_openai_prompt_keeps_skill_trigger() -> None:
    openai_yaml = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert "Kaggle Notebook Research" in openai_yaml
    assert "$kaggle-notebook-research" in openai_yaml
