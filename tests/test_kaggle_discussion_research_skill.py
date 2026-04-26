# tests/test_kaggle_discussion_research_skill.py
# Where: repository tests for the Kaggle discussion research skill.
# What: Checks that the shared skill keeps required MCP and output workflow anchors.
# Why: Prevent accidental edits from dropping comment-aware discussion research steps.

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills" / "kaggle-discussion-research"


def test_kaggle_discussion_research_skill_mentions_required_kaggle_mcp_tools() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "name: kaggle-discussion-research" in skill_text
    assert "list_forum_topics" in skill_text
    assert "get_forum_topic" in skill_text
    assert "includeComments=true" in skill_text
    assert "get_writeup_by_topic" in skill_text
    assert "docs/discussion/" in skill_text


def test_kaggle_discussion_research_skill_requires_comment_and_source_tracking() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "comments[].raw_markdown" in skill_text
    assert "replies[].raw_markdown" in skill_text
    assert "#<comment_id>" in skill_text
    assert "Source Index" in skill_text
    assert "未確認" in skill_text


def test_kaggle_discussion_research_skill_collects_topics_broadly_before_search() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "網羅パス" in skill_text
    assert 'sortBy="Top"' in skill_text
    assert 'sortBy="Hot"' in skill_text
    assert 'sortBy="Recent"' in skill_text
    assert 'sortBy="Active"' in skill_text
    assert "votes" in skill_text
    assert "comment_count" in skill_text
    assert "候補一覧" in skill_text


def test_kaggle_discussion_research_skill_filters_low_value_noise() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "ノイズを判定" in skill_text
    assert "`read` / `skim` / `skip`" in skill_text
    assert "Notebook実行エラー" in skill_text
    assert "環境構築エラー" in skill_text
    assert "提出失敗ログ" in skill_text
    assert "個人環境の実行エラーのみ" in skill_text
    assert "host回答" in skill_text


def test_kaggle_discussion_research_skill_stays_competition_generic() -> None:
    skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    assert "BirdCLEF" not in skill_text
    assert "birdclef" not in skill_text
    assert "<competition-slug>" in skill_text
    assert "表形式" in skill_text
    assert "画像" in skill_text
    assert "音声" in skill_text
    assert "NLP" in skill_text


def test_kaggle_discussion_research_openai_prompt_keeps_skill_trigger() -> None:
    openai_yaml = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")

    assert "Kaggle Discussion Research" in openai_yaml
    assert "$kaggle-discussion-research" in openai_yaml
